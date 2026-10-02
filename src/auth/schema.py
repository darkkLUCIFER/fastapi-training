from typing import Annotated

from pydantic import Field, EmailStr, BaseModel, ConfigDict, StringConstraints, model_validator

from src.core import settings
from src.auth.constants import RoleChoices
from src.core.exceptions import NotMatchError


__all__ = (
    'LoginUserSchema',
    'TokenUserSchema',
    'RefreshTokenSchema',
    'RegisterUserSchema',
    'PermissionListSchema',
    'PermissionDetailSchema',
    'RegisterSuperUserSchema',
    'RegisterUserResponseSchema',
    'CreateRolePermissionSchema',
    'DetailRolePermissionSchema',
    'UpdateRolePermissionSchema',
)

Username = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=100,
        strip_whitespace=True,
        to_lower=True,
        pattern=r'^[a-z0-9_]+$',
    ),
]

Password = Annotated[
    str,
    Field(
        min_length=8,
        max_length=50,
    ),
]


class RegisterUserSchema(BaseModel):
    username: Username
    email: EmailStr
    password: Password
    password_confirmation: Password

    @model_validator(mode='after')
    def validate_passwords(self):
        if self.password != self.password_confirmation:
            raise NotMatchError
        return self

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'username': 'sorena',
                'email': 'test@test.com',
                'password': '12345678',
                'password_confirmation': '12345678',
            }
        }
    )


class RegisterUserResponseSchema(BaseModel):
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class RegisterSuperUserSchema(BaseModel):
    username: Username
    email: EmailStr
    password: Password
    password_confirmation: Password
    role: str

    @model_validator(mode='after')
    def validate_passwords(self):
        if self.password != self.password_confirmation:
            raise NotMatchError
        return self

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'username': 'sorena',
                'email': 'test@test.com',
                'password': '12345678',
                'password_confirmation': '12345678',
                'role': 'admin',
            }
        }
    )


class LoginUserSchema(BaseModel):
    username: Username
    password: Password


class TokenUserSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = settings.jwt_token_location


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class PermissionListSchema(BaseModel):
    id: int
    key: str
    description: str | None
    is_active: bool


class CreateRolePermissionSchema(BaseModel):
    role: RoleChoices
    permission_id: int
    access: Annotated[
        bool,
        Field(
            default=True,
        ),
    ]


class PermissionDetailSchema(BaseModel):
    id: int
    key: str
    description: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DetailRolePermissionSchema(BaseModel):
    id: int
    role: RoleChoices
    permission: PermissionDetailSchema
    access: bool

    model_config = ConfigDict(from_attributes=True)


class UpdateRolePermissionSchema(BaseModel):
    role: RoleChoices
    permission_id: int
    access: bool
