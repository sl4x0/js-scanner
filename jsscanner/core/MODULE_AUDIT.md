# jsscanner/core - Audit Report & Testing Directives

## 1. High-Level Summary

**Purpose:**
The `jsscanner/core` package contains the central orchestration and state management components of JS Scanner. It coordinates discovery, parallel download, analysis, secret scanning, beautification, Semgrep static analysis, reporting, and graceful shutdown / checkpointing.

> **[AI TEST INSTRUCTION]:** Create a `TestScanEngineIntegration` suite. This should use extensive mocking of the network/filesystem layer to simulate a full scan lifecycle without actually hitting the internet, ensuring all phases trigger in the correct order.

**Business Logic:**
`ScanEngine` is the main orchestrator that implements the multi-phase pipeline described in the README: discovery → download → (recursive discovery) → secrets scanning → extraction → beautification → Semgrep → cleanup. `State` implements all persistent state, incremental scanning, atomic checkpointing, bloom-based deduplication, and cross-platform file locking. `subengines` wraps phased logic into smaller, testable units (DiscoveryEngine, DownloadEngine, AnalysisEngine) and `ScanDashboard` provides a TUI for live monitoring.

---

## 2. Technical Hierarchy & Contents

**Key Classes:**

- ScanEngine (core/engine.py)
- Responsibility: Full pipeline lifecycle, phase orchestration, progress logging, dependency validation, graceful shutdown and emergency cleanup, saving final results.

> **[AI TEST INSTRUCTION]:** Unit test `ScanEngine`:
>
> 1. Test `run()` with `use_subjs=True` vs `False`. Verify `DiscoveryEngine` is called with correct args.
> 2. Test `run()` with `resume=True`. Verify `State.get_resume_state` is called.
> 3. Verify `_save_final_results` generates the JSON report at the end.

- State (core/state.py)
- Responsibility: Persistent state storage (history, metadata, checkpoint), thread-safe file locking, bloom filter optional support, incremental scanning, checkpoint management and config-change detection.

> **[AI TEST INSTRUCTION]:** Unit test `State`:
>
> 1. Test `save_checkpoint` and `load_checkpoint`. Ensure data persists to disk and reloads correctly.
> 2. Test `check_config_changed`. Modify a dummy config dict and assert it returns `True`.
> 3. Test locking: Attempt to write to `state.json` from two threads/tasks simultaneously (if possible in test env) or ensure `portalocker` logic is invoked.

- DiscoveryEngine (core/subengines.py)
- Responsibility: Encapsulate discovery strategies: Katana, SubJS, Live Browser; handles strategy-level concurrency and result aggregation.

> **[AI TEST INSTRUCTION]:** Unit test `DiscoveryEngine`:
>
> 1. Mock `KatanaStrategy` and `SubJSStrategy`.
> 2. Run `discover()`. Assert that results from both strategies are combined into a unique list.

- DownloadEngine (core/subengines.py)
- Responsibility: Chunked parallel download orchestration, deduplication via State, manifest persistence, batch aggregation of counters and diagnostics, fallback classification for failures.

> **[AI TEST INSTRUCTION]:** Unit test `DownloadEngine`:
>
> 1. Input: List of 50 URLs. Config `chunk_size` = 10.
> 2. Mock the `fetcher`.
> 3. Assert `download_all` processes the URLs in 5 batches.
> 4. Verify `State.is_scanned` prevents re-downloading previously scanned hashes.

- AnalysisEngine (core/subengines.py)
- Responsibility: Delegates to analysis modules: secrets scanning, AST extraction, Semgrep scanning, beautification (parallelized), and saving extracts.

> **[AI TEST INSTRUCTION]:** Unit test `AnalysisEngine`:
>
> 1. Mock `SecretScanner`, `Processor`, and `SemgrepAnalyzer`.
> 2. Pass a list of files to `process_files`.
> 3. Assert that `SecretScanner.scan_file` is called for each.
> 4. Assert that `Processor.process` is called for non-vendor files.

- ScanDashboard (core/dashboard.py)
- Responsibility: TUI rendering with Rich — shows progress, stats and throttles updates to avoid flicker.

