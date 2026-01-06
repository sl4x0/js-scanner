"""
Pytest configuration and shared fixtures for JS Scanner tests
"""
import pytest
import json
import asyncio
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from typing import Dict, Any, List


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_binary: mark test as requiring external binary (semgrep, trufflehog, etc.)")


# ============================================================================
# EVENT LOOP FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def event_loop_policy():
    """Use WindowsSelectorEventLoopPolicy on Windows for curl_cffi compatibility"""
    import sys
    if sys.platform == 'win32':
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="function")
def event_loop(event_loop_policy):
    """Create an event loop for each test"""
    asyncio.set_event_loop_policy(event_loop_policy)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# ============================================================================
# LOGGER FIXTURES
# ============================================================================

@pytest.fixture
def mock_logger():
    """Mock logger with all standard methods"""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def default_config():
    """Default configuration for tests"""
    return {
        'noise_filter': {
            'min_file_size_kb': 50,
            'max_newlines': 20
        },
        'beautification': {
            'timeout_small': 120,
            'timeout_medium': 300,
            'timeout_large': 900,
            'timeout_xlarge': 1800
        },
        'bundle_unpacker': {
            'enabled': True,
            'min_file_size': 102400  # 100KB
        },
        'semgrep': {
            'enabled': True,
            'timeout': 300,
            'version_timeout': 30,
            'version_check_retries': 3,
            'max_target_bytes': 2000000,
            'jobs': 4,
            'ruleset': 'p/javascript',
            'chunk_size': 100,
            'max_files': 100
        },
        'trufflehog_max_concurrent': 5,
        'trufflehog_timeout': 300,
        'ast': {
            'max_file_size_mb': 15
        }
    }


@pytest.fixture
def minimal_config():
    """Minimal configuration for tests that don't need full config"""
    return {}


# ============================================================================
# FILESYSTEM FIXTURES
# ============================================================================

@pytest.fixture
def tmp_result_paths(tmp_path):
    """Create temporary result directory structure"""
    base = tmp_path / "results" / "test_target"
    
    paths = {
        'base': str(base),
        'unique_js': str(base / 'unique_js'),
        'findings': str(base / 'findings'),
        'extracts': str(base / 'extracts'),
        'unpacked': str(base / 'unpacked'),
        'sourcemaps': str(base / 'sourcemaps')
    }
    
    # Create directories
    for path in paths.values():
        Path(path).mkdir(parents=True, exist_ok=True)
    
    return paths


@pytest.fixture
def ignored_patterns_config(tmp_path):
    """Create a temporary ignored_patterns.json file"""
    config_file = tmp_path / "ignored_patterns.json"
    
    config_data = {
        'cdn_domains': [
            'cdnjs.cloudflare.com',
            'cdn.jsdelivr.net',
            'unpkg.com',
            'googleapis.com',
            'google-analytics.com',
            'googletagmanager.com'
        ],
        'url_patterns': [
            '*/jquery*.js',
            '*/bootstrap*.js',
            '*/react*.js',
            '*/vue*.js',
            '*/angular*.js',
            '*vendor*.js',
            '*chunk-vendors*.js'
        ],
        'known_library_hashes': {
            'jquery-3.6.0': 'fc35490a00c8db6ce6e41baacaec5a63',
            'bootstrap-5.1.3': 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
        }
    }
    
    config_file.write_text(json.dumps(config_data, indent=2))
    return str(config_file)


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_js_minified():
    """Sample minified JavaScript"""
    return """!function(e,t){"object"==typeof exports&&"object"==typeof module?module.exports=t():"function"==typeof define&&define.amd?define([],t):"object"==typeof exports?exports.MyLib=t():e.MyLib=t()}(window,(function(){return function(e){var t={};function n(r){if(t[r])return t[r].exports;var o=t[r]={i:r,l:!1,exports:{}};return e[r].call(o.exports,o,o.exports,n),o.l=!0,o.exports}return n.m=e,n.c=t,n.d=function(e,t,r){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:r})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var r=Object.create(null);if(n.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var o in e)n.d(r,o,function(t){return e[t]}.bind(null,o));return r},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="",n(n.s=0)}([function(e,t){console.log("Hello World")}])}));"""


@pytest.fixture
def sample_js_beautified():
    """Sample beautified JavaScript"""
    return """function myFunction() {
    var message = "Hello World";
    console.log(message);
}

myFunction();"""


