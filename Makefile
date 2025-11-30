SHELL := bash
PATH := ./venv/bin:${PATH}
PYTHON = python3.13	
PROJECT = agave
sources = $(PROJECT)/**/*.py examples/**/*.py tests/**/*.py


.PHONY: all
all: test

venv:
	$(PYTHON) -m venv --prompt $(PROJECT) venv
	pip install -qU pip

.PHONY: install
install:
	pip install -qU -r requirements.txt

.PHONY: install-test
install-test: install
	pip install -qU -r requirements-test.txt

.PHONY: test
test: clean install-test lint
	pytest

.PHONY: format
format:
	ruff check --fix .
	ruff format .

.PHONY: lint
lint:
	ruff check .
	ruff format --check .
	mypy $(sources)

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist

.PHONY: release
release: test clean
	python setup.py sdist bdist_wheel
	twine upload dist/*