> **[AI TEST INSTRUCTION]:** Smoke test `ScanDashboard`. Initialize it, call `update_stats` with dummy data, and ensure no exceptions are raised. (Visual testing is manual, logic testing checks state updates).

**Key Functions:**

- ScanEngine
- \_deduplicate_urls(urls) -> URL normalization and deduplication (removes query-duplication, invalids, corrupted URLs).

> **[AI TEST INSTRUCTION]:** Test `_deduplicate_urls` with:
>
> 1. `http://example.com` vs `http://example.com/` (Should dedupe).
> 2. `http://example.com?a=1` vs `http://example.com?b=2` (Should keep both if configured, or dedupe based on logic).
> 3. `javascript:void(0)` (Should filter out).

- \_is_minified(content) -> multi-heuristic minification detection.

> **[AI TEST INSTRUCTION]:** Test `_is_minified`:
>
> 1. Input: Standard `jquery.min.js` content. Expect `True`.
> 2. Input: Formatted code with comments. Expect `False`.
> 3. Input: Code with very long lines (1000+ chars). Expect `True`.

- \_save_current_progress() and \_emergency_shutdown() -> synchronous emergency flush & cleanup.

> **[AI TEST INSTRUCTION]:** Test `_emergency_shutdown`: verify that it calls `fetcher.cleanup()`, `notifier.stop()`, and `state.save_checkpoint()`.

- State
- is_scanned(file_hash), mark_as_scanned_if_new(file_hash, url) -> atomic hash checks & marking.

> **[AI TEST INSTRUCTION]:** Test `mark_as_scanned_if_new`:
>
> 1. Call with Hash A (returns True).
> 2. Call with Hash A again (returns False).

- add_secret(secret_data) -> append verified secrets to locked file.

> **[AI TEST INSTRUCTION]:** Test `add_secret`: verify it appends valid JSON lines to `secrets.txt` (or json file) without overwriting existing data.

- DownloadEngine
- download_all(urls) -> chunked worker pool, per-chunk aggregation, deduplication via state, saves manifest.

> **[AI TEST INSTRUCTION]:** Test `download_all` failure modes: mock the fetcher to raise exceptions (Timeout, 404). Assert that `failed_breakdown` stats are updated correctly.

---

## 3. Integration & Configuration

**Config Usage:**

- `config.yaml` centrally controls concurrency, timeouts, checkpoint behavior, download chunking, semgrep toggles, minification heuristics, and secrets streaming options. `ScanEngine` uses these values throughout lifecycle for gating and tuning.
  > **[AI TEST INSTRUCTION]:** Integration Test: Load a test config where `semgrep.enabled` is `False`. Run `ScanEngine` and ensure `AnalysisEngine.run_semgrep` is NEVER called.

---

## 4. QA & Testing Strategy (Crucial)

### Test Cases to Write (unit + integration)

(Prefer pytest + pytest-asyncio, tmp_path, and heavy mocking for external processes)

ScanEngine tests:

1. run() orchestration (happy path):

- Mock DiscoveryEngine, DownloadEngine, AnalysisEngine, SecretScanner, SemgrepAnalyzer, and Discord notifier. Ensure that phases are called in order, checkpoints saved at major milestones, final `scan_results.json` exists and `generate_report` invoked.

> **[AI TEST INSTRUCTION]:** Implement test `test_scan_engine_happy_path`. Use `unittest.mock.MagicMock` for all sub-engines. Assert call order: Discovery -> Download -> Analysis -> Report.

2. \_deduplicate_urls():

- Provide mixed list (duplicates with query params, malformed URLs, URLs >2000 chars). Assert invalids are filtered and duplicates deduplicated, and warning logged for invalid URLs.

> **[AI TEST INSTRUCTION]:** Implement test `test_scan_engine_deduplication`.

3. \_is_minified() heuristics: several inputs to exercise each heuristic (avg line length, semicolon density, whitespace ratio, short variable ratio, comments): assert correct minified detection at threshold boundaries.

   > **[AI TEST INSTRUCTION]:** Implement test `test_minification_heuristics`. Create synthetic strings to trigger each specific heuristic (e.g., one with 50% semicolons, one with 0 newlines).

