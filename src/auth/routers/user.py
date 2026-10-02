from typing import Annotated

from fastapi import Depends, APIRouter
from starlette import status

from src.auth.models import User
from src.auth.dependencies import get_current_user


router = APIRouter()


# TODO(MAHDI): add endpoint for update profile & change password with validation


@router.get(
    '/me/',
    status_code=status.HTTP_200_OK,
    summary='Current user',
    description='Current User Info',
)
def get_me(user: Annotated[User, Depends(get_current_user)]):
    return {'id': user.id, 'username': user.username, 'role': user.role}
