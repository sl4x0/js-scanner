"""
Tests for PassiveFetcher (SubJS-based URL discovery)
Tests URL discovery, scope filtering, retry logic, and batch processing
"""
import pytest
import subprocess
import asyncio
from unittest.mock import Mock, patch, call
from jsscanner.strategies.passive import PassiveFetcher


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

@pytest.mark.unit
def test_passive_fetcher_initialization():
    """Test PassiveFetcher initialization with config"""
    config = {
        'subjs': {
            'enabled': True,
            'timeout': 60
        },
        'retry': {
            'subprocess_calls': 3,
            'backoff_base': 2.0
        }
    }
    
    mock_logger = Mock()
    fetcher = PassiveFetcher(config, logger=mock_logger)
    
    assert fetcher.config == config
    assert fetcher.timeout == 60
    assert fetcher.enabled is True
    assert fetcher.logger == mock_logger


@pytest.mark.unit
def test_passive_fetcher_default_config():
    """Test PassiveFetcher with default configuration"""
    config = {}
    fetcher = PassiveFetcher(config)
    
    assert fetcher.timeout == 60  # default
    assert fetcher.enabled is True  # default


@pytest.mark.unit
def test_passive_fetcher_disabled():
    """Test PassiveFetcher when disabled in config"""
    config = {
        'subjs': {
            'enabled': False
        }
    }
    
    fetcher = PassiveFetcher(config)
    assert fetcher.enabled is False


# ============================================================================
# BASIC URL FETCHING TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_success(mock_run, sample_subjs_output):
    """Test successful SubJS execution with valid output"""
    # Mock subprocess.run to return sample SubJS output
    mock_run.return_value = Mock(
        returncode=0,
        stdout=sample_subjs_output,
        stderr=""
    )
    
    config = {'subjs': {'enabled': True, 'timeout': 60}}
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # Verify subprocess was called correctly
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    assert call_args[0][0] == ['subjs']
    assert 'https://example.com' in call_args[1]['input']
    
    # Verify URLs were parsed correctly
    assert len(urls) >= 5
    assert 'https://example.com/app.js' in urls
    assert 'https://example.com/vendor.js' in urls
    assert 'https://example.com/bundle.min.js' in urls


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_parsing_filters_invalid(mock_run):
    """Test URL parsing filters out invalid lines"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/valid.js
invalid-url
not-a-url
ftp://example.com/file.js
https://example.com/another.js
garbage text
""",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # Only valid HTTP(S) URLs should be included
    assert len(urls) == 2
    assert 'https://example.com/valid.js' in urls
    assert 'https://example.com/another.js' in urls
    assert 'invalid-url' not in urls
    assert 'ftp://example.com/file.js' not in urls


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_empty_result(mock_run):
    """Test handling of empty SubJS output"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    assert urls == []


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_adds_https_prefix(mock_run):
    """Test that HTTPS prefix is added to domains without protocol"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="https://example.com/app.js\n",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    # Call with domain without protocol
    urls = fetcher.fetch_urls('example.com')
    
    # Verify https:// was added in input
    call_args = mock_run.call_args
    assert 'https://example.com' in call_args[1]['input']


