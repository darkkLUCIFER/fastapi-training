import pytest
from pydantic import ValidationError

from src.auth.schema import (
    LoginUserSchema,
    RegisterUserSchema,
    RegisterSuperUserSchema,
    CreateRolePermissionSchema,
    RegisterUserResponseSchema,
    UpdateRolePermissionSchema,
)
from src.auth.constants import RoleChoices
from src.core.exceptions import NotMatchError


def registration_data(**overrides):
    values = {
        'username': 'ada_lovelace',
        'email': 'ada@example.com',
        'password': 'password123',
        'password_confirmation': 'password123',
    }
    return {**values, **overrides}


def test_registration_accepts_valid_username_and_email():
    data = RegisterUserSchema.model_validate(registration_data())

    assert data.username == 'ada_lovelace'
    assert data.email == 'ada@example.com'


@pytest.mark.parametrize('username', ['ab', 'has space', 'has-dash', 'ümlaut', 'x' * 101])
def test_registration_rejects_invalid_usernames(username):
    with pytest.raises(ValidationError):
        RegisterUserSchema.model_validate(registration_data(username=username))


@pytest.mark.parametrize('password', ['short', 'x' * 51])
def test_registration_rejects_password_outside_length_limits(password):
    with pytest.raises(ValidationError):
        RegisterUserSchema.model_validate(registration_data(password=password, password_confirmation=password))


def test_registration_rejects_invalid_email():
    with pytest.raises(ValidationError):
        RegisterUserSchema.model_validate(registration_data(email='not-an-email'))


def test_registration_rejects_mismatched_password_confirmation():
    with pytest.raises(NotMatchError, match='Input data does not match'):
        RegisterUserSchema.model_validate(registration_data(password_confirmation='different123'))


def test_superuser_schema_validates_role_and_password_confirmation():
    data = RegisterSuperUserSchema.model_validate(registration_data(role=RoleChoices.ADMIN.value))

    assert data.role == 'admin'


def test_login_schema_accepts_valid_username():
    assert LoginUserSchema(username='ada', password='password123').username == 'ada'


def test_role_permission_schemas_validate_role_and_ids():
    created = CreateRolePermissionSchema(role=RoleChoices.ADMIN, permission_id=4)
    updated = UpdateRolePermissionSchema(role=RoleChoices.USER, permission_id=4, access=False)

    assert created.access is True
    assert updated.access is False
    with pytest.raises(ValidationError):
        CreateRolePermissionSchema(role='unknown', permission_id=4)


def test_registration_response_schema_has_only_public_fields():
    assert set(RegisterUserResponseSchema.model_fields) == {'username', 'email'}
