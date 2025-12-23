# Discord Notification Fix - Hash Lookup Issue

## Problem Identified

The Discord notifications were missing critical information (URL, domain, line number) because the manifest lookup was failing.

### Root Cause

The `file_manifest.json` is keyed by **MD5 hash** (e.g., `abc123def456...`), but the code was trying to look up by **filename** (e.g., `abc123def456.js`).

**Manifest Structure:**
```json
{
  "abc123def456789...": {
    "url": "https://www.deputy.com/static/js/main.js",
    "filename": "abc123def456789.js",
    "is_minified": false,
    "timestamp": "2025-12-23T16:26:00Z"
  }
}
```

**Previous Lookup (WRONG):**
```python
filename = "abc123def456789.js"
if filename in file_manifest:  # ❌ Always fails - looking for filename, not hash
    ...
```

**Fixed Lookup (CORRECT):**
```python
filename = "abc123def456789.js"
file_hash = filename.replace('.js', '').replace('.min', '')  # Extract hash
if file_hash in file_manifest:  # ✅ Correct - looking for hash
    ...
```

## Changes Made

### 1. Fixed Hash Extraction in `secrets.py`

**File:** `jsscanner/analysis/secrets.py`

**Function:** `scan_directory()` - Line ~413

**Change:**
- Extract hash from filename before lookup
- Use hash as key instead of filename
- Add fallback metadata when manifest entry not found
- Add logging for debugging

### 2. Improved Manifest Loading

**Function:** `_load_file_manifest()` - Line ~340

**Changes:**
- Dynamic path resolution (works with both `.warehouse/raw_js` and `files/unminified`)
- Walk up directory tree to find manifest
- Add logging for successful load and warnings for missing manifest
- Better error handling

### 3. Added Fallback Metadata

When manifest entry is not found, the code now sets basic metadata:
```python
finding['SourceMetadata'] = {
    'url': '',  # Empty but present
    'file': filename,  # At least show filename
    'line': line_num,  # Line number from TruffleHog
    'domain': 'Unknown'  # Indicates missing info
}
```

## Expected Notification Format (After Fix)

### Before (Missing Info):
```
🟠 Privacy Secret
🔐 Secret Preview: a09a4cd8-a909-41e9-93f3-f03e59...
✓ Status: ⚠️ Unverified
```

### After (Complete Info):
```
🟠 Privacy Secret • www.deputy.com

🎯 Target Domain: www.deputy.com
📄 JavaScript File: https://www.deputy.com/static/js/chunk-vendors.abc123.js
📍 Line Number: 1548
🔐 Secret Preview: a09a4cd8-a909-41e9-93f3-f03e59...

✓ Status: ⚠️ Unverified
📊 Entropy: 3.9
```

## Testing Instructions

### On Linux Server (where scan was run):

1. **Re-run the scan:**
   ```bash
   cd ~/js-scanner
   python -m jsscanner -t www.deputy.com --subjs-only
   ```

2. **Verify manifest exists:**
   ```bash
   ls -la results/www.deputy.com/file_manifest.json
   cat results/www.deputy.com/file_manifest.json | head -n 20
   ```

3. **Check Discord notifications:**
   - Should now show full URL
   - Should show exact line numbers
   - Should show domain prominently

### Debug if Issues Persist:

1. **Check if manifest is being created:**
   ```bash
   # After Phase 2 (Download) completes
   cat results/www.deputy.com/file_manifest.json
   ```

2. **Check logs for manifest loading:**
   ```bash
   grep "manifest" results/www.deputy.com/logs/scan.log
   ```

   Should see:
   ```
   ✅ Loaded file manifest with XXX entries from results/www.deputy.com/file_manifest.json
   ```

3. **Check secrets file structure:**
   ```bash
   cat results/www.deputy.com/findings/secrets/trufflehog_full.json | jq '.secrets[0].SourceMetadata'
   ```

   Should show:
   ```json
   {
     "url": "https://www.deputy.com/static/js/...",
     "file": "abc123def.js",
     "line": 42,
     "domain": "www.deputy.com"
   }
   ```

## Files Modified

1. `jsscanner/analysis/secrets.py`:
   - Fixed hash extraction for manifest lookup
   - Improved manifest loading with path resolution
   - Added fallback metadata
   - Enhanced logging

2. `jsscanner/output/discord.py`:
   - Already fixed in previous update
   - Enhanced embed formatting with domain/URL/line prominently displayed

## Next Steps

1. **Pull latest changes on Linux server:**
   ```bash
   git pull origin main
   ```

2. **Run a new scan** to test the fixes

3. **Verify Discord notifications** contain all required information

4. **If issues persist**, check debug logs for manifest loading errors

---

**Status:** ✅ Fixed - Awaiting test scan on Linux server
**Impact:** Critical - Enables proper triage and validation of secret findings
