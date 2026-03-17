FROM python:3.13-slim

COPY pyproject.toml /srv/
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && pip3 install --no-cache-dir $(python3 -c "import tomllib; print(' '.join(tomllib.load(open('/srv/pyproject.toml','rb'))['project']['dependencies']))") \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /srv/src/
COPY crontab.conf start.sh monitor.toml /srv/
RUN chmod +x /srv/start.sh

CMD ["/srv/start.sh"]
