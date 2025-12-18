# VPS Testing Guide for JS Scanner v3.2

This guide covers deploying and testing JS Scanner on a VPS (Ubuntu/Debian recommended).

## 📋 Prerequisites

- VPS with Ubuntu 20.04+ or Debian 11+
- At least 2GB RAM (4GB+ recommended for large scans)
- Python 3.9 or higher
- Root or sudo access

## 🚀 Quick Setup (Ubuntu/Debian)

### 1. Connect to VPS

```bash
ssh user@your-vps-ip
```

### 2. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ and essential tools
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Install Playwright dependencies (for headless browser)
sudo apt install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2

# Optional: Install Node.js for webcrack (bundle unpacking)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 3. Clone and Setup JS Scanner

```bash
# Clone repository
git clone https://github.com/sl4x0/js-scanner.git
cd js-scanner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (headless)
playwright install chromium
playwright install-deps chromium

# Optional: Install webcrack for bundle unpacking
npm install -g webcrack
```

### 4. Configure Scanner

```bash
# Copy example config
cp config.yaml.example config.yaml

# Edit config with your settings
nano config.yaml
```

**Key VPS Config Settings:**

```yaml
# Recommended VPS settings
threads: 30  # Lower than local machine (VPS usually has less resources)
timeout: 60  # Higher timeout for slower networks

# Discord webhook for notifications
discord_webhook: "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"
discord_status_enabled: true  # Get notifications on scan progress

# Playwright settings for VPS
playwright:
  headless: true  # MUST be true on VPS (no display)
  max_concurrent: 3  # Keep low to avoid memory issues
  page_timeout: 30000
  restart_after: 50  # Restart browser every 50 pages

# Batch processing (important for VPS)
batch_processing:
  enabled: true
  batch_size: 100  # Process 100 URLs at a time
  cleanup_minified: true  # Save disk space

# Checkpoint system (critical for VPS)
checkpoint:
  enabled: true
  interval: 300  # Save checkpoint every 5 minutes
```

## 🧪 Testing New Features (v3.2)

### Test 1: Config Validation

Create an invalid config to test validation:

```bash
# Create test config with invalid values
cat > test_invalid.yaml << 'EOF'
threads: 999  # Too high
timeout: 1    # Too low
discord_webhook: "http://bad-url.com"  # Wrong format
EOF

# Run scanner with invalid config
python -m jsscanner -t test --config test_invalid.yaml -u https://example.com/app.js
```

**Expected Output:**
```
======================================================================
❌ CONFIGURATION VALIDATION FAILED
======================================================================
❌ Invalid Discord webhook URL
   → Must start with: https://discord.com/api/webhooks/
❌ Invalid Concurrent threads: 999
   → Must be between 1 and 200
❌ Invalid HTTP timeout (seconds): 1
   → Must be between 5 and 300
```

```bash
# Clean up
rm test_invalid.yaml
```

### Test 2: Progress Reporting with ETA

Test the new progress bars and ETA calculation:

```bash
# Create test targets file
cat > test_targets.txt << 'EOF'
https://jquery.com/jquery.min.js
https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js
https://cdnjs.cloudflare.com/ajax/libs/vue/3.3.4/vue.global.prod.js
https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js
https://unpkg.com/react@18/umd/react.production.min.js
EOF

# Run scan and watch progress bars
python -m jsscanner -t progress-test -i test_targets.txt --no-beautify
```

**Expected Output:**
```
📊 Download Files: [████████████████████░░░░░░░░░░] 20/25 (80.0%), ETA: 5s (4.2 items/s) - 18 saved
```

```bash
# Clean up
rm test_targets.txt
rm -rf results/progress-test
```

### Test 3: Browser Cleanup (Thread Safety)

Test that Playwright cleanup doesn't crash on Ctrl+C:

```bash
# Start a long-running scan
python -m jsscanner -t cleanup-test -u https://example.com --subjs

# Press Ctrl+C after 10 seconds
# Should see clean shutdown messages
```

**Expected Output:**
```
⚠️  Shutdown requested (Ctrl+C). Saving data and exiting...
Browser manager closed successfully
Playwright stopped successfully
✅ Graceful shutdown complete
```

### Test 4: Config Change Detection

Test resume with modified config:

```bash
# Run a partial scan
timeout 30 python -m jsscanner -t config-test -i test_targets.txt || true

# Modify config
sed -i 's/threads: 30/threads: 50/' config.yaml

# Try to resume (should warn about config change)
python -m jsscanner -t config-test -i test_targets.txt --resume
```

**Expected Output:**
```
⚠️  WARNING: Configuration has changed since last scan!
   Resuming with modified config may produce inconsistent results.
   Consider starting a fresh scan instead.
   Continuing anyway in 3 seconds... (Ctrl+C to cancel)
```

```bash
# Clean up
rm -rf results/config-test
git checkout config.yaml  # Restore original config
```

### Test 5: Discord Notification Queue Limit

Test that notification queue doesn't overflow:

```bash
# This requires many secrets to trigger queue limit
# For testing, you can monitor the logs during a large scan
python -m jsscanner -t large-scan -i domains.txt --subjs -v 2>&1 | grep "queue"
```

**Expected in Logs (if queue fills):**
```
Discord queue full (1000), dropped 101 messages
```

### Test 6: Rate Limit Recovery

Test Discord rate limit handling (requires hitting rate limits):

```bash
# Monitor Discord notifications during a scan
python -m jsscanner -t rate-test -i large_targets.txt -v 2>&1 | grep "429\|rate limit"
```

**Expected Output (if rate limited):**
```
Discord rate limited (429), retry after 2.5s (attempt 1/3)
```

