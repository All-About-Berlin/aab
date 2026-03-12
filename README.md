# All About Berlin

This is the main repository for [All About Berlin](https://allaboutberlin.com). It contains the templates, content and backend to render the website.

## Quick overview

### Frontend

The frontend is a static website built with [ursus](https://github.com/all-about-berlin/ursus/), a purpose-built static site generator. This is the website you see when you visit [allaboutberlin.com](https://allaboutberlin.com). The ursus static site generator is [in a separate repository](https://github.com/all-about-berlin/ursus/).

Directory structure:

- `frontend` contains all files needed to render the website
- `frontend/templates` contains the templates used to generate the website's pages. That's also where the frontend code for the calculators is stored.
- `frontend/content` contains the website's content: guides, tools, glossary entries, images etc.
- `frontend/extensions` contains ursus extensions and linters that are specific to All About Berlin.
- `frontend/scripts` contains utility scripts

### Backend

The backend a REST API built with Django and Django REST Framework. The API handles form submissions, email scheduling and other dynamic features. It also proxies APIs for newsletter subscriber management and currency conversions.

Most tools on the website entirely run in the browser, so they don't call the API.

## Building

This project uses [mise](https://mise.jdx.dev/) to simplify dev tasks. You must install it first.

1. Run `mise install` to install required tools.
2. Run `mise setup` to install local dependencies, set up commit hooks, etc.
3. Run `mise dev` to start docker, build the website and start a local server. This will build and start the project inside docker containers. The website is served at `https://localhost`. The frontend/backend are reloaded on changes.

You can also run `mise site` to only run a minimal frontend. It's much faster than running docker, and it's enough for frontend development and content changes.

### Production

See the [production README](.prod/README.md).

## Testing

`mise test` runs all available tests.

`mise test-ui` only runs the UI tests. Run `mise update-snapshots` to generate new visual testing snapshots when the UI changes.

Run `mise test-api` to only run the backend and API tests.

There are frontend unit tests. You can see them at `https://localhost/tests/unit`. These are run with the other tests.

## Linting

`mise lint` runs the project's various linters. It's run automatically before committing.

`mise format` automatically applies certain linting rules.

## Contributing

See the [notes for contributors](CONTRIBUTORS.md).