@pytest.fixture
def sample_js_with_hex():
    """Sample JavaScript with hex-encoded strings"""
    return '''var secret = "\\x41\\x50\\x49\\x5F\\x4B\\x45\\x59\\x3D\\x73\\x65\\x63\\x72\\x65\\x74";
var endpoint = "\\x68\\x74\\x74\\x70\\x73\\x3A\\x2F\\x2F\\x61\\x70\\x69\\x2E\\x65\\x78\\x61\\x6D\\x70\\x6C\\x65\\x2E\\x63\\x6F\\x6D";
console.log(secret, endpoint);'''


@pytest.fixture
def sample_js_with_sourcemap():
    """Sample JavaScript with inline sourcemap"""
    return """function test(){console.log("test")}
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbImFwcC5qcyJdLCJuYW1lcyI6WyJ0ZXN0IiwiY29uc29sZSIsImxvZyJdLCJtYXBwaW5ncyI6IkFBQUEsU0FBU0EsS0FDUEMsUUFBUUMsSUFBSSxPQUNkIiwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gdGVzdCgpIHtcbiAgY29uc29sZS5sb2coXCJ0ZXN0XCIpO1xufVxuIl19"""


@pytest.fixture
def sample_js_vendor_jquery():
    """Sample vendor JavaScript (jQuery signature)"""
    return """/*! jQuery v3.6.0 | (c) OpenJS Foundation and other contributors | jquery.org/license */
!function(e,t){"use strict";"object"==typeof module&&"object"==typeof module.exports?module.exports=e.document?t(e,!0):function(e){if(!e.document)throw new Error("jQuery requires a window with a document");return t(e)}:t(e)}("undefined"!=typeof window?window:this,function(e,t){"use strict";var n=[],r=e.document,i=Object.getPrototypeOf,o=n.slice,a=n.concat,s=n.push,u=n.indexOf,l={},c=l.toString,f=l.hasOwnProperty,p=f.toString,d=p.call(Object),h={},g=function e(t){return"function"==typeof t&&"number"!=typeof t.nodeType},y=function e(t){return null!=t&&t===t.window},v={type:!0,src:!0,nonce:!0,noModule:!0};""" + "x" * 10000  # Make it large


@pytest.fixture
def sample_webpack_bundle():
    """Sample Webpack bundle"""
    return """(function(modules) {
    var installedModules = {};
    function __webpack_require__(moduleId) {
        if(installedModules[moduleId]) {
            return installedModules[moduleId].exports;
        }
        var module = installedModules[moduleId] = {
            i: moduleId,
            l: false,
            exports: {}
        };
        modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
        module.l = true;
        return module.exports;
    }
    return __webpack_require__(__webpack_require__.s = 0);
})([
    function(module, exports) {
        console.log("webpack bundle");
    }
]);"""


@pytest.fixture
def sample_secret_finding():
    """Sample TruffleHog secret finding"""
    return {
        "SourceMetadata": {
            "url": "https://example.com/app.js",
            "file": "app.js"
        },
        "SourceID": 1,
        "SourceType": 1,
        "SourceName": "filesystem",
        "DetectorType": 2,
        "DetectorName": "AWS",
        "DecoderName": "PLAIN",
        "Verified": True,
        "Raw": "AKIAIOSFODNN7EXAMPLE",
        "RawV2": "AKIAIOSFODNN7EXAMPLE",
        "Redacted": "AKIA****************",
        "ExtraData": None,
        "StructuredData": None
    }


# ============================================================================
# MOCK HTTP CLIENT
# ============================================================================

class MockHTTPResponse:
    """Mock HTTP response"""
    def __init__(self, status_code: int, text: str = "", json_data: dict = None):
        self.status_code = status_code
        self._text = text
        self._json_data = json_data
        self.headers = {}
    
    @property
    def text(self):
        return self._text
    
    def json(self):
        if self._json_data is not None:
            return self._json_data
        return json.loads(self._text)


