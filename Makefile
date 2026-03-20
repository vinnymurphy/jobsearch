# JobSearch Project Automation
PYTHON = python3
MANAGE = $(PYTHON) manage.py
BACKUP_DIR = backups
TIMESTAMP = $(shell date +%F_%H%M%S)


.PHONY: help install migrate run test shell clean

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies from requirements.txt"
	@echo "  make migrate  - Generate and apply database migrations"
	@echo "  make run      - Start the Django development server"
	@echo "  make test     - Run the test suite (Performance & Logic)"
	@echo "  make shell    - Open the Django interactive shell"
	@echo "  make backup   - Export database to timestamped JSON"
	@echo "  make restore  - Load data from the most recent backup file"
	@echo "  make clean    - Remove __pycache__ and build artifacts"

install:
	pip install -r requirements.txt

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

run:
	$(MANAGE) runserver

test:
	$(MANAGE) test jobs

shell:
	$(MANAGE) shell

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

backup:
	@mkdir -p $(BACKUP_DIR)
	@echo "----------------------------------------------------------------"
	@echo "BUILD STATUS: Exporting JobSearch data..."
	@echo "TARGET: $(BACKUP_DIR)/db_backup_$(TIMESTAMP).json"
	@$(MANAGE) dumpdata --indent 2 --exclude auth.permission --exclude contenttypes > $(BACKUP_DIR)/db_backup_$(TIMESTAMP).json
	@echo "RESULT: Backup completed successfully at $(shell date)."
	@echo "----------------------------------------------------------------"

restore:
	@echo "----------------------------------------------------------------"
	@echo "BUILD STATUS: Restoring latest data state..."
	@$(MANAGE) loaddata $(shell ls -t $(BACKUP_DIR)/*.json | head -1)
	@echo "RESULT: Database synchronized with $(shell ls -t $(BACKUP_DIR)/*.json | head -1)"
	@echo "----------------------------------------------------------------"