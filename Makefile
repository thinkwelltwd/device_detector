.PHONY: clean-pyc clean-build help
.DEFAULT_GOAL := help
PYTHON=python3.11

help:
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

clean: clean-build clean-pyc format scan

clean-build: ## Remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr .tox/

clean-pyc: ## Remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

format: ## Run code formatting
	ruff format device_detector
	ruff check --fix device_detector

scan: ## Run code scanning checks
	bandit device_detector -r -c pyproject.toml

test: ## Run the tests
	$(PYTHON) -m unittest

release: clean ## Package new release
	$(PYTHON) -m build
