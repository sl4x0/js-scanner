"""
Quick debug script to test fetch_content behavior
"""
import asyncio
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from jsscanner.strategies.active import ActiveFetcher

async def test_fetch():
    config = {
        'timeout': 15,
        'max_file_size': 5242880,
        'verbose': True,
        'retry': {'http_requests': 3, 'backoff_base': 2.0, 'jitter': True},
        'session_management': {'download_timeout': 45},
        'playwright': {'headless': True}
    }

    mock_logger = Mock()
    fetcher = ActiveFetcher(config, logger=mock_logger)

    # Mock session
    mock_session = AsyncMock()
    fetcher.session = mock_session
    fetcher.session_pool = [mock_session]

    # Mock response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "console.log('test');"
    mock_response.headers = {'Content-Type': 'application/javascript'}
    mock_session.get = AsyncMock(return_value=mock_response)

    # Mock components
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))

    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked_async = AsyncMock(return_value=False)
    fetcher.circuit_breaker.record_success = AsyncMock()
    fetcher.circuit_breaker.record_failure = AsyncMock()

    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()

    fetcher.browser_manager = None  # No browser

    # Call fetch_content
    print("Calling fetch_content...")
    try:
        content = await fetcher.fetch_content('https://example.com/app.js')
        print(f"Result: {content!r}")
        expected = "console.log('test');"
        print(f"Expected: {expected!r}")
        print(f"Match: {content == expected}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_fetch())
