import structlog
from fastapi import status
from fastapi.testclient import TestClient
from linkpulse.app import app
from linkpulse.tests.test_user import user

logger = structlog.get_logger()


def test_rate_limit(user):
    args = {"email": user.email, "password": "password"}

    with TestClient(app) as client:
        for _ in range(6):
            response = client.post("/api/login", json=args)
            assert response.status_code == status.HTTP_200_OK

        # 7th request should be rate limited
        response = client.post("/api/login", json=args)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Retry-After" in response.headers
        assert int(response.headers["Retry-After"]) > 1
