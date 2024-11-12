"""Miscellaneous endpoints for the Linkpulse API."""

from pathlib import Path
from typing import Any

import structlog
import toml
from fastapi import APIRouter
from fastapi_cache.decorator import cache
from linkpulse.utilities import get_db

logger = structlog.get_logger(__name__)

router = APIRouter()

db = get_db()


@router.get("/api/version")
@cache(expire=None)
async def version() -> dict[str, str]:
    """Get the version of the API.
    :return: The version of the API.
    :rtype: dict[str, str]
    """

    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    version = "unknown"
    if pyproject_path.exists() and pyproject_path.is_file():
        data = toml.load(pyproject_path)
        version = data["tool"]["poetry"]["version"]
        logger.debug("Version loaded from pyproject.toml", version=version)
    else:
        version = "error"

    return {"version": version}


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
