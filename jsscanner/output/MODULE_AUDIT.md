
# jsscanner/output - Audit Report & Testing Directives

## 1. High-Level Summary

**Purpose:**
The `jsscanner/output` package handles reporting and notification responsibilities: generating a human-readable markdown report (`REPORT.md`) summarizing findings, and sending real-time alerts to Discord via webhook for critical items (secrets, status updates).

**Business Logic:**
This module surfaces scanner results to humans and external tooling: `reporter.generate_report` compiles a concise executive report from per-scan artifacts, while `Discord` implements a robust, rate-aware, queued notification system used by the engine to escalate verified/unverified secret findings and scan lifecycle status messages.

---

## 2. Technical Hierarchy & Contents

**Key Classes:**

* Discord
* Responsibility: Queue-based Discord webhook sender with rate limiting, retry/backoff on 429, deduplication, and graceful shutdown/draining.


> **[AI TEST INSTRUCTION]:** Unit test `Discord`:
> 1. Initialize `Discord` with a dummy webhook URL.
> 2. Call `start()`.
> 3. Call `queue_alert()` with a dummy secret.
> 4. Verify (via mocks) that the worker picks up the item and attempts an HTTP POST.
> 5. Call `stop(drain_queue=True)` and verify the queue empties.
> 
> 



**Key Functions:**

* Discord
* queue_alert(secret_data: dict): Queue a single secret alert (deduplicates by detector+secret+source).


> **[AI TEST INSTRUCTION]:** Test deduplication logic:
> 1. Call `queue_alert` with Secret A.
> 2. Call `queue_alert` with Secret A again (same content).
> 3. Verify that the internal queue size increased by only 1.
> 
> 


* _can_send() -> bool: Sliding-window check to ensure adherence to messages/minute limit and 429-driven backoff windows.


> **[AI TEST INSTRUCTION]:** Test rate limiting:
> 1. Set `rate_limit` to 2 messages/min.
> 2. Simulate sending 2 messages.
> 3. Assert `_can_send()` returns `False` immediately after.
> 4. Advance clock (mock time) by 61 seconds.
> 5. Assert `_can_send()` returns `True`.
> 
> 


* _send_webhook(session, embed): Send a webhook and handle 429, 4xx/5xx responses, with per-message retry counts and temporary reduced rate limits.


> **[AI TEST INSTRUCTION]:** Test error handling:
> 1. Mock `session.post` to return status 429 with header `Retry-After: 5`.
> 2. Call `_send_webhook`.
> 3. Verify it waits (mocks sleep) and retries.
> 4. Mock a permanent failure (404). Verify it logs an error and drops the message after retries.
> 
> 


* reporter.generate_report(target_name, base_path, stats, logger=None) -> bool
* Aggregates TruffleHog JSON lines, extracts endpoints/params/domains from files in `findings/`, and writes a concise `REPORT.md` with summary tables and top secrets.


> **[AI TEST INSTRUCTION]:** Unit test `generate_report`:
> 1. Create a temp directory structure mimicking scan results (`findings/trufflehog.json`, `findings/endpoints.txt`).
> 2. Populate these files with dummy data.
> 3. Run `generate_report`.
> 4. Assert `REPORT.md` is created and contains specific strings from the dummy data (e.g., "Critical Secret Found").
> 
> 



---

## 3. Integration & Configuration

**Dependencies:**

* External: `curl_cffi` — uses `curl_cffi.requests.AsyncSession(impersonate='chrome110')` to send HTTP POSTs. This is a performance and WAF-resilience choice.
> **[AI TEST INSTRUCTION]:** Integration/Mock Test: Verify that `AsyncSession` is initialized with `impersonate` arguments correctly (inspect arguments passed to constructor).



**Config Usage:**

* The engine passes `discord_webhook`, `discord_rate_limit`, and `discord_max_queue` from `config.yaml` when creating `Discord`. The module respects runtime configuration for queue sizing and rate limits and logs helpful guidance when misconfigured (e.g., 404/400 responses or full queue drops).
> **[AI TEST INSTRUCTION]:** Test config propagation: Initialize `Discord` with specific `rate_limit` and `max_queue_size` values. Verify these are stored in instance attributes correctly.



---

## 4. QA & Testing Strategy (Crucial)

### Test Cases to Write

(Use pytest + pytest-asyncio; mock `curl_cffi.requests.AsyncSession` to avoid network access)

Discord notifier tests:

1. Rate limiting window enforcement
* Mock `AsyncSession.post` to return 200; call `queue_alert` > rate_limit messages and assert `_can_send()` prevents sending more than `rate_limit` messages in a 60s sliding window; confirm `message_times` management.


> **[AI TEST INSTRUCTION]:** Implement test `test_discord_rate_limit_enforcement`.


2. 429 handling & retry logic
* Mock first `post` to return 429 with `Retry-After=1`, ensure message is requeued, `temporary_rate_limit` is set, and after retries exceeding 3 attempts the message is dropped and logged as error.


> **[AI TEST INSTRUCTION]:** Implement test `test_discord_429_backoff`. Mock `asyncio.sleep` to avoid slow tests.


3. Queue overflow behavior
* Configure `discord_max_queue` small (e.g., 3), enqueue 10 messages, assert `_messages_dropped` increases, and that a warning is logged on first drop.


> **[AI TEST INSTRUCTION]:** Implement test `test_discord_queue_overflow`.


4. Deduplication
* Call `queue_alert` with identical secret payloads, assert only the first is enqueued and duplicates are skipped (and logged at debug level).


> **[AI TEST INSTRUCTION]:** Implement test `test_discord_deduplication`.


5. Worker resilience on exception
* Mock `AsyncSession.post` to raise an exception intermittently; verify `_send_webhook` catches exceptions, logs them, and the worker continues processing other messages.


> **[AI TEST INSTRUCTION]:** Implement test `test_discord_worker_resilience`.



Reporter tests:

1. REPORT.md generation for verified/unverified secrets
* Create a test `base_path` with a simulated `findings/trufflehog.json` (newline-delimited JSON lines) containing both verified and unverified secrets; call `generate_report` and validate `REPORT.md` contains a Verified section with expected short previews and metadata.


> **[AI TEST INSTRUCTION]:** Implement test `test_reporter_secrets_section`.


2. Extracts inclusion and truncation
* Create `findings/endpoints.txt` and `params.txt` with many entries, ensure `generate_report` includes top entries and truncates displays correctly (no exceptions on large lists).


> **[AI TEST INSTRUCTION]:** Implement test `test_reporter_large_extracts`. Create input files with 1000 lines. Check output for truncation markers (e.g., "...and X more").


3. Missing/corrupted files
* Simulate missing `trufflehog.json` or a corrupted file with invalid JSON line; assert `generate_report` still produces a report without crashing and logs warnings if logger provided.


> **[AI TEST INSTRUCTION]:** Implement test `test_reporter_resilience`. Pass a path to a non-existent directory or file with garbage content. Assert function returns `True` (success) or degrades gracefully.



### Integration / CI Guidance

* For CI, add a test helper that acts as a fake webhook server (simple aiohttp endpoint capturing POSTs) to validate real HTTP interactions in an integration test. For unit tests, patch `curl_cffi.requests.AsyncSession.post` returning mock responses (status codes, headers, text).
> **[AI TEST INSTRUCTION]:** Create a `MockWebhookServer` fixture using `aiohttp` or `pytest-httpserver`. Use this in an integration test to verify the actual HTTP request body structure sent by `Discord`.