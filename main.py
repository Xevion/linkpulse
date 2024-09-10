from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()


@app.get("/")
async def get_current_time(request: Request):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_ip = request.headers.get("X-Forwarded-For")
    return {"time": current_time, "ip": user_ip}
