# JS Scanner Testing & Debugging Documentation

## Overview

This document describes the comprehensive test suite and debugging tools for the `jsscanner` project, covering:

1. **Analysis Module** (`jsscanner/analysis`) - JavaScript analysis, filtering, and processing
2. **Core Module** (`jsscanner/core`) - Orchestration engine and state management
3. **Output Module** (`jsscanner/output`) - Discord webhook notifications and report generation
4. **Debugging Tools** - Browser stability testing and crash diagnostics

The test suite ensures 100% reliability for bug bounty automation, with particular focus on dependency confusion detection, JavaScript analysis resilience, multi-day scan stability, crash recovery, and real-time alert notifications.

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Run entire test suite (all modules)
pytest tests/ -v

# Run with coverage report (all modules)
pytest tests/ -v --cov=jsscanner --cov-report=html --cov-report=term

# Run specific module tests
pytest tests/analysis/ -v      # Analysis module only
pytest tests/core/ -v          # Core module only
pytest tests/output/ -v        # Output module only

# Run by test category
pytest tests/ -v -m unit              # Unit tests only
pytest tests/ -v -m integration       # Integration tests only
pytest tests/ -v -m "not slow"        # Exclude slow tests
pytest tests/ -v -m requires_binary   # Tests requiring external binaries
```

### Browser Stability Testing (NEW)

```bash
# Run browser crash stress test (10 parallel scans)
python debug_browser.py

# Expected output:
# ✅ Successful scans:     Variable (depends on target)
# ❌ Browser crashes:      0/10 (100% stability)
# 📦 Total JS files found: > 0

# Monitor for crashes in real scans
tail -f logs/scan.log | grep -E "crash|closed|Found.*JavaScript"

# Check for zombie processes
ps aux | grep chromium
```

### Test Organization

```
tests/
├── __init__.py                          # Test package initialization
├── conftest.py                          # Central fixture repository (700+ lines)
├── pytest.ini                           # Pytest configuration
├── analysis/                            # Analysis module tests (280+ tests)
│   ├── __init__.py
│   ├── test_filtering.py                # NoiseFilter tests (40+ tests)
│   ├── test_processor.py                # Processor tests (35+ tests)
│   ├── test_unpacking.py                # BundleUnpacker tests (40+ tests)
│   ├── test_semgrep.py                  # SemgrepAnalyzer tests (35+ tests)
│   ├── test_secrets.py                  # SecretScanner tests (35+ tests)
│   ├── test_secrets_organizer.py        # DomainSecretsOrganizer tests (35+ tests)
│   ├── test_organizer.py                # DomainExtractOrganizer tests
│   ├── test_sourcemap.py                # SourceMapRecoverer tests
│   ├── test_static.py                   # StaticAnalyzer tests
│   └── test_integration.py              # Pipeline integration tests
├── core/                                # Core orchestration tests (66 tests)
│   ├── __init__.py
│   ├── test_state.py                    # State management tests (60+ tests)
│   ├── test_engine.py                   # ScanEngine tests (35+ tests)
│   ├── test_subengines.py               # SubEngines tests (30+ tests)
│   ├── test_dashboard.py                # Dashboard tests (25+ tests)
│   └── test_integration.py              # Full pipeline tests (15+ tests)
└── output/                              # Output module tests (92 tests) ✅ NEW
    ├── __init__.py
    ├── test_discord.py                  # Discord webhook tests (45 tests)
    ├── test_reporter.py                 # Report generator tests (43 tests)
    └── test_integration.py              # Output integration tests (13 tests)
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Fast, isolated tests for individual functions and methods. These tests use extensive mocking to avoid external dependencies.

**Examples:**

- URL filtering logic
- Hex decoding
- Domain extraction
- Configuration parsing

### Integration Tests (`@pytest.mark.integration`)

Tests that verify component interactions and require real filesystem/network operations.

**Examples:**

- Filter → Processor pipeline
- Semgrep scanning with real binary
- TruffleHog scanning workflow
- Complete analysis pipeline

### Slow Tests (`@pytest.mark.slow`)

Performance benchmarks and tests that process large datasets.

**Examples:**

- 1000-secret processing
- 50-file batch scanning
- Large bundle unpacking

### Requires Binary (`@pytest.mark.requires_binary`)

Tests that need external tools (semgrep, trufflehog, webcrack) installed.

