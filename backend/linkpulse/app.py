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

    FastAPICache.init(backend=InMemoryBackend(), prefix="fastapi-cache", cache_status_header="X-Cache")

    scheduler.start()

    yield

    scheduler.shutdown()

    if not db.is_closed():
        db.close()


from linkpulse.routers import auth, misc

app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)
app.include_router(auth.router)
app.include_router(misc.router)

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
