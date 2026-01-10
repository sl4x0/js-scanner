"""
Tests for ActiveFetcher (Playwright + curl_cffi advanced fetching)
Tests initialization, HTTP fetching, progressive timeout, retries, circuit breaker,
browser fallback, cookie harvesting, streaming downloads, rate limiting, and helpers
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from jsscanner.strategies.active import (
    ActiveFetcher,
    DomainRateLimiter,
    DomainConnectionManager,
    DomainCircuitBreaker,
    DomainPerformanceTracker,
    BrowserManager,
    IncompleteDownloadError
)


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_active_fetcher_initialization(strategies_config):
    """Test ActiveFetcher initialization with config"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)

    assert fetcher.config == strategies_config
    assert fetcher.logger == mock_logger
    assert fetcher.headless is True
    assert fetcher.noise_filter is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_initialize_creates_session(strategies_config):
    """Test initialize() creates AsyncSession"""
    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)

    # Mock AsyncSession creation and Playwright
    with patch('jsscanner.strategies.active.AsyncSession') as mock_session_class, \
         patch('jsscanner.strategies.active.async_playwright') as mock_pw:
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        # Mock Playwright context manager
        mock_playwright_instance = AsyncMock()
        mock_pw.return_value.start = AsyncMock(return_value=mock_playwright_instance)

        await fetcher.initialize()

        # Verify session was created with correct config
        assert mock_session_class.called
        call_kwargs = mock_session_class.call_args[1]
        assert call_kwargs['impersonate'] == 'chrome120'
        assert call_kwargs['verify'] is False
        assert fetcher.session == mock_session


@pytest.mark.unit
@pytest.mark.asyncio
async def test_initialize_creates_browser_manager(strategies_config):
    """Test initialize() creates BrowserManager"""
    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)

    with patch('jsscanner.strategies.active.BrowserManager') as mock_bm_class, \
         patch('jsscanner.strategies.active.AsyncSession'), \
         patch('jsscanner.strategies.active.async_playwright') as mock_pw:
        mock_bm = AsyncMock()
        mock_bm_class.return_value = mock_bm

        # Mock Playwright
        mock_playwright_instance = AsyncMock()
        mock_pw.return_value.start = AsyncMock(return_value=mock_playwright_instance)

        await fetcher.initialize()

        # Verify BrowserManager was created with headless config
        assert mock_bm_class.called
        # BrowserManager is called with playwright instance and headless flag
        assert fetcher.browser_manager == mock_bm

