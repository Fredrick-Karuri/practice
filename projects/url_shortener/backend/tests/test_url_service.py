import pytest
from unittest.mock import Mock, AsyncMock
from ..services.url import UrlShortenerService
from ..models.model import UrlMapping

@pytest.fixture
def mock_repos():
    url_repo = Mock()
    stats_repo = Mock()
    cache = Mock()
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
    url_mapping.short_code =None

    url_repo.get_by_long_url = AsyncMock(return_value = None)
    url_repo.create= AsyncMock(return_value=url_mapping)
    stats_repo.create=AsyncMock()
    url_repo.commit=AsyncMock()
    cache.set_url=AsyncMock()

    # execute
    short_code = await service.shorten_url("https://example.com")

    # veryfy
    assert short_code is not None
    url_repo.create.assert_called_once()
    stats_repo.create.assert_called_once()
    cache.set_url.assert_called_once()