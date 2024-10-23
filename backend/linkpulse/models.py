from peewee import Model, CharField, DateTimeField
from playhouse.db_url import connect
from os import environ

class BaseModel(Model):
    class Meta:
        database = connect(url=environ.get('DATABASE_URL'))


class IPAddress(BaseModel):
    ip = CharField(primary_key=True)
    lastSeen = DateTimeField()