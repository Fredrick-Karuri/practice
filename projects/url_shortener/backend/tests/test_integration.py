import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
os.environ["DATABASE_URL"]= "sqlite+aiosqlite:///:memory:"

from backend.models.database import Base
from backend.database import get_db
from backend.main import app

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:",echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine,class_=AsyncSession,expire_on_commit=False)
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db

    yield

    await engine.dispose()
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_shorten_url_flow(test_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
        ) as client:
        response = await client.post("/shorten",json={
            "long_url":"https://example.com/very/long/url"
        })
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert "short_url" in data
        assert data["short_url"].endswith(data["short_code"])
