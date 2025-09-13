# containers/base/Dockerfile
# syntax=docker/dockerfile:1.7

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# minimal OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    bzip2 ca-certificates curl git procps tzdata tini \
    && rm -rf /var/lib/apt/lists/*

# Install Mambaforge (multi-arch)
ARG MAMBA_VERSION="23.11.0-0"
ARG TARGETARCH
RUN case "${TARGETARCH}" in \
    amd64) MAMBA_ARCH="x86_64" ;; \
    arm64) MAMBA_ARCH="aarch64" ;; \
    *) echo "Unsupported arch: ${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL \
    "https://github.com/conda-forge/miniforge/releases/download/${MAMBA_VERSION}/Mambaforge-${MAMBA_VERSION}-Linux-${MAMBA_ARCH}.sh" \
    -o /tmp/mamba.sh \
    && bash /tmp/mamba.sh -b -p /opt/conda \
    && rm /tmp/mamba.sh

# Make conda available
ENV PATH=/opt/conda/bin:$PATH

# Use bash -lc for subsequent RUN so "conda/mamba" works
SHELL ["/bin/bash", "-lc"]

# Set default channels (conda-forge first), faster solvers
RUN conda config --system --add channels conda-forge \
    && conda config --system --set channel_priority strict \
    && conda config --system --set always_yes true

# Create a non-root user for safety
RUN useradd -m -u 1000 app
USER app
WORKDIR /data

# TODO: Pre-create an environment so child images can be smaller/faster
# COPY environment.yml /tmp/environment.yml
# RUN mamba env create -n base-env -f /tmp/environment.yml \
#  && conda clean -afy \
#  && echo 'export PATH=/opt/conda/envs/base-env/bin:$PATH' >> ~/.profile

ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["/bin/bash"]
