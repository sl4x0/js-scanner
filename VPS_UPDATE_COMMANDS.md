# 🔧 VPS Update Commands - Fix All Errors

## Issue Summary
Your VPS logs show errors that have been fixed in the latest commits:
1. ✅ `SubJSFetcher.fetch_batch()` - Added in commit 4e98689
2. ✅ `all_discovered_urls` undefined - Fixed in commit f10968b
3. ℹ️  ERROR logs appear in both files by design (scan.log has ALL logs, errors.log has WARNINGS+ only)

## 📥 Pull Latest Fixes

Run these commands on your VPS:

```bash
cd ~/js-scanner

# Pull all latest fixes
git pull origin main

# Verify you have the latest commit
git log --oneline -3
# Should show:
# f10968b fix: initialize all_discovered_urls in recursive discovery
# 4e98689 some configs
# 3bc5442 config: Hunter-Architect v3.5 - uvloop optimized configuration

# Check SubJS has fetch_batch method
grep -n "async def fetch_batch" jsscanner/modules/subjs_fetcher.py
# Should return: 108:    async def fetch_batch(self, domains: List[str]...

# Check all_discovered_urls is initialized
grep -n "all_discovered_urls = set()" jsscanner/core/engine.py
# Should return: 2159:        all_discovered_urls = set()  # Track all discovered URLs...
```

## 🧪 Test the Fixes

```bash
# Test 1: Verify imports work
python3 -c "from jsscanner.modules.subjs_fetcher import SubJSFetcher; print('✅ SubJS imports OK')"

# Test 2: Quick scan to verify no errors
python3 -m jsscanner -t example.com --threads 10 --no-playwright

# Test 3: Full SubJS test
python3 -m jsscanner -t hackerone.com --subjs-only --threads 50 --no-beautify

# Monitor for errors
tail -f logs/errors.log
# Should NOT see:
# - 'SubJSFetcher' object has no attribute 'fetch_batch'
# - name 'all_discovered_urls' is not defined
```

## 📊 Expected Log Behavior (This is Normal)

**scan.log** = Complete audit trail (DEBUG + INFO + WARNING + ERROR)
- Shows everything that happens
- Used for debugging and forensics

**errors.log** = Error-only view (WARNING + ERROR only)
- Shows only problems
- Quick way to spot issues

**Why errors appear in scan.log:**
- scan.log captures ALL log levels (DEBUG+)
- errors.log captures only WARNING+
- This is intentional - scan.log shows full context around errors

## ✅ Verification Checklist

After pulling and testing, verify:
- [ ] `git log` shows commit f10968b
- [ ] `grep fetch_batch` finds the method in subjs_fetcher.py
- [ ] `grep all_discovered_urls` finds the initialization in engine.py
- [ ] Test scan completes without those two specific errors
- [ ] logs/errors.log only shows WARNING+ (no DEBUG/INFO spam)

## 🚀 Performance Notes

With the latest updates, you now have:
- uvloop for 2-4x I/O speed (Linux only)
- TaskGroup for better crash handling
- Optimized config (threads: 100, download_threads: 250)
- Fixed SubJS batch processing
- Fixed recursive discovery

All systems operational! 🦅
