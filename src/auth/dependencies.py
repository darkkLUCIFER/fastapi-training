from typing import Any, Annotated

import jwt
from fastapi import Form, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core import SecurityUtils
from src.auth.uow import AuthUow, PermissionUow, RolePermissionUow
from src.auth.schema import LoginUserSchema
from src.core.config import settings
from src.auth.services import AuthService, PermissionService, AuthorizationService, RolePermissionService
from src.core.dependencies import get_security_utils
from src.core.database.session import get_db


__all__ = (
    'get_auth_service',
    'get_current_user',
    'get_current_payload',
    'login_user_form_schema',
    'get_permission_service',
    'get_authorization_service',
    'get_role_permission_service',
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(
    security: Annotated[SecurityUtils, Depends(get_security_utils)], db: Annotated[Session, Depends(get_db)]
) -> AuthService:
    return AuthService(uow=AuthUow(db), security=security)


def login_user_form_schema(
    username: Annotated[str, Form(min_length=3, max_length=100)],
    password: Annotated[str, Form(min_length=8, max_length=50)],
):
    return LoginUserSchema(
        username=username,
        password=password,
    )


def get_current_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    security: Annotated[SecurityUtils, Depends(get_security_utils)],
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': settings.jwt_token_location},
        )
    if credentials.scheme.lower() != settings.jwt_token_location.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid auth scheme, expected {settings.jwt_token_location}',
        )
    try:
        payload = security.decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
        ) from exc
    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access token required',
        )
    return payload


def get_current_user(
    payload: Annotated[dict[str, Any], Depends(get_current_payload)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = service.uow.repository.get_one(user_id=int(payload['sub']))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found or inactive',
        )
    return user


def get_authorization_service(db: Annotated[Session, Depends(get_db)]) -> AuthorizationService:
    return AuthorizationService(uow=RolePermissionUow(db))


def get_permission_service(db: Annotated[Session, Depends(get_db)]) -> PermissionService:
    return PermissionService(uow=PermissionUow(db))


def get_role_permission_service(db: Annotated[Session, Depends(get_db)]) -> RolePermissionService:
    return RolePermissionService(uow=RolePermissionUow(db))
