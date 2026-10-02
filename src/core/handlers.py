from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    ConflictError,
    NotFoundError,
    NotMatchError,
    BadRequestError,
    PermissionDenied,
)


__all__ = (
    'conflict_error_handler',
    'not_found_error_handler',
    'not_match_error_handler',
    'permission_denied_handler',
    'bad_request_error_handler',
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


async def conflict_error_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={'detail': str(exc)},
    )


async def bad_request_error_handler(request: Request, exc: BadRequestError):
    return JSONResponse(
        status_code=400,
        content={'detail': str(exc)},
    )
