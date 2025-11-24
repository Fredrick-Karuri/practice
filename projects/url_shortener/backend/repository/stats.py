from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import UrlStats,UrlMapping
from sqlalchemy import select

class StatsRepository:
    def __init__(self,db:AsyncSession):
        self.db=db

    async def create(self,short_code:str)->UrlStats:
        stats =UrlStats(
            short_code = short_code,
            click_count = 0
        )
        self.db.add(stats)
        return stats

    async def increment_click(self,short_code:str):
        stmt = select(UrlStats).where(UrlStats.short_code == short_code)
        result = await self.db.execute(stmt)
        stats=result.scalar_one_or_none()
        if stats:
            stats.click_count+=1
            stats.last_clicked_at = datetime.utcnow()
            await self.db.commit()
    
    async def get_with_mapping(self,short_code:str)->Optional[tuple[UrlMapping,UrlStats]]:
        """
        Retrieves a UrlMapping and its corresponding UrlStats from the database.
        """
        stmt = select(UrlMapping,UrlStats).join(
                UrlStats,UrlMapping.short_code == UrlStats.short_code
            ).where(UrlMapping.short_code == short_code)
        result = await self.db.execute(stmt)
        return result.first()