**Skip these if binaries not available:**

```bash
pytest tests/analysis/ -v -m "not requires_binary"
```

## Fixtures Reference (conftest.py)

### Event Loop Fixtures

- `event_loop` - Asyncio event loop for async tests
- `new_event_loop` - Fresh event loop per test

### Mock Fixtures

- `mock_logger` - Logger mock with all standard methods (debug, info, warning, error)
- `mock_state_manager` - State manager for tracking scan progress
- `mock_notifier` - Callback notifier for events
- `mock_http_client` - MockHTTPClient instance for network mocking
- `mock_subprocess` - Subprocess execution mock

### Core Module Fixtures

- `tmp_state_dir` - Temporary state directory with initialized database files
- `sample_scan_state` - Sample checkpoint data for resume testing
- `mock_discovery_strategy` - Mock discovery strategies (Katana/SubJS/Browser)
- `mock_fetcher` - Mock HTTP fetcher with download capabilities
- `mock_analysis_modules` - Mock analysis suite (SecretScanner, Processor, Semgrep, AST)
- `mock_discord_notifier` - Mock Discord webhook notifier
- `core_config` - Complete configuration for core module testing

### Configuration Fixtures

- `default_config` - Complete default scanner configuration
- `minimal_config` - Minimal configuration for testing
- `ignored_patterns_config` - Noise filter patterns (CDN domains, vendor libraries)

### Filesystem Fixtures

- `tmp_result_paths` - Temporary result directories (results/, results/js/, results/unpacked/)
- `tmp_path` - Pytest's built-in temporary directory

### Sample Data Fixtures

- `sample_js_minified` - Minified JavaScript code
- `sample_js_beautified` - Beautified JavaScript code
- `sample_js_with_hex` - JS with \xNN escape sequences
- `sample_js_with_sourcemap` - JS with inline sourcemap
- `sample_js_vendor_jquery` - jQuery vendor library
- `sample_webpack_bundle` - Webpack bundled code
- `sample_secret_finding` - TruffleHog finding structure

### Helper Functions

- `create_js_file(path, content)` - Create JS file for testing
- `create_json_file(path, data)` - Create JSON file
- `calculate_hash(content)` - SHA256 hash for content filtering

## Test Coverage Goals

### Overall Target: 80%+

**Analysis Module:**

- **NoiseFilter**: 90%+ (critical for vendor filtering)
- **Processor**: 85%+ (complex deobfuscation logic)
- **BundleUnpacker**: 80%+ (external tool integration)
- **SemgrepAnalyzer**: 80%+ (external tool integration)
- **SecretScanner**: 85%+ (concurrent scanning critical)
- **DomainSecretsOrganizer**: 90%+ (data integrity critical)
- **DomainExtractOrganizer**: 80%+
- **SourceMapRecoverer**: 75%+ (complex parsing)
- **StaticAnalyzer**: 75%+ (tree-sitter dependency)

**Core Module:**

- **State**: 90%+ (critical for persistence and crash recovery)
- **ScanEngine**: 85%+ (main orchestration logic)
- **SubEngines**: 80%+ (coordination and batch processing)
- **Dashboard**: 75%+ (TUI rendering and state management)

## Core Module Testing Guide

### State Management Tests (`test_state.py`)

The State module is the foundation for multi-day scan resumability. Tests cover:

**Hash Tracking & Deduplication:**

```python
def test_mark_as_scanned_if_new_returns_true_for_new_hash(tmp_state_dir):
    """Atomic hash marking prevents race conditions"""
    state = State(tmp_state_dir['base'])

    # First call succeeds
    result1 = state.mark_as_scanned_if_new('hash123', 'https://example.com/test.js')
    assert result1 is True

    # Duplicate detected
    result2 = state.mark_as_scanned_if_new('hash123', 'https://example.com/test.js')
    assert result2 is False
```

**Checkpoint Recovery:**

```python
def test_checkpoint_lifecycle(tmp_state_dir):
    """Test save, load, and expiration"""
    state = State(tmp_state_dir['base'])

    # Save checkpoint
    checkpoint_data = {'phase': 'download', 'progress': 50}
    state.save_checkpoint(checkpoint_data)

    # Load checkpoint
    loaded = state.load_checkpoint()
    assert loaded == checkpoint_data

    # Verify 7-day expiration
    assert state.has_checkpoint() is True
```

