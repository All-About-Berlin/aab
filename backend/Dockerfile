FROM python:3.14-slim AS base

# Install dependencies
# cron for various Django commands
# rsync and ssh for database backups
COPY requirements.txt /requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client rsync cron \
    && pip3 install --no-cache-dir -r /requirements.txt \
    && rm -rf /var/lib/apt/lists/* /requirements.txt

COPY gunicorn_config.py crontab.conf start.sh /srv/

WORKDIR /srv/app

EXPOSE 80

# = PROD =======================================================================

FROM base AS prod
ENV DEBUG=0
COPY src/ /srv/app/

CMD ["/srv/start.sh"]

# = DEV ========================================================================

FROM base AS dev
ENV DEBUG=1

CMD ["/srv/start.sh"]