# ============================================================================
# ERROR HANDLING & RETRY TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_timeout_retry(mock_run):
    """Test retry logic on TimeoutExpired"""
    # Simulate timeout on first call, success on second
    mock_run.side_effect = [
        subprocess.TimeoutExpired('subjs', 60),
        Mock(returncode=0, stdout="https://example.com/app.js\n", stderr="")
    ]
    
    config = {
        'subjs': {'enabled': True, 'timeout': 60},
        'retry': {'subprocess_calls': 2, 'backoff_base': 0.1}  # Fast backoff for testing
    }
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # Verify it retried and succeeded
    assert len(mock_run.call_args_list) == 2
    assert len(urls) == 1
    assert urls[0] == 'https://example.com/app.js'


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_subprocess_error_retry(mock_run):
    """Test retry logic on subprocess error"""
    # Simulate error on first call, success on second
    mock_run.side_effect = [
        Mock(returncode=1, stdout="", stderr="Connection failed"),
        Mock(returncode=0, stdout="https://example.com/app.js\n", stderr="")
    ]
    
    config = {
        'subjs': {'enabled': True},
        'retry': {'subprocess_calls': 2, 'backoff_base': 0.1}
    }
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # Verify it retried and succeeded
    assert len(mock_run.call_args_list) == 2
    assert len(urls) == 1


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_max_retries_exceeded(mock_run):
    """Test behavior when all retries are exhausted"""
    # Simulate failure on all attempts
    mock_run.side_effect = [
        subprocess.TimeoutExpired('subjs', 60),
        subprocess.TimeoutExpired('subjs', 60),
        subprocess.TimeoutExpired('subjs', 60),
    ]
    
    config = {
        'subjs': {'enabled': True, 'timeout': 60},
        'retry': {'subprocess_calls': 3, 'backoff_base': 0.1}
    }
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # Verify it tried 3 times and returned empty list
    assert len(mock_run.call_args_list) == 3
    assert urls == []


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_binary_not_found(mock_run):
    """Test handling of missing SubJS binary"""
    mock_run.side_effect = FileNotFoundError("subjs not found")
    
    config = {'subjs': {'enabled': True}}
    mock_logger = Mock()
    fetcher = PassiveFetcher(config, logger=mock_logger)
    
    urls = fetcher.fetch_urls('example.com')
    
    assert urls == []
    # Verify error was logged
    mock_logger.error.assert_called_once()
    assert "not installed" in str(mock_logger.error.call_args)


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_generic_exception(mock_run):
    """Test handling of unexpected exceptions"""
    mock_run.side_effect = RuntimeError("Unexpected error")
    
    config = {'subjs': {'enabled': True}}
    mock_logger = Mock()
    fetcher = PassiveFetcher(config, logger=mock_logger)
    
    urls = fetcher.fetch_urls('example.com')
    
    assert urls == []
    mock_logger.error.assert_called_once()


@pytest.mark.unit
def test_fetch_urls_when_disabled():
    """Test fetch_urls returns empty list when SubJS is disabled"""
    config = {'subjs': {'enabled': False}}
    mock_logger = Mock()
    fetcher = PassiveFetcher(config, logger=mock_logger)
    
    urls = fetcher.fetch_urls('example.com')
    
    assert urls == []
    mock_logger.debug.assert_called_once()


# ============================================================================
# SCOPE FILTERING TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
def test_scope_filter_removes_out_of_scope(mock_run):
    """Test scope filtering removes URLs not matching target domain"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/app.js
https://example.com/vendor.js
https://other-domain.com/script.js
https://cdn.cloudflare.com/lib.js
https://api.example.com/data.js
https://completely-different.com/file.js""",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com'}
    urls = fetcher.fetch_urls('example.com', scope_domains=scope_domains)
    
    # Only example.com and api.example.com should be included
    assert len(urls) == 3
    assert 'https://example.com/app.js' in urls
    assert 'https://example.com/vendor.js' in urls
    assert 'https://api.example.com/data.js' in urls  # subdomain should be included
    assert 'https://other-domain.com/script.js' not in urls
    assert 'https://cdn.cloudflare.com/lib.js' not in urls


@pytest.mark.unit
@patch('subprocess.run')
def test_scope_filter_preserves_in_scope(mock_run):
    """Test scope filtering preserves URLs from target domain"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/app.js
https://example.com/vendor.js""",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com'}
    urls = fetcher.fetch_urls('example.com', scope_domains=scope_domains)
    
    assert len(urls) == 2
    assert all('example.com' in url for url in urls)


@pytest.mark.unit
@patch('subprocess.run')
def test_scope_filter_subdomain_handling(mock_run):
    """Test subdomain inclusion in scope filtering"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/app.js
https://api.example.com/api.js
https://cdn.example.com/cdn.js
https://sub.api.example.com/deep.js
https://other.com/other.js""",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com'}
    urls = fetcher.fetch_urls('example.com', scope_domains=scope_domains)
    
    # All example.com subdomains should be included
    assert len(urls) == 4
    assert 'https://example.com/app.js' in urls
    assert 'https://api.example.com/api.js' in urls
    assert 'https://cdn.example.com/cdn.js' in urls
    assert 'https://sub.api.example.com/deep.js' in urls
    assert 'https://other.com/other.js' not in urls


@pytest.mark.unit
@patch('subprocess.run')
def test_scope_filter_with_port(mock_run):
    """Test scope filtering handles ports correctly"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com:8080/app.js
https://example.com/normal.js
https://other.com:8080/other.js""",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com'}
    urls = fetcher.fetch_urls('example.com', scope_domains=scope_domains)
    
    # Both URLs with and without port for example.com should be included
    assert len(urls) == 2
    assert 'https://example.com:8080/app.js' in urls
    assert 'https://example.com/normal.js' in urls
    assert 'https://other.com:8080/other.js' not in urls