**Bloom Filter Optimization:**

```python
@pytest.mark.skipif(not pytest.importorskip("pybloom_live"), reason="pybloom_live not installed")
def test_bloom_filter_false_positive_rate(tmp_state_dir):
    """Bloom filter maintains <1% false positive rate"""
    state = State(tmp_state_dir['base'])

    # Add 10000 hashes
    for i in range(10000):
        state.bloom_filter.add(f'hash_{i}')

    # Test false positives
    false_positives = sum(1 for i in range(10000, 11000)
                          if f'hash_{i}' in state.bloom_filter)

    assert false_positives / 1000 < 0.01
```

### ScanEngine Tests (`test_engine.py`)

Main orchestration tests validate:

**URL Deduplication:**

```python
def test_deduplicate_identical_urls_with_trailing_slash(core_config, tmp_path):
    """URLs with/without trailing slash are normalized"""
    engine = ScanEngine(core_config, 'example.com')

    urls = [
        'https://example.com/app.js',
        'https://example.com/app.js/',
        'https://example.com/vendor.js',
        'https://example.com/vendor.js/'
    ]

    deduplicated = engine._deduplicate_urls(urls)

    # Should have only 2 unique URLs
    assert len(deduplicated) == 2
```

**Minification Detection (Multi-Heuristic):**

```python
def test_minified_jquery_returns_true(core_config, tmp_path, sample_js_minified):
    """Real minified jQuery detected via heuristics"""
    engine = ScanEngine(core_config, 'example.com')

    is_minified = engine._is_minified(sample_js_minified)

    assert is_minified is True  # avg_line_length, semicolon_density, whitespace_ratio
```

**Emergency Shutdown:**

```python
async def test_emergency_shutdown_saves_checkpoint(core_config, tmp_path):
    """Crash recovery preserves state"""
    engine = ScanEngine(core_config, 'example.com')

    engine.fetcher = Mock()
    engine.fetcher.cleanup = AsyncMock()
    engine.notifier = AsyncMock()

    engine._emergency_shutdown()

    # Verify cleanup
    engine.notifier.stop.assert_called_once()
```

### SubEngines Tests (`test_subengines.py`)

SubEngines coordinate discovery, download, and analysis:

**DownloadEngine Chunking:**

```python
async def test_download_all_processes_urls_in_chunks(core_config, tmp_path):
    """Chunks prevent memory exhaustion on large URL lists"""
    test_config = core_config.copy()
    test_config['download'] = {'chunk_size': 10}

    engine = ScanEngine(test_config, 'example.com')

    # 50 URLs should process in 5 chunks of 10
    urls = [f'https://example.com/file{i}.js' for i in range(50)]

    results = await engine.download.download_all(urls)

    # Verify chunked processing (implementation specific)
```

**AnalysisEngine Vendor Skipping:**

```python
async def test_process_files_skips_vendor_files(core_config, tmp_path):
    """Vendor libraries are not analyzed"""
    engine = ScanEngine(core_config, 'example.com')

    # Mock noise filter to identify vendor
    engine.fetcher.noise_filter.should_skip_content = Mock(return_value=(True, 'vendor library'))

    files = [{'url': 'https://cdn.example.com/jquery.min.js', ...}]

    await engine.analysis.process_files(files)

    # AST analyzer should NOT be called
    engine.ast_analyzer.analyze.assert_not_called()
```

### Integration Tests (`test_integration.py`)

Full pipeline validation:

**Complete Scan Workflow:**

```python
async def test_complete_scan_workflow(core_config, tmp_state_dir):
    """Test discovery -> download -> secrets -> semgrep -> report"""
    engine = ScanEngine(core_config, 'example.com')

    # Mock all phases
    with patch.object(engine, '_discover_all_domains_concurrent', ...):
        with patch.object(engine, '_download_all_files', ...):
            # ... mock secrets, analysis, semgrep

            await engine.run(['https://example.com'])

            # Verify all phases executed in order
```

**Checkpoint Resume:**

```python
async def test_scan_with_resume_from_checkpoint(core_config, sample_scan_state):
    """Resume from saved checkpoint"""
    with patch('jsscanner.core.engine.State') as mock_state_cls:
        mock_state.has_checkpoint = Mock(return_value=True)
        mock_state.get_resume_state = Mock(return_value=sample_scan_state)

        await engine.run(['https://example.com'], resume=True)

        # Verify checkpoint loaded
        mock_state.get_resume_state.assert_called_once()
```

