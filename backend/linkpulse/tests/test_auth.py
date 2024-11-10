from datetime import datetime, timedelta

import pytest
import structlog
from fastapi import status
from fastapi.testclient import TestClient
from linkpulse.app import app
from linkpulse.tests.test_session import expired_session, session
from linkpulse.tests.test_user import user
from linkpulse.utilities import utc_now

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


def test_auth_login_logout(user):
    """Test full login & logout cycle"""
    args = {"email": user.email, "password": "password"}

    with TestClient(app) as client:
        response = client.post("/api/logout")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.post("/api/login", json=args)
        assert response.status_code == status.HTTP_200_OK
        assert client.cookies.get("session") is not None

        response = client.post("/api/logout")
        assert response.status_code == status.HTTP_200_OK
        assert client.cookies.get("session") is None


def test_auth_logout_expired(expired_session):
    # Test that an expired session cannot be used to logout, but still removes the cookie
    with TestClient(app) as client:
        response = client.post("/api/logout")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Add expired session cookie
        client.cookies.set("session", expired_session.token)
        assert client.cookies.get("session") is not None

        # Attempt to logout
        response = client.post("/api/logout")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert client.cookies.get("session") is None

        # TODO: Ensure ?all=True doesn't do anything either
