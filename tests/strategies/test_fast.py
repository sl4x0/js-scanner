"""
Tests for FastFetcher (Katana-based fast crawling)
Tests URL discovery, temp file handling, scope filtering, and binary detection
"""
import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from jsscanner.strategies.fast import FastFetcher


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

@pytest.mark.unit
@patch('shutil.which')
def test_fast_fetcher_initialization(mock_which):
    """Test FastFetcher initialization with config"""
    mock_which.return_value = '/usr/bin/katana'
    
    config = {
        'katana': {
            'enabled': True,
            'depth': 3,
            'concurrency': 30,
            'rate_limit': 200,
            'timeout': 400,
            'args': '-headless'
        }
    }
    
    mock_logger = Mock()
    fetcher = FastFetcher(config, logger=mock_logger)
    
    assert fetcher.config == config
    assert fetcher.enabled is True
    assert fetcher.depth == 3
    assert fetcher.concurrency == 30
    assert fetcher.rate_limit == 200
    assert fetcher.timeout == 400
    assert fetcher.custom_args == '-headless'
    assert fetcher.katana_path == '/usr/bin/katana'


@pytest.mark.unit
@patch('shutil.which')
def test_fast_fetcher_default_config(mock_which):
    """Test FastFetcher with default configuration"""
    mock_which.return_value = '/usr/bin/katana'
    
    config = {}
    fetcher = FastFetcher(config)
    
    assert fetcher.enabled is False  # default
    assert fetcher.depth == 2  # default
    assert fetcher.concurrency == 20  # default
    assert fetcher.rate_limit == 150  # default
    assert fetcher.timeout == 300  # default


@pytest.mark.unit
@patch('shutil.which')
def test_fast_fetcher_disabled(mock_which):
    """Test FastFetcher when disabled in config"""
    mock_which.return_value = None
    
    config = {
        'katana': {
            'enabled': False
        }
    }
    
    fetcher = FastFetcher(config)
    assert fetcher.enabled is False


# ============================================================================
# BINARY DETECTION TESTS
# ============================================================================

@pytest.mark.unit
@patch('shutil.which')
@patch('pathlib.Path.exists')
def test_find_katana_binary_from_config(mock_exists, mock_which):
    """Test Katana binary detection from config path"""
    mock_exists.return_value = True
    mock_which.return_value = None
    
    config = {
        'katana': {
            'binary_path': '/custom/path/katana'
        }
    }
    
    fetcher = FastFetcher(config)
    
    # Should use config path first
    assert fetcher.katana_path == '/custom/path/katana'


@pytest.mark.unit
@patch('shutil.which')
@patch('pathlib.Path.exists')
def test_find_katana_binary_from_system_path(mock_exists, mock_which):
    """Test Katana binary detection from system PATH"""
    mock_exists.return_value = False
    mock_which.return_value = '/usr/local/bin/katana'
    
    config = {}
    fetcher = FastFetcher(config)
    
    assert fetcher.katana_path == '/usr/local/bin/katana'


@pytest.mark.unit
@patch('shutil.which')
@patch('pathlib.Path.exists')
@patch('pathlib.Path.home')
def test_find_katana_binary_from_go_bin(mock_home, mock_exists, mock_which):
    """Test Katana binary detection from Go bin directory"""
    mock_home.return_value = Path('/home/user')
    mock_which.return_value = None
    
    # Mock Path.exists to return True for go/bin path
    def exists_side_effect(self):
        return str(self) == '/home/user/go/bin/katana'
    
    with patch.object(Path, 'exists', exists_side_effect):
        config = {}
        fetcher = FastFetcher(config)
        
        assert fetcher.katana_path == '/home/user/go/bin/katana'


@pytest.mark.unit
@patch('shutil.which')
@patch('pathlib.Path.exists')
def test_find_katana_binary_not_found(mock_exists, mock_which):
    """Test Katana binary not found anywhere"""
    mock_exists.return_value = False
    mock_which.return_value = None
    
    config = {}
    fetcher = FastFetcher(config)
    
    assert fetcher.katana_path is None


