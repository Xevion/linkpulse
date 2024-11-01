from pydantic import BaseModel


class SeenIP(BaseModel):
    ip: str
    last_seen: str
    count: int
