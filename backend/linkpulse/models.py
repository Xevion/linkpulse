from peewee import Model, CharField, DateTimeField, IntegerField
from playhouse.db_url import connect
from os import environ


class BaseModel(Model):
    class Meta:
        database = connect(url=environ.get("DATABASE_URL"))


class IPAddress(BaseModel):
    ip = CharField(primary_key=True)
    last_seen = DateTimeField()
    count = IntegerField(default=0)
