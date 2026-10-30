from types import SimpleNamespace
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.auth.models import User
from src.todo.models import Todo
from src.auth.constants import RoleChoices
from src.auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_authorization_service,
    get_role_permission_service,
)
from src.todo.dependencies import get_todo_service


def make_user(user_id=1, role=RoleChoices.USER):
    return User(
        id=user_id,
        username=f'user-{user_id}',
        email=f'user-{user_id}@example.test',
        hashed_password='test-hash',
        role=role,
        is_active=True,
    )


def make_todo(todo_id=1, owner_id=1):
    now = datetime.now(UTC)
    return Todo(
        id=todo_id,
        owner_id=owner_id,
        title='Test todo',
        description='Description',
        priority=3,
        completed=False,
        created_at=now,
        updated_at=now,
    )


class FakeAuthService:
    def register_user(self, data):
        return SimpleNamespace(username=data.username, email=data.email)

    def login_user(self, data):
        return SimpleNamespace(access_token='access', refresh_token='refresh', token_type='Bearer')

    def refresh_tokens(self, refresh_token):
        return SimpleNamespace(access_token='new-access', refresh_token='new-refresh', token_type='Bearer')


class FakeTodoService:
    def __init__(self):
        self.todo = make_todo()
        self.deleted_id = None
        self.updated_data = None

    def create(self, data, background_tasks, user):
        self.todo.title = data.title
        self.todo.description = data.description
        self.todo.priority = data.priority
        self.todo.owner_id = user.id
        return self.todo

    def get_all(self, user):
        return [self.todo]

    def get_one(self, todo_id, user):
        return self.todo

    def update_one(self, todo_id, data, user):
        self.updated_data = data.model_dump(exclude_unset=True)
        for field, value in self.updated_data.items():
            setattr(self.todo, field, value)
        return self.todo

    def delete_one(self, todo_id, user):
        self.deleted_id = todo_id


class FakeRolePermissionService:
    def __init__(self):
        self.record = SimpleNamespace(id=4, role=RoleChoices.USER, permission_id=2, access=True)
        self.deleted_id = None

    def get_list_all_role_permissions(self):
        return [self.record]

    def create_role_permission(self, data):
        self.record = SimpleNamespace(id=4, **data.model_dump())
        return self.record

    def get_role_permission(self, role_permission_id):
        return SimpleNamespace(
            id=role_permission_id,
            role=RoleChoices.USER,
            permission=SimpleNamespace(id=2, key='todo.create', description=None, is_active=True),
            access=True,
        )

    def update_role_permission(self, role_permission_id, data):
        self.record = SimpleNamespace(id=role_permission_id, **data.model_dump())
        return self.record

    def delete_role_permission(self, role_permission_id):
        self.deleted_id = role_permission_id


@pytest.fixture
def api_state():
    original_overrides = app.dependency_overrides.copy()
    user = make_user()
    todo_service = FakeTodoService()
    authorization = SimpleNamespace(has_permission=lambda user, permission: True)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_auth_service] = FakeAuthService
    app.dependency_overrides[get_todo_service] = lambda: todo_service
    app.dependency_overrides[get_authorization_service] = lambda: authorization
    with TestClient(app) as client:
        yield client, user, todo_service
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


def test_register_endpoint_returns_public_user_fields(api_state):
    client, _, _ = api_state

    response = client.post(
        '/auth/register/',
        json={
            'username': 'ada_lovelace',
            'email': 'ada@example.com',
            'password': 'password123',
            'password_confirmation': 'password123',
        },
    )

    assert response.status_code == 201
    assert response.json() == {'username': 'ada_lovelace', 'email': 'ada@example.com'}


def test_register_endpoint_rejects_mismatched_passwords(api_state):
    client, _, _ = api_state

    response = client.post(
        '/auth/register/',
        json={
            'username': 'ada',
            'email': 'ada@example.com',
            'password': 'password123',
            'password_confirmation': 'different123',
        },
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'Input data does not match'}


def test_login_endpoint_accepts_form_credentials(api_state):
    client, _, _ = api_state

    response = client.post('/auth/login/', data={'username': 'ada', 'password': 'password123'})

    assert response.status_code == 200
    assert response.json() == {'access_token': 'access', 'refresh_token': 'refresh', 'token_type': 'Bearer'}


