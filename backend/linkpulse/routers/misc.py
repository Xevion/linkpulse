"""Miscellaneous endpoints for the Linkpulse API."""

from typing import Any

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from linkpulse.utilities import get_db

router = APIRouter()

db = get_db()


@router.get("/health")
async def health():
    """An endpoint to check if the service is running.
    :return: OK
    :rtype: Literal['OK']"""
    # TODO: Check database connection
    return "OK"


@router.get("/api/migration")
@cache(expire=60)
async def get_migration() -> dict[str, Any]:
    """Get the last migration name and timestamp from the migratehistory table.
    :return: The last migration name and timestamp.
    :rtype: dict[str, Any]
    """
    # Kind of insecure, but this is just a demo thing to show that migratehistory is available.
    cursor = db.execute_sql("SELECT name, migrated_at FROM migratehistory ORDER BY migrated_at DESC LIMIT 1")
    name, migrated_at = cursor.fetchone()
    return {"name": name, "migrated_at": migrated_at}
