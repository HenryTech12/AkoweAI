.PHONY: help setup install run run-dev celery-worker flower migrate lint format test clean docker-up docker-down

help:
	@echo "AkoweAI Backend Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup         - Complete setup (virtual env, install, db)"
	@echo "  make install       - Install dependencies"
	@echo "  make migrate       - Run database migrations"
	@echo ""
	@echo "Running:"
	@echo "  make run           - Run production server"
	@echo "  make run-dev       - Run development server"
	@echo "  make celery-worker - Run Celery worker"
	@echo "  make flower        - Run Flower monitoring (http://localhost:5555)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make test          - Run tests"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     - Start Docker Compose services"
	@echo "  make docker-down   - Stop Docker Compose services"
	@echo "  make docker-build  - Build Docker image"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove cache and temp files"

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete! Remember to:"
	@echo "1. Update .env with your API keys"
	@echo "2. Ensure PostgreSQL and Redis are running"
	@echo "3. Run 'make migrate' to setup database"

install:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

run-dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

celery-worker:
	celery -A celery_app worker --loglevel=info

flower:
	celery -A celery_app flower --port=5555

lint:
	flake8 .
	mypy .

format:
	black .
	isort .

test:
	pytest -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov

docker-build:
	docker build -t akowe-backend:latest .

docker-up:
	docker-compose up -d
	@echo "Services started:"
	@echo "  Backend: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"
	@echo "  Flower: http://localhost:5555"
	@echo "  Database: localhost:5432"
	@echo "  Redis: localhost:6379"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

docker-shell:
	docker-compose exec backend /bin/bash

db-reset:
	@echo "This will DROP all databases. Are you sure? [y/N]"
	@read -r answer; \
	if [ "$$answer" = "y" ]; then \
		dropdb akowe_db; \
		createdb akowe_db; \
		alembic upgrade head; \
		echo "Database reset complete"; \
	fi

requirements-freeze:
	pip freeze > requirements.txt

check:
	@echo "Running checks..."
	flake8 . --max-line-length=120
	black . --check
	@echo "All checks passed!"
