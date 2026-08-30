from typing import Annotated

from pydantic import Field, EmailStr, BaseModel, ConfigDict, StringConstraints, model_validator

from src.core.exceptions import NotMatchError


__all__ = ('RegisterUserSchema', 'RegisterUserResponseSchema')

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
