# syntax=docker/dockerfile:1
ARG PANE_RUNTIME_BASE_IMAGE=pane-dev-runtime:phase1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS soundatlas-python
FROM ${PANE_RUNTIME_BASE_IMAGE}
USER root
COPY --from=soundatlas-python /usr/local /usr/local
RUN mkdir -p /runtime/project-cache/uv && chown -R pane:pane /runtime/project-cache
USER pane
ENV UV_PROJECT_ENVIRONMENT=/runtime/project-cache/uv
