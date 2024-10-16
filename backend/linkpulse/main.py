from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")

print(os.environ.get("ENVIRONMENT"))

app = FastAPI()

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


@app.get("/api/test")
async def get_current_time(request: Request):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user_ip = request.headers.get("X-Forwarded-For")
    if not user_ip:
        # Fallback, probably not on a proxy
        user_ip = request.client.host

    response = {"time": current_time, "ip": user_ip}

    message = request.query_params.get("message")
    if message:
        response["message"] = message

    return response
