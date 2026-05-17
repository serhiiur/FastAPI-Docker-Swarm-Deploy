export PYTHONPATH := src/:$(PYTHONPATH)

STACK_NAME ?= fastapi-stack

.PHONY: help \
				install \
				clean \
				config \
				migrations \
				migrate \
				run \
				lint \
				type-check \
				test \
				check \
				pre-commit \
				secrets \
				stack-deploy \
				stack-status \
				stack-services \
				stack-teardown

.DEFAULT_GOAL := help

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install project dependencies
	uv sync --all-groups

clean: ## Remove Python and tool cache directories
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache

config: ## Create all config files (from templates) unless they exists
	cp -n ./.env.example ./.env
	cp -n ./configs/api.env.example ./configs/api.env
	cp -n ./configs/uvicorn.env.example ./configs/uvicorn.env

secrets: ## Generate configs to store Docker Secrets with random values
	echo $(openssl rand -base64 15) > ./secrets/db_password.txt

migrations: ## Generate a new migration (usage: make migrations m="message")
ifeq ($(m),)
	$(error Usage: make migrations m="your migration message")
endif
	uv run alembic -c src/alembic/alembic.ini revision --autogenerate -m "$(m)"

migrate: ## Apply database migrations to head
	uv run alembic -c src/alembic/alembic.ini upgrade head

run: ## Start the uvicorn development server (usage: make run RELOAD=1)
	uv run uvicorn src.app.main:app --env-file ./configs/uvicorn.env $(if $(RELOAD),--reload)

lint: ## Run Ruff linter
	uv run ruff check

type-check: ## Run Ty type checker
	uv run ty check

test: ## Run Pytest test suite
	uv run pytest

## Run linter, type checker, and test suite
check: lint type-check test

pre-commit: ## Run pre-commit hooks
	uv run pre-commit run -a

stack-deploy: ## Deploy the stack to the Docker Swarm cluster (usage: make stack-deploy STACK_NAME=my-stack)
	docker stack deploy -c compose.yml $(STACK_NAME)

stack-status: ## Display status of the stack in the Docker Swarm cluster
	docker stack ps $(STACK_NAME)

stack-services: ## Display services of the stack in the Docker Swarm cluster
	docker stack services $(STACK_NAME)

stack-teardown: ## Remove the stack from the Docker Swarm cluster
	docker stack rm $(STACK_NAME)
