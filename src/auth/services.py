from typing import Any

import jwt
from fastapi import HTTPException
from starlette import status

from src.core import NotMatchError, SecurityUtils
from src.auth.uow import AuthUow, PermissionUow, RolePermissionUow
from src.auth.models import User, Permission
from src.auth.schema import (
    LoginUserSchema,
    TokenUserSchema,
    RegisterUserSchema,
    RegisterSuperUserSchema,
    CreateRolePermissionSchema,
)
from src.core.config import settings
from src.auth.constants import RoleChoices
from src.auth.constants.permission import PermissionChoices


__all__ = ('AuthService', 'PermissionService', 'AuthorizationService', 'PermissionSyncService')


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
            if isinstance(data, RegisterSuperUserSchema):
                user = User(
                    email=data.email,
                    username=data.username,
                    hashed_password=self.security.hash_password(data.password),
                    role=RoleChoices(data.role),
                )
            else:
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

    def login_user(self, data: LoginUserSchema) -> TokenUserSchema:
        user = self.uow.repository.get_by_username(username=data.username)
        if not user or not self.security.verify_password(data.password, user.hashed_password):
            raise NotMatchError

        role = getattr(user.role, 'value', user.role)
        access_token = self.security.create_access_token(
            subject=str(user.id),
            extra_claims={'username': user.username, 'role': role},
        )
        refresh_token = self.security.create_refresh_token(subject=str(user.id))
        return TokenUserSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def refresh_tokens(self, refresh_token: str) -> TokenUserSchema:
        try:
            payload = self.security.decode_token(refresh_token)
        except jwt.PyJWTError as exc:
            raise NotMatchError from exc

        if payload.get('type') != 'refresh':
            raise NotMatchError

        jti = payload.get('jti', '')
        if settings.jwt_refresh_rotation and self.security.is_refresh_revoked(jti):
            raise NotMatchError

        user = self.uow.repository.get_one(user_id=int(payload['sub']))
        if not user or not user.is_active:
            raise NotMatchError

        if settings.jwt_refresh_rotation and jti:
            self.security.revoke_refresh_token(jti)

        role = getattr(user.role, 'value', user.role)
        new_access = self.security.create_access_token(
            subject=str(user.id),
            extra_claims={'username': user.username, 'role': role},
        )
        if settings.jwt_refresh_rotation:
            new_refresh = self.security.create_refresh_token(subject=str(user.id))
        else:
            new_refresh = refresh_token
        return TokenUserSchema(access_token=new_access, refresh_token=new_refresh)


class AuthorizationService:
    def __init__(self, uow: RolePermissionUow):
        self.uow = uow

    def get_permissions(self, user: User) -> frozenset[PermissionChoices] | None:
        # TODO(MAHDI): save the result for user in cache with ttl and also handle invalidation
        # for using cache also add version to model and check with version
        # if you dont want to invalidate cache in every where
        #
        # model:
        # User
        # ─────────────
        # id
        # permission_version
        #
        # cache in redis:
        # authz:user:123
        # {
        #     "version": 17,
        #     "permissions": [...]
        # }
        with self.uow:
            all_permissions = self.uow.repository.get_all_for_user(role=user.role)
            return frozenset(all_permissions) if all_permissions else None

    def has_permission(self, user: User, permission: PermissionChoices):
        permissions = self.get_permissions(user=user)
        if not permissions:
            return False
        return permission in permissions

    def update_role_admin_permissions(self) -> int:
        with self.uow:
            return self.uow.repository.update_admin_permissions()


class PermissionSyncService:
    def __init__(self, uow: PermissionUow):
        self.uow = uow

    def sync(self) -> int:
        keys = {permission.value for permission in PermissionChoices}
        return self.uow.repository.create_missing_permissions(keys)


class PermissionService:
    def __init__(self, uow: PermissionUow):
        self.uow = uow

    def list_all_permissions(self):
        with self.uow:
            return self.uow.repository.get_all_permissions()

    def create_permission(self, data: CreateRolePermissionSchema) -> Permission:
        pass
