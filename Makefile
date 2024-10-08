SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

# Setting variables
py = $$(if [ -d $(PWD)/'.venv' ]; then echo $(PWD)/".venv/bin/python3"; else echo "python3"; fi)
pip = $(py) -m pip

# Override PWD so that it's always based on the location of the file and **NOT**
# based on where the shell is when calling `make`. This is useful if `make`
# is called like `make -C <some path>`
PWD := $(realpath $(dir $(abspath $(firstword $(MAKEFILE_LIST)))))
WORKTREE_ROOT := $(shell git rev-parse --show-toplevel 2> /dev/null)

.DEFAULT_GOAL := help
.PHONY: help venv install-dependencies set-up run-locally lint isort test package build run clean
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z\$$/]+.*:.*?##\s/ {printf "\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Make a venv
	@$(py) -m venv .venv
	@touch .venv

install-dependencies: requirements.txt ## Install all dependencies in the venv
	@.venv/bin/pip install -U pip setuptools wheel build 
	@.venv/bin/pip install -U -r requirements.txt

set-up: venv install-dependencies ## Set up the project
	@echo "Project set up finished succesfully"

run-locally: ## Run the execution locally
	@.venv/bin/python local.py

start-server: ## Run the server with the rest api
	@$(ENV_PREFIX)fastapi run main.py

lint: ## Lint the code
	@$(ENV_PREFIX)black .

isort: ## Reorder imports
	@$(ENV_PREFIX)isort .

test: ## Test the code
	@$(ENV_PREFIX)pytest --cov=. --cov-report=term 

package:
	@.venv/bin/python -m build

build: ## Build the docker image
	docker build -t example-ir .

run: ## Run the docker container
	docker run -d -p 8000:8000 --name example-ir-container example-ir

clean: ## Clean the project
	@rm -rf .venv
	@find . -type f -name '*.pyc' -delete
	@echo "Project cleaned"
