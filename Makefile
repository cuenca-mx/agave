SHELL := bash
PATH := ./venv/bin:${PATH}
PYTHON = python3.8
PROJECT = chalicelib
isort = isort $(PROJECT) tests app.py
black = black -S -l 79 --target-version py38 $(PROJECT) $(PROJECT)/lib/* tests app.py


all: test

venv:
	$(PYTHON) -m venv --prompt $(PROJECT) venv
	pip install -qU pip

install:
	pip install -qU -r requirements.txt

install-test: install
	pip install -qU -r requirements-test.txt

test: clean install-test lint
	pytest

format:
	$(isort)
	$(black)

lint:
	flake8 $(PROJECT) tests app.py
	$(isort) --check-only
	$(black) --check
	mypy $(PROJECT) tests app.py

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -rf .chalice/{deployments}

deploy-sandbox:
	chalice deploy --stage sandbox
	chalice deploy --stage sandbox-omni

deploy-stage:
	chalice deploy --stage stage
	chalice deploy --stage stage-omni


.PHONY: all install-test test format lint clean deploy-sandbox deploy-stage
