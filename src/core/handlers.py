from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import NotFoundError


__all__ = ("not_found_error_handler",)


async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )
