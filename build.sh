#!/usr/bin/env bash
# Reproduces this project with edabuilder, then builds and deploys it.
# Run from the directory ABOVE the project (edabuilder init creates it).
set -euo pipefail

VENDOR="${VENDOR:-nokia-gtm}"
PROJECT="${PROJECT:-eda-snake}"
IMAGE="${IMAGE:-ghcr.io/nokia-gtm/eda-snake-ui:v0.1.0}"

step(){ printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }

step "1/7  Initialise the project"
# Creates common/, test/, utils/, PROJECT, go.work, pyproject.toml, .env*
edabuilder init --vendor "$VENDOR" "$PROJECT"
cd "$PROJECT"

step "2/7  Python virtualenv (autocompletion + linting for intents)"
uv sync || echo "uv not installed; skipping venv"

step "3/7  Create the app"
edabuilder create app snake

step "4/7  Create the API resources"
cd snake
# SnakeScore is a plain CRD: no device config is generated, so no config intent.
edabuilder create resource SnakeScore
# SnakeLeaderboard carries the ranking logic, so it gets a state intent.
edabuilder create resource SnakeLeaderboard --scaffold-state

step "5/7  Overlay this repo's sources over the scaffold"
# API types, the real state intent, manifest components, k8s, rbac, bootstrap.
# (In a fresh clone these files are already in place; this is a no-op.)

step "6/7  Generate CRDs, OpenAPI and the python SDK"
# Reads api/v1alpha1/*.go -> crds/, openapiv3/, api/v1alpha1/pysrc/, manifest
edabuilder generate

step "6b/7  App install-time settings"
# Collects the '# app-set: ${...}' annotations from k8s/deployment.yaml
edabuilder generate appsettings
edabuilder generate appsettings-openapi

step "7/7  Build the UI image, then deploy the app"
docker build -t "$IMAGE" .
docker push "$IMAGE" || echo "push skipped (using in-cluster registry?)"

# in-cluster is the default deploy target: builds, publishes and installs in one
# shot against the dev registry + catalog that edabuilder deploys in the cluster.
edabuilder deploy

printf '\n\033[1;32mDone.\033[0m  Snake should now appear in the EDA UI menu tree.\n'
