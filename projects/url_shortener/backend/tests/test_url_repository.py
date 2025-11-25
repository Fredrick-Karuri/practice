import pytest
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer
from backend.models.database import Base,UrlMapping,UrlStats
from backend.repository.url import UrlRepository


@pytest.fixture
async def db_session():

    # Patch ID column for SQLite test runtime(BigInteger in SQLite does not auto increment)
    UrlMapping.__table__.c.id.type = Integer()

    # in-memory SQlite for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:",echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine,class_=AsyncSession,expire_on_commit=False)
    async with async_session () as session:
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_url_mapping(db_session):
    repo = UrlRepository(db_session)

    url = await repo.create("https://example.com",short_code="abc123")
    await db_session.commit()

    assert url.long_url == "https://example.com"
    assert url.short_code == "abc123"
    assert url.id is not None



