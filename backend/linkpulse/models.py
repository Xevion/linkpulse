"""models.py
This module defines the database models for the LinkPulse backend.
It also provides a base model with database connection details.
"""

import datetime
from os import getenv
from typing import Optional

import structlog
from linkpulse.utilities import utc_now
from peewee import (
    AutoField,
    BitField,
    CharField,
    Check,
    DateTimeField,
    ForeignKeyField,
    Model,
)
from playhouse.db_url import connect

logger = structlog.get_logger()


# I can't pollute the class definition with these lines, so I'll move them to a separate function.
def _get_database_url():
    url = getenv("DATABASE_URL")
    if url is None or url.strip() == "":
        raise ValueError("DATABASE_URL is not set")
    return url


class BaseModel(Model):
    class Meta:
        # accessed via `BaseModel._meta.database`
        database = connect(url=_get_database_url())


class User(BaseModel):
    id = AutoField(primary_key=True)
    # arbitrary max length, but statistically reasonable and limits UI concerns/abuse cases
    email = CharField(unique=True, max_length=45)
    flags = BitField()
    # full hash with encoded salt/parameters, argon2 but assume nothing
    password_hash = CharField(max_length=97)
    created_at = DateTimeField(default=utc_now)
    updated_at = DateTimeField(default=utc_now)
    # prefer soft deletes before hard deletes
    deleted_at = DateTimeField(null=True)
    deleted = flags.flag(1)

    # TODO: delete method, ensure sessions are deleted as well
    # TODO: undelete method


class Session(BaseModel):
    """
    A session represents a user's login session.

    For now, a session returned from the API implies it's validity.
    In the future, sessions may be invalidated or revoked, but kept in the database AND returned.
    This could allow sessions to be tracked and audited even after they are no longer valid, or allow more proper 'logout' messages.
    """

    token = CharField(unique=True, primary_key=True, max_length=32)
    user = ForeignKeyField(User, backref="sessions", on_delete="CASCADE")

    expiry = DateTimeField()

    created_at = DateTimeField(default=utc_now)
    last_used = DateTimeField(default=None, null=True)

    class Meta:
        constraints = [
            Check("LENGTH(token) = 32", name="session_token_length"),
            Check("expiry > created_at", name="session_expiry_created_at"),
            Check(
                "last_used IS NULL OR last_used >= created_at",
                name="session_last_used_created_at",
            ),
        ]

    @property
    def expiry_utc(self) -> datetime.datetime:
        return self.expiry.replace(tzinfo=datetime.timezone.utc)  # type: ignore

    def is_expired(
        self, revoke: bool = True, now: Optional[datetime.datetime] = None
    ) -> bool:
        """
        Check if the session is expired. If `revoke` is True, the session will be automatically revoked if it is expired.
        """
        if now is None:
            now = utc_now()

        if self.expiry_utc < now:
            if revoke:
                self.delete_instance()
            return True
        return False

    def use(self, now: Optional[datetime.datetime] = None):
        """
        Update the last_used field of the session.
        """
        if now is None:
            now = utc_now()
        self.last_used = now  # type: ignore
        # TODO: This should be buffered, as it'll be called *constantly*, perhaps every single request.
        # The ideal solution would be emitting updates to a Redis-based cache, and then flushing to the database every few seconds/minute.
        self.save()
