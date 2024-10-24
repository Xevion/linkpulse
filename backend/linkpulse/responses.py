from pydantic import BaseModel
from datetime import datetime


class SeenIP(BaseModel):
    ip: str
    last_seen: str
    count: int