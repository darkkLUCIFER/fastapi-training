from src.auth.models import User
from src.auth.schema import RegisterUserResponseSchema
from src.auth.constants import RoleChoices


def test_registration_response_schema_excludes_password_and_internal_fields():
    user = User(
        id=5,
        username='ada',
        email='ada@example.com',
        hashed_password='sensitive-hash',
        role=RoleChoices.USER,
        is_active=True,
    )

    response = RegisterUserResponseSchema.model_validate(user).model_dump()

    assert response == {'username': 'ada', 'email': 'ada@example.com'}
    assert 'hashed_password' not in response
    assert 'password' not in response