## 🏃 Running Production Scans on VPS

### Basic Scan

```bash
# Activate venv
source venv/bin/activate

# Run scan
python -m jsscanner -t myproject -u https://example.com --subjs
```

### Large-Scale Scan (Multiple Domains)

```bash
# Create domains file
cat > targets.txt << 'EOF'
https://example1.com
https://example2.com
https://example3.com
EOF

# Run with batching and checkpoints
python -m jsscanner -t bulk-scan -i targets.txt --subjs-only --no-beautify
```

### Resume Interrupted Scan

```bash
# If scan was interrupted (Ctrl+C, network issue, etc.)
python -m jsscanner -t myproject -i targets.txt --resume
```

### Background Scan (Long-Running)

```bash
# Using screen (recommended for VPS)
screen -S jsscan
source venv/bin/activate
python -m jsscanner -t myproject -i targets.txt --subjs

# Detach: Ctrl+A, then D
# Reattach later: screen -r jsscan
```

**Alternative: tmux**

```bash
tmux new -s jsscan
source venv/bin/activate
python -m jsscanner -t myproject -i targets.txt --subjs

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t jsscan
```

**Alternative: nohup**

```bash
nohup python -m jsscanner -t myproject -i targets.txt --subjs > scan.log 2>&1 &

# Check progress
tail -f scan.log

# Check if still running
ps aux | grep jsscanner
```

## 📊 Monitoring on VPS

### Check Resource Usage

```bash
# Real-time monitoring
htop

# Memory usage
free -h

# Disk usage
df -h
du -sh results/*
```

### View Live Logs

```bash
# Follow scan logs
tail -f results/myproject/logs/scan.log

# Search for errors
grep "ERROR\|WARNING" results/myproject/logs/scan.log

# Check progress
grep "📊\|Phase\|Progress" results/myproject/logs/scan.log
```

### Check Results

```bash
# Count secrets found
jq length results/myproject/secrets.json

# List secret types
jq 'group_by(.detector_type) | map({type: .[0].detector_type, count: length})' results/myproject/secrets.json

# Count extracted endpoints
wc -l results/myproject/extracts/endpoints.txt

# View domain-specific results
ls -lah results/myproject/extracts/*/
```

## 🔧 Troubleshooting VPS Issues

### Playwright Browser Fails

```bash
# Reinstall Playwright with dependencies
playwright install --with-deps chromium

# Check if running headless
grep "headless: true" config.yaml
```

### Out of Memory

```bash
# Reduce concurrency in config.yaml
threads: 20  # Lower value
playwright:
  max_concurrent: 2  # Lower value

# Enable swap (if not already)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Disk Space Issues

```bash
# Enable cleanup in config.yaml
batch_processing:
  cleanup_minified: true

# Clean old results
rm -rf results/old-project

# Check largest files
du -ah results/ | sort -rh | head -20
```

### Network Timeouts

```bash
# Increase timeout in config.yaml
timeout: 120  # 2 minutes

retry:
  max_attempts: 5  # More retries
  initial_delay: 3
```

## 🎯 Performance Tuning for VPS

### For Small VPS (2GB RAM)

```yaml
threads: 20
playwright:
  max_concurrent: 2
batch_processing:
  batch_size: 50
  cleanup_minified: true
```

### For Medium VPS (4GB RAM)

```yaml
threads: 40
playwright:
  max_concurrent: 3
batch_processing:
  batch_size: 100
  cleanup_minified: true
```

### For Large VPS (8GB+ RAM)

```yaml
threads: 80
playwright:
  max_concurrent: 5
batch_processing:
  batch_size: 200
  cleanup_minified: false  # Keep files for analysis
```

## 📦 Backup Results

```bash
# Compress results for download
tar -czf results_backup_$(date +%Y%m%d).tar.gz results/

# Download to local machine (run on local)
scp user@vps-ip:~/js-scanner/results_backup_*.tar.gz ./

# Or use rsync for incremental backup
rsync -avz --progress user@vps-ip:~/js-scanner/results/ ./local_results/
```

## 🔒 Security Best Practices

1. **Never commit config.yaml** (contains Discord webhook)
2. **Use environment variables** for sensitive data:
   ```bash
   export DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
   # Modify config to read from env
   ```
3. **Restrict file permissions**:
   ```bash
   chmod 600 config.yaml
   chmod 700 results/
   ```
4. **Rotate logs** to prevent disk overflow:
   ```bash
   # Logs auto-rotate at 10MB (built-in)
   # But monitor disk space
   ```

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python 3.9+ installed: `python3 --version`
- [ ] Dependencies installed: `pip list | grep aiohttp`
- [ ] Playwright works: `playwright install chromium`
- [ ] Config valid: `python -m jsscanner --help`
- [ ] Test scan runs: `python -m jsscanner -t test -u https://example.com/app.js`
- [ ] Discord notifications work (check webhook)
- [ ] Resume works: `python -m jsscanner -t test --resume`
- [ ] Progress bars display correctly
- [ ] Graceful shutdown works (Ctrl+C)

## 📞 Getting Help

If you encounter issues:

1. Check logs: `cat results/myproject/logs/scan.log`
2. Run in verbose mode: `-v` flag
3. Test with minimal config
4. Check GitHub issues: https://github.com/sl4x0/js-scanner/issues

## 🎉 Success!

You're now ready to run JS Scanner on your VPS with all v3.2 improvements!

**Next Steps:**
- Run a test scan
- Monitor resource usage
- Set up automated scans with cron
- Configure Discord notifications
- Enjoy hunting! 🎯
