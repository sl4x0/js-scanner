"""
Integration tests for strategies module
Tests complete workflows and interactions between components
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from jsscanner.strategies.passive import PassiveFetcher
from jsscanner.strategies.fast import FastFetcher
from jsscanner.strategies.active import ActiveFetcher


# ============================================================================
# COMPLETE WORKFLOW TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
@patch('subprocess.run')
@patch('shutil.which')
async def test_integration_complete_fetch_workflow(mock_which, mock_run):
    """Test PassiveFetcher → FastFetcher → ActiveFetcher pipeline"""
    # Setup PassiveFetcher
    mock_run.side_effect = [
        # SubJS output
        Mock(returncode=0, stdout="https://example.com/app.js\nhttps://example.com/vendor.js\n", stderr=""),
        # Katana output  
        Mock(returncode=0, stdout="https://example.com/bundle.js\nhttps://example.com/main.js\n", stderr="")
    ]
    mock_which.return_value = '/usr/bin/tool'
    
    # Passive discovery
    passive_config = {'subjs': {'enabled': True}}
    passive_fetcher = PassiveFetcher(passive_config)
    passive_urls = passive_fetcher.fetch_urls('example.com')
    
    assert len(passive_urls) == 2
    assert 'https://example.com/app.js' in passive_urls
    
    # Fast discovery
    fast_config = {'katana': {'enabled': True}}
    fast_fetcher = FastFetcher(fast_config)
    fast_urls = fast_fetcher.fetch_urls(['example.com'])
    
    assert len(fast_urls) == 2
    assert 'https://example.com/bundle.js' in fast_urls
    
    # Combine results
    all_urls = list(set(passive_urls + fast_urls))
    assert len(all_urls) == 4


@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_error_recovery():
    """Test partial failures don't stop pipeline"""
    # PassiveFetcher fails
    passive_config = {'subjs': {'enabled': False}}
    passive_fetcher = PassiveFetcher(passive_config)
    passive_urls = passive_fetcher.fetch_urls('example.com')
    
    assert passive_urls == []  # Failed gracefully
    
    # FastFetcher succeeds (mocked)
    with patch('subprocess.run') as mock_run, patch('shutil.which') as mock_which:
        mock_which.return_value = '/usr/bin/katana'
        mock_run.return_value = Mock(returncode=0, stdout="https://example.com/app.js\n", stderr="")
        
        fast_config = {'katana': {'enabled': True}}
        fast_fetcher = FastFetcher(fast_config)
        fast_urls = fast_fetcher.fetch_urls(['example.com'])
        
        assert len(fast_urls) == 1  # Continues despite passive failure


@pytest.mark.integration
@pytest.mark.asyncio
@patch('subprocess.run')
async def test_integration_concurrent_domains(mock_run):
    """Test multiple domains are fetched in parallel"""
    # Mock responses for batch processing
    mock_run.side_effect = [
        Mock(returncode=0, stdout="https://domain1.com/app.js\n", stderr=""),
        Mock(returncode=0, stdout="https://domain2.com/main.js\n", stderr=""),
        Mock(returncode=0, stdout="https://domain3.com/bundle.js\n", stderr=""),
    ]
    
    passive_config = {'subjs': {'enabled': True}}
    passive_fetcher = PassiveFetcher(passive_config)
    
    domains = ['domain1.com', 'domain2.com', 'domain3.com']
    
    # Time the batch processing
    import time
    start = time.time()
    urls = await passive_fetcher.fetch_batch(domains)
    elapsed = time.time() - start
    
    # Should process all domains
    assert len(urls) == 3
    
    # Should be relatively fast (parallel processing)
    assert elapsed < 2.0  # Generous timeout for CI


# ============================================================================
# WAF FALLBACK SCENARIO (Simplified Mock)
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_waf_fallback():
    """Test WAF-like behavior: curl gets 429, browser succeeds"""
    noise_filter = Mock()
    noise_filter.should_skip_url = Mock(return_value=False)
    
    config = {
        'active': {
            'enabled': True,
            'timeout': 15,
            'browser_fallback': True,
            'max_retries': 1
        },
        'playwright': {'headless': True},
        'curl_cffi': {'impersonate': 'chrome110', 'verify': False}
    }
    
    mock_logger = Mock()
    fetcher = ActiveFetcher(config, logger=mock_logger)
    fetcher.noise_filter = noise_filter
    
    # Mock session that returns 429
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 429
    mock_session.get = AsyncMock(return_value=mock_response)
    fetcher.session = mock_session
    
    # Mock browser that succeeds
    mock_browser = AsyncMock()
    mock_browser.fetch_with_context = AsyncMock(return_value="console.log('success');")
    fetcher.browser_manager = mock_browser
    
    # Mock domain managers
    fetcher.circuit_breakers = {}
    fetcher.rate_limiters = {}
    fetcher.connection_managers = {}
    
    # Fetch should fall back to browser
    content = await fetcher.fetch_content('https://example.com/app.js')
    
    assert content == "console.log('success');"
    mock_browser.fetch_with_context.assert_called_once()