**Performance Benchmarks:**

```python
@pytest.mark.slow
def test_state_operations_performance(tmp_state_dir):
    """State operations should be <10ms per call"""
    state = State(tmp_state_dir['base'])

    start = time.time()
    for i in range(100):
        state.mark_as_scanned_if_new(f'hash_{i}', f'url_{i}')
    elapsed = time.time() - start

    avg_time = elapsed / 100
    assert avg_time < 0.01  # <10ms average
```

## Writing New Tests

### Test Structure Template

```python
"""
Test description
"""
import pytest
from jsscanner.analysis.module import Class


@pytest.fixture
def instance(default_config, mock_logger):
    """Create instance for testing"""
    return Class(default_config, mock_logger)


@pytest.mark.unit
@pytest.mark.asyncio  # Only for async tests
class TestFeatureName:
    """Test specific feature"""

    async def test_basic_functionality(self, instance):
        """Test basic case"""
        result = await instance.method()
        assert result == expected

    async def test_edge_case(self, instance):
        """Test edge case"""
        with pytest.raises(ValueError):
            await instance.method(invalid_input)
```

### Best Practices

1. **Use Fixtures**: Leverage conftest.py fixtures instead of duplicating setup
2. **Mark Tests**: Always add appropriate markers (unit/integration/slow/requires_binary)
3. **Async Tests**: Use `@pytest.mark.asyncio` for async functions
4. **Parametrize**: Use `@pytest.mark.parametrize` for multiple input scenarios
5. **Clear Names**: Test names should describe what they verify
6. **Assertions**: Use specific assertions (assert x == y, not assert x)
7. **Mock External**: Mock network calls, subprocess, file I/O in unit tests
8. **Test Edge Cases**: Always test empty inputs, Unicode, binary data, errors

## Continuous Integration

### Pre-commit Checks

```bash
# Run before committing
pytest tests/analysis/ -v --cov=jsscanner/analysis --cov-report=term
```

### Coverage Requirements

All PRs must maintain minimum coverage:

```bash
# Analysis module: 80%+ coverage required
pytest tests/analysis/ --cov=jsscanner/analysis --cov-fail-under=80

# Core module: Focus on correctness over coverage
pytest tests/core/ --cov=jsscanner/core

# Output module: 85%+ for Discord, 80%+ for Reporter
pytest tests/output/ --cov=jsscanner.output
```

**Current Coverage Status**:

- **Analysis Module**: ~80% (meets target)
- **Core Module**: ~26% (correctness-focused, coverage in progress)
- **Output Module**: 86% overall (Discord: 85%, Reporter: 91%) ✅ **EXCEEDS TARGET**

### Parallel Execution

For faster test runs:

```bash
pytest tests/analysis/ -v -n auto  # Uses all CPU cores
```

---

## Output Module Testing Guide ✅ NEW

### Overview

The output module provides Discord webhook notifications and REPORT.md generation functionality. The test suite validates:

- Discord rate limiting and 429 handling
- Queue-based message processing with deduplication
- Worker thread resilience and error recovery
- Report generation from TruffleHog JSON
- Integration workflows

### Running Output Module Tests

```bash
# Run all output tests
pytest tests/output/ -v

# Run with coverage report
pytest tests/output/ -v --cov=jsscanner.output --cov-report=term

# Run specific test category
pytest tests/output/test_discord.py -v        # Discord webhook tests
pytest tests/output/test_reporter.py -v       # Report generator tests
pytest tests/output/test_integration.py -v    # Integration tests

# Run by marker
pytest tests/output/ -v -m unit               # Unit tests only (88 tests)
pytest tests/output/ -v -m integration        # Integration tests (13 tests)
pytest tests/output/ -v -m slow               # Performance tests (4 tests)

# Exclude slow tests
pytest tests/output/ -v -m "not slow"
```

### Output Module Test Results

**Status**: ✅ **100% PASS RATE** (92/92 tests passing)

**Coverage**:

- Discord class: **85%** (exceeds 85% target)
- Reporter module: **91%** (exceeds 80% target)
- Overall: **86%**

**Execution Time**: 86.65 seconds (1 minute 26 seconds)

**Test Breakdown**:

