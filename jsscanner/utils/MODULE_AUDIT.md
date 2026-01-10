# jsscanner/utils - Audit Report & Testing Directives

## 1. High-Level Summary

**Purpose:**
The `jsscanner/utils` package contains small, focused helpers used across the scanner: filesystem management and path scaffolding (`FileSystem`), hashing utilities for deduplication (`hashing.py`), logging helpers that standardize console + file logging (`log.py`), and robust retry utilities for network/subprocess operations (`net.py`). These modules provide stable primitives that other higher-level modules (engine, strategies, analysis) rely on for correctness and reliability.

**Business Logic:**
Utilities abstract repetitive low-level concerns so that the core pipeline can remain concise: File I/O and directory layout, consistent hashing of content and files, high-quality logging (with forensic file handlers and rotating files), and retry patterns with controlled backoff and jitter. They are intentionally synchronous/async where appropriate to integrate into both sync and async code paths.

---

## 2. Technical Hierarchy & Contents

**Key Classes & Responsibilities:**

* FileSystem
* Responsibility: Create target directory structure (results/<target> tiers), initialize standard JSON files (history, metadata, secrets), and provide async helpers for file writes and appends.


> **[AI TEST INSTRUCTION]:** Unit test `FileSystem`:


> 1. Test `create_result_structure`: verify directory tree creation and initialization of `history.json`/`metadata.json` with correct default content.
> 2. Test `append_to_json`: verify data is appended correctly to a JSON list file.
> 3. Test `append_unique_lines`: verify only unique lines are added to a file.
> 
> 


* StructuredLoggerAdapter
* Responsibility: Attach structured context to log messages and format extra metadata for file logs.


> **[AI TEST INSTRUCTION]:** Unit test `StructuredLoggerAdapter`:


> 1. Create an adapter with context `{'module': 'test'}`.
> 2. Log a message.
> 3. Verify the context appears in the formatted log output (using a `logging.handlers.MemoryHandler` or `StringIO`).
> 
> 


* RetryConfig
* Responsibility: Encapsulate retry policy (backoff, multiplier, jitter) and delay calculation.


> **[AI TEST INSTRUCTION]:** Unit test `RetryConfig`:


> 1. Initialize with specific values.
> 2. Verify attributes hold these values.
> 
> 



**Key Functions:**

* hashing.calculate_hash(content) / calculate_file_hash(filepath) / calculate_hash_sync(content)
* MD5-based hashing helpers (async and sync); used for deduplication and file-manifest keys.


> **[AI TEST INSTRUCTION]:** Unit test hashing:


> 1. `calculate_hash("test")` should equal `md5("test").hexdigest()`.
> 2. `calculate_file_hash` on a file containing "test" should match the string hash.
> 3. Verify async and sync versions return identical results for identical inputs.
> 
> 


* log.setup_logger(name, log_file=None) -> Logger
* Sets console colored handler (INFO) and two rotating file handlers: `logs/scan.log` (DEBUG) and `logs/errors.log` (WARNING+). Ensures Windows UTF-8 encoding compatibility and initializes `logs/` dir.


> **[AI TEST INSTRUCTION]:** Unit test `setup_logger`:


> 1. Mock `Path("logs")`.
> 2. Call `setup_logger("test_logger")`.
> 3. Assert `scan.log` and `errors.log` file handlers are attached.
> 4. Assert handlers have the correct log levels (DEBUG vs WARNING).
> 
> 


* net.retry_async(...), net.retry_sync(...)
* Decorators that add retries with exponential backoff, jitter, configurable exceptions to retry on, and optional shutdown abort handling.


> **[AI TEST INSTRUCTION]:** Unit test retry decorators:


> 1. Decorate a function that raises `ValueError` 3 times then succeeds.
> 2. Call it with `max_attempts=4`. Assert success.
> 3. Call it with `max_attempts=2`. Assert it raises `ValueError`.
> 4. Verify `asyncio.sleep` (for async) or `time.sleep` (for sync) is called with increasing delays.
> 
> 



---

## 3. Integration & Configuration

**Config usage & alignment with project docs:**

