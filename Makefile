.PHONY: help makemigrations migrate downgrade current history

help:
	@echo "FastAPI Database Management Commands:"
	@echo "  make makemigrations    - Generate a new Alembic migration (will prompt for message)"
	@echo "  make migrate           - Apply all pending migrations to the database"
	@echo "  make downgrade         - Rollback the database by 1 migration step"
	@echo "  make current           - Show the current migration version in the database"
	@echo "  make history           - Show the list of all migrations"

makemigrations:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate:
	@echo "Applying migrations..."
	@alembic upgrade head
	@echo "Migrations applied successfully."

downgrade:
	@echo "Rolling back 1 step..."
	@alembic downgrade -1

current:
	@alembic current

history:
	@alembic history --verbose
