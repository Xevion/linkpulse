import re
from linkpulse.utilities import utc_now
from fastapi.testclient import TestClient

from linkpulse.app import app


def test_utcnow_tz_aware():
    dt = utc_now()
    dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def test_api_version():
    with TestClient(app) as client:
        response = client.get("/api/version")
        assert response.status_code == 200
        assert "version" in response.json()

        version = response.json()["version"]
        assert isinstance(version, str)
        assert re.match(r"^\d+\.\d+\.\d+$", version)
