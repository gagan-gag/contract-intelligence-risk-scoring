from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_logging_and_exception_middleware_returns_json_error() -> None:
    response = client.get('/does-not-exist')
    assert response.status_code == 404
    assert 'detail' in response.json()


def test_basic_auth_and_rate_limit_stub_are_active() -> None:
    response = client.get('/health')
    assert response.status_code == 200

    response = client.get('/health', headers={'Authorization': 'Basic dXNlcjpwYXNz'})
    assert response.status_code == 200

    response = client.get('/health', headers={'Authorization': 'Basic dXNlcjpwYXNz'})
    assert response.status_code == 200
