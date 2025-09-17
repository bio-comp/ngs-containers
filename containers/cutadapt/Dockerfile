# containers/cutadapt/Dockerfile
# syntax=docker/dockerfile:1.7
ARG BASE_IMAGE=ghcr.io/bio-comp/ngs-base:latest
FROM ${BASE_IMAGE}
SHELL ["/bin/bash","-lc"]



# Install cutadapt directly
RUN mamba install -y -n base-env -c conda-forge -c bioconda \
    "cutadapt==5.1" "xopen<2.0" \
    && conda clean -afy

RUN cutadapt --version
