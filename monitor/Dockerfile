FROM python:3.13-slim AS base

COPY pyproject.toml /srv/
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && pip3 install --no-cache-dir $(python3 -c "import tomllib; print(' '.join(tomllib.load(open('/srv/pyproject.toml','rb'))['project']['dependencies']))") \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY crontab.conf start.sh /srv/
RUN chmod +x /srv/start.sh

# = PROD =======================================================================

FROM base AS prod
COPY src/ /srv/src/
COPY config/ /srv/config/
CMD ["/srv/start.sh"]

# = DEV ========================================================================

FROM base AS dev
CMD ["/srv/start.sh", "--debug"]