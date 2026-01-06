# Utils Module Testing Plan

**Related Changes**: `20260106-utils-module-testing-changes.md`  
**Implementation Date**: 2026-01-06

## Objective

Implement comprehensive test suite for `jsscanner/utils` module covering all utilities: filesystem management (FileSystem), hashing (MD5), logging (structured logging with rotation), and network retry utilities (exponential backoff with jitter).

## Scope

### In Scope

- [ ] FileSystem class: directory structure creation, JSON operations, unique line appending
- [ ] Hashing utilities: async/sync MD5 hashing for content and files
- [ ] Logging setup: console + file handlers, rotation, UTF-8 encoding, structured adapters
- [ ] Retry utilities: async/sync decorators with exponential backoff, jitter, shutdown handling
- [ ] Integration tests: cross-component workflows
- [ ] Concurrency tests: race condition validation for filesystem operations
- [ ] Edge cases: large files, corrupt data, Unicode handling, Windows path compatibility

### Out of Scope

- Security audits (hardcoded keys are acceptable for private usage)
- Performance benchmarks beyond what's necessary for VPS optimization

## Success Criteria

1. ✅ **100% Test Pass Rate**: All tests pass without failures
2. ✅ **80%+ Code Coverage**: Achieve target coverage for all utils modules
3. ✅ **Zero Implementation Bugs**: Fix any bugs discovered during testing
4. ✅ **Complete Documentation**: Update CHANGELOG.md and DOCUMENTATION.md with all findings

## Test Infrastructure

### Phase 1: Setup Test Foundation

- [ ] **Task 1.1**: Create `tests/utils/` directory structure

  - Create `tests/utils/__init__.py`
  - Create test file stubs for all submodules

- [ ] **Task 1.2**: Extend `tests/conftest.py` with utils-specific fixtures
  - Add `tmp_logs_dir` fixture for isolated log file testing
  - Add `mock_logger_handler` fixture with StringIO for log capture
  - Add `mock_filesystem` fixture for filesystem operations
  - Add `sample_json_data` fixture for JSON file testing
  - Add `retry_test_helpers` fixture for retry testing

### Phase 2: FileSystem Tests (test_fs.py)

- [ ] **Task 2.1**: Basic directory structure creation

  - Test `create_result_structure` creates all expected directories
  - Test initialization of `history.json` with default structure
  - Test initialization of `metadata.json` with default fields
  - Test creation of `secrets/` subdirectory

- [ ] **Task 2.2**: JSON append operations

  - Test `append_to_json` appends data to existing JSON list
  - Test `append_to_json` creates new file if not exists
  - Test `append_to_json` handles concurrent writes
  - Test `append_to_json` with invalid JSON recovery

- [ ] **Task 2.3**: Unique line appending

  - Test `append_unique_lines` adds only new lines
  - Test `append_unique_lines` handles concurrent appends
  - Test `append_unique_lines` with large line sets (10,000+ lines)
  - Test `append_unique_lines` with Unicode content

- [ ] **Task 2.4**: File write operations

  - Test `write_text_file` with 'w' mode (overwrite)
  - Test `write_text_file` with 'a' mode (append)
  - Test UTF-8 encoding on Windows
  - Test binary content handling

- [ ] **Task 2.5**: Edge cases
  - Test behavior with read-only filesystem
  - Test handling of extremely long file paths (Windows MAX_PATH)
  - Test concurrent access to same file from multiple coroutines
  - Test recovery from partial writes

### Phase 3: Hashing Tests (test_hashing.py)

- [ ] **Task 3.1**: Content hashing

  - Test `calculate_hash` returns correct MD5 for known strings
  - Test `calculate_hash_sync` matches async version
  - Test empty string hashing
  - Test large content (>10MB) hashing

- [ ] **Task 3.2**: File hashing

  - Test `calculate_file_hash` matches content hash
  - Test handling of missing files
  - Test handling of binary files
  - Test handling of empty files

- [ ] **Task 3.3**: Consistency validation

  - Test async and sync versions produce identical results
  - Test deterministic hashing (same input = same output)
  - Test hash collision detection (statistical validation)

- [ ] **Task 3.4**: Edge cases
  - Test Unicode content hashing (emoji, special characters)
  - Test very large files (100MB+) memory efficiency
  - Test concurrent hashing of same content

### Phase 4: Logging Tests (test_log.py)

- [ ] **Task 4.1**: Logger setup

  - Test `setup_logger` creates console handler
  - Test `setup_logger` creates `logs/scan.log` with DEBUG level
  - Test `setup_logger` creates `logs/errors.log` with WARNING level
  - Test log rotation configuration (10MB max size)

- [ ] **Task 4.2**: StructuredLoggerAdapter

  - Test adapter adds context to log messages
  - Test adapter's `process` method formats extras
  - Test adapter with nested context dictionaries
  - Test adapter with various data types (int, list, dict)