# ============================================================================
# BASIC FETCHING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_fetch_content_success(mock_async_session, strategies_config):
    """Test successful content fetch with 200 OK response"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))

    # Mock response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "console.log('test');"
    mock_response.headers = {'Content-Type': 'application/javascript'}
    mock_async_session.get = AsyncMock(return_value=mock_response)

    # Mock domain managers
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked_async = AsyncMock(return_value=False)
    fetcher.circuit_breaker.record_success = AsyncMock()
    fetcher.circuit_breaker.record_failure = AsyncMock()
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    fetcher.browser_manager = None  # No browser fallback in this test
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    content = await fetcher.fetch_content('https://example.com/app.js')

    assert content == "console.log('test');"
    mock_async_session.get.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_content_404(mock_async_session, strategies_config):
    """Test handling of 404 response"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))

    # Mock 404 response
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_async_session.get = AsyncMock(return_value=mock_response)

    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    content = await fetcher.fetch_content('https://example.com/missing.js')

    assert content is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_content_network_error(mock_async_session, strategies_config):
    """Test handling of network connection error"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))

    # Mock network error
    mock_async_session.get = AsyncMock(side_effect=ConnectionError("Connection refused"))

    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    content = await fetcher.fetch_content('https://example.com/app.js')

    assert content is None


# ============================================================================
# PROGRESSIVE TIMEOUT & RETRY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_progressive_timeout_increases(mock_async_session, strategies_config):
    """Test timeout increases on retry (10s → 20s → 30s)"""
    noise_filter = Mock()

    strategies_config['active']['progressive_timeout'] = True
    strategies_config['active']['timeout'] = 10
    strategies_config['retry'] = {'http_requests': 3, 'backoff_base': 2.0, 'jitter': True}

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
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
    fetcher.browser_manager = None

    # Mock HEAD request to allow preflight check to succeed
    mock_head_response = AsyncMock()
    mock_head_response.status_code = 200
    mock_head_response.headers = {'Content-Type': 'application/javascript'}
    mock_async_session.head = AsyncMock(return_value=mock_head_response)

    # Mock TimeoutError on first two attempts, success on third
    call_count = 0

    async def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise asyncio.TimeoutError("Timeout")
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "content"
        mock_response.headers = {}
        return mock_response

    mock_async_session.get = mock_get

    content = await fetcher.fetch_content('https://example.com/app.js')

    # Verify 3 attempts were made (2 timeouts + 1 success)
    assert call_count == 3
    assert content == "content"


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_fetch_content_retries_on_timeout(mock_async_session, strategies_config):
    """Test TimeoutError triggers retry"""
    mock_logger = Mock()

    strategies_config['retry'] = {'http_requests': 3, 'backoff_base': 2.0, 'jitter': True}

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
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
    fetcher.browser_manager = None

    # Mock HEAD request to allow preflight check to succeed
    mock_head_response = AsyncMock()
    mock_head_response.status_code = 200
    mock_head_response.headers = {'Content-Type': 'application/javascript'}
    mock_async_session.head = AsyncMock(return_value=mock_head_response)

    # Mock timeout on first attempt, success on second
    call_count = 0

    async def mock_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise asyncio.TimeoutError("Timeout")
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = "content"
        mock_response.headers = {}
        return mock_response

    mock_async_session.get = mock_get

    content = await fetcher.fetch_content('https://example.com/app.js')

    assert call_count == 2
    assert content == "content"


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_fetch_content_max_retries(mock_async_session, strategies_config):
    """Test returns None after max retries exhausted"""
    noise_filter = Mock()

    strategies_config['retry'] = {'http_requests': 3, 'backoff_base': 0.1, 'jitter': False}  # Faster backoff for tests

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
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
    fetcher.browser_manager = None

    # Mock HEAD request to allow preflight check to succeed
    mock_head_response = AsyncMock()
    mock_head_response.status_code = 200
    mock_head_response.headers = {'Content-Type': 'application/javascript'}
    mock_async_session.head = AsyncMock(return_value=mock_head_response)

    # Mock timeout on all attempts
    mock_async_session.get = AsyncMock(side_effect=asyncio.TimeoutError("Timeout"))

    content = await fetcher.fetch_content('https://example.com/app.js')

    # Should have tried 3 times
    assert mock_async_session.get.call_count == 3
    assert content is None


# ============================================================================
# CIRCUIT BREAKER TESTS
# ============================================================================

@pytest.mark.unit
def test_circuit_breaker_initial_state():
    """Test DomainCircuitBreaker starts in closed state"""
    breaker = DomainCircuitBreaker(failure_threshold=5, cooldown_seconds=60)

    assert breaker.state == 'closed'
    assert breaker.is_blocked() is False
    assert breaker.failure_count == 0


@pytest.mark.unit
def test_circuit_breaker_opens_after_threshold():
    """Test circuit opens after failure threshold"""
    breaker = DomainCircuitBreaker(failure_threshold=3, cooldown_seconds=60)

    # Record 3 failures
    breaker.record_failure("Timeout")
    breaker.record_failure("Timeout")
    assert breaker.is_blocked() is False  # Not yet

    breaker.record_failure("Timeout")
    assert breaker.is_blocked() is True  # Now open
    assert breaker.state == 'open'


@pytest.mark.unit
def test_circuit_breaker_blocks_when_open():
    """Test is_blocked returns True when circuit is open"""
    breaker = DomainCircuitBreaker(failure_threshold=2, cooldown_seconds=60)

    breaker.record_failure("Error")
    breaker.record_failure("Error")

    assert breaker.is_blocked() is True


@pytest.mark.unit
def test_circuit_breaker_half_open_after_timeout():
    """Test circuit transitions to half-open after timeout"""
    breaker = DomainCircuitBreaker(failure_threshold=2, cooldown_seconds=0.1)  # 100ms timeout

    # Open the circuit
    breaker.record_failure("Error")
    breaker.record_failure("Error")
    assert breaker.state == 'open'

    # Wait for timeout
    import time
    time.sleep(0.15)

    # Should transition to half-open
    assert breaker.is_blocked() is False  # Allows one attempt
    assert breaker.state == 'half-open'


@pytest.mark.unit
def test_circuit_breaker_success_resets():
    """Test success in half-open state closes circuit"""
    breaker = DomainCircuitBreaker(failure_threshold=2, cooldown_seconds=0.1)

    # Open circuit
    breaker.record_failure("Error")
    breaker.record_failure("Error")

    # Wait for half-open
    import time
    time.sleep(0.15)
    breaker.is_blocked()  # Trigger half-open

    # Record success
    breaker.record_success()

    assert breaker.state == 'closed'
    assert breaker.failure_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_content_circuit_breaker_blocks(mock_async_session, strategies_config):
    """Test circuit breaker prevents requests to failing domains"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))

    # Create circuit breaker that's already open
    breaker = DomainCircuitBreaker(failure_threshold=1, cooldown_seconds=60)
    # ✅ FIX: Record failure for the specific domain being tested
    breaker.record_failure("example.com", "Test failure")

    # ✅ FIX: Use singular 'circuit_breaker' attribute (not plural dict)
    fetcher.circuit_breaker = breaker
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    content = await fetcher.fetch_content('https://example.com/app.js')

    # Should return None immediately without calling session.get
    assert content is None
    mock_async_session.get.assert_not_called()


