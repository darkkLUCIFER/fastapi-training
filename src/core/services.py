from uuid import uuid4
from typing import Any
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.core.config import settings


__all__ = ('SecurityUtils',)


class SecurityUtils:
    password_context = CryptContext(
        schemes=['bcrypt_sha256'],
        deprecated='auto',
    )

    # NOTE: in-memory revoked refresh jti set. Replace with Redis/DB in production
    # so revocation survives restarts and works across workers.
    # TODO(MAHDI): in future changes, add redis and handle revocation with redis
    _revoked_refresh_jti: set[str] = set()

    def hash_password(self, password: str) -> str:
        return self.password_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_context.verify(plain_password, hashed_password)

    def create_access_token(self, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
        claims = {'type': 'access', **(extra_claims or {})}
        return self._create_token(
            subject=subject,
            expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
            extra_claims=claims,
        )

    def create_refresh_token(self, subject: str) -> str:
        return self._create_token(
            subject=subject,
            expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
            extra_claims={'type': 'refresh'},
        )

    @staticmethod
    def _create_token(subject: str, expires_delta: timedelta, extra_claims: dict[str, Any] | None = None) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            'sub': subject,
            'iat': now,
            'exp': now + expires_delta,
            'jti': uuid4().hex,
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_token(token: str) -> dict[str, Any]:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    @classmethod
    def revoke_refresh_token(cls, jti: str) -> None:
        cls._revoked_refresh_jti.add(jti)

    @classmethod
    def is_refresh_revoked(cls, jti: str) -> bool:
        return jti in cls._revoked_refresh_jti
