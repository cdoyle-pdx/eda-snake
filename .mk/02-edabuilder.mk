# TODO: Should be download edabuilder here but then how will the get the scaffold ?
# probably should download it here if we don't find it in path maybe
# depend on gh to download latest or pin a version
# curl a binary ?
EB := $(shell command -v edabuilder 2> /dev/null)

# ifeq ($(EB),)
# $(error [ERROR] Could not find edabuilder in $$PATH)
# endif
