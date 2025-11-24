from database import get_db
from services.cache import CacheService
from repository.stats import StatsRepository
from repository.url import UrlRepository
from services.url import UrlShortenerService
from sqlalchemy.ext.asyncio import AsyncSession
from redis_client import get_redis
from fastapi import Depends

async def get_url_service(db:AsyncSession=Depends(get_db))->UrlShortenerService:
    redis_client = await get_redis()
    url_repo = UrlRepository(db)
    stats_repo = StatsRepository(db)
    cache = CacheService(redis_client)
    return UrlShortenerService(url_repo,stats_repo,cache)