# containers/cutadapt/Dockerfile
# syntax=docker/dockerfile:1.7
ARG BASE_IMAGE=ghcr.io/bio-comp/ngs-base:latest
FROM ${BASE_IMAGE}
SHELL ["/bin/bash","-lc"]

# Update the base-env created in the base image
COPY containers/cutadapt/environment.yaml /tmp/environment.yaml
RUN mamba env update -n base-env -f /tmp/environment.yaml && conda clean -afy

# Sanity check
RUN cutadapt --version