class MockHTTPClient:
    """Mock HTTP client for testing"""
    def __init__(self):
        self.responses = {}
        self.get_calls = []
        self.post_calls = []
    
    def add_response(self, url: str, response: MockHTTPResponse):
        """Add a mock response for a URL"""
        self.responses[url] = response
    
    async def get(self, url: str, **kwargs):
        """Mock GET request"""
        self.get_calls.append({'url': url, 'kwargs': kwargs})
        if url in self.responses:
            return self.responses[url]
        return MockHTTPResponse(404, "Not Found")
    
    async def post(self, url: str, **kwargs):
        """Mock POST request"""
        self.post_calls.append({'url': url, 'kwargs': kwargs})
        if url in self.responses:
            return self.responses[url]
        return MockHTTPResponse(404, "Not Found")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass


@pytest.fixture
def mock_http_client():
    """Mock HTTP client fixture"""
    return MockHTTPClient()


# ============================================================================
# MOCK STATE MANAGER
# ============================================================================

@pytest.fixture
def mock_state_manager(tmp_path):
    """Mock state manager"""
    state = Mock()
    state.base_path = str(tmp_path / "state")
    state.get_file_manifest = Mock(return_value={})
    state.update_file_manifest = Mock()
    state.load_state = Mock(return_value={})
    state.save_state = Mock()
    return state


# ============================================================================
# MOCK NOTIFIER
# ============================================================================

@pytest.fixture
def mock_notifier():
    """Mock Discord notifier"""
    notifier = AsyncMock()
    notifier.notify_secrets = AsyncMock()
    notifier.notify_finding = AsyncMock()
    notifier.notify_error = AsyncMock()
    return notifier


# ============================================================================
# SUBPROCESS MOCKING
# ============================================================================

class MockSubprocessResult:
    """Mock subprocess result"""
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout.encode() if isinstance(stdout, str) else stdout
        self.stderr = stderr.encode() if isinstance(stderr, str) else stderr


class MockAsyncSubprocess:
    """Mock async subprocess"""
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self._stdout = stdout
        self._stderr = stderr
        self.stdout = AsyncMock()
        self.stderr = AsyncMock()
    
    async def communicate(self):
        """Mock communicate"""
        return self._stdout.encode() if isinstance(self._stdout, str) else self._stdout, \
               self._stderr.encode() if isinstance(self._stderr, str) else self._stderr
    
    async def wait(self):
        """Mock wait"""
        return self.returncode


