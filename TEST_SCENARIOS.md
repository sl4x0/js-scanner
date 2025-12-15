# Test Scenarios for Scope vs. Discovery Mode Refactoring

## Overview

This document describes test scenarios to validate the new argument structure that separates scope definition from discovery behavior.

## Test Scenarios

### Scenario 1: Full Discovery for a Single Domain ✅

**Command:**

```bash
python -m jsscanner -t example.com --discovery
```

**Expected Behavior:**

1. ✅ Fetch all `*.example.com` URLs from Wayback Machine
2. ✅ Crawl live site at `example.com`
3. ✅ Scan all discovered JavaScript files
4. ✅ Filter results to match scope `example.com`

**Verify:**

- Discovery Mode: ON (Wayback + Live)
- Wayback API is queried
- Live site is crawled with Playwright
- Both sources contribute to the URL list

---

### Scenario 2: Scan Specific Subdomains (e.g., httpx output) - Live Only ✅

**Command:**

```bash
python -m jsscanner -t example.com -i subdomains.txt
```

**Expected Behavior:**

1. ✅ Read each line from `subdomains.txt`
2. ✅ For each subdomain:
   - Open the page in Playwright
   - Extract JavaScript files from that specific page only
   - Scan the extracted JS files
3. ✅ **Does NOT** query Wayback Machine for each subdomain
4. ✅ **Does NOT** attempt subdomain enumeration or guessing
5. ✅ Only scans what is explicitly listed in the input file

**Verify:**

- Discovery Mode: OFF (Direct scan only)
- No Wayback API calls
- Live Playwright scan for each input line only
- No automatic additional discovery

---

### Scenario 3: Multiple Root Domains with Discovery ✅

**Command:**

```bash
python -m jsscanner -t "program-name" -i domains.txt --discovery
```

**Expected Behavior:**

1. ✅ Read `domains.txt` (e.g., contains `google.com`, `youtube.com`)
2. ✅ For each domain:
   - Run Wayback Machine discovery
   - Run live site crawling
   - Scan all discovered JavaScript files
3. ✅ Use "program-name" as the scope identifier for filtering and output organization

**Verify:**

- Discovery Mode: ON (Wayback + Live)
- Both Wayback and Live discovery per domain
- All domains processed with full discovery
- Proper scope filtering applied

---

### Scenario 4: Direct JS URL List (No Discovery) ✅

**Command:**

```bash
python -m jsscanner -t example.com -i js-urls.txt
```

**Where `js-urls.txt` contains:**

```
https://example.com/static/app.js
https://example.com/vendor/jquery.min.js
https://cdn.example.com/bundle.js
```

**Expected Behavior:**

1. ✅ Read each JS URL from file
2. ✅ Download and scan each file directly
3. ✅ **NO** discovery (no Wayback, no live crawling)
4. ✅ Only scan the exact URLs provided

**Verify:**

- Discovery Mode: OFF
- Direct file downloads only
- No Wayback or live crawling

---

### Scenario 5: Single Domain Auto-Discovery (No Input) ✅

**Command:**

```bash
python -m jsscanner -t example.com
```

**Expected Behavior:**

1. ✅ Auto-enable discovery mode (since no input file provided)
2. ✅ Run full discovery for `example.com`
3. ✅ Query Wayback Machine
4. ✅ Crawl live site

**Verify:**

- Discovery Mode: Automatically ON
- Both Wayback and Live discovery
- Message indicates discovery auto-enabled

---

### Scenario 6: Specific URLs via CLI (No Discovery) ✅

**Command:**

```bash
python -m jsscanner -t example.com -u https://example.com/app.js https://example.com/main.js
```

**Expected Behavior:**

1. ✅ Scan only the two specified URLs
2. ✅ **NO** discovery
3. ✅ Direct download and scan

**Verify:**

- Discovery Mode: OFF
- Only 2 files scanned
- No additional discovery

---

## Implementation Verification Checklist

### CLI Arguments (`cli.py`)

- [x] Added `--discovery` flag
- [x] Updated help examples
- [x] Flag defaults to `False` (discovery OFF)

### Main Entry Point (`__main__.py`)

- [x] Input handling refactored
- [x] Separate input sources from discovery behavior
- [x] Auto-enable discovery when no input provided
- [x] Pass `discovery_mode` to engine
- [x] Display discovery mode status to user

### Scan Engine (`engine.py`)

- [x] Updated `run()` signature to accept `inputs` and `discovery_mode`
- [x] Conditional Wayback querying based on `discovery_mode`
- [x] Always fetch live JS (unless `--no-live`)
- [x] Removed `_read_input_file()` method
- [x] Removed `_discover_urls()` method
- [x] Removed `_discover_urls_for_domain()` method
- [x] Removed `_is_valid_domain()` method
- [x] Removed `_domain_matches_target()` method

### Fetcher Module (`fetcher.py`)

- [x] Documented that it doesn't control discovery
- [x] Provides methods but doesn't make decisions
- [x] Clean separation of concerns

---

## Expected Output Examples

### With Discovery ON:

```
🎯 Project Scope: example.com
📂 Input Items: 1
🔍 Discovery Mode: ON (Wayback + Live)
============================================================
📍 Processing input: example.com
  ├─ Live scan: Found 15 JS files
  └─ Wayback scan: Found 342 JS files
================================================================================
📊 Total unique JavaScript files to scan: 298
================================================================================
```

### With Discovery OFF:

```
🎯 Project Scope: example.com
📂 Input Items: 25
🔍 Discovery Mode: OFF (Direct scan only)
============================================================
📍 Processing input: https://app.example.com
  ├─ Live scan: Found 8 JS files
  └─ Wayback scan: Skipped (discovery mode OFF)
📍 Processing input: https://api.example.com
  ├─ Live scan: Found 3 JS files
  └─ Wayback scan: Skipped (discovery mode OFF)
...
================================================================================
📊 Total unique JavaScript files to scan: 47
================================================================================
```

---

## Benefits of Refactoring

1. **Predictable Behavior**: Users know exactly what will be scanned based on flags
2. **Performance Improvement**: No unwanted Wayback queries when scanning specific URL lists
3. **Flexibility**: Supports both targeted scanning and broad discovery modes
4. **Clear Separation**: Scope definition vs. discovery behavior are now distinct
5. **Better UX**: Clear feedback about what mode is active
6. **Resource Efficiency**: Reduces unnecessary API calls and bandwidth usage
