# Core Module Testing Implementation Plan

**Module**: `jsscanner/core`
**Date**: 2026-01-06
**Status**: In Progress

## Objective

Implement a bulletproof test suite for the core orchestration engine to ensure 100% reliability for bug bounty automation. The core module is the heart of the scanner - it must NEVER fail during multi-day scans.

## Scope

### Files to Test

- `jsscanner/core/engine.py` - ScanEngine (main orchestrator)
- `jsscanner/core/state.py` - State (persistence, checkpointing, locking)
- `jsscanner/core/subengines.py` - DiscoveryEngine, DownloadEngine, AnalysisEngine
- `jsscanner/core/dashboard.py` - ScanDashboard (TUI)

### Test Categories

1. **Unit Tests** - Isolated component testing with heavy mocking
2. **Integration Tests** - Multi-component workflows
3. **State Management Tests** - Persistence, locking, bloom filters
4. **Resilience Tests** - Crash recovery, emergency shutdown
5. **Edge Case Tests** - Malformed data, race conditions, resource exhaustion

## Success Criteria

- [ ] 80%+ test coverage for all core files
- [ ] All test directives from MODULE_AUDIT.md implemented
- [ ] Zero tolerance for flaky tests
- [ ] All tests pass on Windows (VPS environment)
- [ ] Emergency shutdown and checkpoint recovery validated
- [ ] No memory leaks in long-running scan simulations

---

## Phase 1: Infrastructure Setup

### 1.1 Extend Test Fixtures (conftest.py)

- [ ] Add `mock_discovery_strategy` (Katana, SubJS, Browser)
- [ ] Add `mock_fetcher` with network simulation
- [ ] Add `mock_analysis_modules` (SecretScanner, Processor, Semgrep)
- [ ] Add `mock_discord_notifier`
- [ ] Add `sample_scan_state` fixture
- [ ] Add `tmp_state_dir` with state.json, bloom, checkpoint files

### 1.2 Create Test File Structure

- [ ] `tests/core/__init__.py`
- [ ] `tests/core/test_engine.py` - ScanEngine tests
- [ ] `tests/core/test_state.py` - State management tests
- [ ] `tests/core/test_subengines.py` - Subengine tests
- [ ] `tests/core/test_dashboard.py` - Dashboard smoke tests
- [ ] `tests/core/test_integration.py` - Full pipeline integration

---

## Phase 2: State Management Tests (test_state.py)

### 2.1 Basic State Operations

- [ ] Test state initialization (creates directories, state.json)
- [ ] Test `save_checkpoint()` creates atomic .tmp -> checkpoint
- [ ] Test `load_checkpoint()` reads valid checkpoint data
- [ ] Test `has_checkpoint()` validates age (7-day expiration)
- [ ] Test checkpoint cleanup after expiration

### 2.2 Hash Tracking & Deduplication

- [ ] Test `mark_as_scanned_if_new()` returns True for new hash
- [ ] Test `mark_as_scanned_if_new()` returns False for duplicate
- [ ] Test `is_scanned()` correctly checks hash existence
- [ ] Test hash persistence across state reloads

### 2.3 Bloom Filter Integration

- [ ] Test bloom filter creation when pybloom_live installed
- [ ] Test graceful degradation when pybloom_live missing
- [ ] Test bloom filter persistence to disk
- [ ] Test bloom filter loading on state init
- [ ] Test false positive rate stays below 1%

### 2.4 File Locking (Critical for VPS)

- [ ] Test `portalocker` acquires exclusive lock on state.json
- [ ] Test concurrent write attempts fail gracefully
- [ ] Test lock release on state cleanup
- [ ] Test lock timeout configuration

### 2.5 Secrets Management

- [ ] Test `add_secret()` appends valid JSON lines
- [ ] Test secrets file thread-safety
- [ ] Test secret deduplication by hash
- [ ] Test corrupt secrets file recovery

### 2.6 Configuration Change Detection

