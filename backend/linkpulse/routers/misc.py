from fastapi import APIRouter
from fastapi_cache.decorator import cache
from linkpulse.utilities import get_db

router = APIRouter()

db = get_db()


@router.get("/health")
async def health():
    # TODO: Check database connection
    return "OK"


@router.get("/api/migration")
@cache(expire=60)
async def get_migration():
    """
    Returns the details of the most recent migration.
    """
    # Kind of insecure, but this is just a demo thing to show that migratehistory is available.
    cursor = db.execute_sql(
        "SELECT name, migrated_at FROM migratehistory ORDER BY migrated_at DESC LIMIT 1"
    )
    name, migrated_at = cursor.fetchone()
    return {"name": name, "migrated_at": migrated_at}
