from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.config import settings
from src.core.middleware import add_middleware


def test_cors_middleware_allows_configured_origin_and_credentials(monkeypatch):
    monkeypatch.setattr(settings, 'cors_origins', ['https://frontend.example'])
    app = FastAPI()
    add_middleware(app)

    @app.get('/')
    def root():
        return {'ok': True}

    with TestClient(app) as client:
        response = client.options(
            '/',
            headers={
                'Origin': 'https://frontend.example',
                'Access-Control-Request-Method': 'GET',
            },
        )

    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'https://frontend.example'
    assert response.headers['access-control-allow-credentials'] == 'true'
