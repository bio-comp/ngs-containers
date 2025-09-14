UID := $(shell id -u)
GID := $(shell id -g)

#  Container build targets
build-base:
		docker build -t bio-comp/ngs-containers/base:latest ./containers/base/

build-cutadapt: build-base
		docker build -t  bio-comp/ngs-containers/cutadapt:latest ./containers/cutadapt


# Container run targets
run-cutadapt:
		docker run --rm --it \
				-v $(CURDIR):/data  \
				-u $(UID):$(GID) \
				bio-comp/ngs-containers/cutadapt:latest $(ARGS)

.PHONY build-base build-cutadapt run-cutadapt
