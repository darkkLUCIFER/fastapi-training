from passlib.context import CryptContext


__all__ = ('SecurityUtils',)


class SecurityUtils:
    password_context = CryptContext(
        schemes=['bcrypt_sha256'],
        deprecated='auto',
    )

    def hash_password(self, password: str) -> str:
        return self.password_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_context.verify(plain_password, hashed_password)
