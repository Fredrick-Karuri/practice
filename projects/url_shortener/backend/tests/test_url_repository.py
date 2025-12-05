import pytest
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer,select
from backend.models.database import Base,UrlMapping,UrlStats
from backend.repository.url import UrlRepository
from backend.repository.stats import StatsRepository


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

@pytest.mark.asyncio
async def test_get_by_long_url(db_session):
    repo = UrlRepository(db_session)
    long_url = "https://example.com"
    short_code = "abc123"

    await repo.create(long_url,short_code)
    await db_session.commit()

    found = await repo.get_by_long_url(long_url)

    assert found is not None
    assert found.short_code == short_code


@pytest.mark.asyncio
async def test_get_by_short_code(db_session):
    repo = UrlRepository(db_session)
    long_url = "https://example.com"
    short_code = "abc123"

    await repo.create(long_url,short_code)
    await db_session.commit()

    found = await repo.get_by_short_code(short_code)

    assert found is not None
    assert found.long_url == long_url

@pytest.mark.asyncio
async def test_custom_code_exists(db_session):
    repo = UrlRepository(db_session)
    long_url = "https://example.com"
    short_code = "taken"

    await repo.create(long_url,short_code)
    await db_session.commit()

    assert await repo.custom_code_exists("taken") is True
    assert await repo.custom_code_exists("available") is False

@pytest.mark.asyncio
async def test_create_stats(db_session):
    stats_repo = StatsRepository(db_session)
    short_code = "abc123"

    stats = await stats_repo.create(short_code)
    await db_session.commit()

    assert stats.short_code == short_code
    assert stats.click_count == 0

@pytest.mark.asyncio
async def test_increment_click(db_session):
    stats_repo = StatsRepository(db_session)
    short_code = "abc123"

    await stats_repo.create(short_code)
    await db_session.commit()

    await stats_repo.increment_click(short_code)

    result = await db_session.execute(
        select(UrlStats.click_count).where(UrlStats.short_code == short_code)
    )
    count = result.scalar()
    assert count == 1

@pytest.mark.asyncio
async def test_get_with_mapping(db_session):
    url_repo  = UrlRepository(db_session)
    stats_repo = StatsRepository(db_session)
    long_url = "https://example.com"
    short_code = 'abc123'

    await url_repo.create(long_url,short_code)
    await stats_repo.create(short_code)
    await db_session.commit()

    result = await stats_repo.get_with_mapping(short_code)

    assert result is not None
    url_mapping,url_stats = result
    assert url_mapping.long_url == long_url
    assert url_stats.click_count == 0