@pytest.mark.unit
@patch('subprocess.run')
def test_scope_filter_case_insensitive(mock_run):
    """Test scope filtering is case-insensitive"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://Example.COM/app.js
https://EXAMPLE.com/vendor.js
https://example.COM/bundle.js""",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com'}
    urls = fetcher.fetch_urls('example.com', scope_domains=scope_domains)
    
    # All case variations should be included
    assert len(urls) == 3


# ============================================================================
# BATCH PROCESSING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
@patch('subprocess.run')
async def test_fetch_batch_concurrency(mock_run):
    """Test batch processing handles multiple domains concurrently"""
    # Mock different responses for different domains
    mock_run.side_effect = [
        Mock(returncode=0, stdout="https://domain1.com/app.js\n", stderr=""),
        Mock(returncode=0, stdout="https://domain2.com/main.js\n", stderr=""),
        Mock(returncode=0, stdout="https://domain3.com/bundle.js\n", stderr=""),
    ]
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    domains = ['domain1.com', 'domain2.com', 'domain3.com']
    urls = await fetcher.fetch_batch(domains)
    
    # Verify all domains were processed
    assert len(mock_run.call_args_list) == 3
    assert len(urls) == 3
    assert 'https://domain1.com/app.js' in urls
    assert 'https://domain2.com/main.js' in urls
    assert 'https://domain3.com/bundle.js' in urls


@pytest.mark.unit
@pytest.mark.asyncio
@patch('subprocess.run')
async def test_fetch_batch_aggregation(mock_run):
    """Test batch processing aggregates results from multiple domains"""
    # Each domain returns multiple URLs
    mock_run.side_effect = [
        Mock(returncode=0, stdout="https://domain1.com/a.js\nhttps://domain1.com/b.js\n", stderr=""),
        Mock(returncode=0, stdout="https://domain2.com/c.js\nhttps://domain2.com/d.js\n", stderr=""),
    ]
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    domains = ['domain1.com', 'domain2.com']
    urls = await fetcher.fetch_batch(domains)
    
    # Verify all URLs were aggregated
    assert len(urls) == 4
    assert 'https://domain1.com/a.js' in urls
    assert 'https://domain1.com/b.js' in urls
    assert 'https://domain2.com/c.js' in urls
    assert 'https://domain2.com/d.js' in urls


@pytest.mark.unit
@pytest.mark.asyncio
@patch('subprocess.run')
async def test_fetch_batch_partial_failure(mock_run):
    """Test batch processing continues when some domains fail"""
    # First domain fails, second succeeds
    mock_run.side_effect = [
        subprocess.TimeoutExpired('subjs', 60),
        Mock(returncode=0, stdout="https://domain2.com/app.js\n", stderr=""),
    ]
    
    config = {
        'subjs': {'enabled': True},
        'retry': {'subprocess_calls': 1, 'backoff_base': 0.1}  # No retries for faster test
    }
    fetcher = PassiveFetcher(config)
    
    domains = ['domain1.com', 'domain2.com']
    urls = await fetcher.fetch_batch(domains)
    
    # Only successful domain should contribute URLs
    assert len(urls) == 1
    assert 'https://domain2.com/app.js' in urls


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_batch_empty_domains():
    """Test batch processing with empty domain list"""
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    urls = await fetcher.fetch_batch([])
    
    assert urls == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_batch_when_disabled():
    """Test batch processing returns empty when SubJS is disabled"""
    config = {'subjs': {'enabled': False}}
    fetcher = PassiveFetcher(config)
    
    urls = await fetcher.fetch_batch(['domain1.com', 'domain2.com'])
    
    assert urls == []


@pytest.mark.unit
@pytest.mark.asyncio
@patch('subprocess.run')
async def test_fetch_batch_with_scope_filter(mock_run):
    """Test batch processing applies scope filtering"""
    mock_run.side_effect = [
        Mock(returncode=0, stdout="https://domain1.com/app.js\nhttps://other.com/bad.js\n", stderr=""),
        Mock(returncode=0, stdout="https://domain2.com/main.js\nhttps://domain1.com/shared.js\n", stderr=""),
    ]
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'domain1.com', 'domain2.com'}
    domains = ['domain1.com', 'domain2.com']
    urls = await fetcher.fetch_batch(domains, scope_domains=scope_domains)
    
    # Only in-scope URLs should be included
    assert len(urls) == 3
    assert 'https://domain1.com/app.js' in urls
    assert 'https://domain1.com/shared.js' in urls
    assert 'https://domain2.com/main.js' in urls
    assert 'https://other.com/bad.js' not in urls


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_unicode_urls(mock_run):
    """Test handling of URLs with Unicode characters"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="https://例え.com/app.js\nhttps://example.com/файл.js\n",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # Unicode URLs should be preserved
    assert len(urls) == 2
    assert 'https://例え.com/app.js' in urls
    assert 'https://example.com/файл.js' in urls


@pytest.mark.unit
@patch('subprocess.run')
def test_fetch_urls_malformed_urls(mock_run):
    """Test filtering of malformed URLs"""
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/valid.js
http:/malformed
https://
://no-protocol.js
https://example.com/another.js""",
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # Only valid URLs should be included
    assert len(urls) == 2
    assert 'https://example.com/valid.js' in urls
    assert 'https://example.com/another.js' in urls