@pytest.fixture
def mock_subprocess():
    """Mock subprocess module"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MockSubprocessResult()
        yield mock_run


# ============================================================================
# FILE CONTENT HELPERS
# ============================================================================

def create_js_file(directory: Path, filename: str, content: str) -> Path:
    """Helper to create a JavaScript file"""
    file_path = directory / filename
    file_path.write_text(content, encoding='utf-8')
    return file_path


def create_json_file(directory: Path, filename: str, data: dict) -> Path:
    """Helper to create a JSON file"""
    file_path = directory / filename
    file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return file_path


def calculate_hash(content: str) -> str:
    """Calculate MD5 hash of content"""
    return hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()


# Export helpers
pytest.create_js_file = create_js_file
pytest.create_json_file = create_json_file
pytest.calculate_hash = calculate_hash


# ============================================================================
# ASYNC HELPERS
# ============================================================================

async def async_return(value):
    """Helper to return a value asynchronously"""
    return value


async def async_raise(exception):
    """Helper to raise an exception asynchronously"""
    raise exception


# Export async helpers
pytest.async_return = async_return
pytest.async_raise = async_raise


# ============================================================================
# CORE MODULE FIXTURES (for jsscanner/core testing)
# ============================================================================

@pytest.fixture
def tmp_state_dir(tmp_path):
    """Create temporary state directory structure"""
    base = tmp_path / "results" / "test_target"
    db_path = base / '.warehouse' / 'db'
    findings_path = base / 'findings'
    
    # Create directories
    db_path.mkdir(parents=True, exist_ok=True)
    findings_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize state files
    history_file = db_path / 'history.json'
    history_file.write_text(json.dumps({
        'scanned_hashes': [],
        'scan_metadata': {}
    }, indent=2))
    
    metadata_file = db_path / 'metadata.json'
    metadata_file.write_text(json.dumps({
        'target': 'example.com',
        'created_at': '2026-01-06T00:00:00Z'
    }, indent=2))
    
    secrets_file = findings_path / 'secrets.json'
    secrets_file.write_text('')  # Empty secrets file
    
    state_file = db_path / 'state.json'
    state_file.write_text(json.dumps({
        'version': '1.0',
        'config_hash': None
    }, indent=2))
    
    return {
        'base': str(base),
        'db_path': str(db_path),
        'findings_path': str(findings_path),
        'history_file': str(history_file),
        'metadata_file': str(metadata_file),
        'secrets_file': str(secrets_file),
        'state_file': str(state_file),
        'checkpoint_file': str(db_path / 'checkpoint.json'),
        'bloom_path': str(db_path / 'state.bloom')
    }


@pytest.fixture
def sample_scan_state():
    """Sample scan state data"""
    return {
        'phase': 'download',
        'timestamp': '2026-01-06T10:30:00Z',
        'phase_progress': {
            'current_phase': 2,
            'total_phases': 4
        },
        'urls_discovered': 100,
        'files_downloaded': 50,
        'files_processed': 25,
        'secrets_found': 5
    }


@pytest.fixture
def mock_discovery_strategy():
    """Mock discovery strategy (Katana/SubJS/Browser)"""
    strategy = AsyncMock()
    strategy.fetch_urls = AsyncMock(return_value=[
        'https://example.com/app.js',
        'https://example.com/vendor.js',
        'https://example.com/bundle.js'
    ])
    strategy.is_installed = Mock(return_value=True)
    return strategy


@pytest.fixture
def mock_fetcher():
    """Mock fetcher for download operations"""
    fetcher = AsyncMock()
    
    # Mock methods
    fetcher.fetch_and_write_with_fallback = AsyncMock(return_value=True)
    fetcher.validate_domain = AsyncMock(return_value=(True, None))
    fetcher.fetch_live = AsyncMock(return_value=['https://example.com/live.js'])
    fetcher.cleanup = AsyncMock()
    fetcher.last_failure_reason = None
    
    # Mock noise filter
    noise_filter = Mock()
    noise_filter.should_skip_content = Mock(return_value=False)
    noise_filter.should_skip_url = Mock(return_value=False)
    fetcher.noise_filter = noise_filter
    
    return fetcher


@pytest.fixture
def mock_analysis_modules():
    """Mock analysis modules (SecretScanner, Processor, Semgrep, AST)"""
    modules = {
        'secret_scanner': AsyncMock(),
        'processor': AsyncMock(),
        'semgrep_analyzer': AsyncMock(),
        'ast_analyzer': AsyncMock()
    }
    
    # SecretScanner
    modules['secret_scanner'].scan_file = AsyncMock(return_value=[])
    modules['secret_scanner'].cleanup = AsyncMock()
    
    # Processor
    modules['processor'].process = AsyncMock(return_value={
        'beautified_content': 'beautified code',
        'decoded_content': 'decoded code',
        'extracts': {}
    })
    
    # SemgrepAnalyzer
    modules['semgrep_analyzer'].check_binary = Mock(return_value=True)
    modules['semgrep_analyzer'].analyze_directory = AsyncMock(return_value=[])
    
    # AST Analyzer
    modules['ast_analyzer'].analyze = Mock(return_value={
        'endpoints': [],
        'interesting_vars': []
    })
    
    return modules


@pytest.fixture
def mock_discord_notifier():
    """Mock Discord notifier"""
    notifier = AsyncMock()
    notifier.start = AsyncMock()
    notifier.stop = AsyncMock()
    notifier.send_status = AsyncMock()
    notifier.send_secret_batch = AsyncMock()
    notifier.send_finding = AsyncMock()
    return notifier


@pytest.fixture
def core_config():
    """Configuration specific for core module testing"""
    return {
        'threads': 50,
        'max_concurrent_domains': 10,
        'verbose': False,
        'force_rescan': False,
        'no_scope_filter': False,
        'discord_status_enabled': False,
        'discord_webhook': None,
        'discord_rate_limit': 30,
        'discord_max_queue': 1000,
        'checkpoint': {
            'enabled': True,
            'interval_minutes': 10
        },
        'download': {
            'chunk_size': 1000
        },
        'minification_detection': {
            'sample_size': 10000,
            'avg_line_length': 300,
            'semicolon_density': 0.5,
            'whitespace_ratio': 0.02,
            'short_var_ratio': 0.3
        },
        'semgrep': {
            'enabled': True,
            'timeout': 300
        },
        'trufflehog_enabled': True,
        'trufflehog_timeout': 300,
        'bundle_unpacker': {
            'enabled': True
        }
    }


# ============================================================================
# OUTPUT MODULE FIXTURES (for jsscanner/output testing)
# ============================================================================

@pytest.fixture
def sample_trufflehog_findings():
    """Sample TruffleHog findings (newline-delimited JSON)"""
    return [
        {
            "SourceMetadata": {
                "url": "https://example.com/app.js",
                "file": "app.js",
                "domain": "example.com",
                "line": 42
            },
            "SourceID": 1,
            "SourceType": 1,
            "SourceName": "filesystem",
            "DetectorType": 2,
            "DetectorName": "AWS",
            "DecoderName": "PLAIN",
            "Verified": True,
            "Raw": "AKIAIOSFODNN7EXAMPLE",
            "RawV2": "AKIAIOSFODNN7EXAMPLE",
            "Redacted": "AKIA****************",
            "ExtraData": None,
            "StructuredData": None,
            "Entropy": 4.2
        },
        {
            "SourceMetadata": {
                "url": "https://example.com/config.js",
                "file": "config.js",
                "domain": "example.com",
                "line": 15
            },
            "SourceID": 2,
            "SourceType": 1,
            "SourceName": "filesystem",
            "DetectorType": 3,
            "DetectorName": "GitHub",
            "DecoderName": "PLAIN",
            "Verified": False,
            "Raw": "ghp_1234567890abcdefghijklmnopqrstuv",
            "RawV2": "ghp_1234567890abcdefghijklmnopqrstuv",
            "Redacted": "ghp_***********************************",
            "ExtraData": None,
            "StructuredData": None,
            "Entropy": 3.8
        }
    ]


@pytest.fixture
def sample_report_data(tmp_path):
    """Create sample report input data structure"""
    base = tmp_path / "results" / "test_target"
    findings_dir = base / "findings"
    findings_dir.mkdir(parents=True, exist_ok=True)
    
    # Create trufflehog.json with newline-delimited JSON
    trufflehog_file = findings_dir / "trufflehog.json"
    secrets = [
        {
            "SourceMetadata": {
                "url": "https://example.com/app.js",
                "Data": {"Filesystem": {"file": "app.js"}},
                "domain": "example.com"
            },
            "DetectorName": "AWS",
            "Verified": True,
            "Raw": "AKIAIOSFODNN7EXAMPLE",
            "Redacted": "AKIA****************"
        },
        {
            "SourceMetadata": {
                "url": "https://example.com/config.js",
                "Data": {"Filesystem": {"file": "config.js"}},
                "domain": "example.com"
            },
            "DetectorName": "GitHub",
            "Verified": False,
            "Raw": "ghp_1234567890abcdefghijklmnopqrstuv",
            "Redacted": "ghp_***********************************"
        }
    ]
    
    with open(trufflehog_file, 'w', encoding='utf-8') as f:
        for secret in secrets:
            f.write(json.dumps(secret) + '\n')
    
    # Create extracts files
    endpoints_file = findings_dir / "endpoints.txt"
    endpoints_file.write_text("\n".join([
        "https://api.example.com/v1/users",
        "https://api.example.com/v1/posts",
        "https://api.example.com/v1/comments"
    ]))
    
    params_file = findings_dir / "params.txt"
    params_file.write_text("\n".join([
        "user_id",
        "api_key",
        "auth_token",
        "session_id"
    ]))
    
    domains_file = findings_dir / "domains.txt"
    domains_file.write_text("\n".join([
        "api.example.com",
        "cdn.example.com",
        "assets.example.com"
    ]))
    
    return {
        'base_path': str(base),
        'findings_dir': str(findings_dir),
        'trufflehog_file': str(trufflehog_file),
        'endpoints_file': str(endpoints_file),
        'params_file': str(params_file),
        'domains_file': str(domains_file)
    }


@pytest.fixture
def tmp_report_paths(tmp_path):
    """Create temporary report directory structure"""
    base = tmp_path / "results" / "test_target"
    findings = base / "findings"
    artifacts = base / "artifacts" / "source_code"
    logs = base / "logs"
    warehouse = base / ".warehouse" / "db"
    
    for path in [findings, artifacts, logs, warehouse]:
        path.mkdir(parents=True, exist_ok=True)
    
    return {
        'base': str(base),
        'findings': str(findings),
        'artifacts': str(artifacts),
        'logs': str(logs),
        'warehouse': str(warehouse)
    }


# ============================================================================
# STRATEGIES MODULE FIXTURES (for jsscanner/strategies testing)
# ============================================================================

@pytest.fixture
def mock_async_session():
    """Mock curl_cffi AsyncSession for HTTP requests"""
    session = AsyncMock()
    
    # Mock response object
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "console.log('test');"
    mock_response.content = b"console.log('test');"
    mock_response.headers = {
        'Content-Type': 'application/javascript',
        'Content-Length': '22'
    }
    
    # Mock aiter_content for streaming
    async def mock_aiter_content(chunk_size):
        yield b"console.log('test');"
    
    mock_response.aiter_content = mock_aiter_content
    
    # Mock session methods
    session.get = AsyncMock(return_value=mock_response)
    session.head = AsyncMock(return_value=mock_response)
    session.close = AsyncMock()
    
    # Context manager support
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock()
    
    return session


@pytest.fixture
def mock_playwright_page():
    """Mock Playwright page object"""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.content = AsyncMock(return_value="<html><body>console.log('test');</body></html>")
    page.evaluate = AsyncMock()
    page.cookies = AsyncMock(return_value=[
        {'name': 'session_id', 'value': 'abc123', 'domain': '.example.com'}
    ])
    page.close = AsyncMock()
    return page


@pytest.fixture
def mock_playwright_context():
    """Mock Playwright browser context"""
    context = AsyncMock()
    
    # Mock page creation
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.content = AsyncMock(return_value="console.log('playwright content');")
    mock_page.cookies = AsyncMock(return_value=[])
    mock_page.close = AsyncMock()
    
    context.new_page = AsyncMock(return_value=mock_page)
    context.cookies = AsyncMock(return_value=[])
    context.close = AsyncMock()
    
    return context


@pytest.fixture
def mock_playwright_browser():
    """Mock Playwright browser instance"""
    browser = AsyncMock()
    
    # Mock context creation
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.content = AsyncMock(return_value="console.log('browser content');")
    mock_page.cookies = AsyncMock(return_value=[])
    mock_page.close = AsyncMock()
    
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.cookies = AsyncMock(return_value=[])
    mock_context.close = AsyncMock()
    
    browser.new_context = AsyncMock(return_value=mock_context)
    browser.close = AsyncMock()
    browser.is_connected = Mock(return_value=True)
    
    return browser


@pytest.fixture
def mock_browser_manager(mock_playwright_browser):
    """Mock BrowserManager for ActiveFetcher"""
    manager = AsyncMock()
    manager.browser = mock_playwright_browser
    manager._ensure_browser = AsyncMock(return_value=mock_playwright_browser)
    manager.fetch_with_context = AsyncMock(return_value="console.log('fetched');")
    manager.get_cookies = AsyncMock(return_value=[
        {'name': 'cf_clearance', 'value': 'xyz789', 'domain': '.example.com'}
    ])
    manager.close = AsyncMock()
    return manager


@pytest.fixture
def mock_circuit_breaker():
    """Mock DomainCircuitBreaker"""
    breaker = Mock()
    breaker.is_blocked = Mock(return_value=False)
    breaker.record_success = Mock()
    breaker.record_failure = Mock()
    breaker.state = 'closed'
    breaker.failure_count = 0
    return breaker


@pytest.fixture
def mock_rate_limiter():
    """Mock DomainRateLimiter"""
    limiter = AsyncMock()
    limiter.acquire = AsyncMock()
    limiter.throttle = Mock()
    limiter.current_rps = 10
    return limiter


@pytest.fixture
def mock_connection_manager():
    """Mock DomainConnectionManager"""
    manager = AsyncMock()
    manager.acquire = AsyncMock()
    manager.release = Mock()
    manager.active_connections = 0
    manager.max_connections = 5
    return manager


@pytest.fixture
def mock_performance_tracker():
    """Mock DomainPerformanceTracker"""
    tracker = Mock()
    tracker.record_request = Mock()
    tracker.get_success_rate = Mock(return_value=0.95)
    tracker.get_avg_latency = Mock(return_value=0.5)
    tracker.should_use_browser_first = Mock(return_value=False)
    return tracker


@pytest.fixture
def sample_subjs_output():
    """Sample SubJS stdout output"""
    return """https://example.com/app.js