- [ ] **Task 4.3**: Cross-platform compatibility

  - Test UTF-8 encoding on Windows (console + file)
  - Test log file creation in nested directories
  - Test handling of Windows-specific path issues

- [ ] **Task 4.4**: Log message validation

  - Test formatted messages include timestamp
  - Test formatted messages include log level
  - Test formatted messages include module name
  - Test multiline log messages

- [ ] **Task 4.5**: Edge cases
  - Test behavior when logs/ directory is read-only
  - Test log rotation under high write volume
  - Test concurrent logging from multiple coroutines
  - Test very long log messages (>10KB)

### Phase 5: Retry Utility Tests (test_net.py)

- [ ] **Task 5.1**: Async retry decorator

  - Test `retry_async` succeeds after N failures
  - Test `retry_async` respects max_attempts limit
  - Test `retry_async` with exponential backoff calculation
  - Test `retry_async` with jitter variance

- [ ] **Task 5.2**: Sync retry decorator

  - Test `retry_sync` succeeds after N failures
  - Test `retry_sync` respects max_attempts limit
  - Test `retry_sync` with exponential backoff calculation
  - Test `retry_sync` with jitter variance

- [ ] **Task 5.3**: Exception filtering

  - Test retries only on specified exceptions
  - Test immediate failure on non-retryable exceptions
  - Test exception chaining preservation

- [ ] **Task 5.4**: Shutdown handling

  - Test `shutdown_callback` aborts retry early
  - Test shutdown returns None without raising
  - Test shutdown doesn't trigger retry delay

- [ ] **Task 5.5**: RetryConfig

  - Test config initialization with custom values
  - Test delay calculation formula
  - Test backoff multiplier effect
  - Test max_delay cap enforcement

- [ ] **Task 5.6**: Edge cases
  - Test retry with 0 max_attempts (immediate failure)
  - Test retry with function that returns None
  - Test retry with async generator functions
  - Test nested retry decorators

### Phase 6: Integration Tests (test_integration.py)

- [ ] **Task 6.1**: FileSystem + Hashing workflow

  - Test creating files and hashing them in pipeline
  - Test deduplication using file hashes
  - Test concurrent file creation with hash verification

- [ ] **Task 6.2**: Retry + Real async operations

  - Test retry with real aiohttp requests (mocked)
  - Test retry with subprocess calls
  - Test retry with file I/O operations

- [ ] **Task 6.3**: Logging in concurrent scenarios

  - Test structured logging across multiple async tasks
  - Test log rotation doesn't corrupt during concurrent writes
  - Test error logs capture exception tracebacks

- [ ] **Task 6.4**: Complete utility stack
  - Test FileSystem + logging + retry in one workflow
  - Test error recovery with retry and proper logging
  - Test state persistence with checksums

### Phase 7: Test Execution & Bug Fixing

- [ ] **Task 7.1**: Run test suite

  - Execute `pytest tests/utils/ -v --cov=jsscanner/utils --cov-report=html`
  - Collect coverage report
  - Identify any failing tests

- [ ] **Task 7.2**: Fix implementation bugs

  - Debug and fix any bugs found in `jsscanner/utils/` code
  - Ensure fixes maintain backward compatibility
  - Re-run tests to verify fixes

- [ ] **Task 7.3**: Achieve 100% pass rate
  - Address any remaining test failures
  - Validate edge cases are properly handled
  - Confirm no regressions in other modules

### Phase 8: Documentation Updates

- [ ] **Task 8.1**: Update CHANGELOG.md

  - Document all tests added (with file names and test counts)
  - Document any bugs fixed in utils module
  - Document test results (pass rate, coverage)

- [ ] **Task 8.2**: Update DOCUMENTATION.md

  - Add Utils Module Testing section
  - Document test fixtures and their usage
  - Add examples of running utils tests
  - Document coverage targets and results

- [ ] **Task 8.3**: Update MODULE_AUDIT.md
  - Mark all test instructions as completed
  - Add test execution results
  - Document any deviations from the plan

## Test Metrics (Target)

- **Total Test Files**: 5 (fs, hashing, log, net, integration)
- **Total Test Cases**: 80+ comprehensive tests
- **Lines of Test Code**: ~2,000
- **Coverage Target**: 85%+ for jsscanner/utils
- **Pass Rate Target**: 100%

## Dependencies

- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock
- aiofiles (for async file operations)

## Risk Mitigation

1. **Windows Path Issues**: Use `tmp_path` fixture and pathlib for cross-platform compatibility
2. **Race Conditions**: Use asyncio.Lock in tests to validate thread-safety
3. **File System Permissions**: Mock filesystem for tests that would require elevated permissions
4. **Log File Pollution**: Use isolated temp directories for all log tests

## Notes

- All tests must be isolated and not affect the actual workspace
- Use extensive mocking to avoid filesystem side effects
- Focus on correctness, not performance, for unit tests
- Performance tests should be marked with `@pytest.mark.slow`
