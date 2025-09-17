# containers/base/Dockerfile
# syntax=docker/dockerfile:1.7
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

# OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    bzip2 ca-certificates curl git graphviz pigz procps tzdata tini \
    && rm -rf /var/lib/apt/lists/*

# ---- Mambaforge (multi-arch) ----
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

ENV PATH=/opt/conda/bin:$PATH
SHELL ["/bin/bash","-lc"]

# Channels + solver
RUN conda config --system --add channels conda-forge \
    && conda config --system --set channel_priority strict \
    && conda config --system --set always_yes true

# ---- Create env ----
ARG CONDA_ENV_NAME=base-env
COPY containers/base/environment.yaml /tmp/environment.yaml
RUN mamba env create -n ${CONDA_ENV_NAME} -f /tmp/environment.yaml \
    && conda clean -afy

# Make the env active for all later layers and runtime
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/conda/bin:$PATH

# ---- Install Python package into the env ----
WORKDIR /app

# Copy metadata first
COPY pyproject.toml ./
COPY README.md LICENSE* ./

# Copy the package
COPY ngs_core ./ngs_core/

# Debug
RUN python -V && python -m pip --version && ls -al && find ngs_core -maxdepth 2 -type f -print

# Install with verbose logs and without build isolation
# (so it uses the conda env you just created)
RUN python -m pip install -vv --no-build-isolation --no-cache-dir .

# Default logging mode
ENV LOG_FORMAT=json

# Non-root
RUN useradd -m -u 1000 app
USER app
WORKDIR /data

ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["/bin/bash"]