https://example.com/vendor.js
https://example.com/bundle.min.js
https://cdn.example.com/lib.js
https://example.com/config.js
invalid-url
https://other-domain.com/script.js
https://example.com/main.js"""


@pytest.fixture
def sample_katana_output():
    """Sample Katana stdout output"""
    return """[INF] Starting Katana
https://example.com/app.js
https://example.com/styles.css
https://example.com/api/data.json
https://example.com/bundle.js
https://example.com/image.png
https://example.com/vendor.min.js
[INF] Crawl complete"""


@pytest.fixture
def strategies_config():
    """Configuration specific for strategies module testing"""
    return {
        'passive': {
            'enabled': True,
            'timeout': 30,
            'retries': 3
        },
        'fast': {
            'enabled': True,
            'timeout': 60,
            'depth': 3
        },
        'active': {
            'enabled': True,
            'threads': 50,
            'timeout': 15,
            'progressive_timeout': True,
            'max_retries': 3,
            'preflight_head_check': True,
            'browser_fallback': True,
            'cookie_harvest': True,
            'rate_limit_rps': 10,
            'max_concurrent_per_domain': 5,
            'circuit_breaker': {
                'enabled': True,
                'failure_threshold': 5,
                'timeout_seconds': 60
            }
        },
        'playwright': {
            'headless': True,
            'timeout': 30000,
            'user_agent': 'Mozilla/5.0'
        },
        'curl_cffi': {
            'impersonate': 'chrome110',
            'verify': False
        }
    }


