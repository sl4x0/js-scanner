# Linux VPS Deployment Guide

## ✅ Platform Requirements

**This tool is designed for Linux VPS deployment ONLY.**

- ✅ Ubuntu 20.04+, Debian 11+, CentOS 8+
- ✅ Python 3.8+
- ✅ 2GB+ RAM recommended (4GB for large targets)
- ✅ 10GB+ free disk space

❌ **NOT compatible with Windows** (uses Linux-only `fcntl` for file locking)  
❌ **WSL not recommended** (use native Linux VPS instead)

---

## Quick VPS Setup (5 minutes)

### 1. Connect to Your VPS

```bash
ssh user@your-vps-ip
```

### 2. Run Automated Setup

```bash
# Clone or upload the project
cd /home/youruser/js-scanner

# Make setup script executable
chmod +x setup.sh

# Run setup (installs everything automatically)
./setup.sh
```

The script will:

- Check system resources (RAM, disk space)
- Install Python 3, pip, and dependencies
- Install Playwright browsers
- Install TruffleHog
- Create directory structure
- Set up virtual environment

### 3. Configure Discord Webhook

```bash
# Copy template
cp config.yaml.example config.yaml

# Edit with your webhook
nano config.yaml

# Replace: YOUR_DISCORD_WEBHOOK_URL_HERE
# With your actual webhook from Discord
```

**Get Discord Webhook:**

1. Go to your Discord server
2. Server Settings → Integrations → Webhooks
3. Create New Webhook
4. Copy Webhook URL

### 4. Test Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Test with small target
python -m jsscanner -t example.com --no-recursion

# Check results
ls -la results/example.com/
```

---

## VPS Performance Tuning

### For 2GB RAM VPS

Edit `config.yaml`:

```yaml
threads: 10
playwright:
  max_concurrent: 2
  restart_after: 50
```

### For 4GB RAM VPS (Recommended)

```yaml
threads: 25
playwright:
  max_concurrent: 3
  restart_after: 100
```

### For 8GB+ RAM VPS

```yaml
threads: 50
playwright:
  max_concurrent: 5
  restart_after: 150
```

---

## 24/7 Continuous Scanning

### Using systemd (Recommended)

```bash
# Create service file
sudo nano /etc/systemd/system/jsscanner.service
```

Add:

```ini
[Unit]
Description=JS Scanner for target.com
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/js-scanner
Environment="PATH=/home/youruser/js-scanner/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/youruser/js-scanner/venv/bin/python -m jsscanner -t target.com
Restart=always
RestartSec=3600  # Restart every hour

# Resource limits
MemoryLimit=2G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable jsscanner
sudo systemctl start jsscanner

# Check status
sudo systemctl status jsscanner

# View logs
sudo journalctl -u jsscanner -f
```

---

## Security Best Practices

### 1. Protect Your Webhook

```bash
# Never commit config.yaml to Git
git rm --cached config.yaml  # If already committed
git add .gitignore
git commit -m "Remove webhook from tracking"

# Regenerate your Discord webhook if exposed
```

### 2. Use Environment Variables (Optional)

```bash
# Create .env file
cat > .env << EOF
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK
TRUFFLEHOG_PATH=/usr/local/bin/trufflehog
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

### 3. Set Proper Permissions

```bash
# Restrict access to results
chmod 700 results/
chmod 600 config.yaml

# Only your user can read
ls -la config.yaml
# Should show: -rw------- 1 youruser youruser
```

---

## Monitoring & Maintenance

### Real-time Monitoring

```bash
# Monitor logs
tail -f results/target.com/logs/scan.log

# Monitor system resources
htop  # Install: sudo apt install htop

# Monitor disk usage
df -h
du -sh results/
```

### Check Scan Progress

```bash
# View metadata
cat results/target.com/metadata.json | jq

# Count secrets found
cat results/target.com/secrets.json | jq length

# Count files scanned
ls results/target.com/files/minified/ | wc -l
```

### Automated Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
tar -czf backups/results-$DATE.tar.gz results/
# Keep only last 7 backups
ls -t backups/results-*.tar.gz | tail -n +8 | xargs rm -f
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/youruser/js-scanner/backup.sh
```

---

## Troubleshooting

### Out of Memory

```bash
# Check memory usage
free -h

# Add swap if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Clean old results
find results/ -type d -mtime +30 -exec rm -rf {} \;  # Delete >30 days old

# Clean Playwright cache
rm -rf /home/youruser/.cache/ms-playwright/
playwright install chromium
```

### TruffleHog Not Found

```bash
# Reinstall TruffleHog
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

# Verify installation
which trufflehog
trufflehog --version

# Update config if path changed
nano config.yaml
# Set: trufflehog_path: "/usr/local/bin/trufflehog"
```

### Playwright Issues

```bash
# Reinstall browsers
source venv/bin/activate
playwright install chromium
playwright install-deps chromium

# If still fails, install system dependencies
sudo apt-get install -y \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
  libxdamage1 libxfixes3 libxrandr2 libgbm1 \
  libpango-1.0-0 libcairo2 libasound2
```

---

## Firewall Configuration

If you need to whitelist IPs:

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow outgoing HTTPS (for fetching JS)
sudo ufw allow out 443/tcp

# Allow DNS
sudo ufw allow out 53

# Enable firewall
sudo ufw enable
```

---

## Performance Benchmarks

**Expected performance on different VPS tiers:**

| VPS Specs      | Files/Hour | RAM Usage | CPU Usage |
| -------------- | ---------- | --------- | --------- |
| 2GB RAM, 1 CPU | ~500       | 1.5GB     | 70%       |
| 4GB RAM, 2 CPU | ~1500      | 2.5GB     | 80%       |
| 8GB RAM, 4 CPU | ~3000      | 4GB       | 85%       |

_Note: Actual performance varies based on file sizes and network speed_

---

## Why Linux Only?

The tool uses `fcntl` (POSIX file locking) which is:

- ✅ Native to Linux/Unix
- ✅ Highly reliable for concurrent file access
- ✅ No external dependencies needed
- ❌ Not available on Windows

For production bug bounty work, Linux VPS is recommended for:

- Better stability
- Lower cost
- 24/7 availability
- Superior memory management

---

## Next Steps

1. ✅ Complete VPS setup with `./setup.sh`
2. ✅ Configure Discord webhook in `config.yaml`
3. ✅ Test with small target
4. ✅ Set up systemd service for 24/7 scanning
5. ✅ Configure backups
6. ✅ Monitor and optimize based on your VPS specs

**Your Linux VPS is now ready for bug bounty hunting! 🎯**