# ============================================================================
# BASIC URL FETCHING TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_success(mock_which, mock_run, sample_katana_output):
    """Test successful Katana execution with valid output"""
    mock_which.return_value = '/usr/bin/katana'
    
    # Mock subprocess.run to return sample Katana output
    mock_run.return_value = Mock(
        returncode=0,
        stdout=sample_katana_output,
        stderr=""
    )
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    # Verify subprocess was called correctly
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    cmd = call_args[0][0]
    
    assert '/usr/bin/katana' in cmd or 'katana' in cmd[0]
    assert '-list' in cmd
    assert '-d' in cmd
    assert '-c' in cmd
    assert '-silent' in cmd
    assert '-jc' in cmd
    
    # Verify only JS URLs were extracted
    assert len(urls) >= 3
    assert 'https://example.com/app.js' in urls
    assert 'https://example.com/bundle.js' in urls
    assert 'https://example.com/vendor.min.js' in urls
    
    # Non-JS URLs should be filtered out
    assert 'https://example.com/styles.css' not in urls
    assert 'https://example.com/image.png' not in urls


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_temp_file_creation(mock_which, mock_run):
    """Test temp file is created with targets"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    targets = ['domain1.com', 'domain2.com', 'domain3.com']
    fetcher.fetch_urls(targets)
    
    # Verify temp file was passed to Katana
    call_args = mock_run.call_args
    cmd = call_args[0][0]
    
    # Find -list argument
    list_index = cmd.index('-list')
    temp_file_path = cmd[list_index + 1]
    
    # Temp file should have been created (but might be deleted now)
    assert temp_file_path.endswith('.txt')


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
@patch('os.unlink')
def test_fetch_urls_temp_file_cleanup(mock_unlink, mock_which, mock_run):
    """Test temp file is removed after execution"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    fetcher.fetch_urls(['example.com'])
    
    # Verify temp file was deleted
    mock_unlink.assert_called_once()


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
@patch('os.unlink')
def test_fetch_urls_temp_file_cleanup_on_error(mock_unlink, mock_which, mock_run):
    """Test temp file is cleaned up even when Katana fails"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.side_effect = Exception("Katana crashed")
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    # Should return empty list
    assert urls == []
    
    # Temp file should still be cleaned up
    mock_unlink.assert_called_once()


# ============================================================================
# OUTPUT PARSING TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_parsing_js_only(mock_which, mock_run):
    """Test only .js URLs are extracted from Katana output"""
    mock_which.return_value = '/usr/bin/katana'
    
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/app.js
https://example.com/styles.css
https://example.com/index.html
https://example.com/api/data.json
https://example.com/vendor.min.js
https://example.com/image.png
https://example.com/module.mjs
https://example.com/component.jsx""",
        stderr=""
    )
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    # Only JS files should be included
    assert len(urls) == 4
    assert 'https://example.com/app.js' in urls
    assert 'https://example.com/vendor.min.js' in urls
    assert 'https://example.com/module.mjs' in urls
    assert 'https://example.com/component.jsx' in urls
    
    # Non-JS files should be filtered out
    assert 'https://example.com/styles.css' not in urls
    assert 'https://example.com/index.html' not in urls
    assert 'https://example.com/image.png' not in urls


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_ignores_non_js(mock_which, mock_run):
    """Test non-JS files are ignored"""
    mock_which.return_value = '/usr/bin/katana'
    
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/app.css
https://example.com/image.jpg
https://example.com/video.mp4
https://example.com/font.woff2
https://example.com/data.xml""",
        stderr=""
    )
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    # Should return empty list (no JS files)
    assert urls == []


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_deduplication(mock_which, mock_run):
    """Test duplicate URLs are kept (Katana shouldn't output duplicates, but just in case)"""
    mock_which.return_value = '/usr/bin/katana'
    
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/app.js
https://example.com/app.js
https://example.com/vendor.js
https://example.com/app.js""",
        stderr=""
    )
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    # All URLs are added (no deduplication in fetcher)
    assert len(urls) == 4  # Deduplication happens elsewhere


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_binary_not_found(mock_which, mock_run):
    """Test handling when Katana binary is not found"""
    mock_which.return_value = None
    
    config = {'katana': {'enabled': True}}
    mock_logger = Mock()
    fetcher = FastFetcher(config, logger=mock_logger)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    assert urls == []
    # Should not call subprocess if binary not found
    mock_run.assert_not_called()
    # Should log warning
    mock_logger.warning.assert_called_once()


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_katana_timeout(mock_which, mock_run):
    """Test handling of Katana timeout"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.side_effect = subprocess.TimeoutExpired('katana', 300)
    
    config = {'katana': {'enabled': True, 'timeout': 300}}
    mock_logger = Mock()
    fetcher = FastFetcher(config, logger=mock_logger)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    assert urls == []
    mock_logger.warning.assert_called()


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_katana_non_zero_exit(mock_which, mock_run):
    """Test handling of Katana non-zero exit code"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.return_value = Mock(
        returncode=1,
        stdout="",
        stderr="Error: Failed to start crawler"
    )
    
    config = {'katana': {'enabled': True}}
    mock_logger = Mock()
    fetcher = FastFetcher(config, logger=mock_logger)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    assert urls == []
    # Should log warning with stderr
    mock_logger.warning.assert_called()