- [ ] Test `check_config_changed()` detects modified config
- [ ] Test config hash persistence
- [ ] Test incremental scan invalidation on config change

### 2.7 File Manifest

- [ ] Test `_save_file_manifest()` creates valid JSON
- [ ] Test `get_url_from_filename()` retrieves correct mapping
- [ ] Test manifest persistence across restarts

---

## Phase 3: ScanEngine Tests (test_engine.py)

### 3.1 Engine Initialization

- [ ] Test ScanEngine initialization with valid config
- [ ] Test dependency validation (trufflehog, semgrep, webcrack)
- [ ] Test output directory creation
- [ ] Test state manager initialization

### 3.2 URL Deduplication (`_deduplicate_urls`)

- [ ] Test identical URLs with/without trailing slash
- [ ] Test URLs with different query parameters
- [ ] Test malformed URLs filtered out
- [ ] Test `javascript:void(0)` and data: URLs filtered
- [ ] Test URLs exceeding 2000 chars filtered
- [ ] Test Unicode URL handling
- [ ] Test case-insensitive deduplication

### 3.3 Minification Detection (`_is_minified`)

- [ ] Test real jQuery.min.js returns True
- [ ] Test beautified code returns False
- [ ] Test avg_line_length > 300 triggers minified
- [ ] Test semicolon_density > 0.5 triggers minified
- [ ] Test whitespace_ratio < 0.02 triggers minified
- [ ] Test short_var_ratio > 0.3 triggers minified
- [ ] Test comments presence prevents minified flag
- [ ] Test edge case: empty file
- [ ] Test edge case: single-line file

### 3.4 Full Scan Orchestration (`run`)

- [ ] Test happy path: discovery -> download -> analysis -> report
- [ ] Test resume from checkpoint
- [ ] Test skip discovery when URLs provided via file
- [ ] Test SubJS vs non-SubJS paths
- [ ] Test semgrep enabled/disabled based on config
- [ ] Test secrets scanning enabled/disabled
- [ ] Test incremental scan skips already-scanned files
- [ ] Test final results saved to scan_results.json

### 3.5 Progress & Checkpointing

- [ ] Test `_save_current_progress()` updates state
- [ ] Test checkpoint saved after each major phase
- [ ] Test progress restoration after crash

### 3.6 Emergency Shutdown

- [ ] Test `_emergency_shutdown()` cancels tasks
- [ ] Test fetcher.cleanup() called
- [ ] Test notifier.stop() called
- [ ] Test state.save_checkpoint() called
- [ ] Test graceful exit even with exceptions

### 3.7 File Manifest Integration

- [ ] Test manifest created with URL -> filename mapping
- [ ] Test `get_url_from_filename()` integration
- [ ] Test manifest used by SecretScanner for URL enrichment

---

## Phase 4: SubEngines Tests (test_subengines.py)

### 4.1 DiscoveryEngine

- [ ] Test initialization with strategies
- [ ] Test `discover()` aggregates results from all strategies
- [ ] Test strategy deduplication
- [ ] Test empty results from all strategies
- [ ] Test partial strategy failures
- [ ] Test progress callback invocation

### 4.2 DownloadEngine

- [ ] Test `download_all()` processes URLs in chunks
- [ ] Test chunk_size configuration respected
- [ ] Test deduplication via state.mark_as_scanned_if_new()
- [ ] Test manifest creation after downloads
- [ ] Test failed_breakdown counters aggregated
- [ ] Test timeout failures categorized correctly
- [ ] Test 404 failures categorized correctly
- [ ] Test network errors categorized correctly
- [ ] Test vendor files marked as skipped

### 4.3 AnalysisEngine

- [ ] Test `process_files()` calls analyzer for each file
- [ ] Test vendor files skipped
- [ ] Test extracts saved via organizer
- [ ] Test `unminify_all_files()` beautifies minified JS
- [ ] Test beautification timeout fallback to original
- [ ] Test `run_semgrep()` executes when enabled
- [ ] Test `run_semgrep()` skipped when disabled
- [ ] Test semgrep timeout handling
- [ ] Test semgrep file size threshold

