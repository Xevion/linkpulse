import random
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import AsyncIterator

import human_readable
import pytz
import structlog
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
from asgi_correlation_id import CorrelationIdMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from linkpulse.logging import setup_logging
from linkpulse.middleware import LoggingMiddleware
from linkpulse.utilities import get_ip, hide_ip, is_development
from peewee import PostgresqlDatabase
from psycopg2.extras import execute_values

load_dotenv(dotenv_path=".env")

from linkpulse import models, responses  # type: ignore

db: PostgresqlDatabase = models.BaseModel._meta.database  # type: ignore


def flush_ips():
    if len(app.state.buffered_updates) == 0:
        return

    try:
        with db.atomic():
            sql = """
                WITH updates (ip, last_seen, increment) AS (VALUES %s)
                INSERT INTO ipaddress (ip, last_seen, count)
                SELECT ip, last_seen, increment
                FROM updates
                ON CONFLICT (ip)
                DO UPDATE
                SET count = ipaddress.count + EXCLUDED.count, last_seen = EXCLUDED.last_seen;
            """
            rows = [
                (ip, data.last_seen, data.count)
                for ip, data in app.state.buffered_updates.items()
            ]

            cur = db.cursor()
            execute_values(cur, sql, rows)
    except Exception as e:
        logger.error("Failed to flush IPs to Database", error=e)

    i = len(app.state.buffered_updates)
    logger.debug("Flushed IPs to Database", count=i)

    # Finish up
    app.state.buffered_updates.clear()


scheduler = BackgroundScheduler()
scheduler.add_job(flush_ips, IntervalTrigger(seconds=5))


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Originally, this was used to generate a pool of random IP addresses so we could demo a changing list.
    # Now, this isn't necessary, but I just wanna test it for now. It'll be removed pretty soon.
    random.seed(42)  # 42 is the answer to everything
    app.state.ip_pool = [
        ".".join(str(random.randint(0, 255)) for _ in range(4)) for _ in range(50)
    ]

    # Connect to database, ensure specific tables exist
    db.connect()
    db.create_tables([models.IPAddress])

    # Delete all randomly generated IP addresses
    with db.atomic():
        logger.info(
            "Deleting Randomized IP Addresses", ip_pool_count=len(app.state.ip_pool)
        )
        query = models.IPAddress.delete().where(
            models.IPAddress.ip << app.state.ip_pool
        )
        row_count = query.execute()
        logger.info("Randomized IP Addresses deleted", row_count=row_count)

    FastAPICache.init(
        backend=InMemoryBackend(), prefix="fastapi-cache", cache_status_header="X-Cache"
    )

    app.state.buffered_updates = defaultdict(IPCounter)

    scheduler.start()

    yield

    scheduler.shutdown()
    flush_ips()

    if not db.is_closed():
        db.close()


@dataclass
class IPCounter:
    # Note: This is not the true 'seen' count, but the count of how many times the IP has been seen since the last flush.
    count: int = 0
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


app = FastAPI(lifespan=lifespan)

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


@app.get("/api/ips")
async def get_ips(request: Request, response: Response):
    """
    Returns a list of partially redacted IP addresses, as well as submitting the user's IP address to the database (buffered).
    """
    now = datetime.now(timezone.utc)

    # Get the user's IP address
    user_ip = get_ip(request)

    # If the IP address is not found, return an error
    if user_ip is None:
        logger.warning("unable to acquire user IP address")
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"error": "Unable to handle request."}

    # Update the buffered updates
    app.state.buffered_updates[user_ip].count += 1
    app.state.buffered_updates[user_ip].last_seen = now

    # Query the latest IPs
    latest_ips = (
        models.IPAddress.select(
            models.IPAddress.ip, models.IPAddress.last_seen, models.IPAddress.count
        )
        .order_by(models.IPAddress.last_seen.desc())
        .limit(10)
    )

    return {
        "ips": [
            responses.SeenIP(
                ip=hide_ip(ip.ip) if ip.ip != user_ip else ip.ip,
                last_seen=human_readable.date_time(
                    value=pytz.utc.localize(ip.last_seen),
                    when=datetime.now(timezone.utc),
                ),
                count=ip.count,
            )
            for ip in latest_ips
        ]
    }
