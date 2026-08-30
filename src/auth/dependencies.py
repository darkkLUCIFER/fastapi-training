from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core import SecurityUtils
from src.auth.uow import AuthUow
from src.auth.services import AuthService
from src.core.dependencies import get_security_utils
from src.core.database.session import get_db


__all__ = ('get_auth_service',)


def get_auth_service(
    security: Annotated[SecurityUtils, Depends(get_security_utils)], db: Annotated[Session, Depends(get_db)]
) -> AuthService:
    return AuthService(uow=AuthUow(db), security=security)