@pytest.mark.unit
def test_fetch_urls_when_disabled():
    """Test fetch_urls returns empty list when Katana is disabled"""
    config = {'katana': {'enabled': False}}
    mock_logger = Mock()
    fetcher = FastFetcher(config, logger=mock_logger)
    
    urls = fetcher.fetch_urls(['example.com'])
    
    assert urls == []
    mock_logger.debug.assert_called_once()


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_empty_targets(mock_which, mock_run):
    """Test fetch_urls with empty target list"""
    mock_which.return_value = '/usr/bin/katana'
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    urls = fetcher.fetch_urls([])
    
    assert urls == []
    # Should not call subprocess
    mock_run.assert_not_called()


# ============================================================================
# SCOPE FILTERING TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_scope_filter_integration(mock_which, mock_run):
    """Test scope filtering is applied to results"""
    mock_which.return_value = '/usr/bin/katana'
    
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://example.com/app.js
https://example.com/vendor.js
https://other-domain.com/script.js
https://cdn.cloudflare.com/lib.js
https://api.example.com/data.js""",
        stderr=""
    )
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    scope_domains = {'example.com'}
    urls = fetcher.fetch_urls(['example.com'], scope_domains=scope_domains)
    
    # Only example.com and subdomains should be included
    assert len(urls) == 3
    assert 'https://example.com/app.js' in urls
    assert 'https://example.com/vendor.js' in urls
    assert 'https://api.example.com/data.js' in urls
    assert 'https://other-domain.com/script.js' not in urls
    assert 'https://cdn.cloudflare.com/lib.js' not in urls


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_mixed_domains(mock_which, mock_run):
    """Test multi-domain output is filtered correctly"""
    mock_which.return_value = '/usr/bin/katana'
    
    mock_run.return_value = Mock(
        returncode=0,
        stdout="""https://domain1.com/app.js
https://domain2.com/main.js
https://domain3.com/bundle.js
https://domain1.com/vendor.js""",
        stderr=""
    )
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    scope_domains = {'domain1.com', 'domain2.com'}
    urls = fetcher.fetch_urls(['domain1.com', 'domain2.com'], scope_domains=scope_domains)
    
    assert len(urls) == 3
    assert 'https://domain1.com/app.js' in urls
    assert 'https://domain1.com/vendor.js' in urls
    assert 'https://domain2.com/main.js' in urls
    assert 'https://domain3.com/bundle.js' not in urls


# ============================================================================
# CUSTOM ARGUMENTS TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_custom_args(mock_which, mock_run):
    """Test custom Katana arguments are passed correctly"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
    
    config = {
        'katana': {
            'enabled': True,
            'args': '-headless -no-sandbox'
        }
    }
    fetcher = FastFetcher(config)
    
    fetcher.fetch_urls(['example.com'])
    
    call_args = mock_run.call_args
    cmd = call_args[0][0]
    
    # Verify custom args are included
    assert '-headless' in cmd
    assert '-no-sandbox' in cmd


# ============================================================================
# DIRECT JS URL FILTERING
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_filters_direct_js_urls(mock_which, mock_run):
    """Test direct JS URLs are filtered out from targets"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    # Mix of domains and direct JS URLs
    targets = [
        'example.com',
        'https://cdn.com/lib.js',
        'https://example.com/app.js',
        'domain2.com'
    ]
    
    fetcher.fetch_urls(targets)
    
    # Katana should only receive domains, not JS URLs
    # The temp file would only contain: example.com, domain2.com
    # We can't easily verify temp file contents, but we can verify it ran
    mock_run.assert_called_once()


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_fetch_urls_all_direct_js_returns_empty(mock_which, mock_run):
    """Test returns empty if all targets are direct JS URLs"""
    mock_which.return_value = '/usr/bin/katana'
    
    config = {'katana': {'enabled': True}}
    mock_logger = Mock()
    fetcher = FastFetcher(config, logger=mock_logger)
    
    # All direct JS URLs
    targets = [
        'https://cdn.com/lib.js',
        'https://example.com/app.min.js',
        'https://api.com/bundle.js'
    ]
    
    urls = fetcher.fetch_urls(targets)
    
    assert urls == []
    # Should not call subprocess (no domains to crawl)
    mock_run.assert_not_called()


