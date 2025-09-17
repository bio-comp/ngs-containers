# containers/base/Dockerfile
# syntax=docker/dockerfile:1.7
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8

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

# mamba on PATH
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

# *** Make the env active for all later layers AND runtime ***
ENV PATH=/opt/conda/envs/${CONDA_ENV_NAME}/bin:/opt/conda/bin:$PATH

# ---- Install your Python package into the env ----
WORKDIR /app
COPY pyproject.toml ./
COPY ngs_core ./ngs_core/
# Use uv since it's in the env; fallback to pip if needed
RUN (uv --version >/dev/null 2>&1 && uv sync --frozen-lockfile) || true \
    && (uv --version >/dev/null 2>&1 && uv pip install --no-cache --no-deps -e .) \
    || python -m pip install --no-cache-dir .

# Default logging mode
ENV LOG_FORMAT=json

# Non-root
RUN useradd -m -u 1000 app
USER app
WORKDIR /data

ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["/bin/bash"]