# ============================================================================
# SCOPE FILTERING INTEGRATION
# ============================================================================

@pytest.mark.integration
@patch('subprocess.run')
def test_integration_scope_filtering_passive(mock_run):
    """Test scope filtering works end-to-end with PassiveFetcher"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://target.com/app.js
https://target.com/vendor.js
https://cdn.cloudflare.com/lib.js
https://other-domain.com/script.js
https://api.target.com/data.js""",
        stderr=""
    )
    
    passive_config = {'subjs': {'enabled': True}}
    passive_fetcher = PassiveFetcher(passive_config)
    
    scope_domains = {'target.com'}
    urls = passive_fetcher.fetch_urls('target.com', scope_domains=scope_domains)
    
    # Only target.com and subdomains should be included
    assert len(urls) == 3
    assert all('target.com' in url for url in urls)


@pytest.mark.integration
@patch('subprocess.run')
@patch('shutil.which')
def test_integration_scope_filtering_fast(mock_which, mock_run):
    """Test scope filtering works end-to-end with FastFetcher"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://target.com/app.js
https://cdn.jsdelivr.net/lib.js
https://target.com/bundle.js
https://other.com/script.js""",
        stderr=""
    )
    
    fast_config = {'katana': {'enabled': True}}
    fast_fetcher = FastFetcher(fast_config)
    
    scope_domains = {'target.com'}
    urls = fast_fetcher.fetch_urls(['target.com'], scope_domains=scope_domains)
    
    assert len(urls) == 2
    assert all('target.com' in url for url in urls)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
@patch('subprocess.run')
async def test_integration_performance_batch_processing(mock_run):
    """Test batch processing of 50 domains completes in reasonable time"""
    # Mock fast responses for all domains
    def mock_subprocess(*args, **kwargs):
        return Mock(returncode=0, stdout="https://example.com/app.js\n", stderr="")
    
    mock_run.side_effect = mock_subprocess
    
    passive_config = {'subjs': {'enabled': True}, 'retry': {'subprocess_calls': 1}}
    passive_fetcher = PassiveFetcher(passive_config)
    
    # Generate 50 domains
    domains = [f'domain{i}.com' for i in range(50)]
    
    import time
    start = time.time()
    urls = await passive_fetcher.fetch_batch(domains)
    elapsed = time.time() - start
    
    # Should complete all 50 domains
    assert len(urls) == 50
    
    # Should be reasonably fast with parallel processing
    assert elapsed < 30.0  # 30 seconds max for 50 domains


# ============================================================================
# EDGE CASE INTEGRATION
# ============================================================================

@pytest.mark.integration
@patch('subprocess.run')
def test_integration_all_strategies_fail_gracefully(mock_run):
    """Test graceful handling when all strategies return empty"""
    # SubJS returns nothing
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
    
    passive_config = {'subjs': {'enabled': True}}
    passive_fetcher = PassiveFetcher(passive_config)
    passive_urls = passive_fetcher.fetch_urls('example.com')
    
    assert passive_urls == []
    
    # FastFetcher also returns nothing
    with patch('shutil.which') as mock_which:
        mock_which.return_value = '/usr/bin/katana'
        fast_config = {'katana': {'enabled': True}}
        fast_fetcher = FastFetcher(fast_config)
        fast_urls = fast_fetcher.fetch_urls(['example.com'])
        
        assert fast_urls == []
    
    # Pipeline should handle empty results gracefully
    all_urls = passive_urls + fast_urls
    assert all_urls == []


@pytest.mark.integration
@patch('subprocess.run')
@patch('shutil.which')
def test_integration_mixed_success_failure(mock_which, mock_run):
    """Test some URLs succeed, some fail"""
    mock_which.return_value = '/usr/bin/katana'
    
    # Mix of successful and failed responses
    mock_run.side_effect = [
        Mock(returncode=0, stdout="https://domain1.com/app.js\n", stderr=""),
        Mock(returncode=1, stdout="", stderr="Error: timeout"),
        Mock(returncode=0, stdout="https://domain3.com/bundle.js\n", stderr=""),
    ]
    
    fast_config = {'katana': {'enabled': True}}
    fast_fetcher = FastFetcher(fast_config)
    
    # Process multiple targets
    urls1 = fast_fetcher.fetch_urls(['domain1.com'])
    urls2 = fast_fetcher.fetch_urls(['domain2.com'])  # This one fails
    urls3 = fast_fetcher.fetch_urls(['domain3.com'])
    
    # Should handle mixed results
    assert len(urls1) == 1
    assert len(urls2) == 0  # Failed
    assert len(urls3) == 1
