import asyncio
from unittest.mock import AsyncMock, Mock
from jsscanner.strategies.active import ActiveFetcher

async def reproduce():
    cfg = {'retry':{'http_requests':3}, 'playwright':{'max_concurrent':1,'restart_after':5,'page_timeout':30000,'headless':True}}
    fetcher = ActiveFetcher(cfg, logger=Mock())
    mock_async_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "console.log('test');"
    mock_response.headers = {'Content-Type':'application/javascript'}
    mock_async_session.get = AsyncMock(return_value=mock_response)
    # no head mock
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = Mock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()

    result = await fetcher._fetch_content_impl('https://example.com/app.js')
    print('RESULT:',repr(result))

if __name__ == '__main__':
    asyncio.run(reproduce())