4. Emergency shutdown:

- Simulate running engine with mocked tasks and set shutdown flag. Call `_emergency_shutdown()` and assert fetcher.cleanup() and notifier.stop() were invoked and tasks were cancelled.

> **[AI TEST INSTRUCTION]:** Implement test `test_emergency_shutdown_cleanup`.

5. \_save_file_manifest() and get_url_from_filename():

- Save manifest entries and read them back via `get_url_from_filename()` to ensure consistency and JSON formatting.

> **[AI TEST INSTRUCTION]:** Implement test `test_manifest_integrity`. Write entries, verify `file_manifest.json` on disk is valid JSON, and read back.

State tests:

1. Atomic mark_as_scanned_if_new():

- Using tmp_path, run multiple invocations (simulated concurrency using threads or processes) and ensure duplicate check prevents race conditions.

> **[AI TEST INSTRUCTION]:** Implement test `test_state_atomic_updates`.

2. Bloom filter fallback & persistence:

- When `pybloom_live` not installed, ensure code gracefully degrades and methods still work; when mocked installed, ensure bloom file is saved and loaded.

> **[AI TEST INSTRUCTION]:** Implement test `test_state_bloom_filter_toggle`. Use `unittest.mock.patch.dict` to simulate missing `pybloom_live`.

3. Checkpoint lifecycle:

- Save checkpoints via save_checkpoint, validate atomic `.tmp` -> checkpoint file replacement, `has_checkpoint()` aging logic (simulate timestamp > 7 days), and `get_resume_state()` returns expected data.

> **[AI TEST INSTRUCTION]:** Implement test `test_checkpoint_lifecycle`. Manipulate file timestamps to test the 7-day expiration logic.

DownloadEngine tests (via subengines.DownloadEngine):

1. download_all() success & failure aggregation:

- Mock engine.fetcher.fetch_and_write_with_fallback to return True/False and assert that the return structure includes 'result' entries, that failed_breakdown counters are merged correctly, manifest entries saved.

> **[AI TEST INSTRUCTION]:** Implement test `test_download_engine_aggregation`. Assert the returned `stats` dict matches the sum of mocked outcomes.

2. Duplicate detection:

- Mock state.mark_as_scanned_if_new to return False for duplicates and ensure duplicates are skipped and `failures.duplicates` counters incremented.

> **[AI TEST INSTRUCTION]:** Implement test `test_download_engine_skips_duplicates`.

AnalysisEngine tests:

1. process_files():

- Ensure vendor files are skipped (mock fetcher.noise_filter.should_skip_content=True) and AST analyzer.analyze is called for non-vendor files; assert extracts saved via save_organized_extracts.

> **[AI TEST INSTRUCTION]:** Implement test `test_analysis_engine_vendor_skip`.

2. unminify_all_files():

- Mock processor.process to return beautified content and ensure files are written to `files_unminified` path; simulate jsbeautifier timeout to assert fallback to original content and limited logging.

> **[AI TEST INSTRUCTION]:** Implement test `test_unminify_timeout_fallback`.

3. run_semgrep():

- Mock semgrep_analyzer.validate() to True and scan_directory to return findings; ensure findings saved to file and `engine.stats['semgrep_findings']` updated.

> **[AI TEST INSTRUCTION]:** Implement test `test_run_semgrep_integration`.

### Testing Guidance & Tools

- Use `pytest-asyncio` for coroutine tests and `tmp_path` for filesystem isolation.

  > **[AI TEST INSTRUCTION]:** Mark all async tests with `@pytest.mark.asyncio`.

- Use `unittest.mock` to stub out `fetcher`, `processor`, `semgrep_analyzer`, `secret_scanner`, and notifier (`Discord`) to avoid network and heavy external process dependencies.
  > **[AI TEST INSTRUCTION]:** Create a `MockScanContext` fixture that sets up the engine with all external dependencies mocked out.
