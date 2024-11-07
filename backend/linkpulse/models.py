"""models.py
This module defines the database models for the LinkPulse backend.
It also provides a base model with database connection details.
"""

from datetime import datetime
from os import getenv

import structlog
from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, Model
from playhouse.db_url import connect

from linkpulse.utilities import utc_now

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
    # full hash with encoded salt/parameters, argon2 but assume nothing
    password_hash = CharField(max_length=96)
    created_at = DateTimeField(default=utc_now)
    updated_at = DateTimeField(default=utc_now)


class Session(BaseModel):
    """
    A session represents a user's login session.
    """

    token = CharField(unique=True, primary_key=True, max_length=32)
    user = ForeignKeyField(User, backref="sessions")

    expiry = DateTimeField()

    created_at = DateTimeField(default=utc_now)
    last_used = DateTimeField(null=True)
