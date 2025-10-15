FROM python:3.14-slim AS base

# Install dependencies
COPY requirements.txt /requirements.txt

# Rsync needed for prod builds
# Git needed by ursus to build the site
RUN apt-get update \
    && apt-get install -y --no-install-recommends git rsync \
        build-essential \
        python3-dev \
    && pip3 install --no-cache-dir -r /requirements.txt \
    && mkdir -p /var/output /var/live-output \
    && rm -rf /var/lib/apt/lists/* /requirements.txt

WORKDIR /var/project/frontend

# = PROD =======================================================================

FROM base AS prod
CMD python3 /var/project/frontend/build-for-prod.py

# = DEV ========================================================================

FROM base AS dev

# Build properly once, rebuild quickly on file changes
CMD ursus && ursus --fast --watch