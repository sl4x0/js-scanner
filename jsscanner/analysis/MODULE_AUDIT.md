# jsscanner/analysis - Audit Report & Testing Directives

## 1. High-Level Summary

**Purpose:**
The `jsscanner/analysis` package implements the core static-analysis and post-download processing pipeline for JS Scanner: filtering vendor/CDN files, beautifying and deobfuscating JavaScript, extracting embedded/external source maps, unpacking modern bundles (Webpack/Vite/Parcel), running Semgrep SAST scans, and detecting/organizing secrets via TruffleHog.

> **[AI TEST INSTRUCTION]:** Create a high-level integration test suite for `jsscanner/analysis`. Simulate the flow where a raw JS file enters the pipeline and verify it passes through filtering, processing, and scanning stages sequentially.

**Business Logic:**
This module transforms downloaded JavaScript into analyzable artifacts and findings for the rest of the pipeline. It:

* Prevents wasteful analysis on vendor/CDN files (NoiseFilter).
> **[AI TEST INSTRUCTION]:** Generate a test case with a known jQuery/Bootstrap file. Assert that `NoiseFilter` blocks it and that subsequent steps (Semgrep/Secrets) are NOT triggered for this file.


* Attempts to recover original source (Processor + BundleUnpacker + sourcemap extraction).
> **[AI TEST INSTRUCTION]:** Create a test with a minified file containing a `sourceMappingURL`. Assert that `Processor` retrieves the map and extracts the original source code.


* Runs security analysis at scale (SemgrepAnalyzer).
> **[AI TEST INSTRUCTION]:** Mock the `semgrep` binary. Verify that `SemgrepAnalyzer` is called with the correct arguments and that it saves a valid `semgrep.json` output.


* Streams secret findings to disk and organizes them per domain (SecretScanner + DomainSecretsOrganizer).
> **[AI TEST INSTRUCTION]:** Create a large dummy input stream of secrets. Verify that `SecretScanner` writes them to disk immediately (streaming) and does not hold them all in memory.


* Provides utilities to save organized extracts and reporting-friendly summaries for downstream reporting components.
> **[AI TEST INSTRUCTION]:** Verify `DomainExtractOrganizer` creates the expected folder structure and summary JSON files that match the schema required by the Reporting module.



---

## 2. Technical Hierarchy & Contents

**Key Classes (Name, Inheritance, Responsibility):**

* NoiseFilter
* Responsibility: Detect & skip vendor/CDN files by URL, pattern, content hash, or heuristic.


> **[AI TEST INSTRUCTION]:** Unit test `NoiseFilter`:
> 1. Feed it URLs from `data/ignored_patterns.json` (expect SKIP).
> 2. Feed it specific hashes of known libs (expect SKIP).
> 3. Feed it custom code (expect PASS).
> 
> 


* DomainExtractOrganizer
* Responsibility: Persist and summarize AST extracts grouped by source domain; maintain legacy outputs.


> **[AI TEST INSTRUCTION]:** Unit test `DomainExtractOrganizer`:
> 1. Pass a dummy AST extract.
> 2. Check if a directory matching the domain is created.
> 3. Check if `extracts.json` is updated correctly.
> 
> 


* Processor
* Responsibility: Beautify JS, decode obfuscation techniques (hex arrays, bracket notation), extract inline/external source maps, orchestrate bundle unpacking.


> **[AI TEST INSTRUCTION]:** Unit test `Processor`:
> 1. Input: Obfuscated JS with hex arrays (`\x61\x62`). Output: Clean ASCII (`ab`).
> 2. Input: One-line minified JS. Output: Multi-line beautified JS.
> 3. Mock `BundleUnpacker` and verify `Processor` delegates to it when a bundle signature is found.
> 
> 


* BundleUnpacker
* Responsibility: Detect bundles and call `webcrack` to reconstruct original directory & files; robust cleanup and retry handling.


> **[AI TEST INSTRUCTION]:** Unit test `BundleUnpacker`:
> 1. Mock `webcrack` CLI failure (non-zero exit code). Verify retry logic and cleanup of temp directories.
> 2. Mock success. Verify it returns the correct list of extracted files.
> 
> 


* SemgrepAnalyzer
* Responsibility: Validate/drive Semgrep CLI scans in chunks, pre-filter vendor files, aggregate & save findings safely.


> **[AI TEST INSTRUCTION]:** Unit test `SemgrepAnalyzer`:
> 1. Test logic when `semgrep` binary is missing (should return False/Warn, not crash).
> 2. Test chunking logic: Provide 1000 files and ensure `scan_directory` breaks them into batches respecting `chunk_size`.
> 
> 


