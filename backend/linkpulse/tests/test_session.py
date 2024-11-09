from datetime import timedelta

import pytest
import structlog
from linkpulse.models import Session
from linkpulse.tests.random import random_string
from linkpulse.tests.test_user import user
from linkpulse.utilities import utc_now

logger = structlog.get_logger()


@pytest.fixture
def db():
    return Session._meta.database


@pytest.fixture
def session(user):
    return Session.create(
        user=user, token=random_string(32), expiry=utc_now() + timedelta(hours=1)
    )


@pytest.fixture
def expired_session(session):
    session.expiry = utc_now() - timedelta(hours=1)
    return session


def test_session_create(session):
    assert Session.get_or_none(Session.token == session.token) is not None


def test_auto_revoke(db, expired_session):
    # Expired, but still exists
    assert Session.get_or_none(Session.token == expired_session.token) is not None
    # Test revoke=False
    assert expired_session.is_expired(revoke=False) is True
    # Test revoke=True
    assert expired_session.is_expired(revoke=True) is True
    # Expired, and no longer exists
    assert Session.get_or_none(Session.token == expired_session.token) is None


def test_expiry_valid(session):
    assert session.is_expired() is False


def test_expiry_invalid(expired_session):
    assert expired_session.is_expired() is True
