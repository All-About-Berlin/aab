# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

All About Berlin is a website for people moving to or living in Berlin. It consists of:
- **Frontend**: Static site built with [Ursus](https://github.com/ursus-ssg/ursus) (Python-based SSG with Jinja2 templates)
- **Backend**: Django REST API handling form submissions, email scheduling, and API proxying
- **Proxy**: Caddy reverse proxy routing between services

## Development Commands

All tasks are run via `mise` (task runner defined in `mise.toml`).

| Command | Description |
|---|---|
| `mise setup` | Install dependencies and set up commit hooks (run once after clone) |
| `mise site` | Run frontend only (fast, no Docker) |
| `mise dev` | Run full stack with Docker (frontend + backend + proxy) |
| `mise test` | Run all tests (UI + API) |
| `mise test-ui` | Run Playwright UI tests only |
| `mise test-api` | Run Django tests only |
| `mise lint` | Run all linters (shellcheck, ruff, ursus) |
| `mise format` | Auto-format code (ruff) |
| `mise update-snapshots` | Regenerate visual regression snapshots |

### Running a single test

**UI tests (Playwright):**
```bash
pytest tests/tools/health_insurance_calculator/test_health_insurance_start.py
pytest tests/tools/health_insurance_calculator/test_health_insurance_start.py::test_function_name
```

**Backend tests (Django):**
```bash
docker compose exec backend python3 manage.py test forms.tests
```

## Architecture

### Frontend (`frontend/`)

- `content/` — Source content: guides, glossary, images, structured data (mostly Markdown + YAML)
- `templates/` — Jinja2 templates for page layout and JavaScript calculators/tools
- `extensions/` — Custom Ursus extensions and linters
- `scripts/` — Utility scripts for content management
- `output/` — Generated static HTML (do not edit directly)

Ursus processes `content/` + `templates/` → `output/` (static HTML served by Caddy).

### Backend (`backend/src/`)

Django app with REST Framework. Key Django apps:
- `api/` — REST API endpoints
- `forms/` — Form submissions and email responses
- `insurance/` — Insurance-related features
- `discussion/` — Comments/discussion features

Uses SQLite in development. Runs under Gunicorn in Docker.

### Tests (`tests/`)

Playwright tests using `pytest-playwright`. Tests run on three device profiles (mobile/tablet/desktop) defined in `conftest.py`. Visual regression snapshots are in `tests/snapshots/`. Default timeout is 2 seconds.

### Monitor (`monitor/`)

Standalone ETL pipeline that monitors external websites for relevant changes. Uses an LLM to filter content and triggers actions when relevant changes are detected.

Crawlers and actions are discovered via Python entry points defined in `pyproject.toml` (`aab_monitor.crawlers` and `aab_monitor.actions` groups). Domain-level config (delay, selector) is merged with monitor-level config, with monitor-level taking precedence.

### Infrastructure

Docker Compose runs four services: `frontend`, `backend`, `proxy`, `monitor`. Caddy routes `/api/*` to Django and everything else to the static frontend.

## Commit Messages

Format: `scope: Description` (imperative mood, sentence case, no period)

- Use the filename or topic as the scope when the change is localized: `health-insurance-calculator: Mention spam folder`
- Omit the scope for cross-cutting changes: `Remove noise from daily digest email`
- Capitalize the description; keep it concise

## Environment Variables

Copy `.env.example` to `.env`. Required external services: Google Maps API (JavaScript, Places, TTS), Buttondown (newsletter), Open Exchange Rates, OpenAI (monitor LLM filtering), GitHub token (monitor PR creation).