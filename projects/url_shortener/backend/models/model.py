from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class UrlMapping(BaseModel):
    id: int
    long_url: str
    short_code: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime

    model_config=ConfigDict(
        from_attributes=True
    )

class UrlStats(BaseModel):
    short_code: str
    click_count: int = 0
    last_clicked_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes= True
    )