@pytest.mark.unit
@pytest.mark.slow
@patch('subprocess.run')
def test_fetch_urls_large_output(mock_run):
    """Test handling of large SubJS output (10k+ URLs)"""
    # Generate 10000 URLs
    urls_output = '\n'.join([f'https://example.com/file{i}.js' for i in range(10000)])
    
    mock_run.return_value = Mock(
        returncode=0,
        stdout=urls_output,
        stderr=""
    )
    
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    urls = fetcher.fetch_urls('example.com')
    
    # All URLs should be parsed
    assert len(urls) == 10000
    assert 'https://example.com/file0.js' in urls
    assert 'https://example.com/file9999.js' in urls


# ============================================================================
# STATIC METHOD TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
def test_is_installed_returns_true(mock_run):
    """Test is_installed() returns True when SubJS is available"""
    mock_run.return_value = Mock(returncode=0)
    
    assert PassiveFetcher.is_installed() is True
    
    # Verify it checked for SubJS help
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0] == ['subjs', '-h']


@pytest.mark.unit
@patch('subprocess.run')
def test_is_installed_returns_false_on_not_found(mock_run):
    """Test is_installed() returns False when SubJS is not found"""
    mock_run.side_effect = FileNotFoundError()
    
    assert PassiveFetcher.is_installed() is False


@pytest.mark.unit
@patch('subprocess.run')
def test_is_installed_returns_false_on_timeout(mock_run):
    """Test is_installed() returns False on timeout"""
    mock_run.side_effect = subprocess.TimeoutExpired('subjs', 5)
    
    assert PassiveFetcher.is_installed() is False


# ============================================================================
# HELPER METHOD TESTS
# ============================================================================

@pytest.mark.unit
def test_is_valid_url():
    """Test _is_valid_url helper method"""
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    assert fetcher._is_valid_url('https://example.com/app.js') is True
    assert fetcher._is_valid_url('http://example.com/app.js') is True
    assert fetcher._is_valid_url('ftp://example.com/file.js') is False
    assert fetcher._is_valid_url('example.com/app.js') is False
    assert fetcher._is_valid_url('') is False
    assert fetcher._is_valid_url(None) is False


@pytest.mark.unit
def test_is_in_scope_exact_match():
    """Test _is_in_scope with exact domain match"""
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com', 'api.example.com'}
    
    assert fetcher._is_in_scope('example.com', scope_domains) is True
    assert fetcher._is_in_scope('api.example.com', scope_domains) is True
    assert fetcher._is_in_scope('other.com', scope_domains) is False


@pytest.mark.unit
def test_is_in_scope_subdomain_match():
    """Test _is_in_scope with subdomain matching"""
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com'}
    
    # Subdomains should match parent domain
    assert fetcher._is_in_scope('api.example.com', scope_domains) is True
    assert fetcher._is_in_scope('cdn.example.com', scope_domains) is True
    assert fetcher._is_in_scope('sub.api.example.com', scope_domains) is True
    
    # Non-subdomains should not match
    assert fetcher._is_in_scope('examplenotcom.com', scope_domains) is False
    assert fetcher._is_in_scope('notexample.com', scope_domains) is False


@pytest.mark.unit
def test_is_in_scope_case_insensitive():
    """Test _is_in_scope is case-insensitive"""
    config = {'subjs': {'enabled': True}}
    fetcher = PassiveFetcher(config)
    
    scope_domains = {'example.com'}
    
    assert fetcher._is_in_scope('Example.COM', scope_domains) is True
    assert fetcher._is_in_scope('EXAMPLE.COM', scope_domains) is True
    assert fetcher._is_in_scope('API.Example.Com', scope_domains) is True
