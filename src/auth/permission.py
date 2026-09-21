from typing import Annotated

from fastapi import Depends

from src.core import PermissionDenied
from src.auth.models import User
from src.auth.services import AuthorizationService
from src.auth.dependencies import get_current_user, get_authorization_service
from src.auth.constants.permission import PermissionChoices


__all__ = ('RequirePermission',)


class RequirePermission:
    def __init__(self, permission: PermissionChoices):
        self.permission = permission

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        authorization_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    ) -> None:
        allowed = authorization_service.has_permission(user=current_user, permission=self.permission)

        if not allowed:
            raise PermissionDenied
