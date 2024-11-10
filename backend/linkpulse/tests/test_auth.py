from fastapi import status
from fastapi.testclient import TestClient
from linkpulse.app import app
from linkpulse.tests.test_user import user


def test_auth_login(user):
    args = {"email": "test@test.com", "password": "test"}

    with TestClient(app) as client:
        response = client.post("/api/login", json=args)
        assert response.status_code == status.HTTP_200_OK
        # assert response.json()["token"] is not None

        response = client.post("/api/login", json={**args, "email": "invalid_email"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.post("/api/login", json={**args, "password": "invalid_password"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
