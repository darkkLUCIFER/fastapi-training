from fastapi import FastAPI

from src.todo import router as todos_router
from src.auth.routers import (
    user as user_router,
    admin as admin_router,
    common as auth_router,
)
from src.core.logging import configure_logging
from src.core.handlers import (
    conflict_error_handler,
    not_found_error_handler,
    not_match_error_handler,
    bad_request_error_handler,
    permission_denied_handler,
)
from src.core.exceptions import (
    ConflictError,
    NotFoundError,
    NotMatchError,
    BadRequestError,
    PermissionDenied,
)
from src.core.middleware import add_middleware


app = FastAPI()

configure_logging()
add_middleware(app)
app.add_exception_handler(NotFoundError, not_found_error_handler)  # noqa
app.add_exception_handler(NotMatchError, not_match_error_handler)  # noqa
app.add_exception_handler(PermissionDenied, permission_denied_handler)  # noqa
app.add_exception_handler(ConflictError, conflict_error_handler)  # noqa
app.add_exception_handler(BadRequestError, bad_request_error_handler)  # noqa

app.include_router(todos_router.router, tags=['todos'], prefix='/todo')
app.include_router(auth_router.router, tags=['auth'], prefix='/auth')
app.include_router(admin_router.router, tags=['admin'], prefix='/admin')
app.include_router(user_router.router, tags=['users'], prefix='/users')
