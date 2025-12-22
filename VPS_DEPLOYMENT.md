# 🚀 VPS Deployment Guide - JS-Scanner Elite Edition v3.1

## 🎯 Latest Updates (December 2025)

**Elite Notification Framework v3.1:**
- ✅ Domain context in all Discord notifications
- ✅ Fixed "0 secrets found" bug (now shows verified + unverified counts)
- ✅ Complete Discord queue processing (100% message delivery)
- ✅ Domain-organized batching for efficient manual triaging

## 📋 Quick Start (Existing Installation)

If you already have js-scanner on your VPS, update to the latest version:

```bash
cd ~/js-scanner  # or wherever your installation is
git pull origin main
source venv/bin/activate  # or 'venv\Scripts\activate' on Windows

# No new dependencies for v3.1 - just code fixes
python -m jsscanner --version  # Verify update
```

---

## 🆕 Fresh Installation (New VPS)

### Step 1: System Requirements

**Minimum Specs:**

- OS: Ubuntu 20.04+ / Debian 11+ / RHEL 8+
- RAM: 2GB minimum, 4GB recommended
- CPU: 2 cores minimum
- Disk: 10GB free space

**Required Software:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install Playwright dependencies
sudo apt install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# Install Git
sudo apt install -y git
```

---

### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/sl4x0/js-scanner.git
cd js-scanner
```

---

### Step 3: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install tree-sitter with correct versions
pip install tree-sitter==0.21.3 tree-sitter-javascript==0.21.4

# Install Playwright browsers
playwright install chromium
```

---

### Step 4: Configuration

```bash
# Copy config template
cp config.yaml.example config.yaml

# Edit configuration
nano config.yaml
```

**Critical Settings to Update:**

```yaml
# Discord Webhook (REQUIRED for notifications)
discord_webhook: "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"

# Concurrency (Adjust based on VPS specs)
threads: 50 # 2GB RAM: 20, 4GB RAM: 50, 8GB+ RAM: 100

# Recursion Settings
recursion:
  enabled: true
  max_depth: 2 # Increase to 3 for deeper scans (more time)
  validate_with_head: true

# Resource Limits (Prevent OOM on small VPS)
max_file_size_mb: 10 # Skip files larger than 10MB
semaphore_limit: 50 # Max concurrent operations
```

---

### Step 5: Install External Tools (Optional but Recommended)

#### TruffleHog (Secret Scanning)

```bash
# Download TruffleHog
wget https://github.com/trufflesecurity/trufflehog/releases/download/v3.63.2/trufflehog_3.63.2_linux_amd64.tar.gz
tar -xzf trufflehog_3.63.2_linux_amd64.tar.gz
sudo mv trufflehog /usr/local/bin/
rm trufflehog_3.63.2_linux_amd64.tar.gz

# Verify installation
trufflehog --version
```

#### SubJS (Passive Discovery - Go Required)

```bash
# Install Go (if not installed)
sudo apt install -y golang-go

# Install SubJS
go install -v github.com/lc/subjs@latest

# Add to PATH (add to ~/.bashrc)
export PATH=$PATH:~/go/bin
source ~/.bashrc

# Verify installation
subjs -h
```

#### webcrack (Bundle Unpacking - Node.js Required)

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install webcrack globally (may fail on some systems - optional)
sudo npm install -g webcrack

# Verify installation
webcrack --version
```

---

## 🎯 Verify Installation

```bash
# Test scan with built-in test server
python test_server.py &
sleep 3
python -m jsscanner -t install_test -u "http://localhost:9999/" --force --no-beautify
kill %1  # Stop test server

# Check results
ls -lh results/install_test/unique_js/
cat results/install_test/file_manifest.json
```

**Expected Output:**

- ✅ 4+ JS files downloaded to `unique_js/`
- ✅ File manifest with hash→URL mappings
- ✅ Tree-sitter initialized (v0.21.3)
- ✅ Noise filter loaded (41 CDNs, 62 patterns)

---

## 🔧 Production Deployment

### Option 1: Systemd Service (Recommended)

Create `/etc/systemd/system/js-scanner.service`:

```ini
[Unit]
Description=JS-Scanner Bug Bounty Automation
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/js-scanner
Environment="PATH=/home/yourusername/js-scanner/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/yourusername/js-scanner/venv/bin/python -m jsscanner -i /home/yourusername/targets.txt --threads 50 --config /home/yourusername/js-scanner/config.yaml
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable js-scanner
sudo systemctl start js-scanner
sudo systemctl status js-scanner

# View logs
sudo journalctl -u js-scanner -f
```

---

### Option 2: Screen/Tmux Session

```bash
# Using screen
screen -S js-scanner
cd ~/js-scanner
source venv/bin/activate
python -m jsscanner -i targets.txt --threads 50 --config config.yaml
# Press Ctrl+A, then D to detach

# Reattach later
screen -r js-scanner

# Using tmux
tmux new -s js-scanner
cd ~/js-scanner
source venv/bin/activate
python -m jsscanner -i targets.txt --threads 50 --config config.yaml
# Press Ctrl+B, then D to detach

# Reattach later
tmux attach -t js-scanner
```

---

### Option 3: Cron Job (Scheduled Scans)

```bash
# Edit crontab
crontab -e

# Add line (scan every 6 hours)
0 */6 * * * cd /home/yourusername/js-scanner && /home/yourusername/js-scanner/venv/bin/python -m jsscanner -i /home/yourusername/targets.txt --threads 50 --config /home/yourusername/js-scanner/config.yaml --force >> /home/yourusername/js-scanner/cron.log 2>&1
```

---

## 📊 Monitoring & Maintenance

