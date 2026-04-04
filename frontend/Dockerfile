FROM ghcr.io/astral-sh/uv:0.9.1-python3.13-bookworm-slim AS base

# Rsync needed for prod builds
# Git needed by ursus to build the site
RUN apt-get update \
    && apt-get install -y --no-install-recommends git rsync \
        build-essential \
        python3-dev \
        curl \
    && mkdir -p /var/output /var/live-output \
    && rm -rf /var/lib/apt/lists/* \
    && sh -c 'curl -fsSL https://esbuild.github.io/dl/v0.27.3 | sh' \
    && mv ./esbuild /usr/local/bin/esbuild

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN uv pip install --system --no-cache -r /requirements.txt \
    && rm /requirements.txt

ENV URSUS_OUTPUT_DIR=/var/output

WORKDIR /var/project/frontend

# = PROD =======================================================================

FROM base AS prod
CMD python3 /var/project/frontend/build-for-prod.py

# = DEV ========================================================================

FROM base AS dev

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s CMD [ -n "$BUILD_FINISHED" ] || exit 1

# Build properly once, rebuild quickly on file changes
CMD rm -f /tmp/build_finished;\
    ursus;\
    touch /tmp/build_finished;\
    ursus --fast --watch

# Container becomes healthy after initial build
HEALTHCHECK --start-interval=1s --start-period=15m \
  CMD [ -f /tmp/build_finished ] || exit 1