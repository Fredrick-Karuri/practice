from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine
from redis_client import init_redis,close_redis

from models.database import Base

from api.endpoints import router



@asynccontextmanager
async def lifespan(app:FastAPI):
    # startup
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # initialize redis
    await init_redis()
    yield

    # shutdown
    await close_redis()
    
app = FastAPI(title="Url Shortener", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)


@app.get("/")
async def health():
    return {"status":"healthy"}