---

## Phase 5: Dashboard Tests (test_dashboard.py)

### 5.1 Smoke Tests

- [ ] Test ScanDashboard initialization
- [ ] Test `update_stats()` updates without exceptions
- [ ] Test `stop()` cleanup
- [ ] Test throttled updates (debouncing)

---

## Phase 6: Integration Tests (test_integration.py)

### 6.1 Full Pipeline Simulation

- [ ] Test complete scan: discovery -> download -> secrets -> semgrep -> report
- [ ] Test resume from checkpoint mid-scan
- [ ] Test incremental scan skips duplicates
- [ ] Test configuration change invalidates incremental state
- [ ] Test crash recovery with emergency shutdown
- [ ] Test manifest accuracy across full pipeline

### 6.2 Concurrency & Resource Management

- [ ] Test bounded concurrency (semaphore limits)
- [ ] Test no memory leaks with 1000+ files
- [ ] Test graceful handling of resource exhaustion

### 6.3 Real-World Scenarios

- [ ] Test scan of real bug bounty target (if safe/allowed)
- [ ] Test multi-day scan simulation (checkpoint every 100 files)
- [ ] Test VPS constraints (4 vCPU, 12GB RAM limits)

---

## Phase 7: Edge Cases & Resilience

### 7.1 Malformed Data

- [ ] Test corrupt state.json recovery
- [ ] Test corrupt checkpoint recovery
- [ ] Test corrupt bloom filter recovery
- [ ] Test corrupt secrets file recovery
- [ ] Test corrupt manifest recovery

### 7.2 Race Conditions

- [ ] Test concurrent state updates (threading)
- [ ] Test concurrent checkpoint saves
- [ ] Test concurrent secret additions

### 7.3 Resource Limits

- [ ] Test disk full scenario
- [ ] Test memory limit scenario
- [ ] Test file descriptor exhaustion
- [ ] Test network timeout scenarios

---

## Phase 8: Documentation & Finalization

- [ ] Update CHANGELOG.md with all test additions
- [ ] Update DOCUMENTATION.md with core module testing guide
- [ ] Create pytest.ini configuration for core tests
- [ ] Add coverage targets (80%+)
- [ ] Create README for tests/core/ directory

---

## Implementation Notes

### Priority Order

1. **Critical Path**: State tests (Phase 2) - foundation for everything
2. **High Priority**: Engine orchestration (Phase 3) - main scan logic
3. **Medium Priority**: SubEngines (Phase 4) - component validation
4. **Low Priority**: Dashboard (Phase 5) - UI/UX, less critical
5. **Essential**: Integration (Phase 6) - validates everything works together

### Testing Philosophy

- Mock all external I/O (network, subprocess, filesystem where possible)
- Use tmp_path for all file operations
- Test failure paths as rigorously as success paths
- Every test must have clear assertion
- No flaky tests tolerated

### Performance Targets

- State operations: < 10ms per call
- Full scan simulation: < 60s for 100 files
- Checkpoint save: < 100ms
- Bloom filter lookup: < 1ms

---

## Risk Mitigation

### Known Challenges

1. **Windows File Locking**: portalocker behavior on Windows vs Linux
   - Mitigation: Test both platforms, use conservative timeout
2. **Bloom Filter Memory**: Large scans may exhaust memory
   - Mitigation: Test with 100k+ hashes, validate graceful degradation
3. **Race Conditions**: Concurrent access to state files
   - Mitigation: Extensive threading tests, validate lock acquisition

---

## Completion Checklist

- [ ] All phases marked complete
- [ ] Coverage report shows 80%+ for all core files
- [ ] All tests pass on Windows VPS environment
- [ ] No flaky tests (run test suite 10x, all pass)
- [ ] CHANGELOG.md updated
- [ ] DOCUMENTATION.md updated
- [ ] Changes tracking file completed with release summary
