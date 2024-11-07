from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
from asgi_correlation_id import CorrelationIdMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from linkpulse.logging import setup_logging
from linkpulse.middleware import LoggingMiddleware
from linkpulse.utilities import get_db, is_development

load_dotenv(dotenv_path=".env")

from linkpulse import models  # type: ignore

db = get_db()


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Connect to database, ensure specific tables exist
    db.connect()
    db.create_tables([models.User, models.Session])

    FastAPICache.init(
        backend=InMemoryBackend(), prefix="fastapi-cache", cache_status_header="X-Cache"
    )

    scheduler.start()

    yield

    scheduler.shutdown()

    if not db.is_closed():
        db.close()


from routers import authentication

app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.include_router(authentication.router)

setup_logging()

logger = structlog.get_logger()

if is_development:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/health")
async def health():
    return "OK"


@app.get("/api/migration")
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
