from fastapi import FastAPI
from src.core.exceptions import NotFoundError
from src.core.handlers import not_found_error_handler
from src.core.logging import configure_logging
from src.core.middleware import add_middleware
from src.todo import router as todos_router
from src.auth import router as auth_router


app = FastAPI()

configure_logging()
add_middleware(app)
app.add_exception_handler(NotFoundError, not_found_error_handler)  # noqa

app.include_router(todos_router.router, tags=["todos"], prefix="/todo")
app.include_router(auth_router.router, tags=["auth"], prefix="/auth")