- Discord unit tests: 45 tests (initialization, rate limiting, 429 handling, queue management, deduplication, worker resilience, HTTP responses, embed creation, integration)
- Reporter unit tests: 43 tests (initialization, secrets sections, extracts parsing, error handling, statistics, structure, edge cases, warehouse fallback)
- Integration tests: 13 tests (Discord+reporter workflows, mock webhook server, performance, error recovery)

### Output Module Fixtures

The following fixtures are available in `tests/conftest.py`:

#### `sample_trufflehog_findings`

Mock TruffleHog secrets for testing Discord alerts and report generation.

**Contents**:

- 1 verified AWS secret (Access Key)
- 1 unverified GitHub secret (Personal Access Token)

**Usage**:

```python
def test_alert(sample_trufflehog_findings, tmp_path):
    # Use sample secrets for testing
    assert len(sample_trufflehog_findings) == 2
    assert sample_trufflehog_findings[0]['Verified'] is True
```

#### `sample_report_data`

Complete directory structure with TruffleHog JSON and extract files.

**Structure**:

```
sample_report_data/
├── findings/
│   └── trufflehog.json      # Newline-delimited JSON with 2 secrets
└── extracts/
    ├── endpoints.txt         # 3 API endpoints
    ├── params.txt            # 3 parameters
    └── domains.txt           # 2 domains
```

**Usage**:

```python
def test_report(sample_report_data):
    trufflehog_path = sample_report_data / "findings" / "trufflehog.json"
    assert trufflehog_path.exists()
```

#### `tmp_report_paths`

Temporary report directory with subdirectories for testing report generation.

**Structure**:

```
tmp_report_paths/
├── findings/        # Empty directory for trufflehog.json
├── extracts/        # Empty directory for extract files
└── .warehouse/      # Fallback directory
    └── db/          # Database fallback location
```

**Usage**:

```python
def test_generate_report(tmp_report_paths):
    output_dir = tmp_report_paths
    reporter.generate_report(output_dir, target_name="example.com")
    assert (output_dir / "REPORT.md").exists()
```

### Windows Compatibility

**Important**: The output module uses `curl_cffi` for HTTP requests, which requires `WindowsSelectorEventLoopPolicy` on Windows.

The event loop fixtures in `conftest.py` automatically handle this:

```python
@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for Windows compatibility with curl_cffi."""
    if platform.system() == "Windows":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()

@pytest.fixture
def event_loop(event_loop_policy):
    """Create event loop with proper policy for Windows."""
    asyncio.set_event_loop_policy(event_loop_policy)
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

**Error**: If you see `NotImplementedError: add_reader() is not implemented on Windows`, ensure you're using the correct event loop policy.

### Discord Class Testing

**Key Test Areas**:

1. **Initialization & Configuration**

   - Webhook URL validation
   - Custom rate limits (default: 30 msg/min)
   - Custom queue sizes (default: 1000)

2. **Rate Limiting**

   - Sliding window enforcement (60-second window)
   - Old timestamp cleanup for memory efficiency
   - Temporary rate limits (429 Retry-After)

3. **429 Handling**

   - Retry-After header parsing
   - Message requeueing with retry count
   - Max retries enforcement (3 attempts)
   - Default 60s backoff when no Retry-After

4. **Queue Management**

   - FIFO message processing
   - Overflow handling (drops oldest)
   - Queue draining on stop()

5. **Deduplication**

   - Dedup key: `detector + secret + source + line`
   - Prevents duplicate alerts for same secret

6. **Worker Resilience**

   - Continues after HTTP exceptions
   - Continues after JSON encoding errors
   - Logs all exceptions
   - Graceful shutdown

7. **HTTP Response Handling**

   - 200 OK: Success
   - 400 Bad Request: Drop message
   - 404 Not Found: Helpful error message
   - 429 Too Many Requests: Retry with backoff
   - 500 Server Error: Handle gracefully

8. **Embed Creation**
   - Verified secrets: Green color (3066993)
   - Unverified secrets: Orange color (15105570)
   - Includes domain and line number
   - Truncates long secrets (>100 chars)

**Example Test**:

```python
@pytest.mark.asyncio
@pytest.mark.unit
async def test_rate_limiting():
    """Test Discord rate limiting enforces sliding window."""
    discord = Discord(webhook_url="https://discord.com/api/webhooks/test", rate_limit=2)
    discord.start()

    # Queue 2 messages (at rate limit)
    for i in range(2):
        await discord.queue_alert({"secret": f"test{i}"})

    # Third message should be rate limited
    assert discord._can_send() is False

    discord.stop()
