# Quick Reference: New Features and Configuration

## New Configuration Options

### TruffleHog Rate Limiting

```yaml
# Limit concurrent TruffleHog processes to prevent system overload
trufflehog_max_concurrent: 5 # Default: 5
```

**What it does:** Prevents too many TruffleHog processes from running simultaneously, which can cause system overload on large scans.

**Recommended values:**

- Low-end systems (2-4GB RAM): 2-3
- Mid-range systems (8GB RAM): 5
- High-end systems (16GB+ RAM): 10

---

### Discord Status Notifications

```yaml
# Control whether status notifications are sent (start/complete)
discord_status_enabled: false # Default: false
```

**What it does:** When `false`, only sends secret alerts to Discord. When `true`, also sends scan start/complete notifications.

---

### Configurable Timeouts

```yaml
timeouts:
  http_request: 30 # HTTP fetch timeout (seconds)
  wayback_request: 120 # Wayback API timeout (seconds)
  playwright_page: 60000 # Playwright page load timeout (milliseconds)
  trufflehog: 300 # TruffleHog scan timeout per file (seconds)
```

**What it does:** Allows customization of timeout values based on your network speed and target characteristics.

**When to adjust:**

- **Slow network:** Increase `http_request` and `wayback_request`
- **Heavy JavaScript sites:** Increase `playwright_page`
- **Large JS files:** Increase `trufflehog`

---

## New Command-Line Features

### Enhanced --version Output

```bash
python -m jsscanner --version
```

**Output example:**

```
JS Scanner v1.0.0

Dependencies:
  Python: 3.11.5
  aiohttp: 3.9.1
  playwright: 1.40.0
  tree-sitter: 0.20.4
  jsbeautifier: 1.14.11
  PyYAML: 6.0.1
```

**What it does:** Shows versions of all key dependencies for troubleshooting compatibility issues.

---

## Automatic Improvements

### TruffleHog Validation (Automatic)

The scanner now validates TruffleHog installation at startup:

- ✅ Checks if TruffleHog binary exists
- ✅ Verifies it's executable
- ✅ Shows version information
- ❌ Fails fast with helpful error messages if not found

**Error example:**

```
❌ TruffleHog not found at: /usr/local/bin/trufflehog
   Install: curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
   Or update 'trufflehog_path' in config.yaml
```

---

### Wayback Machine Warning (Automatic)

When Wayback returns more than 5,000 JavaScript files:

```
⚠️  Wayback returned 12,453 JS files!
   This may take a long time to scan.
   Consider using --no-wayback for faster scanning.
```

**What it does:** Alerts you to potentially very long scans so you can make informed decisions.

---

### URL Validation (Automatic)

Wayback URLs are now validated for:

- ❌ Null bytes (`\x00`)
- ❌ XSS attempts (`<script`, `javascript:`)
- ❌ Excessive length (>2048 chars)
- ❌ Invalid characters (non-ASCII)

**What it does:** Prevents crashes from malformed URLs in Wayback results.

---

### Rate Limit Handling (Automatic)

HTTP 429 and 503 errors now trigger exponential backoff:

- 1st retry: Wait 1 second
- 2nd retry: Wait 2 seconds
- 3rd retry: Wait 4 seconds
- Respects `Retry-After` header if present

**What it does:** Automatically retries rate-limited requests without failing the entire scan.

---

### Browser Memory Leak Prevention (Automatic)

Browser now restarts more cleanly:

- Waits 1 second after close for cleanup
- Additional Chromium flags to prevent memory leaks
- Debug logging when browser restarts

**What it does:** Prevents memory accumulation during long scans with many pages.

---

### AST Memory Cleanup (Automatic)

Tree-sitter AST objects are now explicitly freed:

- Validates parsed tree structure
- Deletes tree objects after use
- Prevents memory leaks with large JS files

**What it does:** Reduces memory usage when analyzing large JavaScript files.

---

### Beautifier Timeout (Automatic)

JavaScript beautification now has a 30-second timeout:

- Falls back to original content if timeout occurs
- Prevents hanging on extremely large minified files

