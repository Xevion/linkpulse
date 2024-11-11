from fastapi.testclient import TestClient

from linkpulse.app import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == "OK"


def test_migration():
    with TestClient(app) as client:
        response = client.get("/api/migration")
        assert response.status_code == 200
