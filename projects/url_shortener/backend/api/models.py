from datetime import datetime
from pydantic import BaseModel,HttpUrl

class ShortenRequest(BaseModel):
    long_url:HttpUrl
    custom_code:str | None = None

class ShortenResponse(BaseModel):
    """
    Response model for shortened URLs.

    Attributes:
    short_code (str): Short code for the shortened URL.
    short_url (str): Shortened URL.
    """
    short_code:str
    short_url:str

class StatsResponse(BaseModel):
    short_code:str
    long_url:str
    clicks:int
    created_at:datetime
    last_clicked_at:datetime | None