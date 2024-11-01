import logging
import os
import random

from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator

from asgi_correlation_id import CorrelationIdMiddleware
import human_readable
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from linkpulse.utilities import get_ip, hide_ip, pluralize
from linkpulse.middleware import LoggingMiddleware
from peewee import PostgresqlDatabase
from psycopg2.extras import execute_values

from linkpulse.logging import setup_logging

setup_logging(json_logs=False, log_level="DEBUG")

load_dotenv(dotenv_path=".env")

from linkpulse import models, responses  # type: ignore

# global variables
is_development = os.getenv("ENVIRONMENT") == "development"
db: PostgresqlDatabase = models.BaseModel._meta.database  # type: ignore
logger = logging.getLogger()


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
    except:
        logging.error("Failed to flush IPs to the database.")

    i = len(app.state.buffered_updates)
    logging.debug("Flushed {} IP{} to the database.".format(i, pluralize(i)))

    # Finish up
    app.state.buffered_updates.clear()


scheduler = BackgroundScheduler()
scheduler.add_job(flush_ips, IntervalTrigger(seconds=5))


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if is_development:
        # 42 is the answer to everything
        random.seed(42)
        # Generate a pool of random IP addresses
        app.state.ip_pool = [
            ".".join(str(random.randint(0, 255)) for _ in range(4)) for _ in range(50)
        ]

    # Connect to database, ensure specific tables exist
    db.connect()
    db.create_tables([models.IPAddress])

    # Delete all randomly generated IP addresses
    with db.atomic():
        logger.info(
            "Deleting Randomized IP Addresses",
            {"ip_pool_count": len(app.state.ip_pool)},
        )
        query = models.IPAddress.delete().where(
            models.IPAddress.ip << app.state.ip_pool
        )
        row_count = query.execute()
        logger.info("Randomized IP Addresses deleted", {"row_count": row_count})

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
    last_seen: datetime = field(default_factory=datetime.now)


app = FastAPI(lifespan=lifespan)


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
    now = datetime.now()

    # Get the user's IP address
    user_ip = get_ip(request)

    # If the IP address is not found, return an error
    if user_ip is None:
        logging.info("No IP found!")
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
                last_seen=human_readable.date_time(ip.last_seen),
                count=ip.count,
            )
            for ip in latest_ips
        ]
    }
