.PHONY: format lint typecheck check shellcheck test test-api test-ui help

# Python source directories (excludes migrations and venv)
PY_BACKEND := backend/src
PY_FRONTEND := frontend/extensions frontend/scripts frontend/build-for-prod.py frontend/ursus_config.py
PY_TESTS := tests
PY_ALL := $(PY_BACKEND) $(PY_FRONTEND) $(PY_TESTS)

# Shell scripts
SH_FILES := $(shell find . -type f -name "*.sh" -not -path '*/[@.]*')

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# = FORMATTING =================================================================

format: ## Auto-format all code (Python via ruff)
	@echo "[format] Python (ruff format)..."
	@ruff format $(PY_ALL)
	@echo "[format] Done."

# = LINTING ====================================================================

lint: lint-python lint-shell lint-editorconfig lint-ursus ## Run all linters
	@echo "[lint] All linters passed."

lint-python: ## Lint Python files (ruff check)
	@echo "[lint] Python (ruff check)..."
	@ruff check $(PY_ALL)

lint-shell: ## Lint shell scripts (shellcheck)
	@echo "[lint] Shell scripts (shellcheck)..."
	@$(if $(SH_FILES),shellcheck $(SH_FILES),echo "  No shell scripts found.")

lint-editorconfig: ## Check file formatting consistency (editorconfig-checker)
	@echo "[lint] EditorConfig (ec)..."
	@ec

lint-ursus: ## Lint content and templates (ursus lint)
	@echo "[lint] Ursus content..."
	@ursus lint --level=ERROR -c frontend/ursus_config.py

# = TYPE CHECKING ==============================================================

typecheck: ## Type-check Python code (pyrefly)
	@echo "[typecheck] Python (pyrefly)..."
	@pyrefly check $(PY_BACKEND) $(PY_FRONTEND)

# = COMBINED CHECKS ============================================================

check: format lint typecheck ## Run format + lint + typecheck (full pre-commit suite)
	@echo "[check] All checks passed."

# = TESTING ====================================================================

test: test-api test-ui ## Run all tests
	@echo "[test] All tests passed."

test-api: ## Run backend API tests (Django, inside Docker)
	@echo "[test] API tests..."
	@docker compose exec backend python3 manage.py test -b --verbosity 0

test-ui: ## Run UI snapshot tests (Playwright)
	@echo "[test] UI tests..."
	@pytest tests

# = UTILITIES ==================================================================

setup: ## Install dependencies and bootstrap dev environment
	@mise setup

dev: ## Start full Docker stack (frontend + backend + proxy)
	@mise dev

site: ## Start frontend-only dev server (fast, no Docker)
	@mise site