**What it does:** Prevents the scanner from hanging indefinitely on massive minified files.

---

### Log Rotation (Automatic)

Log files now rotate automatically:

- Maximum size: 10MB per log file
- Keeps 5 backup files
- Old backups are automatically deleted

**What it does:** Prevents log files from growing unbounded and filling disk space.

**Files created:**

```
scan.log       # Current log
scan.log.1     # Previous log
scan.log.2     # 2 logs ago
scan.log.3     # 3 logs ago
scan.log.4     # 4 logs ago
scan.log.5     # 5 logs ago (deleted when new backup is created)
```

---

### Discord Timeout (Automatic)

Discord webhooks now have a 10-second timeout:

- Prevents hanging if Discord is down
- Logs timeout errors

**What it does:** Prevents the entire scan from hanging if Discord API is unavailable.

---

## Troubleshooting

### "TruffleHog not found" Error

**Solution:** Install TruffleHog:

```bash
# Linux/macOS
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

# Or specify custom path in config.yaml
trufflehog_path: "/custom/path/to/trufflehog"
```

### Scan Too Slow with Wayback

**Solution:** Use `--no-wayback` flag:

```bash
python -m jsscanner -t example.com -i urls.txt --no-wayback
```

### Rate Limited by Target

**Solution:** Increase backoff delay or reduce threads:

```yaml
threads: 10 # Reduce from default 50
```

### Memory Issues During Long Scans

**Solutions:**

1. Reduce concurrent TruffleHog processes:

   ```yaml
   trufflehog_max_concurrent: 2
   ```

2. Reduce browser concurrency:

   ```yaml
   playwright:
     max_concurrent: 1
     restart_after: 50
   ```

3. Reduce overall threads:
   ```yaml
   threads: 10
   ```

### Tree-sitter Version Issues

The scanner now automatically detects tree-sitter version and uses the correct API. If you encounter issues:

1. Check installed version:

   ```bash
   python -m jsscanner --version
   ```

2. Update tree-sitter:
   ```bash
   pip install --upgrade tree-sitter tree-sitter-javascript
   ```

---

## Performance Tuning

### High-Performance Configuration (16GB+ RAM, Good Network)

```yaml
threads: 50
trufflehog_max_concurrent: 10
playwright:
  max_concurrent: 5
  restart_after: 200
timeouts:
  http_request: 30
  wayback_request: 120
```

### Low-Resource Configuration (4GB RAM, Slow Network)

```yaml
threads: 10
trufflehog_max_concurrent: 2
playwright:
  max_concurrent: 1
  restart_after: 50
timeouts:
  http_request: 60
  wayback_request: 240
```

### Balanced Configuration (8GB RAM, Average Network)

```yaml
threads: 25
trufflehog_max_concurrent: 5
playwright:
  max_concurrent: 3
  restart_after: 100
timeouts:
  http_request: 30
  wayback_request: 120
```

---

## Migration Guide

### Updating from Previous Version

1. **Backup your current config:**

   ```bash
   cp config.yaml config.yaml.backup
   ```

2. **Add new configuration options:**

   ```yaml
   # Add these to your existing config.yaml
   trufflehog_max_concurrent: 5
   discord_status_enabled: false

   timeouts:
     http_request: 30
     wayback_request: 120
     playwright_page: 60000
     trufflehog: 300
   ```

3. **Test the scanner:**

   ```bash
   python -m jsscanner --version  # Verify dependencies
   python -m jsscanner -t example.com -u https://example.com/test.js  # Test scan
   ```

4. **Monitor first full scan:**
   - Watch for any new warnings or errors
   - Monitor memory usage
   - Check that log rotation is working

---

## Tips and Best Practices

1. **Start with conservative settings** and increase as needed
2. **Monitor system resources** during first scan with new settings
3. **Use `--no-wayback`** for quick scans of known URLs
4. **Check log files** regularly for warnings about rate limits or timeouts
5. **Update dependencies** periodically: `pip install --upgrade -r requirements.txt`
6. **Test TruffleHog** manually to verify it's working: `trufflehog --version`
