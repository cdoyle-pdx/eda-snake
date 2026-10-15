# EDA generated start
SHELL ?= /bin/bash -eo pipefail
.DEFAULT_GOAL=help

TOP_DIR := $(abspath $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
MKLIBS=$(TOP_DIR)/.mk
include $(sort $(wildcard $(MKLIBS)/*.mk))
# EDA generated stop
