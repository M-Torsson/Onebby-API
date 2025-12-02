# Makefile for Onebby API

.PHONY: help install migrate upgrade test lint format clean run docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make migrate     - Create a new migration"
	@echo "  make upgrade     - Apply migrations"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting"
	@echo "  make format      - Format code"
	@echo "  make clean       - Clean cache and logs"
	@echo "  make run         - Run the application"
	@echo "  make docker-up   - Start Docker containers"
	@echo "  make docker-down - Stop Docker containers"

install:
	pip install -r requirements.txt

migrate:
	python -m alembic revision --autogenerate -m "$(msg)"

upgrade:
	python -m alembic upgrade head

downgrade:
	python -m alembic downgrade -1

test:
	pytest -v

lint:
	flake8 app/ main.py
	mypy app/ main.py

format:
	black app/ main.py tests/
	isort app/ main.py tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf logs/*.log

run:
	python main.py

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api
