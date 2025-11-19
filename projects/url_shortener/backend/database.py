from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from utils.postgres_conversion import convert_postgres_sync_to_async

DATABASE_URL = convert_postgres_sync_to_async(os.getenv("DATABASE_URL"))

engine = create_async_engine(DATABASE_URL,echo=False,pool_size=20,max_overflow=0)

AsyncSessionLocal = sessionmaker(
    engine,
    class_= AsyncSession,
    expire_on_commit=False
)

async def get_db ():
    async with AsyncSessionLocal() as session:
        yield session
      