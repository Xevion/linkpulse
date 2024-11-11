import pytest
import structlog
from linkpulse.models import User
from linkpulse.routers.auth import hasher
from linkpulse.tests.random import random_email

logger = structlog.get_logger()


@pytest.fixture
def user():
    return User.create(email=random_email(), password_hash=hasher.hash("password"))
