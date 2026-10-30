import asyncio

import pytest
from starlette.requests import Request

from src.core.handlers import (
    conflict_error_handler,
    not_found_error_handler,
    not_match_error_handler,
    bad_request_error_handler,
    permission_denied_handler,
)
from src.core.exceptions import ConflictError, NotFoundError, NotMatchError, BadRequestError, PermissionDenied


def make_request():
    return Request({'type': 'http', 'method': 'GET', 'path': '/', 'headers': [], 'query_string': b''})


@pytest.mark.parametrize(
    ('handler', 'exception', 'status_code', 'detail'),
    [
        (not_found_error_handler, NotFoundError(8, 'Todo'), 404, 'Todo with id: 8 not found'),
        (not_match_error_handler, NotMatchError(), 404, 'Input data does not match'),
        (permission_denied_handler, PermissionDenied(), 403, 'Permission denied'),
        (conflict_error_handler, ConflictError('already exists'), 409, 'already exists'),
        (bad_request_error_handler, BadRequestError('invalid value'), 400, 'invalid value'),
    ],
)
def test_domain_exception_handler_returns_expected_http_response(handler, exception, status_code, detail):
    response = asyncio.run(handler(make_request(), exception))

    assert response.status_code == status_code
    assert response.body == ('{"detail":"' + detail + '"}').encode()