* DomainSecretsOrganizer
* Responsibility: Stream secrets to disk, flush buffer periodically, organize secrets per-domain and write full results.


> **[AI TEST INSTRUCTION]:** Unit test `DomainSecretsOrganizer`:
> 1. Trigger `save_single_secret` multiple times.
> 2. Verify `_flush_secrets` writes to the file handle correctly.
> 3. Verify `organize_secrets` correctly groups a flat list of secrets by their `domain` field.
> 
> 


* SecretScanner
* Responsibility: Manage TruffleHog CLI streaming scanning (per-file and directory), enrich findings with manifest-derived URLs, stream to disk and notify via notifier interface.


> **[AI TEST INSTRUCTION]:** Unit test `SecretScanner`:
> 1. Mock `trufflehog` outputting JSON lines.
> 2. Verify findings are parsed and enriched with source URLs from the file manifest.
> 3. Verify the `notifier` callback is invoked for each finding.
> 
> 



**Key Functions (Name, Inputs, Outputs, Purpose):**

* NoiseFilter
* should_skip_url(url) -> (bool, reason) — checks vendor patterns & CDN domains.


> **[AI TEST INSTRUCTION]:** Test `should_skip_url` with inputs: `https://cdn.google.com/lib.js` (True), `https://mysite.com/app.js` (False). Assert exact reason strings.


* should_skip_content(content, filename="") -> (bool, reason) — checks known library hashes & heuristics.


> **[AI TEST INSTRUCTION]:** Calculate the hash of a real jQuery file. Test `should_skip_content` with that content. Verify it returns True.


* _is_likely_vendor_library(content) -> (bool, reason) — heuristic patterns & thresholds.


> **[AI TEST INSTRUCTION]:** Create dummy content with high density of keywords like `Copyright`, `License`, `webpack`. Verify `_is_likely_vendor_library` returns True.


* Processor
* _decode_hex_arrays(content) -> content — decode "\xNN" sequences when safe.


> **[AI TEST INSTRUCTION]:** Test `_decode_hex_arrays` with mixed content: `var a = "\x41";`. Expect `var a = "A";`. Ensure it ignores invalid/unsafe sequences.


* _beautify(content) -> beautified | original — with timeouts and size guards.


> **[AI TEST INSTRUCTION]:** Test `_beautify` with a massive string (mock size > limit) to ensure it returns original content immediately without processing.


* BundleUnpacker
* should_unpack(content, file_size) -> bool — checks config, webcrack availability, size & signatures.


> **[AI TEST INSTRUCTION]:** Test `should_unpack` with config `enabled=False` (Expect False). Test with content containing `webpackJsonp` (Expect True).


* SemgrepAnalyzer
* validate() -> bool — checks semgrep binary and version, with retries/backoff.


> **[AI TEST INSTRUCTION]:** Mock `subprocess.run`. 1st call raises Error, 2nd call succeeds. Verify `validate()` handles the retry and eventually returns True.


* DomainSecretsOrganizer
* _flush_secrets() — writes buffer safely handling corrupted file formats.


> **[AI TEST INSTRUCTION]:** Test `_flush_secrets` when the target JSON file is corrupted/malformed. Verify it backs up the old file and starts a fresh one without crashing.


* SecretScanner
* scan_file(file_path, source_url) -> int — streaming TruffleHog per-file with concurrency limit & notifier batching.


> **[AI TEST INSTRUCTION]:** Run `scan_file` concurrently on 10 files. Verify via mocks that `trufflehog_max_concurrent` semaphore limits the active processes.



---

## 3. Integration & Configuration

**Config Usage:**

* All major behaviors are configurable via `config.yaml`:
* `noise_filter` (min size, max_newlines, cdn domains, url_patterns)
* `beautification` timeouts per file size bucket
* `bundle_unpacker.enabled` and `min_file_size`
* `semgrep` section for chunk_size, timeout, ruleset, binary_path
* `trufflehog` settings including `trufflehog_max_concurrent` and timeouts


> **[AI TEST INSTRUCTION]:** Create a `TestConfigIntegration` suite.
> 1. Load a temporary `config.yaml` with non-default values.
> 2. Initialize all Analyzers (`NoiseFilter`, `Processor`, etc.).
> 3. Assert that the classes have adopted the values from the config (e.g., check `semgrep.timeout` matches yaml).
> 
> 



