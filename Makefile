# JobSearch Project Automation
VENV = venv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python3
MANAGE = $(PYTHON) manage.py
BACKUP_DIR = backups
TIMESTAMP := $(shell date +%F_%H%M%S)


.PHONY: help setup install migrate run test shell clean backup restore format lint all

help: ## Display this help screen
	@perl -ne 'printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 if /^([a-zA-Z_-]+):.*##\s*(.*)$$/' $(MAKEFILE_LIST) | sort

setup:  ## Create venv and install dependencies
	@echo "[INFO] Initializing Virtual Environment..."
	python3 -m venv $(VENV) && \
	$(BIN)/pip install --upgrade pip && \
	$(BIN)/pip install -r requirements.txt
	@echo "[SUCCESS] Environment ready. Run 'make migrate' next."

migrate: ## Generate and apply database migrations
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run: ## Start the Django development server
	$(MANAGE) runserver 127.0.0.1:8080

test: ## Run the test suite (Performance & Logic)
	$(MANAGE) test -v 2 jobs

shell: ## Open the Django interactive shell
	$(MANAGE) shell

clean: ## Clean .pyc and __pycache__ files
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

backup: ## Export database to timestamped JSON
	@mkdir -p $(BACKUP_DIR)
	@echo "BUILD STATUS: Exporting JobSearch data..."
	@echo "TARGET: $(BACKUP_DIR)/db_backup_$(TIMESTAMP).json"
	@$(MANAGE) dumpdata --indent 2 --exclude auth.permission --exclude contenttypes > $(BACKUP_DIR)/db_backup_$(TIMESTAMP).json
	@echo "RESULT: Backup completed successfully at $(shell date)."

restore: ## Load data from the most recent backup file
	@echo "BUILD STATUS: Restoring latest data state..."
	@$(MANAGE) loaddata $(shell ls -t $(BACKUP_DIR)/*.json | head -1)
	@echo "RESULT: Database synchronized with $(shell ls -t $(BACKUP_DIR)/*.json | head -1)"


format: ## Fix lint-like tasks on the code base
	@echo "BUILD STATUS: Formatting with Ruff and djlint..."
	@$(BIN)/ruff format . && \
	$(BIN)/ruff check --fix . && \
	$(BIN)/djlint . --reformat
	@echo "RESULT: Codebase formatted and auto-fixed."

lint:  ## Run lint-like check on the code base
	@echo "BUILD STATUS: Linting with Ruff and djlint..."
	@$(BIN)/ruff check . && \
	$(BIN)/djlint . --check
	@echo "RESULT: Linting complete."

# The "Safety Suite" - Run everything in one go
check: format test backup  ## Safety Suite where we run format, test, backup
	@echo "PIPELINE STATUS: ALL CHECKS PASSED"
