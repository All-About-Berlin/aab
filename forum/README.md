# Forum

This is the [Misago](https://misago-project.org/) forum served at `/forum`, behind the same Caddy proxy as the rest of the site.

## Quick overview

### Services

The forum runs as four containers, all defined in `forum/docker-compose.yml` and included from the top-level compose files:

- `forum` — the Misago Django app, served over uWSGI on port 80 (proxied by Caddy).
- `forum-celery` — background worker for asynchronous tasks (email sending, thread reindexing, etc.).
- `forum-postgres` — Postgres database, pinned to a specific minor Alpine tag.
- `forum-redis` — Redis for caching and as the Celery broker, pinned to a specific minor Alpine tag.

Static files and uploaded media are written to the `forum_staticfiles` and `forum_media` named volumes, mounted read-only into the Caddy proxy so `/forum/static/*` and `/forum/media/*` are served directly without hitting Django.

### Image

The forum image is built directly from [rafalp/misago_docker](https://github.com/rafalp/misago_docker) via Docker Compose's git-URL build context, pinned to a specific commit SHA. Nothing is vendored into this repo. Migrations and `collectstatic` run automatically on container boot.

### Settings

`settings_override.py` holds our Django settings overrides (sub-path deployment, cookie scoping, TLS-behind-proxy, logging). It's bind-mounted into the container at `/misago/misagodocker/settings_override.py`; upstream's `settings.py` imports it at the end.

## Building

The forum starts as part of the normal `mise dev`. After the first boot, create an admin user:

```
mise forum:createsuperuser
```

The forum reads the shared `SECRET_KEY` env var (see `.env.example`) — the same Django secret key used by the backend API.

The Postgres database is only reachable on the internal Docker network, so it uses trust auth (no password). Connection details live in `settings_override.py`.

## Removal

Delete `forum/` and remove the two `include:` lines that reference it from the top-level compose files. The forum has no coupling to the frontend or backend.