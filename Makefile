.PHONY: help lint-all lint-python lint-yaml test clean docker-build

VENV = ./venv
PYTHON = $(VENV)/bin/python
RUFF = $(VENV)/bin/ruff
YAMLLINT = $(VENV)/bin/yamllint
PYTEST = $(VENV)/bin/pytest

# Setup target to bootstrap the enviroment and dependencies


help:
	@echo "Available commands:"
	@echo "  make setup        - Create Venv and install all required tools"
	@echo "  make lint-all     - Run all linters (python, yaml)"
	@echo "  make lint-python  - Run Ruff for python linting and formatting"
	@echo "  make lint-yaml    - Run yamllint for workflow files"
	@echo "  make test         - Run lightweight basic tests"
	@echo "  make test-full    - Run full TDD suite (requires model assets)"
	@echo "  make docker-build - Build the docker container"
	@echo "  make clean        - Remove temporary files and logs"


setup:
	@echo "Creating virtual enviroment."
	python3 -m venv $(VENV)
	@echo "Upgrading pip..."
	$(VENV)/bin/pip install --upgrade pip --default-timeout=100
	@echo "Installing required linters and tools."
	$(VENV)/bin/pip install ruff yamllint pytest --default-timeout=100
	@echo "Setup complete!"


lint-all: lint-python lint-yaml

lint-python:
	$(RUFF) check .
	$(RUFF) format --check .

lint-yaml:
	$(YAMLLINT) .github/workflows/*.yml

test:
	$(PYTHON) -m pytest tests/test_basic.py

test-full:
	$(PYTHON) -m pytest tests/

docker-build:
	sudo docker build -t seanpor/arabic-translator:latest .

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	rm -f docs/translation_session.log translation_session.log
