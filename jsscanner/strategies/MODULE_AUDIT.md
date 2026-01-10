# jsscanner/strategies - Audit Report & Testing Directives

## 1. High-Level Summary

**Purpose:**
The `jsscanner/strategies` package implements URL discovery and fetching strategies. It contains three primary strategies:

* Passive (SubJS): historical archive-based discovery,
* Fast (Katana): breadth-first high-speed crawling,
* Active (Playwright + curl_cffi): live browser and HTTP fetching for file downloads and WAF-robust retrieval.

**Business Logic:**
These modules supply the engine with candidate JavaScript URLs (discovery) and provide robust, high-throughput, resource-aware download mechanisms. They encapsulate network interactions, retries, fallbacks (browser vs HTTP), and per-domain controls (rate-limiting, circuit breakers) so core logic can remain testable and resilient on VPS environments.

---

## 2. Technical Hierarchy & Contents

**Key Classes (Name, Inheritance, Responsibility):**

* PassiveFetcher
* Responsibility: Run `subjs` subprocess safely with retry wrappers; parse and scope-filter results; batch concurrency wrapper for many domains.


> **[AI TEST INSTRUCTION]:** Unit test `PassiveFetcher`:
> 1. Mock `shutil.which` to return a path for `subjs`.
> 2. Mock `subprocess.run` to return specific stdout lines (e.g., `https://example.com/js/main.js`).
> 3. Verify `fetch_urls` parses this output correctly.
> 4. Verify scope filtering removes URLs not matching the target domain.
> 
> 


* FastFetcher
* Responsibility: Run `katana` binary in batch mode, parse output for JS URLs, apply scope filter, and handle binary discovery.


> **[AI TEST INSTRUCTION]:** Unit test `FastFetcher`:
> 1. Mock `shutil.which` for `katana`.
> 2. Mock `subprocess.run`.
> 3. Verify `fetch_urls` creates a temp file with targets, runs the command, and cleans up the temp file.
> 
> 


* ActiveFetcher
* Responsibility: Advanced fetcher that performs preflight HEAD checks, curl-based downloads (curl_cffi.AsyncSession), Playwright fallback, cookie harvesting, per-domain rate-limiting and connection pools, progressive timeouts, circuit breakers, and streaming writes.


> **[AI TEST INSTRUCTION]:** Unit test `ActiveFetcher`:
> 1. Test `initialize()`: Ensure `AsyncSession` and `BrowserManager` are set up.
> 2. Test `fetch_content`: Mock `session.get` success (200 OK) and failure (Timeout).
> 3. Test `fetch_and_write`: Verify file writing behavior and content-length validation.
> 
> 


* BrowserManager, DomainRateLimiter, DomainConnectionManager, DomainPerformanceTracker, DomainCircuitBreaker
* Shared components to manage Playwright browser lifecycle, rate-limiting, per-domain concurrency, adaptive strategy decisions, and failure containment.


> **[AI TEST INSTRUCTION]:** Unit test helper classes:
> 1. `DomainCircuitBreaker`: Trigger failures until it opens. Verify `is_blocked` returns True.
> 2. `BrowserManager`: Test `_ensure_browser` logic (singleton pattern).
> 
> 



**Key Functions (Name, Inputs, Outputs, Purpose):**

* ActiveFetcher.fetch_content(url) -> Optional[str]
* Fetch content with progressive timeout & retry loop, preflight checks, adaptive browser-first logic for failing domains, and circuit-breaker integration.


> **[AI TEST INSTRUCTION]:** Test `ActiveFetcher.fetch_content` logic flow:
> 1. Mock `DomainCircuitBreaker.is_blocked` to return True. Assert returns None immediately.
> 2. Mock `_fetch_content_impl` to raise Exception. Assert retries happen with increasing timeout.
> 
> 


* ActiveFetcher._fetch_content_impl(url, timeout_override) -> Optional[str]
* Actual GET implementation with streaming, content validation (HTML detection, size checks), and noise filtering.


> **[AI TEST INSTRUCTION]:** Test `_fetch_content_impl` validation:
> 1. Mock response with `Content-Type: text/html`. Assert returns None (if strict mode).
> 2. Mock response size > max limit. Assert returns None.
> 
> 


* ActiveFetcher.fetch_with_playwright(url) -> Optional[str]
* Browser-based fetch (Playwright) used as fallback for WAF or when required.


> **[AI TEST INSTRUCTION]:** Test `fetch_with_playwright`:
> 1. Mock `browser_manager.fetch_with_context`.
> 2. Verify it calls `page.goto` and `page.content`.
> 
> 


* ActiveFetcher.fetch_and_write_with_fallback(url, out_path) -> bool
* Curl download first; if failed for certain reasons, fallback to browser and write file.


> **[AI TEST INSTRUCTION]:** Test fallback logic:
> 1. Mock `fetch_and_write` to return `False`.
> 2. Mock `fetch_with_playwright` to return content.
> 3. Verify it writes that content to `out_path` and returns `True`.
> 
> 



---

## 3. Integration & Configuration

**Config Usage:**

