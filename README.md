For management commands it's better to use typer if
you need to write custom scripts that actually execute Python code and database queries

for this first you should install typer with the below command:

```shell
pip install typer
```

then make a file named manage.py in root directory of your project
and then make commands like below:

```shell
# manage.py
import os
import subprocess
import typer


app = typer.Typer()


@app.command()
def makemigrations(message: str = typer.Option(..., "-m", "--message", prompt="Migration message")):
    """Generate a new Alembic migration."""
    typer.echo(f"Generating migration: {message}")
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])


@app.command()
def migrate():
    """Apply migrations to the database."""
    typer.echo("Applying migrations...")
    subprocess.run(["alembic", "upgrade", "head"])


@app.command()
def downgrade(steps: int = typer.Option(1, "-s", "--steps")):
    """Rollback migrations."""
    typer.echo(f"Rolling back {steps} step(s)...")
    subprocess.run(["alembic", "downgrade", f"-{steps}"])


if __name__ == "__main__":
    app()

```

# How to use management command with typer package:

- commands are stored inside file manage.py in root directory

## for making migration

```shell
python manage.py makemigrations -m "add users table"
```

## for migrate changes to DB

```shell
python manage.py migrate
```

## for downgrade changes

```shell
python manage.py downgrade -s 1
```

but for simple commands it's better to use `Makefile`
for that first make a file named `Makefile` in root directory

then make commands inside it as below:
```shell
.PHONY: help makemigrations migrate downgrade current history

# Default command when you just type `make`
help:
    @echo "FastAPI Database Management Commands:"
    @echo "  make makemigrations    - Generate a new Alembic migration (will prompt for message)"
    @echo "  make migrate           - Apply all pending migrations to the database"
    @echo "  make downgrade         - Rollback the database by 1 migration step"
    @echo "  make current           - Show the current migration version in the database"
    @echo "  make history           - Show the list of all migrations"

# Equivalent to Django's makemigrations
makemigrations:
    @read -p "Enter migration message: " msg; \
    alembic revision --autogenerate -m "$$msg"

# Equivalent to Django's migrate
migrate:
    @echo "Applying migrations..."
    @alembic upgrade head
    @echo "Migrations applied successfully."

# Rollback 1 step
downgrade:
    @echo "Rolling back 1 step..."
    @alembic downgrade -1

# Check current state
current:
    @alembic current

# View migration history
history:
    @alembic history --verbose
```
