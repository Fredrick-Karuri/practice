from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine
import redis.asyncio as redis
import os

from backend.models import Base

# global redis client
redis_client = None

@asynccontextmanager
async def lifespan(app:FastAPI):
    # startup
    global redis_client

    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    redis_client = await redis.from_url(
        os.getenv("REDIS_URL","redis://localhost:6379"),
        encoding="utf-8",
        decode_responses=True
    )
    yield

    # shutdown
    await redis_client.close()
    
app = FastAPI(title="Url Shortener", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.get("/health")
async def health():
    return {"status":"healthy"}


