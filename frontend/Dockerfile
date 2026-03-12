FROM python:3.13-slim AS base

# Install dependencies
COPY requirements.txt /requirements.txt

# Rsync needed for prod builds
# Git needed by ursus to build the site
RUN apt-get update \
    && apt-get install -y --no-install-recommends git rsync \
        build-essential \
        python3-dev \
        curl \
    && pip3 install --no-cache-dir -r /requirements.txt \
    && mkdir -p /var/output /var/live-output \
    && rm -rf /var/lib/apt/lists/* /requirements.txt \
    && sh -c 'curl -fsSL https://esbuild.github.io/dl/v0.27.3 | sh' \
    && mv ./esbuild /usr/local/bin/esbuild

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