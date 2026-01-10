# 🔧 CRITICAL BUG FIXES - Failing Tests Analysis & Solutions

**Status**: PHASE 1 - Fixing Broken Tests
**Priority**: 🔴 CRITICAL - Blocking production deployment
**ETA**: 2-3 hours

---

## 📊 FAILURE SUMMARY

**12 Failing Tests** (96.7% → 100% pass rate needed)

| #   | Test                                            | Module           | Root Cause                 | Fix Complexity | Priority    |
| --- | ----------------------------------------------- | ---------------- | -------------------------- | -------------- | ----------- |
| 1   | `test_fetch_content_circuit_breaker_blocks`     | active           | Test uses wrong attr name  | 🟢 Easy        | 🔴 Critical |
| 2   | `test_browser_fallback_on_429`                  | active           | Mock setup incomplete      | 🟡 Medium      | 🔴 Critical |
| 3   | `test_cookie_harvest_after_browser_success`     | active           | Mock setup incomplete      | 🟡 Medium      | 🔴 Critical |
| 4   | `test_harvested_cookies_used_in_curl`           | active           | Mock setup incomplete      | 🟡 Medium      | 🔴 Critical |
| 5   | `test_fetch_and_write_streams_content`          | active           | Async iterator mock broken | 🟡 Medium      | 🔴 Critical |
| 6   | `test_fetch_and_write_validates_content_length` | active           | Async iterator mock broken | 🟡 Medium      | 🔴 Critical |
| 7   | `test_find_katana_binary_from_go_bin`           | fast             | Binary path detection      | 🟡 Medium      | 🟡 High     |
| 8   | `test_is_installed_returns_true_go_bin`         | fast             | Binary path detection      | 🟡 Medium      | 🟡 High     |
| 9   | `test_integration_waf_fallback`                 | integration      | Integration test setup     | 🟡 Medium      | 🔴 Critical |
| 10  | `test_retry_async_succeeds_after_failures`      | net              | Async fixture annotation   | 🟢 Easy        | 🔴 Critical |
| 11  | `test_retry_async_respects_max_attempts`        | net              | Async fixture annotation   | 🟢 Easy        | 🔴 Critical |
| 12  | `test_state_operations_performance`             | core/integration | Performance regression     | 🔴 Hard        | 🟡 High     |

---

## 🔴 CRITICAL FIX #1: Circuit Breaker Test (EASY FIX)

### Issue

**Test**: `test_fetch_content_circuit_breaker_blocks`
**File**: `tests/strategies/test_active.py:440-465`

**Problem**:

```python
# Test creates circuit breaker incorrectly:
fetcher.circuit_breakers = {'example.com': breaker}  # ❌ WRONG - plural dict

# But code expects:
self.circuit_breaker  # ✅ CORRECT - singular instance
```

**Why This Fails**: The `fetch_content()` method checks `self.circuit_breaker.is_blocked_async(domain)`, not `self.circuit_breakers[domain]`.

### Solution

```python
# Fix line 457 in test_active.py:
fetcher.circuit_breaker = breaker  # ✅ Use singular attribute
# Remove line 457: fetcher.circuit_breakers = {'example.com': breaker}
```

### Verification

```bash
pytest tests/strategies/test_active.py::test_fetch_content_circuit_breaker_blocks -v
```

---

## 🔴 CRITICAL FIX #2: Async Fixture Warnings (EASY FIX)

### Issue

**Tests**:

- `test_retry_async_succeeds_after_failures`
- `test_retry_async_respects_max_attempts`

**File**: `tests/utils/test_net.py`

**Problem**: Pytest deprecation warning - async test requesting async fixture without proper annotation.

```python
# Current (WRONG):
@pytest.fixture
async def retry_failure_counter():  # ❌ Regular fixture, async function
    counter = {'failures': 0, 'max_failures': 3}
    return counter

# Should be:
@pytest_asyncio.fixture  # ✅ Use pytest_asyncio decorator
async def retry_failure_counter():
    counter = {'failures': 0, 'max_failures': 3}
    return counter
```

### Solution

Replace `@pytest.fixture` with `@pytest_asyncio.fixture` for all async fixtures in `test_net.py`.

### Verification

```bash
pytest tests/utils/test_net.py::test_retry_async_succeeds_after_failures -v
pytest tests/utils/test_net.py::test_retry_async_respects_max_attempts -v
```

---

## 🔴 CRITICAL FIX #3: Browser Fallback Tests (MEDIUM FIX)