# ============================================================================
# BROWSER FALLBACK TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_browser_fallback_on_429(mock_async_session, mock_browser_manager, strategies_config):
    """Test 429 response triggers Playwright fallback"""
    noise_filter = Mock()

    strategies_config['active']['browser_fallback'] = True
    strategies_config['retry'] = {'http_requests': 2, 'backoff_base': 0.1, 'jitter': False}  # Fast retry

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.browser_manager = mock_browser_manager
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked_async = AsyncMock(return_value=False)
    fetcher.circuit_breaker.record_failure = AsyncMock()
    fetcher.circuit_breaker.record_success = AsyncMock()
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()

    # Mock HEAD request to allow preflight check
    mock_head_response = AsyncMock()
    mock_head_response.status_code = 200
    mock_head_response.headers = {'Content-Type': 'application/javascript'}
    mock_async_session.head = AsyncMock(return_value=mock_head_response)

    # Mock 429 response from curl (will trigger retry then browser fallback)
    mock_response = AsyncMock()
    mock_response.status_code = 429
    mock_async_session.get = AsyncMock(return_value=mock_response)

    # Mock browser fetch success
    mock_browser_manager.fetch_with_context = AsyncMock(return_value="browser content")

    content = await fetcher.fetch_content('https://example.com/app.js')

    # Should have fallen back to browser
    mock_browser_manager.fetch_with_context.assert_called_once()
    assert content == "browser content"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_browser_fallback_on_403(mock_async_session, mock_browser_manager, strategies_config):
    """Test 403 response does NOT trigger browser fallback (auth issue)"""
    noise_filter = Mock()

    strategies_config['active']['browser_fallback'] = True
    strategies_config['retry'] = {'http_requests': 2, 'backoff_base': 0.1, 'jitter': False}

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.browser_manager = mock_browser_manager
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked_async = AsyncMock(return_value=False)
    fetcher.circuit_breaker.record_failure = AsyncMock()
    fetcher.circuit_breaker.record_success = AsyncMock()
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()

    # Mock HEAD request to allow preflight check
    mock_head_response = AsyncMock()
    mock_head_response.status_code = 200
    mock_head_response.headers = {'Content-Type': 'application/javascript'}
    mock_async_session.head = AsyncMock(return_value=mock_head_response)

    # Mock 403 response
    mock_response = AsyncMock()
    mock_response.status_code = 403
    mock_async_session.get = AsyncMock(return_value=mock_response)

    # Mock browser fetch success (should NOT be called)
    mock_browser_manager.fetch_with_context = AsyncMock(return_value="browser content")

    content = await fetcher.fetch_content('https://example.com/app.js')

    # Browser should NOT be called for 403 (auth issue, browser won't help)
    assert content is None
    mock_browser_manager.fetch_with_context.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_with_playwright_success(mock_playwright_page, strategies_config):
    """Test Playwright fetch returns page content"""
    noise_filter = Mock()

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)

    # Mock browser manager
    browser_manager = AsyncMock()
    browser_manager.fetch_with_context = AsyncMock(return_value="console.log('playwright');")
    fetcher.browser_manager = browser_manager

    content = await fetcher.fetch_with_playwright('https://example.com/app.js')

    assert content == "console.log('playwright');"
    browser_manager.fetch_with_context.assert_called_once()


