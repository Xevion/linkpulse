import pytest
from linkpulse.models import User
from linkpulse.tests.random import epoch, random_email, random_string


@pytest.fixture
def user():
    return User.create(
        email=random_email(), password_hash=str(epoch()) + random_string(64)
    )