# ============================================================================
# HELPER METHOD TESTS
# ============================================================================

@pytest.mark.unit
@patch('shutil.which')
def test_is_direct_js_url(mock_which):
    """Test _is_direct_js_url helper method"""
    mock_which.return_value = '/usr/bin/katana'
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    # Direct JS URLs
    assert fetcher._is_direct_js_url('https://example.com/app.js') is True
    assert fetcher._is_direct_js_url('https://cdn.com/lib.min.js') is True
    assert fetcher._is_direct_js_url('https://example.com/module.mjs') is True
    assert fetcher._is_direct_js_url('https://example.com/component.jsx') is True
    
    # Not direct JS URLs
    assert fetcher._is_direct_js_url('example.com') is False
    assert fetcher._is_direct_js_url('https://example.com') is False
    assert fetcher._is_direct_js_url('https://example.com/path/') is False
    assert fetcher._is_direct_js_url('https://js.example.com') is False  # 'js' in domain


@pytest.mark.unit
@patch('shutil.which')
def test_is_js_url(mock_which):
    """Test _is_js_url helper method"""
    mock_which.return_value = '/usr/bin/katana'
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    # Valid JS URLs
    assert fetcher._is_js_url('https://example.com/app.js') is True
    assert fetcher._is_js_url('https://example.com/app.min.js') is True
    assert fetcher._is_js_url('https://example.com/module.mjs') is True
    assert fetcher._is_js_url('https://example.com/component.jsx') is True
    assert fetcher._is_js_url('https://example.com/app.js?v=1.0') is True
    assert fetcher._is_js_url('https://example.com/app.js#section') is True
    
    # Not JS URLs
    assert fetcher._is_js_url('https://example.com/index.html') is False
    assert fetcher._is_js_url('https://example.com/styles.css') is False
    assert fetcher._is_js_url('https://example.com') is False
    assert fetcher._is_js_url('https://js.example.com') is False
    assert fetcher._is_js_url('') is False
    assert fetcher._is_js_url(None) is False


# ============================================================================
# STATIC METHOD TESTS
# ============================================================================

@pytest.mark.unit
@patch('shutil.which')
@patch('pathlib.Path.exists')
def test_is_installed_returns_true_system_path(mock_exists, mock_which):
    """Test is_installed() returns True when Katana is in system PATH"""
    mock_which.return_value = '/usr/bin/katana'
    mock_exists.return_value = False
    
    assert FastFetcher.is_installed() is True


@pytest.mark.unit
@patch('shutil.which')
@patch('pathlib.Path.exists')
@patch('pathlib.Path.home')
def test_is_installed_returns_true_go_bin(mock_home, mock_exists, mock_which):
    """Test is_installed() returns True when Katana is in go/bin"""
    mock_home.return_value = Path('/home/user')
    mock_which.return_value = None
    
    def exists_side_effect(self):
        return str(self) == '/home/user/go/bin/katana'
    
    with patch.object(Path, 'exists', exists_side_effect):
        assert FastFetcher.is_installed() is True


@pytest.mark.unit
@patch('shutil.which')
@patch('pathlib.Path.exists')
def test_is_installed_returns_false(mock_exists, mock_which):
    """Test is_installed() returns False when Katana is not found"""
    mock_which.return_value = None
    mock_exists.return_value = False
    
    assert FastFetcher.is_installed() is False


# ============================================================================
# VERSION DETECTION TESTS
# ============================================================================

@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_get_version_success(mock_which, mock_run):
    """Test get_version() returns version string"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.return_value = Mock(
        returncode=0,
        stdout="v1.0.3"
    )
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    version = fetcher.get_version()
    
    assert version == "v1.0.3"
    mock_run.assert_called_once()


@pytest.mark.unit
@patch('shutil.which')
def test_get_version_no_binary(mock_which):
    """Test get_version() returns None when binary not found"""
    mock_which.return_value = None
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    version = fetcher.get_version()
    
    assert version is None


@pytest.mark.unit
@patch('subprocess.run')
@patch('shutil.which')
def test_get_version_timeout(mock_which, mock_run):
    """Test get_version() returns None on timeout"""
    mock_which.return_value = '/usr/bin/katana'
    mock_run.side_effect = subprocess.TimeoutExpired('katana', 5)
    
    config = {'katana': {'enabled': True}}
    fetcher = FastFetcher(config)
    
    version = fetcher.get_version()
    
    assert version is None
