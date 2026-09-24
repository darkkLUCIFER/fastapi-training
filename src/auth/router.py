from typing import Annotated

from fastapi import Depends, APIRouter
from starlette import status

from src.auth.models import User
from src.auth.schema import (
    LoginUserSchema,
    TokenUserSchema,
    RefreshTokenSchema,
    RegisterUserSchema,
    PermissionListSchema,
    RegisterUserResponseSchema,
)
from src.auth.services import AuthService, PermissionService
from src.auth.permission import RequirePermission
from src.auth.dependencies import get_auth_service, get_current_user, get_permission_service, login_user_form_schema


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


@router.post(
    '/login/',
    status_code=status.HTTP_200_OK,
    response_model=TokenUserSchema,
    summary='Login user',
    description='Login user with username & password',
)
def login(
    login_form: Annotated[LoginUserSchema, Depends(login_user_form_schema)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return service.login_user(data=login_form)


@router.post(
    '/refresh/',
    status_code=status.HTTP_200_OK,
    response_model=TokenUserSchema,
    summary='Refresh tokens',
    description='Rotate refresh token (if enabled) and issue new access token',
)
def refresh(
    request_data: RefreshTokenSchema,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return service.refresh_tokens(refresh_token=request_data.refresh_token)


@router.get(
    '/me/',
    status_code=status.HTTP_200_OK,
    summary='Current user',
    description='Current User Info',
)
def get_me(user: Annotated[User, Depends(get_current_user)]):
    return {'id': user.id, 'username': user.username, 'role': user.role}


@router.get(
    '/permissions/',
    status_code=status.HTTP_200_OK,
    summary='Permissions List',
    description='List of all permissions',
    dependencies=[Depends(RequirePermission)],
    response_model=list[PermissionListSchema],
)
def permission_list(service: Annotated[PermissionService, Depends(get_permission_service)]):
    return service.list_all_permissions()
