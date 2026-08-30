from typing import Any

from fastapi import HTTPException
from starlette import status

from src.core import SecurityUtils
from src.auth.uow import AuthUow
from src.auth.models import User
from src.auth.schema import RegisterUserSchema, RegisterSuperUserSchema


__all__ = ('AuthService',)


class AuthService:
    def __init__(self, uow: AuthUow, security: SecurityUtils):
        self.uow = uow
        self.security = security

    def register_user(self, data: RegisterUserSchema | RegisterSuperUserSchema) -> User:
        with self.uow:
            if self._validate_duplicate_user(email=data.email, username=data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='duplicate user exists',
                )

            user = User(
                email=data.email,
                username=data.username,
                hashed_password=self.security.hash_password(data.password),
            )
            self.uow.repository.create(user)
            self.uow.commit()
            self.uow.refresh(user)
        return user

    def _validate_duplicate_user(self, **filters: Any) -> bool:
        return self.uow.repository.exists(**filters)
