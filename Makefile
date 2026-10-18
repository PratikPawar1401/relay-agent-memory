.PHONY: setup services api web test build demo

setup:
	uv sync --locked
	npm --prefix frontend ci

services:
	docker compose up -d --wait

api:
	uv run uvicorn relay.api:app --host 127.0.0.1 --port 8088

web:
	npm --prefix frontend run dev

test:
	RELAY_INTEGRATION=1 uv run pytest -q
	uv run ruff check src sandbox tests

build:
	npm --prefix frontend run build

demo:
	uv run relay demo
