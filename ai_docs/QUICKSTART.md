# JS Scanner - Quick Start Guide

## Installation (5 minutes)

### Linux/macOS

```bash
# 1. Run automated setup
chmod +x setup.sh
./setup.sh

# 2. Configure Discord webhook
nano config.yaml
# Edit: discord_webhook: "https://discord.com/api/webhooks/YOUR_WEBHOOK"

# 3. Test installation
source venv/bin/activate
python -m jsscanner --help
```

### Windows (WSL Required)

```powershell
# Install WSL first
wsl --install

# Then follow Linux steps inside WSL
```

---

## First Scan (1 minute)

```bash
# Activate environment
source venv/bin/activate

# Run your first scan
python -m jsscanner -t example.com

# Results will be in: results/example.com/
```

---

## Common Use Cases

### 1. Scan a Specific Target

```bash
# Full scan with Wayback + Live + Recursion
python -m jsscanner -t target.com

# Skip Wayback (faster)
python -m jsscanner -t target.com --no-wayback

# Skip Live site
python -m jsscanner -t target.com --no-live

# Disable recursion
python -m jsscanner -t target.com --no-recursion
```

### 2. Scan from URL List

```bash
# Create URLs file
cat > urls.txt << EOF
https://target.com/app.js
https://target.com/bundle.js
https://cdn.target.com/main.js
EOF

# Scan from file
python -m jsscanner -t target.com -i urls.txt
```

### 3. Scan Specific URLs

```bash
python -m jsscanner -t target.com \
  -u https://target.com/app.js https://target.com/main.js
```

### 4. Custom Configuration

```bash
# Use different config
python -m jsscanner -t target.com --config prod-config.yaml

# Override thread count
python -m jsscanner -t target.com --threads 100
```

---

## Monitoring Results

### Real-time Logs

```bash
# Watch scan progress
tail -f results/target.com/logs/scan.log
```

### Check Findings

```bash
TARGET="target.com"

# View secrets found
cat results/$TARGET/secrets.json | jq

# View endpoints
cat results/$TARGET/extracts/endpoints.txt

# View parameters
cat results/$TARGET/extracts/params.txt

# View statistics
cat results/$TARGET/metadata.json | jq
```

### Discord Alerts

Verified secrets are sent to Discord in real-time:
- 🚨 **Red** = Verified secret
- 🟧 **Orange** = Unverified secret
- ✅ **Green** = Scan complete

---

## Performance Tuning

### For Large Targets (1000+ JS files)

```yaml
# Edit config.yaml
threads: 50              # Increase parallelism
playwright:
  max_concurrent: 5      # More concurrent browsers
  restart_after: 50      # Restart more frequently
wayback:
  max_results: 50000     # Get more historical files
```

### For VPS with Limited RAM (2GB)

```yaml
# Edit config.yaml
threads: 10              # Reduce parallelism
playwright:
  max_concurrent: 2      # Fewer concurrent browsers
  restart_after: 25      # Restart more frequently
```

---

## 24/7 Monitoring (VPS)

### Using systemd (Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/jsscanner.service
```

```ini
[Unit]
Description=JS Scanner for target.com
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/js-scanner
ExecStart=/home/youruser/js-scanner/venv/bin/python -m jsscanner -t target.com
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable jsscanner
sudo systemctl start jsscanner

# Check status
sudo systemctl status jsscanner

# View logs
sudo journalctl -u jsscanner -f
```

---

## Troubleshooting

### "TruffleHog not found"

```bash
# Install TruffleHog
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

# Update config.yaml with path
which trufflehog  # Copy this path
nano config.yaml  # Update trufflehog_path
```

### "Playwright browser not found"

```bash
# Reinstall browsers
source venv/bin/activate
playwright install chromium
playwright install-deps
```

### "Discord webhook not working"

```bash
# Test webhook manually
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"Test"}' \
  YOUR_WEBHOOK_URL

# Check rate limiting (30 msg/min max)
# Wait 2 minutes and try again
```

### "Out of memory"

```bash
# Reduce concurrency in config.yaml
playwright:
  max_concurrent: 2
  restart_after: 25
threads: 10

# Or add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Best Practices

### 1. Start Small

```bash
# Test with a small target first
python -m jsscanner -t small-site.com --no-recursion
```

### 2. Monitor Resource Usage

```bash
# Watch memory
watch -n 1 'free -h'

# Watch processes
htop
```

### 3. Regular Backups

```bash
# Backup results
tar -czf results-backup-$(date +%Y%m%d).tar.gz results/

# Backup to remote
rsync -avz results/ user@backup-server:/backups/js-scanner/
```

### 4. Review Findings

```bash
# Check for new endpoints
diff <(sort results/target.com/extracts/endpoints.txt) \
     <(sort previous-scan/endpoints.txt)

# Check for new secrets
diff results/target.com/secrets.json previous-scan/secrets.json
```

---

## Quick Reference

### CLI Options

```
-t, --target        Target domain (required)
-i, --input         Input file with URLs
-u, --urls          Specific URLs to scan
--config           Custom config file
--no-wayback       Skip Wayback Machine
--no-live          Skip live site
--no-recursion     Disable recursive crawling
--threads          Override thread count
-v, --verbose      Enable verbose output
```

### Config File Locations

```
config.yaml              # Default config
results/                 # All scan results
results/{target}/        # Target-specific results
venv/                    # Python virtual environment
logs/                    # Global logs
cache/                   # Playwright cache
```

### Important Files

```
results/{target}/secrets.json      # Verified secrets found
results/{target}/metadata.json     # Scan statistics
results/{target}/logs/scan.log     # Detailed logs
results/{target}/extracts/         # Extracted data
```

---

## Getting Help

### Check Logs

```bash
# Scan logs
cat results/target.com/logs/scan.log

# Errors only
grep ERROR results/target.com/logs/scan.log
```

### Verbose Mode

```bash
# Run with verbose output
python -m jsscanner -t target.com -v
```

### Test Components

```bash
# Run test suite
python -c "
import asyncio
from jsscanner.modules.fetcher import Fetcher
# ... test code ...
"
```

---

## Next Steps

1. ✅ Complete installation
2. ✅ Configure Discord webhook
3. ✅ Run test scan on small target
4. ✅ Review results
5. ✅ Set up 24/7 monitoring (optional)
6. ✅ Configure for your VPS resources
7. ✅ Start hunting! 🎯

---

**Happy hunting! Remember to only scan targets you have permission to test.** 🔒