### Issue

**Tests**:

- `test_browser_fallback_on_429`
- `test_cookie_harvest_after_browser_success`
- `test_harvested_cookies_used_in_curl`

**File**: `tests/strategies/test_active.py`

**Problem**: Incomplete mock setup for browser fallback mechanism. Tests fail because:

1. `mock_browser_manager` not properly initialized
2. Missing `fetch_with_playwright` method mock
3. Cookie storage mechanism not mocked

### Current Test Setup (Incomplete)

```python
async def test_browser_fallback_on_429(mock_async_session, mock_browser_manager, strategies_config):
    # Mock returns 429, but no fallback mock setup ❌
    mock_async_session.get.return_value.status_code = 429
    # ... test expects browser fallback but it's not mocked
```

### Solution

**Step 1**: Add proper browser manager mock with Playwright methods:

```python
@pytest.fixture
def mock_browser_manager():
    """Mock browser manager with full Playwright integration"""
    manager = Mock()
    manager.initialized = True
    manager.is_running = True

    # Mock page object
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock(return_value=Mock(status=200))
    mock_page.content = AsyncMock(return_value="<script>console.log('test');</script>")
    mock_page.evaluate = AsyncMock(return_value=[])
    mock_page.cookies = AsyncMock(return_value=[
        {'name': 'session', 'value': 'abc123', 'domain': 'example.com'}
    ])

    # Mock context
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    # Mock browser
    mock_browser = Mock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)

    manager.get_browser = AsyncMock(return_value=mock_browser)
    manager.cleanup = AsyncMock()

    return manager
```

**Step 2**: Update tests to mock `fetch_with_playwright`:

```python
async def test_browser_fallback_on_429(mock_async_session, mock_browser_manager, strategies_config):
    fetcher = ActiveFetcher(strategies_config)
    fetcher.browser_manager = mock_browser_manager

    # Mock HTTP failure (429)
    mock_async_session.get.return_value.status_code = 429
    mock_async_session.get.return_value.text = "Rate limited"

    # Mock browser fallback success
    with patch.object(fetcher, 'fetch_with_playwright', new_callable=AsyncMock) as mock_playwright:
        mock_playwright.return_value = "console.log('test');"

        content = await fetcher.fetch_content('https://example.com/app.js')

        assert content == "console.log('test');"
        mock_playwright.assert_called_once()
```

### Verification

```bash
pytest tests/strategies/test_active.py::test_browser_fallback_on_429 -v
pytest tests/strategies/test_active.py::test_cookie_harvest_after_browser_success -v
pytest tests/strategies/test_active.py::test_harvested_cookies_used_in_curl -v
```

---

## 🔴 CRITICAL FIX #4: Streaming Download Tests (MEDIUM FIX)

### Issue

**Tests**:

- `test_fetch_and_write_streams_content`
- `test_fetch_and_write_validates_content_length`

**File**: `tests/strategies/test_active.py`

**Problem**: Runtime warning - `coroutine 'AsyncMockMixin._execute_mock_call' was never awaited`.

This means the async iterator mock is not properly configured for `response.content.iter_chunked()`.

### Current Test Setup (Broken)

```python
# Broken async iterator mock:
mock_async_session.get.return_value.content.iter_chunked = Mock()  # ❌ Not awaitable
```

### Solution

**Create proper async generator mock**:

```python
async def test_fetch_and_write_streams_content(tmp_path, mock_async_session, strategies_config):
    """Test streaming download to file"""
    output_file = tmp_path / "test.js"
    test_content = "console.log('test');" * 1000  # 24KB

    # ✅ Create proper async generator for streaming
    async def mock_stream():
        # Simulate chunked download (8KB chunks)
        chunk_size = 8192
        for i in range(0, len(test_content), chunk_size):
            yield test_content[i:i+chunk_size].encode('utf-8')

    # Configure mock response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {'content-length': str(len(test_content))}
    mock_response.content.iter_chunked = mock_stream  # ✅ Async generator

    mock_async_session.get.return_value = mock_response

    # Rest of test...
```

### Verification

```bash
pytest tests/strategies/test_active.py::test_fetch_and_write_streams_content -v
pytest tests/strategies/test_active.py::test_fetch_and_write_validates_content_length -v
```

---

## 🟡 HIGH FIX #5: Katana Binary Detection (MEDIUM FIX)

### Issue

**Tests**:

- `test_find_katana_binary_from_go_bin`
- `test_is_installed_returns_true_go_bin`

