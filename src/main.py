from fastapi import FastAPI
from src.core.exceptions import NotFoundError
from src.core.handlers import not_found_error_handler
from src.core.logging import configure_logging
from src.todo import router as todos_router


# Main
app = FastAPI()

# Logging
configure_logging()
app.add_exception_handler(NotFoundError, not_found_error_handler)  # noqa

# Router
app.include_router(todos_router.router, tags=['todos'], prefix="/todo")