---

## 4. QA & Testing Strategy (Crucial)

### Test Cases to Write (unit + integration)

1. NoiseFilter: URL & content filtering
* Test: `should_skip_url` returns True for known CDN domain from `data/ignored_patterns.json` and vendor URL patterns; increments stats accordingly.


> **[AI TEST INSTRUCTION]:** Implement test `test_noise_filter_cdn_domains`. Use parameterization for multiple CDN examples.


* Test: `should_skip_content` returns True when content hash matches known_library_hash; returns vendor heuristic when signature present.


> **[AI TEST INSTRUCTION]:** Implement test `test_noise_filter_content_hashes`.


2. Processor: Beautify / Source Map / Deobfuscation
* Test: `_extract_source_map` decodes inline base64 map and returns combined `sourcesContent`.


> **[AI TEST INSTRUCTION]:** Implement test `test_processor_sourcemap_extraction`. Provide a file with `//# sourceMappingURL=data:application/json;base64,...`.


* Test: `_beautify` returns original content when `skip_beautification=True`, and times out gracefully for artificially delayed beautifier (mock `jsbeautifier.beautify` via worker and force a timeout).


> **[AI TEST INSTRUCTION]:** Implement test `test_processor_beautify_timeout`. Mock `jsbeautifier` to sleep for 10s and set config timeout to 1s.


3. BundleUnpacker: Detection & unpack flow
* Test: `should_unpack` respects `bundle_unpacker.enabled` False => False; when enabled and signature present => True.


> **[AI TEST INSTRUCTION]:** Implement test `test_bundle_unpacker_config_flags`.


* Test: `unpack_bundle` failure path: simulate `webcrack` returning nonzero with "already exists" stderr and verify retry cleanup path runs and either succeeds or returns None.


> **[AI TEST INSTRUCTION]:** Implement test `test_bundle_unpacker_retry_logic`. Assert that `shutil.rmtree` is called on the output directory before the retry.


4. SemgrepAnalyzer: validate & scan flows
* Test: `validate` returns False when semgrep binary missing; uses retries and logs warnings.


> **[AI TEST INSTRUCTION]:** Implement test `test_semgrep_missing_binary`.


* Test: `scan_directory` with sample JS files: vendor file excluded, non-vendor included; chunking logic invoked for >chunk_size; mock `asyncio.create_subprocess_exec` to return JSON stdout for findings; assert parsed findings count and `save_findings` writes correct `semgrep.json` structure.


> **[AI TEST INSTRUCTION]:** Implement test `test_semgrep_scan_flow`. Create a temp dir with 3 files (1 vendor, 2 valid). Verify `semgrep` is only called for the 2 valid files.


5. SecretScanner + DomainSecretsOrganizer: streaming & manifest enrichment
* Test: `_find_trufflehog_binary` resolves config path or falls back to PATH correctly (simulate platform differences).


> **[AI TEST INSTRUCTION]:** Implement test `test_trufflehog_binary_resolution`.


* Test: `scan_file` streaming parse: mock trufflehog process stdout to yield verified/unverified JSON lines; verify `state.add_secret` called for verified, `secrets_organizer.save_single_secret` invoked and flushed for buffered writes.


> **[AI TEST INSTRUCTION]:** Implement test `test_secret_scanner_streaming`. Feed partial JSON lines to the parser to ensure it handles stream buffering correctly.


* Test: `scan_directory` with manifest present: prepare a `file_manifest.json` mapping file hash to URL, feed sample trufflehog output lines, assert enrichment attaches `url`, `domain`.


> **[AI TEST INSTRUCTION]:** Implement test `test_secret_enrichment`. Verify that the output `secrets.json` contains the `source_url` from the manifest.



### Testing Notes & Mocks

* Mock external CLIs (`webcrack`, `semgrep`, `trufflehog`) using `unittest.mock` and custom asyncio subprocess mocks to simulate stdout/stderr and return codes.
> **[AI TEST INSTRUCTION]:** Create a shared fixture `mock_subprocess` that allows defining expected stdout/stderr/returncode for specific commands.


* Use `pytest-asyncio` for coroutine tests and event loop control.
> **[AI TEST INSTRUCTION]:** Ensure all async tests are decorated with `@pytest.mark.asyncio`.


* Filesystem tests should use `tmp_path` fixtures and assert cleanup behavior after failure flows.
> **[AI TEST INSTRUCTION]:** Review all file-writing tests to ensure they use the `tmp_path` fixture and do not leave artifacts in the source tree.