from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from peewee import PostgresqlDatabase

load_dotenv(dotenv_path=".env")

from linkpulse import models  # type: ignore

db: PostgresqlDatabase = models.BaseModel._meta.database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(backend=InMemoryBackend(), prefix="fastapi-cache", cache_status_header="X-Cache")
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db.connect()
    db.create_tables([models.IPAddress])


@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()


@app.get("/health")
async def health():
    return "OK"


@app.get("/api/migration")
@cache(expire=60)
async def get_migration():
    cursor = db.execute_sql(
        "SELECT name, migrated_at FROM migratehistory ORDER BY migrated_at DESC LIMIT 1"
    )
    name, migrated_at = cursor.fetchone()
    return {"name": name, "migrated_at": migrated_at}


@app.get("/api/test")
async def get_current_time(request: Request):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_ip = request.headers.get("X-Forwarded-For")
    if not user_ip:
        # Fallback, probably not on a proxy
        user_ip = request.client.host

    response = {"time": current_time, "ip": user_ip}

    # Create one record
    new_ip, created = models.IPAddress.get_or_create(
        ip=user_ip, defaults={"lastSeen": datetime.now()}
    )
    if not created:
        new_ip.lastSeen = datetime.now()
    result = new_ip.save()
    print(result, new_ip)

    # Query all records
    for ip in models.IPAddress.select():
        print(ip.ip, ip.lastSeen)

    message = request.query_params.get("message")
    if message:
        response["message"] = message

    return response
