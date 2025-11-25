import pytest
from unittest.mock import Mock, AsyncMock
from backend.services.url import UrlShortenerService
from backend.models.model import UrlMapping
from fastapi import HTTPException

@pytest.fixture
def mock_repos():
    url_repo = AsyncMock()
    stats_repo = AsyncMock()
    cache = AsyncMock()
    return url_repo,stats_repo,cache

@pytest.fixture
def service(mock_repos):
    url_repo, stats_repo,cache = mock_repos
    return UrlShortenerService(url_repo,stats_repo,cache)

@pytest.mark.asyncio
async def test_shorten_url_new(service,mock_repos):
    url_repo,stats_repo,cache =mock_repos

    # setup mocks
    url_mapping:UrlMapping = Mock()
    url_mapping.id =123
    url_mapping.short_code = None

    url_repo.get_by_long_url.return_value=None
    url_repo.create.return_value=url_mapping

    # execute
    short_code = await service.shorten_url("https://example.com")

    # veryfy
    assert short_code is not None
    url_repo.create.assert_called_once()
    stats_repo.create.assert_called_once()
    cache.set_url.assert_called_once()

@pytest.mark.asyncio
async def test_shorten_url_existing(service,mock_repos):
    url_repo,stats_repo,cache =mock_repos
    existing:UrlMapping = Mock()
    existing.short_code="abc123"
    url_repo.get_by_long_url = AsyncMock(return_value= existing)

    short_code = await service.shorten_url("https://example.com")

    assert short_code == "abc123"
    url_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_custom_code_invalid_chars(service,mock_repos):
    url_repo,stats_repo,cache =mock_repos
    url_repo.get_by_long_url.return_value = None
    with pytest.raises (HTTPException) as exc:
        await service.shorten_url("https://example.com",custom_code="abc-123!")
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_custom_code_taken(service,mock_repos):
    url_repo,_,_ = mock_repos
    url_repo.get_by_long_url.return_value = None
    url_repo.custom_code_exists.return_value = True

    with pytest.raises(HTTPException) as exc:
        await service.shorten_url("https://example.com",custom_code='taken')
    assert exc.value.status_code == 409

@pytest.mark.asyncio
async def test_resolve_from_cache(service,mock_repos):
    url_repo,_,cache = mock_repos
    cache.get_url.return_value = "https://cached.com"
    result = await service.resolve_short_code("abc123")

    assert result == "https://cached.com"
    url_repo.get_by_short_code.assert_not_called()

@pytest.mark.asyncio
async def test_resolve_cache_miss(service,mock_repos):
    url_repo,_,cache = mock_repos
    cache.get_url.return_value = None

    mapping = Mock()
    mapping.long_url="https://example.com"
    url_repo.get_by_short_code.return_value = mapping

    result = await service.resolve_short_code("abc123")

    assert result == "https://example.com"
    cache.set_url.assert_called_once_with("abc123","https://example.com")

@pytest.mark.asyncio
async def test_resolve_not_found(service,mock_repos):
    url_repo,_,cache = mock_repos
    cache.get_url.return_value = None
    url_repo.get_by_short_code.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.resolve_short_code("Not Found")
    assert exc.value.status_code == 404