* The utilities are configuration-agnostic for the most part but are used in concert with `config.yaml` (retry parameters, download timeouts are used elsewhere, but retry utilities offer defaults that are performance tuned as per CHANGELOG guidance).
> **[AI TEST INSTRUCTION]:** Integration test:
> 1. Create a dummy config object with retry settings.
> 2. Initialize `RetryConfig` using values from this config.
> 3. Verify the retry object reflects the configuration.
> 
> 



---

## 4. QA & Testing Strategy (Crucial)

### Test Cases to Write (Unit + Async)

(Prefer `pytest` + `pytest-asyncio` and `tmp_path` fixtures)

FileSystem tests

1. create_result_structure creates all expected directories and files
* Use `tmp_path` as base, call `create_result_structure('test', base_path=str(tmp_path))`, assert directories exist and JSON files contain expected defaults (history has `scanned_hashes`, metadata has fields).


> **[AI TEST INSTRUCTION]:** Implement test `test_fs_create_structure`.


2. append_unique_lines and append_to_json concurrency
* Use `pytest-asyncio` to concurrently call `append_unique_lines` with overlapping sets and assert final file contains unique lines only; for `append_to_json`, run many concurrent append calls and verify no data loss (or detect race behavior and add a note to harden implementation).


> **[AI TEST INSTRUCTION]:** Implement test `test_fs_concurrency`. Run 50 concurrent appends of "lineX" and assert file has 50 lines.


3. write_text_file writes content in 'w' and 'a' modes correctly
* Validate UTF-8 write/read roundtrip and that file modes work as intended.


> **[AI TEST INSTRUCTION]:** Implement test `test_fs_write_modes`.



Hashing tests

4. calculate_hash/calculate_file_hash consistency
* Ensure `calculate_hash_sync('abc') == await calculate_hash('abc')` and that `calculate_file_hash` on a temporary file with known content matches hash of the content.


> **[AI TEST INSTRUCTION]:** Implement test `test_hashing_consistency`.



Logging tests

5. setup_logger creates files and handlers
* Create a temp `logs` dir (monkeypatch `Path('logs')` to tmp), call `setup_logger`, assert `scan.log` and `errors.log` exist, and logger has at least 3 handlers (console + two file handlers). Also assert formatted log entries include structured adapter extras when using `create_structured_logger`.


> **[AI TEST INSTRUCTION]:** Implement test `test_logger_setup`.


6. StructuredLoggerAdapter process method
* Use an in-memory handler (StringIO) to capture formatted message; verify that adapter's `extra` is appended to message text for file handlers.


> **[AI TEST INSTRUCTION]:** Implement test `test_structured_adapter`.



Retry utilities tests

7. retry_async retries and succeeds
* Create an async function that fails N times by raising `asyncio.TimeoutError` then returns a value; wrap with `retry_async(max_attempts=N+1, retry_on=(asyncio.TimeoutError,))` and assert the wrapper returns final value and logs include success line.


> **[AI TEST INSTRUCTION]:** Implement test `test_retry_async_success_after_failure`.


8. retry_sync with shutdown callback
* Simulate a function that would be retried; provide a `shutdown_callback` that returns True after first failure and assert wrapper returns None early (no further retries).


> **[AI TEST INSTRUCTION]:** Implement test `test_retry_sync_shutdown_abort`.



### Integration Suggestions

* Add a CI job to run these tests with both `pytest` and `pytest-asyncio` in a matrix: Windows & Linux to validate console encoding fallback and path behaviors.
* For performance-critical FS functions, add a property-based test or fuzz test to ensure `append_unique_lines` behaves well with large inputs (several hundred thousand lines) and recommend improvements if memory is high.

---

## Recommendations & Next Steps

* Add unit tests for `FileSystem` and `net` retry decorators as high priority; these affect correctness across the entire pipeline.
* Consider making `append_to_json` atomic (temp file + rename) or integrate file locking for high-concurrency scanning modes to prevent write loss under heavy load.
* Add a small test that monkeypatches `Path('logs')` to a temp directory so `setup_logger` unit tests do not pollute repository logs and can assert rotation and encoding behavior cross-platform.

> Summary: `jsscanner/utils` contains small but critical primitives; vetting these with focused unit tests will yield outsized reliability improvements for the whole system (deduplication, robust logging, safe retries, and filesystem invariants).