from unittest.mock import MagicMock

from src.core import SecurityUtils
from src.auth.uow import AuthUow, PermissionUow, RolePermissionUow
from src.auth.schema import LoginUserSchema
from src.auth.services import AuthService, PermissionService, AuthorizationService, RolePermissionService
from src.auth.dependencies import (
    get_auth_service,
    get_permission_service,
    login_user_form_schema,
    get_authorization_service,
    get_role_permission_service,
)


def test_auth_service_dependency_wires_session_and_security():
    session = MagicMock()
    security = SecurityUtils()

    service = get_auth_service(security, session)

    assert isinstance(service, AuthService)
    assert isinstance(service.uow, AuthUow)
    assert service.uow.session is session
    assert service.security is security


def test_permission_service_dependencies_use_expected_units_of_work():
    session = MagicMock()

    authorization = get_authorization_service(session)
    permissions = get_permission_service(session)
    role_permissions = get_role_permission_service(session)

    assert isinstance(authorization, AuthorizationService)
    assert isinstance(authorization.uow, RolePermissionUow)
    assert isinstance(permissions, PermissionService)
    assert isinstance(permissions.uow, PermissionUow)
    assert isinstance(role_permissions, RolePermissionService)
    assert isinstance(role_permissions.uow, RolePermissionUow)
    assert all(service.uow.session is session for service in (authorization, permissions, role_permissions))


def test_login_form_dependency_builds_validated_schema():
    result = login_user_form_schema('ada', 'password123')

    assert isinstance(result, LoginUserSchema)
    assert result.username == 'ada'
