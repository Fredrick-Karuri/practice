from fastapi import Request,Depends,HTTPException,APIRouter
from fastapi.responses import RedirectResponse
from api.models import ShortenRequest, ShortenResponse,StatsResponse
from database import get_db,engine
import os

from models.model import UrlMapping,UrlStats
from repository.stats import StatsRepository
from services.url import UrlShortenerService
from sqlalchemy.ext.asyncio import AsyncSession

import asyncio
from dependencies import get_url_service

router = APIRouter()

@router.post("/shorten",response_model=ShortenResponse,status_code=201)
async def shorten_url(
    req:ShortenRequest,
    request:Request,
    service:UrlShortenerService =(Depends(get_url_service))
    ):

    """
    Shorten a given long URL.
    """
    short_code = await service.shorten_url(
        long_url=str(req.long_url),
        custom_code=req.custom_code
    )

    base_url = os.getenv("BASE_URL",str(request.base_url).rstrip('/'))

    return ShortenResponse(
        short_url= f"{base_url}/{short_code}",
        short_code=short_code
    )


@router.get("/{short_code}")
async def redirect_url(
    short_code:str,
    service:UrlShortenerService = Depends(get_db)
    ):
    # check cache first
    """
    Redirects a shortened URL back to its original long URL.

    Also schedules an asynchronous task to increment the click count for the shortened URL.

    """

    long_url = await service.resolve_short_code(short_code)

    # fire and forget click tracking
    asyncio.create_task(track_click_background(short_code))

    redirect_response = RedirectResponse(url=long_url,status_code=302)
    return redirect_response

async def track_click_background(self,short_code:str):
    async with AsyncSession(engine) as session:
        stats_repo = StatsRepository(session)
        await stats_repo.increment_click(short_code)


@router.get("/stats/{short_code}", response_model=StatsResponse)
async def get_stats(
    short_code:str, 
    service:UrlShortenerService = Depends(get_url_service)
    ):

    url_mapping,url_stats = await service.get_stats(short_code)
    
    url_mapping:UrlMapping
    url_stats:UrlStats

    return StatsResponse(
        short_code=url_mapping.short_code,
        long_url=url_mapping.long_url,
        clicks=url_stats.click_count,
        created_at=url_mapping.created_at,
        last_clicked_at=url_stats.last_clicked_at
    )