# ============================================================================
# UTILS MODULE FIXTURES
# ============================================================================

@pytest.fixture
def tmp_logs_dir(tmp_path):
    """Create a temporary logs directory for isolated logging tests"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


@pytest.fixture
def mock_logger_handler():
    """Mock logging handler with StringIO for capturing log output"""
    import io
    import logging
    
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    return {'handler': handler, 'stream': stream}


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing filesystem operations"""
    return {
        'simple': {'key': 'value', 'number': 42},
        'list': [1, 2, 3, 4, 5],
        'nested': {'level1': {'level2': {'level3': 'deep'}}},
        'array_of_objects': [
            {'id': 1, 'name': 'first'},
            {'id': 2, 'name': 'second'},
            {'id': 3, 'name': 'third'}
        ]
    }


@pytest.fixture
def sample_large_content():
    """Generate large content for performance testing"""
    return "x" * (10 * 1024 * 1024)  # 10MB of data


@pytest.fixture
def sample_unicode_content():
    """Sample Unicode content with various scripts"""
    return """
    # English
    Hello World!
    
    # Emoji
    🎉🔥💻🐛🚀
    
    # Japanese
    こんにちは世界
    
    # Arabic
    مرحبا بالعالم
    
    # Russian
    Привет мир
    
    # Chinese
    你好世界
    
    # Special characters
    ñ ü ö ä ß € £ ¥
    """


