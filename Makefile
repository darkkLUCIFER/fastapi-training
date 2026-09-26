.PHONY: help makemigrations migrate downgrade current history run_local_server run_production_server create_super_user update_permissions run_frontend

help:
	@echo "FastAPI Database Management Commands:"
	@echo "  make makemigrations    - Generate a new Alembic migration (will prompt for message)"
	@echo "  make migrate           - Apply all pending migrations to the database"
	@echo "  make downgrade         - Rollback the database by 1 migration step"
	@echo "  make current           - Show the current migration version in the database"
	@echo "  make history           - Show the list of all migrations"
	@echo "  make run_local_server   - start development server"
	@echo "  make run_production_server   - start production server"
	@echo "  make create_super_user   - create admin user"
	@echo "  make update_permissions   - update list of permissions with choices in class PermissionChoices"
	@echo "  make run_frontend         - start frontend project"

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

run_local_server:
	@fastapi dev src/main.py --port 8001

run_production_server:
	@fastapi run src/main.py

create_super_user:
	@python -m scripts.create_admin

update_permissions:
	@python -m scripts.update_permissions

run_frontend:
	@npm --prefix frontend run dev
