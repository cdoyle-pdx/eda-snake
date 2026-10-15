REGISTRY ?= ghcr.io/cdoyle-pdx

# operators
# $1 app dir where the manifest.yaml is.
# $2 name of the operator in $1/operators/<name>
define generate-targets-operators
LIST_BUILD_OPERATORS += $(1)-$(2)-build
HELP_TARGETS += $(1)-$(2)-build
HELP_$(1)-$(2)-build := Build operator binary for $(1)/operators/$(2) (vars: GOOS, GOARCH, CGO_ENABLED)
.PHONY: $(1)-$(2)-build
$(1)-$(2)-build:
	GOOS=$(if $(GOOS),$(GOOS),linux) GOARCH=$(if $(GOARCH),$(GOARCH),amd64) CGO_ENABLED=$(if $(CGO_ENABLED),$(CGO_ENABLED),0) go -C "$(1)" build -a -trimpath -ldflags "-s -w" -o "build/operators/$(2)/$(2)" "./operators/$(2)/cmd"

LIST_PACKAGE_OPERATORS += $(1)-$(2)-package
HELP_TARGETS += $(1)-$(2)-package
HELP_$(1)-$(2)-package := Build operator container for $(1)/operators/$(2) (vars: CONTAINER_TOOL, PLATFORM, REGISTRY, PACKAGE_OPERATION, TARGET_IMAGE, DOCKER_BUILD_ARGS)
.PHONY: $(1)-$(2)-package
$(1)-$(2)-package:
	$(call container-package,$(1)/operators/$(2)/Dockerfile,$(REGISTRY)/$(1)/operators/$(2):latest,$(1))
endef

# workflows
# $1 app dir where the manifest.yaml is.
# $2 name of the operator in $1/operators/<name>
define generate-targets-workflows
LIST_BUILD_WORKFLOWS += $(1)-$(2)-build
HELP_TARGETS += $(1)-$(2)-build
HELP_$(1)-$(2)-build := Build workflow binary for $(1)/workflows/$(2) (vars: GOOS, GOARCH, CGO_ENABLED)
.PHONY: $(1)-$(2)-build
$(1)-$(2)-build:
	GOOS=$(if $(GOOS),$(GOOS),linux) GOARCH=$(if $(GOARCH),$(GOARCH),amd64) CGO_ENABLED=$(if $(CGO_ENABLED),$(CGO_ENABLED),0) go -C "$(1)" build -a -trimpath -ldflags "-s -w" -o "build/workflows/$(2)/$(2)" "./workflows/$(2)/cmd"

LIST_PACKAGE_WORKFLOWS += $(1)-$(2)-package
HELP_TARGETS += $(1)-$(2)-package
HELP_$(1)-$(2)-package := Build workflow container for $(1)/workflows/$(2) (vars: CONTAINER_TOOL, PLATFORM, REGISTRY, PACKAGE_OPERATION, TARGET_IMAGE, DOCKER_BUILD_ARGS)
.PHONY: $(1)-$(2)-package
$(1)-$(2)-package:
	$(call container-package,$(1)/workflows/$(2)/Dockerfile,$(REGISTRY)/$(1)/workflows/$(2):latest,$(1))
endef

# eda-apps
# $1 app dir where the manifest.yaml is.
define generate-targets
LIST_PUBLISH_APPS += $(1)-publish
HELP_TARGETS += $(1)-publish
HELP_$(1)-publish := Build and publish app $(1)
.PHONY: $(1)-publish
$(1)-publish:
	edabuilder --app "$(1)" build-publish

LIST_MOD_TIDY += $(1)-mod-tidy
HELP_TARGETS += $(1)-mod-tidy
HELP_$(1)-mod-tidy := Run go mod tidy for app $(1)
.PHONY: $(1)-mod-tidy
$(1)-mod-tidy:
	go -C "$(1)" mod tidy

LIST_TESTS += $(1)-test
HELP_TARGETS += $(1)-test
HELP_$(1)-test := Run go tests for app $(1)
.PHONY: $(1)-test
$(1)-test:
	go -C "$(1)" test ./...

LIST_GENERATE += $(1)-generate
HELP_TARGETS += $(1)-generate
HELP_$(1)-generate := Run edabuilder generate for app $(1)
.PHONY: $(1)-generate
$(1)-generate:
	edabuilder generate --app "$(1)"

CONTROLLER_$(1) := $$(if $(wildcard $(1)/operators),$$(shell find $(1)/operators -maxdepth 1 -mindepth 1 -type d -exec basename {} \;))
$$(foreach op,$$(CONTROLLER_$(1)),$$(eval $$(call generate-targets-operators,$(1),$$(op))))

WORKFLOWS_$(1) := $$(if $(wildcard $(1)/workflows),$$(shell find $(1)/workflows -maxdepth 1 -mindepth 1 -type d -exec basename {} \;))
$$(foreach wf,$$(WORKFLOWS_$(1)),$$(eval $$(call generate-targets-workflows,$(1),$$(wf))))

endef

ifdef APPS
$(foreach app,$(APPS),$(eval $(call generate-targets,$(app))))
else
$(error [ERROR] could not find any eda applications or APPS=<> is overridden to empty)
endif
