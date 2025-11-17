from fastapi import Request,Depends,HTTPException,APIRouter
from fastapi.responses import RedirectResponse
from backend.api.models import ShortenRequest, ShortenResponse,StatsResponse
from backend.database import get_db,engine
import os

from backend.utils import BASE62, id_to_base
from backend.models import UrlMapping,UrlStats

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime

import asyncio

from redis_client import get_redis
from redis.asyncio import Redis

router = APIRouter()

redis_client:Redis = get_redis()

@router.post("/shorten",response_model=ShortenResponse,status_code=201)
async def shorten_url(req:ShortenRequest,request:Request,db:AsyncSession=Depends(get_db)):

    """
    Shorten a given long URL.

    Args:
        req (ShortenRequest): A model containing the long URL to shorten and an optional custom code.
        request (Request): The FastAPI request object.
        db (AsyncSession): The SQLAlchemy async session dependency.

    Returns:
        ShortenResponse: A model containing the shortened URL and its corresponding short code.

    Raises:
        HTTPException: If the custom code is invalid or already taken.
    """
    long_url = str(req.long_url)

    # check if long_url already exists
    stmt = select(UrlMapping.long_url == long_url)

    existing = await get_url_mapping_if_exists(db, stmt)

    if existing:
        short_code= existing.short_code
    else:
        # handle custom code
        if req.custom_code:
            # validate custom code
            await handle_custom_short_code(req, db, long_url)
        
        else:
            # insert and get autoincrement id
            url_mapping = await create_url_mapping(db, long_url)

            # generate shortcode from ID
            short_code = generate_short_code(url_mapping)

        # initialize stats
        initialize_url_stats(db, short_code)

        await save_url_mapping(db)

        # cache in redis(5 min TTL)
        await cache_url_mapping(long_url, short_code)

    base_url = os.getenv("BASE_URL",str(request.base_url).rstrip('/'))

    return ShortenResponse(
        short_url= f"{base_url}/{short_code}",
        short_code=short_code
    )

async def save_url_mapping(db):
    await db.commit()

async def cache_url_mapping(long_url, short_code):
    await redis_client.setex(f"url:{short_code}",300,long_url)

def initialize_url_stats(db:AsyncSession, short_code):
    url_stats =UrlStats(
            short_code = short_code,
            click_count = 0
        )
    db.add(url_stats)

def generate_short_code(url_mapping:UrlMapping):
    short_code = id_to_base(url_mapping.id)
    url_mapping.short_code =short_code
    return short_code

async def create_url_mapping(db:AsyncSession, long_url):
    url_mapping = UrlMapping(
                long_url=long_url,
                created_at = datetime.utcnow()
            )
    db.add(url_mapping)
    await db.flush()
    return url_mapping

async def handle_custom_short_code(req:ShortenRequest, db:AsyncSession, long_url):
    if not all(c in BASE62 for c in req.custom_code):
        raise HTTPException(400,"Custom code must be Alphanumeric")
            
            # check availability
    stmt = select(UrlMapping).where(UrlMapping.short_code == req.custom_code)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(409,"Custom code already taken")
            
    short_code =req.custom_code

            # insert with custom code
    url_mapping = UrlMapping(
                long_url=long_url,
                short_code = short_code,
                created_at = datetime.utcnow()
            )
    db.add(url_mapping)

async def get_url_mapping_if_exists(db:AsyncSession, stmt):
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    return existing

@router.get("/{short_code}")
async def redirect_url(short_code:str,db:AsyncSession=Depends(get_db)):
    # check cache first
    """
    Redirects a shortened URL back to its original long URL.

    Checks the cache first, and if it's a cache miss, fetches the URL from the database,
    caches it for the next time, and then redirects the client to the original URL.

    Also schedules an asynchronous task to increment the click count for the shortened URL.

    Args:
        short_code (str): The shortened code to redirect.

    Returns:
        RedirectResponse: A response object with the original URL and a status code of 302.
    """
    cached_url = await get_cached_url(short_code)

    if cached_url:
        long_url = cached_url
    else:
        # cache miss fetch from DB
        url_mapping = await get_url_mapping(short_code, db)
        
        long_url = url_mapping.long_url

        # cache for next time
        await cache_long_url(short_code, long_url)
    
    # async increment click count (fire and forget)
    # schedule async without blocking
    
    asyncio.create_task(track_click(short_code))

    redirect_response = RedirectResponse(url=long_url,status_code=302)
    return redirect_response

async def track_click(short_code:str):
    async with AsyncSession(engine) as session:
        stmt = select(UrlStats).where(UrlStats.short_code == short_code)
        result = await session.execute(stmt)
        stats = result.scalar_one_or_none()

        if stats:
            stats.click_count += 1
            stats.last_clicked_at = datetime.utcnow()
            await session.commit()

async def cache_long_url(short_code, long_url):
    await redis_client.setex(f"url:{short_code}",300,long_url)

async def get_url_mapping(short_code, db:AsyncSession):
    stmt = select(UrlMapping).where(UrlMapping.short_code == short_code)
    result = await db.execute(stmt)
    url_mapping = result.scalar_one_or_none()

    if not url_mapping:
        raise HTTPException(404, "Short url not found")
    return url_mapping

async def get_cached_url(short_code):
    cached_url = await redis_client.get(f"url:{short_code}")
    return cached_url


@router.get("/stats/{short_code}", response_model=StatsResponse)
async def get_stats(short_code:str, db:AsyncSession=Depends(get_db)):
    row = await get_url_stats(short_code, db)

    if not row:
        raise HTTPException(404, "Short URL not found")
    
    url_mapping:UrlMapping
    url_stats:UrlStats
    url_mapping, url_stats = row

    return StatsResponse(
        short_code=url_mapping.short_code,
        long_url=url_mapping.long_url,
        clicks=url_stats.click_count,
        created_at=url_mapping.created_at,
        last_clicked_at=url_stats.last_clicked_at
    )

async def get_url_stats(short_code, db:AsyncSession):
    stmt = select(UrlMapping,UrlStats).join(
        UrlStats,UrlMapping.short_code == UrlStats.short_code
    ).where(UrlMapping.short_code == short_code)

    result = await db.execute(stmt)
    row = result.first()
    return row