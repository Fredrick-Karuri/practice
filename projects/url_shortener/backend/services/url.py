from fastapi import HTTPException
from ..repository.url import UrlRepository
from ..repository.stats import StatsRepository
from .cache import CacheService
from typing import Optional
from ..utils.id_to_base import BASE62, id_to_base
from ..models.model import UrlMapping

class UrlShortenerService:
    def __init__(
        self,
        url_repo:UrlRepository,
        stats_repo:StatsRepository,
        cache:CacheService
        ):
        self.url_repo=url_repo
        self.stats_repo=stats_repo
        self.cache=cache
    
    async def shorten_url(self,long_url:str,custom_code:Optional[str]=None)->str:
        # check if url is already shortened
        existing:UrlMapping = await self.url_repo.get_by_long_url(long_url)
        if existing:
            return existing.short_code
        
        # handle custom vs auto-generated code
        if custom_code:
            short_code = await self._create_custom_short_url(long_url,custom_code)
        else:
            short_code = await self._create_auto_short_url(long_url)
        
        # initialize stats and commit
        await self.stats_repo.create(short_code)
        await self.url_repo.commit()

        # cache the mapping
        await self.cache.set_url(short_code,long_url)

        return short_code
    
    async def _create_custom_short_url(self,long_url:str,custom_code:str)-> str:
        # validate custom code
        if not all(c in BASE62 for c in custom_code):
            raise HTTPException(400,"Custom code must be Alphanumeric")
        
        # check availability
        if await self.url_repo.custom_code_exists(custom_code):
            raise HTTPException(409,"Custom code already taken")
        
        # create with custom code
        await self.url_repo.create(long_url,short_code=custom_code)
        return custom_code
    
    async def _create_auto_short_url(self,long_url:str)-> str:
        # create mapping to get auto-increment ID
        url_mapping:UrlMapping = await self.url_repo.create(long_url)

        # generate short_code from ID
        short_code = id_to_base(url_mapping.id)
        url_mapping.short_code = short_code
        return short_code
    
    async def resolve_short_code(self,short_code:str)->str:
        # check cache first
        cached_url = await self.cache.get_url(short_code)
        if cached_url:
            return cached_url

        # cache miss - fetch from db
        url_mapping:UrlMapping = await self.url_repo.get_by_short_code(short_code)
        if not url_mapping:
            raise HTTPException(404, "Short URL not found")
        
        # cache for next time
        await self.cache.set_url(short_code,url_mapping.long_url)

        return url_mapping.long_url
    
    async def track_click(self,short_code:str):
        await self.stats_repo.increment_click(short_code)
    
    async def get_stats(self, short_code:str):
        result = await self.stats_repo.get_with_mapping(short_code) 
        if not result:
            raise HTTPException(404, "Short URL not found")
        return result


    





        