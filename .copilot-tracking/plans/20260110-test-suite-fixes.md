# Test Suite Fixes - 100% Pass Target

**Date**: 2026-01-10
**Status**: In Progress
**Current**: 593 passing / 20 failing / 2 errors (96% passing)
**Target**: 100% passing

## Phase 1: Critical Fixes ✅

- [x] Fix syntax errors in active.py
- [x] Fix error_stats KeyError issues (add setdefault)
- [x] Fix semgrep to scan beautified files
- [x] Fix semgrep timeout issues

## Phase 2: Active Strategy Tests (16 failures)

### Group A: fetch_content Core Logic (5 tests)

- [ ] test_fetch_content_success - Returns None instead of content
- [ ] test_progressive_timeout_increases - Timeout progression not working
- [ ] test_fetch_content_retries_on_timeout - Retry logic not triggered
- [ ] test_fetch_content_max_retries - Max retries not respected
- [ ] test_fetch_content_circuit_breaker_blocks - Circuit breaker not blocking

### Group B: Circuit Breaker (4 tests)

- [ ] test_circuit_breaker_opens_after_threshold - Not opening after threshold
- [ ] test_circuit_breaker_blocks_when_open - Not blocking when open
- [ ] test_circuit_breaker_half_open_after_timeout - Half-open not working
- [ ] test_circuit_breaker_success_resets - Success not resetting state

### Group C: Browser Fallback & Cookie Handling (4 tests)

- [ ] test_browser_fallback_on_429 - Browser fallback not triggered on 429
- [ ] test_browser_fallback_on_403 - Browser fallback not triggered on 403
- [ ] test_cookie_harvest_after_browser_success - Cookies not harvested
- [ ] test_harvested_cookies_used_in_curl - Cookies not used in subsequent requests

### Group D: Streaming & Validation (2 tests + 2 errors)

- [ ] test_fetch_and_write_streams_content - Streaming validation failed
- [ ] test_fetch_and_write_validates_content_length - Content-Length validation failed

## Phase 3: Other Module Tests (4 failures)

- [ ] test_state_operations_performance - Performance benchmark failed
- [ ] test_find_katana_binary_from_go_bin - Katana binary detection
- [ ] test_is_installed_returns_true_go_bin - Katana installation check
- [ ] test_integration_waf_fallback - WAF fallback integration test
- [ ] test_structured_logger_adapter_formats_extras_for_file_handlers - Logger formatting

## Phase 4: Coverage Improvement

**Current Coverage**: 43%
**Target**: 80%

### Low Coverage Modules (Priority)

1. jsscanner/analysis/static.py (12%) - 536 statements, 472 missed
2. jsscanner/analysis/sourcemap.py (23%) - 141 statements, 109 missed
3. jsscanner/core/engine.py (31%) - 971 statements, 666 missed
4. jsscanner/analysis/secrets.py (35%) - 347 statements, 224 missed
5. jsscanner/core/state.py (42%) - 335 statements, 193 missed
6. jsscanner/analysis/semgrep.py (43%) - 208 statements, 119 missed

## Success Criteria

- ✅ All tests passing (100%)
- ✅ Coverage >= 80%
- ✅ No syntax errors
- ✅ No runtime errors in test suite
- ✅ All edge cases handled

## Notes

- Focus on fixing functional bugs first (Phase 2)
- Then improve test coverage (Phase 4)
- Document all changes in CHANGELOG.md
- User wants 100% - no exceptions for low-priority modules
