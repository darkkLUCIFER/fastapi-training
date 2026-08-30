from src.core import SecurityUtils


__all__ = ('get_security_utils',)


def get_security_utils() -> SecurityUtils:
    return SecurityUtils()
