from fastapi import FastAPI

from src.auth import router as auth_router
from src.todo import router as todos_router
from src.core.logging import configure_logging
from src.core.handlers import not_found_error_handler, not_match_error_handler, permission_denied_handler
from src.core.exceptions import NotFoundError, NotMatchError, PermissionDenied
from src.core.middleware import add_middleware


app = FastAPI()

configure_logging()
add_middleware(app)
app.add_exception_handler(NotFoundError, not_found_error_handler)  # noqa
app.add_exception_handler(NotMatchError, not_match_error_handler)  # noqa
app.add_exception_handler(PermissionDenied, permission_denied_handler)  # noqa

app.include_router(todos_router.router, tags=['todos'], prefix='/todo')
app.include_router(auth_router.router, tags=['auth'], prefix='/auth')
