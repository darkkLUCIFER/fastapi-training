from typing import Annotated

from fastapi import Depends, APIRouter
from starlette import status

from src.auth.schema import RegisterUserSchema, RegisterUserResponseSchema
from src.auth.services import AuthService
from src.auth.dependencies import get_auth_service


router = APIRouter()


@router.post(
    '/register/',
    response_model=RegisterUserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Register user',
    description='Register new user with username & email',
)
def register_user(request_data: RegisterUserSchema, service: Annotated[AuthService, Depends(get_auth_service)]):
    return service.register_user(data=request_data)