### Disk Space Management

```bash
# Check disk usage
du -sh ~/js-scanner/results/*

# Clean old results (keep last 7 days)
find ~/js-scanner/results -type d -mtime +7 -exec rm -rf {} +

# Set up automatic cleanup (add to crontab)
0 2 * * * find /home/yourusername/js-scanner/results -type d -mtime +7 -exec rm -rf {} +
```

### Memory Monitoring

```bash
# Watch memory usage during scan
htop  # or top

# If OOM errors occur, reduce threads in config.yaml:
threads: 20  # Lower value for 2GB RAM VPS
```

### Log Rotation

Create `/etc/logrotate.d/js-scanner`:

```
/home/yourusername/js-scanner/results/*/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## 🚨 Troubleshooting

### Issue: Tree-sitter initialization failed

**Solution:**

```bash
pip uninstall tree-sitter tree-sitter-javascript -y
pip install tree-sitter==0.21.3 tree-sitter-javascript==0.21.4
```

### Issue: Playwright browser not found

**Solution:**

```bash
source venv/bin/activate
playwright install chromium
playwright install-deps
```

### Issue: Permission denied on results folder

**Solution:**

```bash
chmod -R 755 ~/js-scanner/results
chown -R $(whoami):$(whoami) ~/js-scanner/results
```

### Issue: Out of Memory (OOM)

**Solution:**

```bash
# Edit config.yaml
threads: 10           # Reduce from 50
semaphore_limit: 10   # Reduce from 50

# Add swap space (2GB VPS)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🎯 VPS Provider Recommendations

### Budget-Friendly (Bug Bounty):

- **DigitalOcean Droplet:** $12/month (2GB RAM, 2 vCPUs, 50GB SSD)
- **Linode Nanode:** $12/month (2GB RAM, 1 vCPU, 50GB SSD)
- **Hetzner Cloud CX21:** €5.83/month (4GB RAM, 2 vCPUs, 40GB SSD)

### High-Performance (Pro Tier):

- **DigitalOcean Droplet:** $24/month (4GB RAM, 2 vCPUs, 80GB SSD)
- **AWS EC2 t3.medium:** ~$30/month (4GB RAM, 2 vCPUs, 50GB EBS)
- **Vultr High Frequency:** $24/month (4GB RAM, 2 vCPUs, 128GB SSD)

---

## 📈 Performance Benchmarks

| VPS Specs   | Threads | Domains/Hour | Files/Hour |
| ----------- | ------- | ------------ | ---------- |
| 2GB / 2 CPU | 20      | ~50          | ~500       |
| 4GB / 2 CPU | 50      | ~150         | ~1500      |
| 8GB / 4 CPU | 100     | ~300         | ~3000+     |

---

## ✅ Post-Deployment Checklist

- [ ] Git repository cloned
- [ ] Python venv created and activated
- [ ] All dependencies installed (requirements.txt)
- [ ] Tree-sitter versions correct (0.21.3 / 0.21.4)
- [ ] Playwright browsers installed
- [ ] TruffleHog installed and in PATH
- [ ] config.yaml created with Discord webhook
- [ ] Test scan completed successfully
- [ ] Systemd service or screen session configured
- [ ] Disk space monitoring set up
- [ ] Log rotation configured

---

## 🔗 Useful Commands

```bash
# Quick status check
python -m jsscanner --version

# Test configuration
python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"

# Check tree-sitter installation
python -c "import tree_sitter; print(tree_sitter.__version__)"

# Monitor active scan
tail -f results/*/logs/scan.log

# Kill stuck scan
pkill -f "python -m jsscanner"

# Update to latest version
git pull origin main && pip install -r requirements.txt --upgrade
```

---

## 🎓 Elite Tips

1. **Target List Management:** Keep `targets.txt` with one domain per line
2. **Incremental Scanning:** Remove `--force` flag to skip previously scanned files
3. **Resume After Crash:** Use `--resume` flag to continue from checkpoint
4. **Scope Control:** Use `--no-scope-filter` to include CDN URLs (noisy but comprehensive)
5. **Speed vs Accuracy:** Lower `threads` for accuracy, higher for speed
6. **Discord Alerts:** Test webhook with `curl -X POST <webhook_url> -d '{"content":"Test"}'`
7. **Notification Control:** 
   - Use `--no-discord` for quiet mode (results saved locally only)
   - Use `--discord-verified-only` to reduce noise (only send verified secrets)
   - Adjust `--discord-batch-size` (1-25) to control message grouping
8. **Manual Triaging:** Secrets now include domain context in title for quick filtering

---

## 🔔 Discord Notification Features (v3.1)

**Enhanced Context for Manual Triaging:**
- Domain/host visible in notification title: `🔴 AWS Secret • account.vkplay.ru`
- Dedicated 🎯 Domain field for quick target identification
- Full source file URLs with line numbers for easy debugging
- Organized batching by domain (related secrets grouped together)
- All findings sent to Discord (verified + unverified)

**Notification Control Flags:**
```bash
# Disable Discord notifications (save locally only)
python -m jsscanner -t example.com --subjs --no-discord

# Send only verified secrets to Discord (reduce noise)
python -m jsscanner -t example.com --subjs --discord-verified-only

# Adjust batch size (1-25 secrets per message)
python -m jsscanner -t example.com --subjs --discord-batch-size 10
```

---

## 📞 Support

- **Issues:** https://github.com/sl4x0/js-scanner/issues
- **Docs:** https://github.com/sl4x0/js-scanner/wiki
- **Updates:** `git pull origin main` (weekly recommended)

---

**🎯 Happy Hunting! May your secrets be plentiful and your bounties be fat.**