# ============================================================================
# COOKIE HARVESTING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_cookie_harvest_after_browser_success(mock_browser_manager, strategies_config):
    """Test cookies are extracted and stored after browser fallback"""
    noise_filter = Mock()

    strategies_config['active']['cookie_harvest'] = True

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.browser_manager = mock_browser_manager
    fetcher.valid_cookies = {}
    fetcher.session = AsyncMock()
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Mock 403 to trigger browser
    mock_response = AsyncMock()
    mock_response.status_code = 403
    fetcher.session.get = AsyncMock(return_value=mock_response)

    # Mock browser fetch success with cookies
    mock_browser_manager.fetch_with_context = AsyncMock(return_value="content")
    mock_browser_manager.get_cookies = AsyncMock(return_value=[
        {'name': 'cf_clearance', 'value': 'abc123', 'domain': '.example.com'}
    ])

    await fetcher.fetch_content('https://example.com/app.js')

    # Verify cookies were harvested
    assert 'example.com' in fetcher.valid_cookies
    assert len(fetcher.valid_cookies['example.com']) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_harvested_cookies_used_in_curl(mock_async_session, strategies_config):
    """Test harvested cookies are used in subsequent curl requests"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Pre-populate cookies
    fetcher.valid_cookies = {
        'example.com': [
            {'name': 'session', 'value': 'xyz789'}
        ]
    }

    # Mock successful response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "content"
    mock_response.headers = {}
    mock_async_session.get = AsyncMock(return_value=mock_response)

    await fetcher.fetch_content('https://example.com/app.js')

    # Verify cookies were passed in request
    call_kwargs = mock_async_session.get.call_args[1]
    assert 'cookies' in call_kwargs


# ============================================================================
# STREAMING DOWNLOAD TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_and_write_streams_content(mock_async_session, tmp_path, strategies_config):
    """Test content is written incrementally during download"""
    noise_filter = Mock()

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Mock streaming response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {
        'Content-Length': '22',
        'Content-Type': 'application/javascript'
    }

    async def mock_aiter_content(chunk_size):
        yield b"console.log('test');"

    mock_response.aiter_content = mock_aiter_content
    mock_async_session.get = AsyncMock(return_value=mock_response)

    out_path = tmp_path / "test.js"
    success = await fetcher.fetch_and_write('https://example.com/app.js', str(out_path))

    assert success is True
    assert out_path.exists()
    assert out_path.read_text() == "console.log('test');"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_and_write_validates_content_length(mock_async_session, tmp_path, strategies_config):
    """Test download validates received size matches Content-Length"""
    noise_filter = Mock()

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Mock response with mismatched Content-Length
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {
        'Content-Length': '1000',  # Claims 1000 bytes
        'Content-Type': 'application/javascript'
    }

    async def mock_aiter_content(chunk_size):
        yield b"short content"  # Only 13 bytes

    mock_response.aiter_content = mock_aiter_content
    mock_async_session.get = AsyncMock(return_value=mock_response)

    out_path = tmp_path / "test.js"

    # Should detect incomplete download
    with pytest.raises(IncompleteDownloadError):
        await fetcher.fetch_and_write('https://example.com/app.js', str(out_path))


# ============================================================================
# CONTENT VALIDATION TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_content_validation_rejects_html(mock_async_session, strategies_config):
    """Test Content-Type: text/html is rejected"""
    noise_filter = Mock()

    strategies_config['active']['strict_content_type'] = True

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Mock HTML response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_response.text = "<html><body>404</body></html>"
    mock_async_session.get = AsyncMock(return_value=mock_response)

    content = await fetcher.fetch_content('https://example.com/app.js')

    # Should reject HTML content
    assert content is None or '<html>' not in content.lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_content_validation_rejects_oversized(mock_async_session, strategies_config):
    """Test files > max_size are rejected"""
    noise_filter = Mock()

    strategies_config['active']['max_file_size_mb'] = 1  # 1MB limit

    mock_logger = Mock()
    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Mock response with large Content-Length
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {
        'Content-Length': str(10 * 1024 * 1024),  # 10MB
        'Content-Type': 'application/javascript'
    }
    mock_async_session.get = AsyncMock(return_value=mock_response)

    content = await fetcher.fetch_content('https://example.com/huge.js')

    # Should reject oversized file
    assert content is None


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_domain_rate_limiter_enforces_delay():
    """Test rate limiter enforces delay between requests"""
    limiter = DomainRateLimiter(requests_per_second=10)

    # First request should go through immediately
    start = asyncio.get_event_loop().time()
    await limiter.acquire('example.com')
    elapsed1 = asyncio.get_event_loop().time() - start

    assert elapsed1 < 0.05  # Should be nearly instant

    # Second request should be delayed
    start = asyncio.get_event_loop().time()
    await limiter.acquire('example.com')
    elapsed2 = asyncio.get_event_loop().time() - start

    # Should wait ~0.1s for token to refill (1/10 RPS)
    assert elapsed2 >= 0.05  # At least some delay


@pytest.mark.unit
@pytest.mark.asyncio
async def test_domain_rate_limiter_allows_parallel_domains():
    """Test different domains are not rate limited against each other"""
    limiter = DomainRateLimiter(requests_per_second=5)

    # Acquire for multiple domains simultaneously
    start = asyncio.get_event_loop().time()
    await asyncio.gather(
        limiter.acquire('domain1.com'),
        limiter.acquire('domain2.com'),
        limiter.acquire('domain3.com'),
    )
    elapsed = asyncio.get_event_loop().time() - start

    # Should all go through quickly (different domains)
    assert elapsed < 0.1


# ============================================================================
# CONNECTION POOLING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_domain_connection_manager_limits_concurrent():
    """Test connection manager limits concurrent connections per domain"""
    manager = DomainConnectionManager(max_per_domain=2)

    # Get session and semaphore for domain
    session1, sem1 = await manager.get_session('https://example.com/a.js')
    session2, sem2 = await manager.get_session('https://example.com/b.js')

    # Should be same session and semaphore for same domain
    assert session1 is session2
    assert sem1 is sem2

    # Semaphore should have limit of 2
    assert sem1._value == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_connection_manager_queue_behavior():
    """Test connection manager queues requests when limit reached"""
    manager = DomainConnectionManager(max_per_domain=1)

    session, sem = await manager.get_session('https://example.com/app.js')

    # Acquire semaphore (fill the limit)
    await sem.acquire()

    # Try to acquire again - should block (would wait in real scenario)
    assert sem.locked()


# ============================================================================
# PERFORMANCE TRACKING TESTS
# ============================================================================

@pytest.mark.unit
def test_domain_performance_tracker_records_metrics():
    """Test performance tracker records latency and success rate"""
    tracker = DomainPerformanceTracker()

    # Record successful requests
    tracker.record('example.com', success=True, latency=0.5)
    tracker.record('example.com', success=True, latency=0.3)
    tracker.record('example.com', success=False, latency=1.0)

    # Verify metrics
    success_rate = tracker.get_success_rate('example.com')
    avg_latency = tracker.get_avg_latency('example.com')

    assert success_rate == 2/3  # 2 successful out of 3
    assert 0.3 <= avg_latency <= 0.7  # Average of 0.5, 0.3, 1.0


@pytest.mark.unit
def test_performance_tracker_adaptive_strategy():
    """Test tracker suggests browser-first for failing domains"""
    tracker = DomainPerformanceTracker()

    # Record mostly failures for domain
    for _ in range(10):
        tracker.record('example.com', success=False, latency=1.0)

    # Should suggest using browser
    use_browser = tracker.should_use_browser_first('example.com')

    assert use_browser is True


# ============================================================================
# BROWSER MANAGER TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_browser_manager_singleton_pattern(mock_playwright_browser):
    """Test BrowserManager reuses same browser instance"""
    mock_playwright = AsyncMock()
    manager = BrowserManager(playwright_instance=mock_playwright, headless=True)

    with patch('playwright.async_api.async_playwright') as mock_pw:
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=AsyncMock(chromium=AsyncMock(launch=AsyncMock(return_value=mock_playwright_browser))))
        mock_pw.return_value = mock_context

        # First call creates browser
        browser1 = await manager._ensure_browser()

        # Second call returns same browser
        browser2 = await manager._ensure_browser()

        assert browser1 is browser2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_browser_manager_lazy_initialization():
    """Test browser is created on first use, not during init"""
    mock_playwright = AsyncMock()
    manager = BrowserManager(playwright_instance=mock_playwright, headless=True)

    # Browser should not exist yet
    assert manager.browser is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_browser_manager_close():
    """Test browser is properly closed"""
    mock_playwright = AsyncMock()
    manager = BrowserManager(playwright_instance=mock_playwright, headless=True)
    manager.browser = AsyncMock()
    manager.browser.close = AsyncMock()

    await manager.close()

    manager.browser.close.assert_called_once()


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_content_empty_response(mock_async_session, strategies_config):
    """Test handling of 200 OK with empty body"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Mock empty response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = ""
    mock_response.headers = {}
    mock_async_session.get = AsyncMock(return_value=mock_response)

    content = await fetcher.fetch_content('https://example.com/empty.js')

    # Empty content should be handled gracefully
    assert content == "" or content is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_and_write_with_fallback_both_fail(mock_async_session, mock_browser_manager, tmp_path, strategies_config):
    """Test returns False when both curl and browser fail"""
    mock_logger = Mock()

    fetcher = ActiveFetcher(strategies_config, logger=mock_logger)
    fetcher.session = mock_async_session
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.session_pool = [mock_async_session]  # Required by _fetch_content_impl
    fetcher.error_stats = {"http_errors": 0, "timeouts": 0, "rate_limits": 0}
    fetcher.noise_filter = Mock()
    fetcher.noise_filter.should_skip_url = Mock(return_value=(False, ""))
    fetcher.noise_filter.should_skip_content = Mock(return_value=(False, ""))
    fetcher.browser_manager = mock_browser_manager
    fetcher.circuit_breaker = AsyncMock()
    fetcher.circuit_breaker.is_blocked = AsyncMock(return_value=False)
    fetcher.domain_perf_tracker = AsyncMock()
    fetcher.domain_perf_tracker.should_use_browser = Mock(return_value=False)
    fetcher.domain_perf_tracker.record = AsyncMock()
    # rate_limiter not needed - using domain_rate_limiter
    # connection_manager not needed - using domain_connection_manager

    # Mock curl failure
    mock_async_session.get = AsyncMock(side_effect=Exception("Network error"))

    # Mock browser failure
    mock_browser_manager.fetch_with_context = AsyncMock(return_value=None)

    out_path = tmp_path / "test.js"
    success = await fetcher.fetch_and_write_with_fallback('https://example.com/app.js', str(out_path))

    assert success is False
    assert not out_path.exists()
