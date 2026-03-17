#!/bin/sh
set -e
set -x

# Start cron for the daily digest
printenv > /etc/environment
crontab /srv/crontab.conf
service cron start

exec python3 /srv/src/main.py --config /srv/monitor.toml