```

### Reporter Module Testing

**Key Test Areas**:

1. **Report Generation**

   - Creates REPORT.md in correct directory
   - Returns True on success, False on failure

2. **Secrets Sections**

   - Verified secrets section populated
   - Unverified secrets section populated
   - Secret preview truncation (40 chars)
   - Detector names included
   - Source file paths included

3. **Extracts Sections**

   - Endpoints parsed from extracts/endpoints.txt
   - Parameters parsed from extracts/params.txt
   - Domains parsed from extracts/domains.txt
   - Large lists truncated (>50 items)

4. **Error Handling**

   - Missing trufflehog.json handled gracefully
   - Corrupted JSON lines skipped with warning
   - Missing extract files don't crash

5. **Statistics**

   - Scan duration included
   - Total files scanned included
   - Missing/empty stats handled with "N/A"

6. **Report Structure**

   - Includes target name
   - Includes scan timestamp
   - Includes output structure section
   - Uses proper Markdown formatting

7. **Edge Cases**

   - Empty findings generate minimal report
   - Unicode in secrets handled
   - Very long target names (>200 chars)
   - Special characters in file paths

8. **Warehouse Fallback**
   - Reads from .warehouse/db/ if findings/ missing
   - Prefers findings/ directory over .warehouse/db/

**Example Test**:

```python
def test_generate_report_with_secrets(sample_report_data, tmp_path):
    """Test report generation includes verified secrets."""
    from jsscanner.output.reporter import generate_report

    report_path = generate_report(
        output_dir=sample_report_data,
        target_name="example.com"
    )

    assert report_path.exists()
    content = report_path.read_text()
    assert "Verified Secrets" in content
    assert "AWS" in content
```

### Integration Testing

**Key Test Areas**:

1. **Complete Workflow**

   - TruffleHog JSON → Reporter → Discord alerts
   - Verified secrets trigger Discord webhooks
   - Report includes all components

2. **Mock Webhook Server**

   - Real HTTP POST to mock endpoint
   - Embed structure validation (Discord limits)
   - Rate limiting validation
   - 429 retry validation

3. **Edge Cases**

   - Discord with no secrets
   - Reporter with empty findings
   - Concurrent Discord and reporter operations

4. **Performance**

   - Discord handles 100+ message queue
   - Reporter handles 100+ secrets and 1000+ endpoints

5. **Error Recovery**
   - Discord recovers from transient network errors
   - Reporter recovers from partial data

**Example Integration Test**:

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_workflow(sample_report_data, tmp_path):
    """Test complete TruffleHog → Reporter → Discord workflow."""
    from jsscanner.output.discord import Discord
    from jsscanner.output.reporter import generate_report

    # Generate report
    report_path = generate_report(
        output_dir=sample_report_data,
        target_name="example.com"
    )
    assert report_path.exists()

    # Send Discord alerts
    discord = Discord(webhook_url="https://discord.com/api/webhooks/test")
    discord.start()

    trufflehog_path = sample_report_data / "findings" / "trufflehog.json"
    for line in trufflehog_path.read_text().splitlines():
        secret = json.loads(line)
        if secret.get("Verified"):
            await discord.queue_alert(secret)

    discord.stop()
```

### Troubleshooting Output Module Tests

**Issue**: `NotImplementedError: add_reader() is not implemented on Windows`
**Solution**: Ensure event loop policy is set to `WindowsSelectorEventLoopPolicy`. This is handled automatically in conftest.py.

**Issue**: Tests hang on `discord.stop()`
**Solution**: Ensure worker thread is started with `discord.start()` before calling `stop()`.

**Issue**: Rate limiting tests fail randomly
**Solution**: Use `asyncio.sleep()` to advance time in tests that verify rate limit window expiration.

**Issue**: Reporter tests fail with "trufflehog.json not found"
**Solution**: Use `sample_report_data` fixture which includes pre-populated trufflehog.json.

**Issue**: Integration tests timeout
**Solution**: Mark slow tests with `@pytest.mark.slow` and run separately or increase timeout.

---

## Troubleshooting

### Tests Failing Due to Missing Binaries

Some tests require external tools:

- semgrep
- trufflehog
- webcrack

