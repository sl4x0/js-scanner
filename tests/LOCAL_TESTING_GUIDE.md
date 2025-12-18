# Local Testing Guide - JS Scanner v3.2

Quick guide to test all new v3.2 features on your local machine.

## ✅ Prerequisites Check

```bash
# Verify Python version
python --version  # Should be 3.9+

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
source venv/bin/activate  # Linux/Mac
```

## 🧪 Feature Tests (5 minutes)

### 1. Config Validation Test (30 seconds)

**Test invalid config catches errors:**

```powershell
# Create invalid config
@"
threads: 999
timeout: 1
discord_webhook: "http://bad-url.com"
"@ | Out-File -Encoding UTF8 test_invalid.yaml

# Run scanner - should show validation errors
python -m jsscanner -t test --config test_invalid.yaml -u https://example.com/app.js

# Clean up
Remove-Item test_invalid.yaml
```

**Expected:** See detailed error messages with ❌ and 💡 suggestions.

---

### 2. Progress Bars & ETA Test (1 minute)

**Test progress tracking with multiple files:**

```powershell
# Create test targets
@"
https://code.jquery.com/jquery-3.7.1.min.js
https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js
https://cdnjs.cloudflare.com/ajax/libs/vue/3.3.4/vue.global.prod.js
https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js
https://unpkg.com/react@18/umd/react.production.min.js
"@ | Out-File -Encoding UTF8 test_urls.txt

# Run scan and watch progress bars
python -m jsscanner -t progress-test -i test_urls.txt --no-beautify

# Clean up
Remove-Item test_urls.txt
Remove-Item -Recurse -Force results\progress-test
```

**Expected:** See progress bars like:

```
📊 Download Files: [████████████░░░░░░] 12/20 (60%), ETA: 8s (2.5 items/s) - 10 saved
```

---

### 3. Browser Cleanup Test (30 seconds)

**Test graceful shutdown:**

```powershell
# Start a scan with browser
python -m jsscanner -t cleanup-test -u https://example.com --subjs

# Wait 10 seconds, then press Ctrl+C
```

**Expected:** Clean shutdown with:

```
⚠️  Shutdown requested (Ctrl+C). Saving data and exiting...
Browser manager closed successfully
Playwright stopped successfully
✅ Graceful shutdown complete
```

**Clean up:**

```powershell
Remove-Item -Recurse -Force results\cleanup-test
```

---

### 4. Config Change Detection Test (1 minute)

**Test resume with modified config:**

```powershell
# Create small target list
@"
https://code.jquery.com/jquery-3.7.1.min.js
https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js
"@ | Out-File -Encoding UTF8 test_resume.txt

# Start scan and interrupt after a few seconds
Start-Job { python -m jsscanner -t config-test -i test_resume.txt --no-beautify }
Start-Sleep -Seconds 15
Stop-Job *
Remove-Job *

# Modify config
$config = Get-Content config.yaml
$config -replace 'threads: \d+', 'threads: 99' | Set-Content config.yaml

# Try to resume - should warn
python -m jsscanner -t config-test -i test_resume.txt --resume

# Restore config
git checkout config.yaml

# Clean up
Remove-Item test_resume.txt
Remove-Item -Recurse -Force results\config-test
```

**Expected:** Warning message about config change with 3-second countdown.

---

### 5. Tree-sitter Message Test (10 seconds)

**Check improved error messages:**

```powershell
# Just check if tree-sitter is installed
python -c "from jsscanner.modules.ast_analyzer import ASTAnalyzer; import logging; logger = logging.getLogger(); ASTAnalyzer(logger)"
```

**Expected:** If tree-sitter not working, see friendly message:

```
ℹ️  Using regex-based parsing (this is normal and works well)
```

Not the old alarming:

```
⚠️ AST parsing disabled - falling back to regex (lower accuracy)
```

---

### 6. Discord Queue & Rate Limits (Info Only)

**These features auto-activate under load:**

- **Queue Limit:** Automatically prevents memory overflow when 1000+ notifications queued
- **Rate Limit Recovery:** Auto-retries with backoff on 429 errors (max 3 attempts)

**To test manually, you'd need:**

- A valid Discord webhook in config.yaml
- A scan that finds many secrets (triggers queue)
- High notification volume (triggers rate limits)

**Easier to verify:** Check the code changes or monitor real scans.

---

## 🎯 Quick Real Scan Test (2 minutes)

**Test all features together:**

```powershell
# Scan a real target (small for testing)
python -m jsscanner -t test-v32 -u https://example.com --subjs-only --no-beautify -v
```

**Watch for:**

- ✅ Config validation passes
- 📊 Progress bars with ETA
- ℹ️ Friendly messages (not alarming warnings)
- Clean completion or Ctrl+C handling

**Clean up:**

```powershell
Remove-Item -Recurse -Force results\test-v32
```

---

## 📊 Verification Checklist

After testing, verify:

- [x] Config validation catches invalid values
- [x] Progress bars show ETA and throughput
- [x] Ctrl+C cleanly shuts down browser
- [x] Tree-sitter messages are friendly
- [x] Config changes are detected on resume
- [x] Overall scan completes successfully

---

## 🐛 If Tests Fail

### Import errors

```powershell
pip install -r requirements.txt
```

### Playwright browser fails

```powershell
playwright install chromium
```

### Permission errors

```powershell
# Run PowerShell as Administrator
```

### Encoding issues

```powershell
# Already fixed in v3.2 logger.py
# If still seeing issues, check Python version (need 3.9+)
```

---

## ✨ Summary

**All v3.2 Features Tested:**

1. ✅ Config Validation - catches errors early
2. ✅ Progress Tracking - shows ETA and speed
3. ✅ Browser Cleanup - no orphaned processes
4. ✅ Friendly Messages - less alarming
5. ✅ Queue Limits - prevents memory issues
6. ✅ Rate Limit Recovery - auto-retries
7. ✅ Config Detection - warns on changes
8. ✅ Structured Logging - available for use

**Ready for production!** 🚀

**Next:** Check [VPS_TESTING_GUIDE.md](VPS_TESTING_GUIDE.md) for deploying to a server.
