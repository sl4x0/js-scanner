# Refactoring Summary: Scope vs. Discovery Mode

## Overview

Successfully implemented a clear separation between **scope definition** and **discovery behavior** in the JS Scanner tool. This refactoring makes the tool predictable and prevents unwanted automatic discovery when scanning specific URL lists.

## Files Modified

### 1. `jsscanner/cli.py` ✅

**Changes:**

- Added `--discovery` flag (boolean, default: OFF)
- Updated help examples to demonstrate new usage patterns

**Code Changes:**

```python
parser.add_argument(
    '--discovery',
    action='store_true',
    help='Enable active discovery (Wayback + Live crawling) for targets. Default: OFF (Scan input list only)'
)
```

---

### 2. `jsscanner/__main__.py` ✅

**Changes:**

- Completely refactored input handling logic
- Separated input sources from discovery behavior
- Auto-enables discovery mode when no input file/URLs provided
- Displays clear status about discovery mode to users

**Key Logic:**

```python
# Determine Input List and Discovery Mode
targets_to_scan = []
discovery_mode = args.discovery

if args.input:
    # Read from input file
    with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
        targets_to_scan = [line.strip() for line in f if line.strip() and not line.startswith('#')]
elif args.urls:
    # Use provided URLs
    targets_to_scan = args.urls
else:
    # If no input file or URLs, force discovery mode ON
    targets_to_scan = targets
    discovery_mode = True

# Pass to engine with new signature
await engine.run(targets_to_scan, discovery_mode=discovery_mode)
```

---

### 3. `jsscanner/core/engine.py` ✅

**Major Refactoring:**

- Updated `run()` signature: `async def run(self, inputs: List[str], discovery_mode: bool = False)`
- Implemented conditional discovery logic
- Removed automatic discovery methods
- Simplified URL processing flow

**New URL Processing Logic:**

```python
for item in inputs:
    # CASE A: Direct JS URL (scan immediately)
    if self._is_valid_js_url(item):
        urls_to_scan.append(item)
        continue

    # CASE B: Domain/Page URL (needs JS extraction)

    # Always fetch LIVE JS (unless --no-live)
    if not self.config.get('skip_live', False):
        live_js = await self.fetcher.fetch_live(item)
        urls_to_scan.extend(live_js)

    # ONLY if Discovery Mode is ON, query Wayback
    if discovery_mode and not self.config.get('skip_wayback', False):
        wb_js = await self.fetcher.fetch_wayback(item)
        urls_to_scan.extend(wb_js)
```

**Removed Methods:**

- ❌ `_read_input_file()` - No longer needed (input handling moved to `__main__.py`)
- ❌ `_discover_urls()` - Discovery logic now inline and conditional
- ❌ `_discover_urls_for_domain()` - Redundant with new flow
- ❌ `_is_valid_domain()` - No longer needed
- ❌ `_domain_matches_target()` - No longer needed

---

### 4. `jsscanner/modules/fetcher.py` ✅

**Changes:**

- Added clarifying documentation
- No logic changes needed (already clean)

**Updated Documentation:**

```python
class Fetcher:
    """
    Fetches JavaScript files from various sources

    This module provides methods for fetching JS URLs from different sources
    but does NOT make decisions about when to use them. The calling code
    (ScanEngine) controls discovery behavior based on user configuration.
    """
```

---

## New Behavior Matrix

| Scenario                           | Command                                 | Discovery Mode | Wayback | Live   | Behavior                   |
| ---------------------------------- | --------------------------------------- | -------------- | ------- | ------ | -------------------------- |
| 1. Full discovery for domain       | `-t example.com --discovery`            | ON             | ✅      | ✅     | Fetch from all sources     |
| 2. Scan subdomain list (httpx)     | `-t example.com -i subs.txt`            | OFF            | ❌      | ✅     | Live scan only, no Wayback |
| 3. Multiple domains with discovery | `-t program -i domains.txt --discovery` | ON             | ✅      | ✅     | Full discovery per domain  |
| 4. Direct JS URL list              | `-t example.com -i urls.txt`            | OFF            | ❌      | Direct | Download URLs directly     |
| 5. Single domain (no input)        | `-t example.com`                        | AUTO-ON        | ✅      | ✅     | Auto-enables discovery     |
| 6. Specific URLs via CLI           | `-t example.com -u url1 url2`           | OFF            | ❌      | Direct | Scan specified URLs only   |

---

## User-Visible Changes

### Before Refactoring:

```bash
# Scanning httpx output would trigger Wayback for each subdomain (unwanted)
python -m jsscanner -t example.com -i subdomains.txt
# 🔴 Problem: Queries Wayback for every subdomain (slow, unnecessary)
```

### After Refactoring:

```bash
# Same command now only scans live pages (as expected)
python -m jsscanner -t example.com -i subdomains.txt
# ✅ Solution: Only scans live pages, no Wayback

# To enable full discovery, use --discovery flag
python -m jsscanner -t example.com -i subdomains.txt --discovery
# ✅ Now Wayback is queried (explicit user intent)
```

---

## Status Output Examples

### Discovery Mode ON:

```
🎯 Project Scope: example.com
📂 Input Items: 1
🔍 Discovery Mode: ON (Wayback + Live)
============================================================
```

### Discovery Mode OFF:

```
🎯 Project Scope: example.com
📂 Input Items: 25
🔍 Discovery Mode: OFF (Direct scan only)
============================================================
```

---

## Benefits

1. ✅ **Predictable Behavior**: Users know exactly what will be scanned
2. ✅ **Performance**: No unwanted Wayback queries (saves time and API calls)
3. ✅ **Flexibility**: Supports both targeted and broad discovery modes
4. ✅ **Clear Separation**: Scope vs. discovery are distinct concepts
5. ✅ **Better UX**: Clear feedback about active mode
6. ✅ **Resource Efficiency**: Reduces unnecessary bandwidth and API usage

---

## Breaking Changes

### ⚠️ API Changes:

- `ScanEngine.run()` signature changed:
  - **Old**: `run(input_file: Optional[str], urls: Optional[List[str]])`
  - **New**: `run(inputs: List[str], discovery_mode: bool = False)`

### ⚠️ Behavior Changes:

- **Old**: Providing `-i` with domains would auto-trigger discovery
- **New**: Must explicitly use `--discovery` flag to enable discovery

### Migration Guide:

```bash
# Old way (auto-discovery on input file):
python -m jsscanner -t example.com -i domains.txt

# New way (explicit discovery):
python -m jsscanner -t example.com -i domains.txt --discovery

# Or for live-only scanning (new default):
python -m jsscanner -t example.com -i domains.txt
```

---

## Testing

See [`TEST_SCENARIOS.md`](TEST_SCENARIOS.md) for comprehensive test scenarios.

---

## Implementation Status

- [x] CLI flag added
- [x] Input handling refactored
- [x] Engine logic updated
- [x] Fetcher documented
- [x] Obsolete methods removed
- [x] No errors in codebase
- [x] Test scenarios documented

---

## Next Steps

1. **Test**: Run the tool with various input scenarios
2. **Validate**: Ensure Wayback is not called when discovery is OFF
3. **Monitor**: Check performance improvements on large subdomain lists
4. **Document**: Update user documentation with new flag
5. **Feedback**: Gather user feedback on the new behavior

---

## Date Completed

December 15, 2025