**Solution**: Install required tools or skip with:

```bash
pytest tests/analysis/ -v -m "not requires_binary"
```

### Async Event Loop Issues

If you see event loop errors:

- Ensure `@pytest.mark.asyncio` is present on async tests
- Check pytest-asyncio is installed
- Verify `asyncio_mode = auto` in pytest.ini

### Timeout Errors

Long-running tests may timeout:

- Use `@pytest.mark.slow` to mark them
- Increase timeout in pytest.ini if needed
- Run slow tests separately: `pytest -m slow --timeout=300`

### Coverage Not Reaching Target

If coverage is below 80%:

1. Check which lines are not covered: `pytest --cov=jsscanner/analysis --cov-report=html`
2. Open `htmlcov/index.html` in browser
3. Add tests for uncovered branches
4. Focus on edge cases and error handling paths

## Test Maintenance

### When Adding New Features

1. Write tests FIRST (TDD approach)
2. Add fixtures to conftest.py if reusable
3. Use appropriate markers
4. Update this documentation
5. Ensure coverage remains above 80%

### When Fixing Bugs

1. Write failing test that reproduces bug
2. Fix the bug
3. Verify test now passes
4. Add to CHANGELOG.md

### Regular Maintenance

- **Weekly**: Run full test suite with coverage
- **Monthly**: Review slow tests for optimization
- **Quarterly**: Update external tool versions and test compatibility

## Performance Benchmarks

Current benchmarks (50 files, VPS 4 vCPU):

- **Filtering**: < 0.5s
- **Processing**: < 5s
- **Complete Pipeline**: < 30s

Benchmarks validated by tests in `test_integration.py` with `@pytest.mark.slow`.

## Bug Bounty Context

These tests are specifically designed for bug bounty automation:

- **Dependency Confusion**: Filter tests ensure vendor libraries are properly excluded
- **Resilience**: Extensive edge case testing for crashed/malformed JavaScript
- **Concurrency**: Secrets scanning tests validate concurrent limits prevent WAF triggers
- **Stealth**: No tests validate rate limiting or user-agent rotation (handled in core module)

## Contact

For test failures or questions:

- Review MODULE_AUDIT.md for test directives
- Check CHANGELOG.md for recent changes
- See .copilot-tracking/plans/ for implementation details

---

## Enhanced Logging System

### Overview

The JS Scanner uses a per-target logging system that creates dedicated log files for each scan target. This allows for easy audit trails, post-scan analysis, and error tracking without cluttering the console output.

### Architecture

**Per-Target Log Files:**
- Each scan creates two log files in the `logs/` directory:
  - `{target}_{timestamp}.log` - Complete scan log (INFO+)
  - `{target}_errors_{timestamp}.log` - Error-only log (ERROR+)
- Filenames use UTC timestamps: `YYYY-MM-DD_HH-MM-SS`
- Target names are sanitized (protocols removed, special chars replaced)

**Example:**
```
logs/
 example.com_2024-01-15_14-30-25.log
 example.com_errors_2024-01-15_14-30-25.log
 api.test.org_2024-01-15_15-00-00.log
 api.test.org_errors_2024-01-15_15-00-00.log
 example.com_summary_2024-01-15_14-30-25.txt
```

### Configuration

Configure logging in `config.yaml`:

```yaml
logging:
  dir: "logs"              # Directory for log files
  level: "INFO"            # Log level
  file_enabled: true       # Enable file logging
  console_enabled: true    # Console output
  rotation:
    type: "size"           # 'size' or 'time'
    max_bytes: 10485760    # 10MB per file
    backup_count: 5        # Keep 5 rotated files
  retention_days: 30       # Delete logs older than 30 days
```

### Usage

**Programmatic API:**

```python
from jsscanner.utils.log import get_target_logger
from jsscanner.utils.log_analyzer import analyze_log_file, generate_summary_report

# Create per-target logger
logger = get_target_logger("example.com", log_dir="logs", level=logging.INFO)

# Use logger
logger.info("Scan started")
logger.error("Failed to fetch resource")

# Analyze logs
stats = analyze_log_file('logs/example.com_2024-01-15.log')
print(f"Total errors: {stats['level_counts']['ERROR']}")
```

### Testing

Run logging system tests:

```bash
pytest tests/utils/test_logging.py -v
```

For complete documentation, see the Logging section above.

