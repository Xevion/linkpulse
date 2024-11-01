"""models.py
This module defines the database models for the LinkPulse backend.
It also provides a base model with database connection details.
"""

from os import getenv

import structlog
from peewee import CharField, DateTimeField, IntegerField, Model
from playhouse.db_url import connect

logger = structlog.get_logger()


# I can't pollute the class definition with these lines, so I'll move them to a separate function.
def __get_database_url():
    url = getenv("DATABASE_URL")
    if url is None or url.strip() == "":
        raise ValueError("DATABASE_URL is not set")
    return url


class BaseModel(Model):
    class Meta:
        # accessed via `BaseModel._meta.database`
        database = connect(url=__get_database_url())


class IPAddress(BaseModel):
    ip = CharField(primary_key=True)
    last_seen = DateTimeField()  # timezone naive
    count = IntegerField(default=0)
