from fastapi.testclient import TestClient

from src.main import app


def test_application_starts_and_exposes_openapi_document():
    with TestClient(app) as client:
        response = client.get('/openapi.json')

    assert response.status_code == 200
    assert response.json()['info']['title'] == app.title
    assert '/todo/' in response.json()['paths']