@pytest.fixture
async def retry_failure_counter():
    """Helper for tracking retry attempts in tests"""
    class FailureCounter:
        def __init__(self):
            self.attempt = 0
            self.max_failures = 0
            
        def reset(self, max_failures: int = 0):
            """Reset counter with new failure threshold"""
            self.attempt = 0
            self.max_failures = max_failures
            
        async def async_fail_then_succeed(self):
            """Async function that fails N times then succeeds"""
            self.attempt += 1
            if self.attempt <= self.max_failures:
                raise ValueError(f"Attempt {self.attempt} failed")
            return f"Success on attempt {self.attempt}"
            
        def sync_fail_then_succeed(self):
            """Sync function that fails N times then succeeds"""
            self.attempt += 1
            if self.attempt <= self.max_failures:
                raise ValueError(f"Attempt {self.attempt} failed")
            return f"Success on attempt {self.attempt}"
    
    return FailureCounter()


@pytest.fixture
def utils_config():
    """Configuration specific for utils module testing"""
    return {
        'retry': {
            'max_attempts': 3,
            'backoff_base': 1.0,
            'backoff_multiplier': 2.0,
            'jitter': True,
            'jitter_range': 0.2
        },
        'logging': {
            'console_level': 'INFO',
            'file_level': 'DEBUG',
            'error_level': 'WARNING',
            'max_bytes': 10485760,  # 10MB
            'backup_count': 5
        },
        'filesystem': {
            'encoding': 'utf-8',
            'create_parents': True,
            'exist_ok': True
        }
    }
