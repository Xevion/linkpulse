"""responses.py

This module contains the response models for the FastAPI application.
"""

from pydantic import BaseModel


class SeenIP(BaseModel):
    ip: str
    last_seen: str
    count: int
