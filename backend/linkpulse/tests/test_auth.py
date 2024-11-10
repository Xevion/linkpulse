from datetime import datetime, timedelta
import structlog
from fastapi import status
from fastapi.testclient import TestClient
from linkpulse.app import app
from linkpulse.tests.test_user import user
from linkpulse.utilities import utc_now

import pytest

logger = structlog.get_logger()


def test_auth_login(user):
    args = {"email": user.email, "password": "password"}

    with TestClient(app) as client:

        def test_expiry(response, expected):
            expiry = datetime.fromisoformat(response.json()["expiry"])
            relative_expiry_days = (expiry - utc_now()).total_seconds() / timedelta(days=1).total_seconds()
            assert relative_expiry_days == pytest.approx(expected, rel=1e-5)

        # Remember Me, default False
        response = client.post("/api/login", json=args)
        assert response.status_code == status.HTTP_200_OK
        test_expiry(response, 0.5)
        assert client.cookies.get("session") is not None

        # Remember Me, True
        response = client.post("/api/login", json={**args, "remember_me": True})
        assert response.status_code == status.HTTP_200_OK
        test_expiry(response, 14)

        # Invalid Email
        response = client.post("/api/login", json={**args, "email": "invalid_email"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Wrong Email
        response = client.post("/api/login", json={**args, "email": "bad@email.com"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Wrong Password
        response = client.post("/api/login", json={**args, "password": "bad_password"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
