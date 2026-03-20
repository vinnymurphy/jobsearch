# JobSearch Project Automation
PYTHON = python3
MANAGE = $(PYTHON) manage.py

.PHONY: help install migrate run test shell clean

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies from requirements.txt"
	@echo "  make migrate  - Generate and apply database migrations"
	@echo "  make run      - Start the Django development server"
	@echo "  make test     - Run the test suite (Performance & Logic)"
	@echo "  make shell    - Open the Django interactive shell"
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
