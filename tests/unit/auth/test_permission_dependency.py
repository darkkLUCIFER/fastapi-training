from types import SimpleNamespace

import pytest

from src.auth.permission import RequirePermission
from src.core.exceptions import PermissionDenied
from src.auth.constants.permission import PermissionChoices


def test_require_permission_allows_authorized_user():
    dependency = RequirePermission(PermissionChoices.TODO_CREATE)
    user = SimpleNamespace(id=1)
    authorization = SimpleNamespace(has_permission=lambda user, permission: True)

    assert dependency(user, authorization) is None


def test_require_permission_rejects_unauthorized_user():
    dependency = RequirePermission(PermissionChoices.TODO_CREATE)
    user = SimpleNamespace(id=1)
    authorization = SimpleNamespace(has_permission=lambda user, permission: False)

    with pytest.raises(PermissionDenied):
        dependency(user, authorization)
