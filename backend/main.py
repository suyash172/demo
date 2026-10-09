import hashlib
import json
import os

import httpx
import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Without this, the browser blocks the frontend from calling the backend (classic CORS error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.from_url(os.environ["REDIS_URL"])
ML_URL = os.environ["ML_URL"]


class Txn(BaseModel):
    amount: float
    merchant: str
    country: str = "IN"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check")
def check(t: Txn):
    key = "txn:" + hashlib.md5(t.model_dump_json().encode()).hexdigest()
    cached = r.get(key)
    if cached:
        return {**json.loads(cached), "cached": True}
    res = httpx.post(f"{ML_URL}/predict", json=t.model_dump(), timeout=5).json()
    r.setex(key, 60, json.dumps(res))
    return {**res, "cached": False}
