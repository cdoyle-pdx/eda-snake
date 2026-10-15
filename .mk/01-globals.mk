ifndef DISABLE_MAKE_DEFAULTS
# Always run jobs in parallel
NO_OF_JOBS ?= $(shell nproc)
MAKEFLAGS += --jobs=$(NO_OF_JOBS)
# Force synced output per target always
MAKEFLAGS += --output-sync=target
endif

# Host properties section start
ARCH_QUERY ?= $(shell uname -m)
ifeq ($(ARCH_QUERY), x86_64)
	ARCH := amd64
else ifeq ($(ARCH_QUERY),$(filter $(ARCH_QUERY), arm64 aarch64))
	ARCH := arm64
else
	ARCH := $(ARCH_QUERY)
endif

# i.e Darwin / Linux
UNAME ?= $(shell uname)
# Lowercase - sane version
OS ?= $(shell echo "$(UNAME)" | tr '[:upper:]' '[:lower:]')
# Host properties section end

CONTAINER_TOOL ?= docker
PACKAGE_OPERATION ?= load
PLATFORM ?= linux/amd64

ifeq ($(CONTAINER_TOOL),podman)
# $1 Dockerfile, $2 image tag, $3 build context
container-package = podman build --platform $(PLATFORM) -f $(1) -t "$(2)" $(if $(TARGET_IMAGE),--build-arg TARGET_IMAGE=$(TARGET_IMAGE),) $(DOCKER_BUILD_ARGS) $(3)$(if $(filter push,$(PACKAGE_OPERATION)), && podman push "$(2)",)
else
container-package = docker buildx build --platform $(PLATFORM) -f $(1) --$(PACKAGE_OPERATION) -t "$(2)" $(if $(TARGET_IMAGE),--build-arg TARGET_IMAGE=$(TARGET_IMAGE),) $(DOCKER_BUILD_ARGS) $(3)
endif

# Global lists to hold targets`
LIST_PUBLISH_APPS=
LIST_MOD_TIDY=
LIST_TESTS=
LIST_GENERATE=

LIST_BUILD_OPERATORS=
LIST_PACKAGE_OPERATORS=

LIST_BUILD_WORKFLOWS=
LIST_PACKAGE_WORKFLOWS=

# Help registry
HELP_TARGETS=

# Find all of the apps
APPS ?= $(shell find * -maxdepth 1 -type f -name manifest.yaml -exec dirname {} \; | sed 's|^\./||')
