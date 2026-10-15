.PHONY: build-operators
HELP_TARGETS += build-operators
HELP_build-operators := Build all operator binaries (vars: GOOS, GOARCH)
build-operators: $(LIST_BUILD_OPERATORS)

.PHONY: build-workflows
HELP_TARGETS += build-workflows
HELP_build-workflows := Build all workflow binaries (vars: GOOS, GOARCH)
build-workflows: $(LIST_BUILD_WORKFLOWS)

.PHONY: package-operators
HELP_TARGETS += package-operators
HELP_package-operators := Build all operator containers (vars: CONTAINER_TOOL, PLATFORM, REGISTRY, PACKAGE_OPERATION, TARGET_IMAGE, DOCKER_BUILD_ARGS)
package-operators: $(LIST_PACKAGE_OPERATORS)

.PHONY: package-workflows
HELP_TARGETS += package-workflows
HELP_package-workflows := Build all workflow containers (vars: CONTAINER_TOOL, PLATFORM, REGISTRY, PACKAGE_OPERATION, TARGET_IMAGE, DOCKER_BUILD_ARGS)
package-workflows: $(LIST_PACKAGE_WORKFLOWS)

.PHONY: publish-apps
HELP_TARGETS += publish-apps
HELP_publish-apps := Build and publish all apps
publish-apps: $(LIST_PUBLISH_APPS)

.PHONY: mod-tidy
HELP_TARGETS += mod-tidy
HELP_mod-tidy := Run go mod tidy for all apps
mod-tidy: $(LIST_MOD_TIDY)

.PHONY: test
HELP_TARGETS += test
HELP_test := Run tests for all apps
test: $(LIST_TESTS)

.PHONY: generate
HELP_TARGETS += generate
HELP_generate := Run edabuilder generate for all apps
generate: $(LIST_GENERATE)

MACHINE_ALL=
MACHINE_ALL += mod-tidy
MACHINE_ALL += test
MACHINE_ALL += generate
MACHINE_ALL += build-operators
MACHINE_ALL += build-workflows
MACHINE_ALL += package-operators
MACHINE_ALL += package-workflows
MACHINE_ALL += publish-apps
.PHONY: all
HELP_TARGETS += all
HELP_all := Run all aggregate targets
all: | $(MACHINE_ALL)

.PHONY: help
HELP_TARGETS += help
HELP_help := Show this help text

define print-target-line
$(info $(shell printf "  %-32s %s" "$(1)" "$(strip $(2))"))
endef

define print-section-header
$(info $(shell printf "  %s:" "$(1)"))
endef

define print-target-line-indented
$(info $(shell printf "    %-40s %s" "$(1)" "$(strip $(2))"))
endef

define print-target-list
$(if $(strip $(2)),$(call print-section-header,$(1))$(foreach t,$(sort $(2)),$(call print-target-line-indented,$(t),$(value HELP_$(t)))),)
endef

help:
	@$(info Aggregate targets:)
	@$(foreach t,$(sort all build-operators build-workflows package-operators package-workflows publish-apps mod-tidy test generate help),$(call print-target-line,$(t),$(value HELP_$(t))))
	@$(foreach app,$(APPS),$(info )$(info $(shell printf "\033[32m%s\033[0m" "$(app)"))$(call print-target-list,app,$(filter $(app)-%,$(LIST_PUBLISH_APPS) $(LIST_MOD_TIDY) $(LIST_TESTS) $(LIST_GENERATE)))$(call print-target-list,operators,$(filter $(app)-%,$(LIST_BUILD_OPERATORS) $(LIST_PACKAGE_OPERATORS)))$(call print-target-list,workflows,$(filter $(app)-%,$(LIST_BUILD_WORKFLOWS) $(LIST_PACKAGE_WORKFLOWS))))
	@$(info )
	@$(info APPS: $(APPS))
	@$(info )
	@$(info Variables:)
	@$(call print-section-header,global (all targets))
	@$(call print-target-line-indented,APPS,Space-separated list of app dirs to operate on (default: all))
	@$(call print-target-line-indented,NO_OF_JOBS,Number of parallel make jobs (default: nproc))
	@$(call print-section-header,package-operators / package-workflows)
	@$(call print-target-line-indented,CONTAINER_TOOL,Container CLI for package targets: docker (default) or podman)
	@$(call print-target-line-indented,PLATFORM,Target platform for package builds (default: linux/amd64))
	@$(call print-target-line-indented,DOCKER_BUILD_ARGS,Extra arguments appended to the container build command)
	@$(call print-target-line-indented,PACKAGE_OPERATION,What buildx does with package images: load (default, into local docker store) or push (to $(REGISTRY)))
	@$(call print-target-line-indented,REGISTRY,If using PACKAGE_OPERATION=push, container registry for package targets (default: $(REGISTRY)))
	@$(call print-target-line-indented,TARGET_IMAGE,Overrides the base image via --build-arg TARGET_IMAGE)
	@true