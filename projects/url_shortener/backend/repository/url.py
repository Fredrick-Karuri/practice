from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import UrlMapping

class UrlRepository:
    def __init__(self,db:AsyncSession):
        self.db = db
    
    async def get_by_long_url(self, long_url:str)->Optional[UrlMapping]:
        stmt = select(UrlMapping).where(UrlMapping.long_url == long_url)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_short_code(self,short_code:str)->Optional[UrlMapping]:
        stmt = select(UrlMapping).where(UrlMapping.short_code == short_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    async def create(self,long_url:str,short_code:Optional[str]=None)->UrlMapping:
        url_mapping = UrlMapping(
            long_url=long_url,
            short_code=short_code,
            created_at=datetime.utcnow()
        )
        self.db.add(url_mapping)
        await self.db.flush()
        return url_mapping

    async def custom_code_exists(self,custom_code:str)-> bool:
        stmt = select(UrlMapping).where(UrlMapping.short_code == custom_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def commit(self):
        await self.db.commit()   