**File**: `tests/strategies/test_fast.py`

**Problem**: Tests assume Katana binary exists in `~/go/bin/katana`, but it doesn't on test machine.

### Current Test Setup (Environment-Dependent)

```python
def test_find_katana_binary_from_go_bin():
    """Should find Katana in GOPATH/bin"""
    katana_path = FastCrawler.find_katana_binary()

    # Assumes binary exists ❌
    assert katana_path is not None
    assert 'katana' in katana_path.lower()
```

### Solution

**Option A - Mock the binary check** (RECOMMENDED):

```python
@patch('os.path.exists')
@patch('os.path.expanduser')
def test_find_katana_binary_from_go_bin(mock_expanduser, mock_exists):
    """Should find Katana in GOPATH/bin"""
    # Mock that binary exists
    mock_expanduser.return_value = '/home/user'
    mock_exists.return_value = True

    with patch('shutil.which', return_value='/home/user/go/bin/katana'):
        katana_path = FastCrawler.find_katana_binary()

        assert katana_path == '/home/user/go/bin/katana'
```

**Option B - Skip if binary not installed**:

```python
@pytest.mark.skipif(not FastCrawler.is_installed(), reason="Katana not installed")
def test_find_katana_binary_from_go_bin():
    """Should find Katana in GOPATH/bin"""
    katana_path = FastCrawler.find_katana_binary()
    assert katana_path is not None
```

### Verification

```bash
pytest tests/strategies/test_fast.py::test_find_katana_binary_from_go_bin -v
pytest tests/strategies/test_fast.py::test_is_installed_returns_true_go_bin -v
```

---

## 🟡 HIGH FIX #6: Performance Regression Test (HARD FIX)

### Issue

**Test**: `test_state_operations_performance`
**File**: `tests/core/test_integration.py`

**Problem**: Performance benchmark failing - state operations taking too long.

### Investigation Needed

1. Check what the performance threshold is
2. Profile the failing operation
3. Determine if it's a real regression or test flakiness

### Temporary Solution (If Flaky)

```python
@pytest.mark.benchmark(min_rounds=10)  # Run multiple rounds for accuracy
def test_state_operations_performance(tmp_state_dir):
    """Benchmark state operations"""
    # ... existing test
```

### Permanent Solution (If Real Regression)

- Profile the state operations to find bottleneck
- Optimize Bloom filter operations
- Check if file I/O is blocking

### Verification

```bash
pytest tests/core/test_integration.py::TestPerformanceBenchmarks::test_state_operations_performance -v
```

---

## 🔴 CRITICAL FIX #7: WAF Integration Test (MEDIUM FIX)

### Issue

**Test**: `test_integration_waf_fallback`
**File**: `tests/strategies/test_integration.py`

**Problem**: Integration test not properly mocking full fallback chain.

### Solution

Combine solutions from browser fallback tests + circuit breaker tests.

---

## 📋 EXECUTION PLAN

### Phase 1: Easy Wins (30 minutes)

- [ ] Fix #1: Circuit breaker attribute name
- [ ] Fix #2: Async fixture decorators

**Expected**: 4/12 failures fixed → 8 remaining

### Phase 2: Mock Infrastructure (1 hour)

- [ ] Fix #3: Browser fallback mock infrastructure
- [ ] Fix #4: Async iterator streaming mocks

**Expected**: 6/12 failures fixed → 6 remaining

### Phase 3: Environment-Dependent Tests (45 minutes)

- [ ] Fix #5: Katana binary detection (use mocks)
- [ ] Fix #7: WAF integration test

**Expected**: 4/12 failures fixed → 2 remaining

### Phase 4: Performance Investigation (30 minutes)

- [ ] Fix #6: Profile and fix performance regression

**Expected**: ALL TESTS PASSING ✅

---

## 🚀 IMPLEMENTATION ORDER

1. **NOW**: Fix #1 and #2 (circuit breaker + async fixtures) - Get 4 easy wins
2. **Next**: Fix #4 (streaming mocks) - Unblock 2 more tests
3. **Then**: Fix #3 (browser fallback) - Most complex, needs careful mocking
4. **Finally**: Fix #5, #6, #7 - Environmental and integration issues

---

## ✅ SUCCESS CRITERIA

- [ ] All 644 tests passing (100%)
- [ ] No runtime warnings
- [ ] No async/await warnings
- [ ] No pytest deprecation warnings
- [ ] Coverage report generates cleanly

---

**NEXT ACTION**: Start implementing fixes in order of priority.
