from sqlalchemy.orm import Session

from src.auth.repository import AuthRepository, PermissionRepository, RolePermissionRepository
from src.core.exceptions import ConflictError
from src.core.database.uow import BaseUow
from src.core.database.integrity import ConstraintViolation, IntegrityErrorTranslator
from src.auth.constants.constraint import (
    EMAIL_UNIQUE_CONSTRAINT,
    PHONE_UNIQUE_CONSTRAINT,
    USERNAME_UNIQUE_CONSTRAINT,
    ROLE_PERMISSION_UNIQUE_CONSTRAINT,
)


__all__ = ('AuthUow', 'PermissionUow', 'RolePermissionUow')

AUTH_INTEGRITY_ERRORS = IntegrityErrorTranslator(
    violations={
        USERNAME_UNIQUE_CONSTRAINT: ConstraintViolation(ConflictError, 'username already exists'),
        EMAIL_UNIQUE_CONSTRAINT: ConstraintViolation(ConflictError, 'email already exists'),
        PHONE_UNIQUE_CONSTRAINT: ConstraintViolation(ConflictError, 'phone already exists'),
    },
)

ROLE_PERMISSION_INTEGRITY_ERRORS = IntegrityErrorTranslator(
    violations={
        ROLE_PERMISSION_UNIQUE_CONSTRAINT: ConstraintViolation(ConflictError, 'role already has this permission'),
    },
)


class AuthUow(BaseUow):
    integrity_errors = AUTH_INTEGRITY_ERRORS

    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = AuthRepository(db=session)


class RolePermissionUow(BaseUow):
    integrity_errors = ROLE_PERMISSION_INTEGRITY_ERRORS

    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = RolePermissionRepository(db=session)


class PermissionUow(BaseUow):
    def __init__(self, session: Session):
        super().__init__(session)
        self.repository = PermissionRepository(db=session)
