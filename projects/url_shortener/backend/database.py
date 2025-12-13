from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from utils.postgres_conversion import convert_postgres_sync_to_async

_engine = None
_AsyncSessionLocal = None

def get_engine():
    global _engine
    if _engine is None:

        DATABASE_URL = convert_postgres_sync_to_async(os.getenv("DATABASE_URL"))

        if DATABASE_URL and "sqlite" in DATABASE_URL:
            _engine = create_async_engine(DATABASE_URL,echo=False)
        else:
            _engine = create_async_engine(
                DATABASE_URL,echo=False,
                pool_size=20,
                max_overflow=0
            )
    return _engine
def get_session_local():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:

        _AsyncSessionLocal = sessionmaker(
            get_engine(),
            class_= AsyncSession,
            expire_on_commit=False
        )
    return _AsyncSessionLocal

async def get_db ():
    async with get_session_local()() as session:
        yield session
      