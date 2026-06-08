.PHONY: install test lint ci dry-run

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest

lint:
	ruff check .

ci: lint test

# Placeholder for future CLI integration.
# The current production script remains pty_calendar_sync.py.
dry-run:
	@echo "Dry-run mode planned. Current operational entrypoint: python3 pty_calendar_sync.py"