def test_refresh_endpoint_returns_rotated_tokens(api_state):
    client, _, _ = api_state

    response = client.post('/auth/refresh/', json={'refresh_token': 'old-refresh'})

    assert response.status_code == 200
    assert response.json() == {
        'access_token': 'new-access',
        'refresh_token': 'new-refresh',
        'token_type': 'Bearer',
    }


def test_todo_create_endpoint_returns_created_resource(api_state):
    client, _, _ = api_state

    response = client.post('/todo/', json={'title': 'Write tests', 'priority': 4})

    assert response.status_code == 201
    assert response.json()['title'] == 'Write tests'
    assert response.json()['priority'] == 4
    assert response.json()['completed'] is False


def test_todo_list_and_detail_endpoints_return_resources(api_state):
    client, _, _ = api_state

    list_response = client.get('/todo/')
    detail_response = client.get('/todo/1/')

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert detail_response.status_code == 200
    assert detail_response.json()['id'] == 1


def test_todo_patch_endpoint_applies_only_supplied_fields(api_state):
    client, _, service = api_state

    response = client.patch('/todo/1/', json={'completed': True})

    assert response.status_code == 200
    assert response.json()['completed'] is True
    assert service.updated_data == {'completed': True}


def test_todo_delete_endpoint_returns_no_content(api_state):
    client, _, service = api_state

    response = client.delete('/todo/1/')

    assert response.status_code == 204
    assert response.content == b''
    assert service.deleted_id == 1


def test_todo_path_parameter_must_be_positive(api_state):
    client, _, _ = api_state

    response = client.get('/todo/0/')

    assert response.status_code == 422


def test_admin_permission_endpoint_requires_permission(api_state):
    client, _, _ = api_state
    app.dependency_overrides[get_authorization_service] = lambda: SimpleNamespace(
        has_permission=lambda user, permission: False
    )

    response = client.get('/admin/permissions/')

    assert response.status_code == 403
    assert response.json() == {'detail': 'Permission denied'}


def test_admin_permission_endpoint_returns_list_when_authorized(api_state):
    client, _, _ = api_state
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    class PermissionService:
        def list_all_permissions(self):
            return [{'id': 1, 'key': 'todo.list.view', 'description': None, 'is_active': True}]

    from src.auth.dependencies import get_permission_service

    app.dependency_overrides[get_permission_service] = PermissionService

    response = client.get('/admin/permissions/')

    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'key': 'todo.list.view', 'description': None, 'is_active': True}]


def test_todo_endpoints_reject_requests_without_authentication():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    try:
        with TestClient(app) as client:
            response = client.get('/todo/')
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)

    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


def test_role_permission_list_endpoint_returns_records(api_state):
    client, _, _ = api_state
    app.dependency_overrides[get_role_permission_service] = FakeRolePermissionService

    response = client.get('/admin/role-permission/')

    assert response.status_code == 200
    assert response.json() == [{'id': 4, 'role': 'user', 'permission_id': 2, 'access': True}]


def test_role_permission_create_endpoint_returns_created_record(api_state):
    client, _, _ = api_state
    app.dependency_overrides[get_role_permission_service] = FakeRolePermissionService

    response = client.post('/admin/role-permission/create/', json={'role': 'admin', 'permission_id': 2})

    assert response.status_code == 201
    assert response.json() == {'id': 4, 'role': 'admin', 'permission_id': 2, 'access': True}


def test_role_permission_detail_endpoint_returns_nested_permission(api_state):
    client, _, _ = api_state
    app.dependency_overrides[get_role_permission_service] = FakeRolePermissionService

    response = client.get('/admin/role-permission/4/')

    assert response.status_code == 200
    assert response.json()['permission']['key'] == 'todo.create'
    assert response.json()['role'] == 'user'


def test_role_permission_update_endpoint_returns_updated_record(api_state):
    client, _, _ = api_state
    app.dependency_overrides[get_role_permission_service] = FakeRolePermissionService

    response = client.patch(
        '/admin/role-permission/4/',
        json={'role': 'admin', 'permission_id': 2, 'access': False},
    )

    assert response.status_code == 201
    assert response.json() == {'id': 4, 'role': 'admin', 'permission_id': 2, 'access': False}


def test_role_permission_delete_endpoint_returns_no_content(api_state):
    client, _, _ = api_state
    service = FakeRolePermissionService()
    app.dependency_overrides[get_role_permission_service] = lambda: service

    response = client.delete('/admin/role-permission/4/')

    assert response.status_code == 204
    assert response.content == b''
    assert service.deleted_id == 4
