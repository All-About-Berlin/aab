# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

All About Berlin is a website for people moving to or living in Berlin. It consists of:
- **Frontend**: Static site built with [Ursus](https://github.com/ursus-ssg/ursus) (Python-based SSG with Jinja2 templates)
- **Backend**: Django REST API handling form submissions, email scheduling, and API proxying
- **Proxy**: Caddy reverse proxy routing between services

## Development Commands

All tasks are run via `mise` (task runner defined in `mise.toml`). Always use these commands to run the website, run tests, etc. Never run `docker compose`, `pytest` and other commands directly.

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

## Architecture

### Frontend (`frontend/`)

- `content/` — Source content: guides, glossary, images, structured data (mostly Markdown + YAML)
- `templates/` — Jinja2 templates for page layout and JavaScript calculators/tools
- `extensions/` — Custom Ursus extensions and linters
- `scripts/` — Utility scripts for content management
- `output/` — Generated static HTML (do not edit directly)

Ursus processes `content/` + `templates/` → `output/` (static HTML served by Caddy).

#### Forms and widgets

Interactive forms, calculators, and letter generators are built with Vue. See `frontend/templates/js/README.md` for the layout of `js/vue/tools`, `js/vue/components`, `js/vue/mixins`, and non-Vue `js/components`.

**Tool metadata.** Every tool in `js/vue/tools/` must have a sibling `<tool-name>.metadata.json` with `label` and `description`. These populate `aria-label`, `aria-description`, the SEO-visible placeholder, and the `<noscript>` fallback rendered by the `{% tool %}` Jinja tag.

```json
{
    "label": "German health insurance calculator",
    "description": "Calculate the cost of German health insurance..."
}
```

**Unique IDs.** A tool can be embedded more than once on a page, so hard-coded `id`/`for` attributes collide. Mix in `uniqueIdsMixin` and wrap every id with `uid(...)`:

```javascript
import uniqueIdsMixin from '/js/vue/mixins/uniqueIds.mjs';
// ...
mixins: [uniqueIdsMixin],
```

```html
<label :for="uid('age')">Age</label>
<age-input :id="uid('age')" v-model="age"></age-input>
```

**Custom inputs.** Prefer the components in `js/vue/components/` (`<checkbox>`, `<radio>`, `<tabs>`, `<date-picker>`, `<country-input>`, `<age-input>`, `<income-input>`, `<email-input>`, `<full-name-input>`, etc.) over raw `<input>` elements. They already handle styling, validation, and `v-model`.

**Form layout.** Wrap each field in `.form-group` (label + control grid). Use `.input-group` inside a `.form-group` when several elements sit inline with the input (units, toggle buttons, secondary hints). For grouped labels without a `<label>` element, use `<span class="label">`.

```html
<div class="form-group">
    <label :for="uid('income')">Income</label>
    <div class="input-group">
        <income-input :id="uid('income')" v-model="inputIncome" required></income-input>&nbsp;€
        <button class="toggle" @click="useMonthlyIncome = !useMonthlyIncome">per {{ useMonthlyIncome ? 'month' : 'year' }}</button>
    </div>
</div>
```

**Input instructions.** Use `.input-instructions` on a `<span>` or `<p>` for helper text under an input, and add `.error` for validation messages. When the helper text links out to a guide or other page on the site for clarifying information, use an `<a>` with both `.input-instructions` and `.internal-link`:

```html
<span class="input-instructions">Use the same date as on your <em><glossary>Wohnungsgeberbestätigung</glossary></em>.</span>
<a class="input-instructions internal-link" href="/guides/german-tax-id-steuernummer#where-to-find-your-tax-id" target="_blank">Find your tax ID</a>
```

**Collapsibles.** Use `<collapsible>` for progressive disclosure (optional sections, advanced options, long explanations). Pass through the tool's `static` prop so the section renders open in the printed/static version:

```html
<collapsible :static="static">
    <template #header>More options</template>
    <!-- content -->
</collapsible>
```

### Backend (`backend/src/`)

Django app with REST Framework. Key Django apps:
- `api/` — REST API endpoints
- `forms/` — Form submissions and email responses
- `insurance/` — Insurance-related features
- `discussion/` — Comments/discussion features

Uses SQLite in development. Runs under Gunicorn in Docker.

### Tests (`tests/`)

Playwright tests using `pytest-playwright`. Tests run on three device profiles (mobile/tablet/desktop) defined in `conftest.py`. Visual regression snapshots are in `tests/snapshots/`. Default timeout is 2 seconds.

### Infrastructure

Docker Compose runs four services: `frontend`, `backend`, `proxy`. Caddy routes `/api/*` to Django and everything else to the static frontend.

## Commit Messages

Format: `scope: Description` (imperative mood, sentence case, no period)

- Use the filename or topic as the scope when the change is localized: `health-insurance-calculator: Mention spam folder`
- Omit the scope for cross-cutting changes: `Remove noise from daily digest email`
- Capitalize the description; keep it concise

## Environment Variables

Copy `.env.example` to `.env`. Required external services: Google Maps API (JavaScript, Places, TTS), Buttondown (newsletter), Open Exchange Rates, OpenAI (monitor LLM filtering), GitHub token (monitor PR creation).