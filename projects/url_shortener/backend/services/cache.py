
from redis.asyncio import Redis
from typing import Optional
class CacheService:
    def __init__(self,redis_client:Redis):
        self.redis = redis_client
        self.ttl = 300 #5 minutes

    def _make_key(self,short_code:str)->str:
        return f"url:{short_code}"
    
    async def get_url(self,short_code:str)->Optional[str]:
        cached = await self.redis.get(self._make_key(short_code))
        return cached.decode() if cached else None
    async def set_url(self,short_code:str,long_url:str):
        await self.redis.setex(self._make_key(short_code),self.ttl,long_url)
    
    async def delete_url(self,short_code:str):
        await self.redis.delete(self._make_key(short_code))