* Strategies are heavily configurable via `config.yaml`. The engine toggles which strategies run and configures their parameters (timeouts, concurrency, timeouts, retry counts, and session pool sizes). Notable: progressive timeout policy, domain-specific timeout multipliers, and cookie harvesting toggles.
> **[AI TEST INSTRUCTION]:** Configuration Integration Test:
> 1. Load a config with `playwright.headless = False`.
> 2. Initialize `ActiveFetcher`.
> 3. Inspect `BrowserManager` args to ensure `headless=False` was passed.
> 
> 



---

## 4. QA & Testing Strategy (Crucial)

### Test Cases to Write

(Use pytest + pytest-asyncio; heavily mock subprocesses, AsyncSession, and Playwright)

PassiveFetcher

1. SubJS success & parsing
* Mock subprocess.run to return stdout with JS URLs (some invalid lines). Assert fetch_urls returns only valid JS URLs and logs a success message.


> **[AI TEST INSTRUCTION]:** Implement test `test_passive_fetcher_parsing`. Input: `["http://valid.com/1.js", "garbage"]`. Output: `["http://valid.com/1.js"]`.


2. SubJS retry/failure handling
* Simulate subprocess raising TimeoutExpired and ensure retry logic is exercised and eventually returns empty list with warning logged.


> **[AI TEST INSTRUCTION]:** Implement test `test_passive_fetcher_retry`. Mock `subprocess.run` to raise `TimeoutExpired` 3 times.


3. fetch_batch concurrency
* Mock fetch_urls to return different lists per domain; call fetch_batch and verify TaskGroup parallelism and aggregation of results.


> **[AI TEST INSTRUCTION]:** Implement test `test_passive_fetch_batch`. Input: `["d1.com", "d2.com"]`. Assert combined results.



FastFetcher

4. Katana integration & temp file cleanup
* Mock katana stdout to include JS lines and simulate returncode 0; verify fetch_urls returns parsed list and temporary file is removed.


> **[AI TEST INSTRUCTION]:** Implement test `test_fast_fetcher_cleanup`. Verify `os.remove` is called on the temp input file.


5. Katana missing
* Simulate no katana binary found and assert function returns empty list and logs a clear warning.


> **[AI TEST INSTRUCTION]:** Implement test `test_fast_fetcher_missing_binary`.



ActiveFetcher

6. Progressive timeout & retries
* Mock `_fetch_content_impl` to raise asyncio.TimeoutError first two times, and succeed on third attempt; assert fetch_content increases timeout on retries and returns content.


> **[AI TEST INSTRUCTION]:** Implement test `test_active_fetcher_progressive_timeout`.


7. Circuit breaker and domain blocking
* Simulate repeated failures causing `record_failure` to trigger block; assert subsequent fetch_content returns early with reason 'circuit_breaker_blocked'.


> **[AI TEST INSTRUCTION]:** Implement test `test_active_fetcher_circuit_breaker`.


8. Browser fallback and cookie harvesting
* Mock curl `session.get` to return 429, then mock `fetch_with_playwright` to return content; ensure fetch_content uses browser fallback and returns content; verify cookie harvesting updates `valid_cookies` when applicable.


> **[AI TEST INSTRUCTION]:** Implement test `test_active_fetcher_fallback_harvest`. Verify `browser_manager.get_cookies` is called after successful fallback.


9. Streaming download & incomplete detection
* Mock response with Content-Length larger than actual streamed bytes to raise IncompleteDownloadError; assert fetch_content retries and eventually reports incomplete or fails gracefully.


> **[AI TEST INSTRUCTION]:** Implement test `test_active_fetcher_incomplete_download`.


10. fetch_and_write_with_fallback end-to-end
* Mock fetch_and_write to fail and fetch_with_playwright to return content; test that out_path is written and function returns True; assert proper logging.


> **[AI TEST INSTRUCTION]:** Implement test `test_fetch_and_write_fallback_flow`.



Integration tests

11. Hybrid scenario with WAF-like behavior
* Use an HTTP test server that returns 429 for curl user-agent but 200 when Playwright visits (simulate cookies/challenges). Run ActiveFetcher.initialize + fetch_and_write_with_fallback to verify browser fallback path and cookie harvest flow.


> **[AI TEST INSTRUCTION]:** Implement test `test_integration_waf_fallback`. Use `pytest-httpserver` to simulate the conditional 429/200 logic.


12. High-load session rotation
* Simulate many concurrent downloads (> rotate_after) and asserts that `_rotate_session` is invoked and sessions replaced without exceptions.


> **[AI TEST INSTRUCTION]:** Implement test `test_session_rotation`. Mock `session_management.rotate_after` to a small number (e.g., 2) and perform 5 requests.



### Testing Notes & Mocks

* For active tests: mock `curl_cffi.requests.AsyncSession` methods (get/head) and `playwright.async_api` objects to avoid real network and browsers. Use `pytest-asyncio` event loop control.
> **[AI TEST INSTRUCTION]:** Create `MockAsyncSession` and `MockPlaywrightContext` fixtures.


* For subprocess-based tests: patch `subprocess.run` to return desired outputs or raise expected exceptions and validate retry behavior.
> **[AI TEST INSTRUCTION]:** Create `MockSubprocess` fixture.