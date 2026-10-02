from typing import Annotated

from fastapi import Path, Depends, APIRouter
from starlette import status

from src.auth.schema import (
    PermissionListSchema,
    CreateRolePermissionSchema,
    DetailRolePermissionSchema,
    UpdateRolePermissionSchema,
)
from src.auth.services import PermissionService, RolePermissionService
from src.auth.permission import RequirePermission
from src.auth.dependencies import get_permission_service, get_role_permission_service
from src.auth.constants.permission import PermissionChoices


router = APIRouter()


@router.get(
    '/permissions/',
    status_code=status.HTTP_200_OK,
    summary='Permissions List',
    description='List of all permissions',
    dependencies=[Depends(RequirePermission(PermissionChoices.PERMISSION_LIST_VIEW))],
    response_model=list[PermissionListSchema],
)
def permission_list(service: Annotated[PermissionService, Depends(get_permission_service)]):
    return service.list_all_permissions()


@router.get(
    '/role-permission/',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequirePermission(PermissionChoices.ROLE_PERMISSION_LIST_VIEW))],
    summary='List Role Permissions',
    description='List All Role Permissions',
)
def list_role_permission(service: Annotated[RolePermissionService, Depends(get_role_permission_service)]):
    return service.get_list_all_role_permissions()


@router.post(
    '/role-permission/create/',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermission(PermissionChoices.ROLE_PERMISSION_CREATE))],
    summary='Create new role permission',
    description='Create new role permission with role admin',
)
def create_role_permission(
    service: Annotated[RolePermissionService, Depends(get_role_permission_service)], data: CreateRolePermissionSchema
):
    return service.create_role_permission(data=data)


@router.get(
    '/role-permission/{role_permission_id}/',
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequirePermission(PermissionChoices.ROLE_PERMISSION_DETAIL))],
    response_model=DetailRolePermissionSchema,
    summary='Detail role permission',
    description='Detail role permission',
)
def detail_role_permission(
    service: Annotated[RolePermissionService, Depends(get_role_permission_service)],
    role_permission_id: Annotated[int, Path(ge=1, description='Role permission ID')],
):
    return service.get_role_permission(role_permission_id=role_permission_id)


@router.patch(
    '/role-permission/{role_permission_id}/',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RequirePermission(PermissionChoices.ROLE_PERMISSION_UPDATE))],
    summary='Update  role permission',
    description='Update ont role permission',
)
def update_role_permission(
    service: Annotated[RolePermissionService, Depends(get_role_permission_service)],
    request: UpdateRolePermissionSchema,
    role_permission_id: Annotated[int, Path(ge=1, description='Role permission ID')],
):
    return service.update_role_permission(data=request, role_permission_id=role_permission_id)


@router.delete(
    '/role-permission/{role_permission_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RequirePermission(PermissionChoices.ROLE_PERMISSION_DELETE))],
    summary='Delete one role permission',
    description='Delete one role permission',
)
def delete_role_permission(
    service: Annotated[RolePermissionService, Depends(get_role_permission_service)],
    role_permission_id: Annotated[int, Path(ge=1, description='Role permission ID')],
):
    return service.delete_role_permission(role_permission_id=role_permission_id)
