import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.auth.models import User
from src.auth.constants import RoleChoices
from src.auth.dependencies import get_current_user


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_current_user_endpoint_returns_only_public_user_fields(client):
    user = User(
        id=7,
        username='ada',
        hashed_password='not-a-real-password-hash',
        role=RoleChoices.USER,
        is_active=True,
    )
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.get('/users/me/')
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    assert response.json() == {'id': 7, 'username': 'ada', 'role': 'user'}
    assert 'hashed_password' not in response.json()


def test_current_user_endpoint_rejects_anonymous_requests(client):
    response = client.get('/users/me/')

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}
