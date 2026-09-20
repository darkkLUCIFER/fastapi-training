from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import NotFoundError, NotMatchError, PermissionDenied


__all__ = (
    'not_found_error_handler',
    'not_match_error_handler',
    'permission_denied_handler',
)


async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={'detail': str(exc)},
    )


async def not_match_error_handler(request: Request, exc: NotMatchError):
    return JSONResponse(
        status_code=404,
        content={'detail': str(exc)},
    )


async def permission_denied_handler(request: Request, exc: PermissionDenied):
    return JSONResponse(
        status_code=403,
        content={'detail': str(exc)},
    )
