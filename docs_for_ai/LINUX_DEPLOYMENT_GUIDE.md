# Cross-Platform Deployment Guide

## Overview
The js-scanner tool is now fully cross-platform compatible, supporting both **Windows** and **Linux** environments. This guide covers deployment procedures for Linux VPS.

---

## ✅ Cross-Platform Features Implemented

### 1. **OS-Aware Binary Detection**
- **File**: [jsscanner/modules/secret_scanner.py](../jsscanner/modules/secret_scanner.py)
- **Feature**: Automatic TruffleHog binary detection
- **Logic**:
  ```
  Priority Order:
  1. Config file path (if specified)
  2. Project root: trufflehog.exe (Windows) or trufflehog (Linux)
  3. System PATH lookup
  ```
- **Configuration**: Set `trufflehog_path: ""` in [config.yaml](../config.yaml) for auto-detection

### 2. **UTF-8 Encoding Everywhere**
All file operations now explicitly use `encoding='utf-8'`:
- [jsscanner/core/state_manager.py](../jsscanner/core/state_manager.py) - JSON state management
- [jsscanner/utils/file_ops.py](../jsscanner/utils/file_ops.py) - File read/write
- [jsscanner/__main__.py](../jsscanner/__main__.py) - Config loading
- [jsscanner/utils/logger.py](../jsscanner/utils/logger.py) - Console output

**Why?** Windows defaults to cp1252 encoding, Linux uses UTF-8. Explicit encoding prevents:
- `UnicodeDecodeError` when reading files with emojis/Unicode
- `UnicodeEncodeError` when writing non-ASCII characters

### 3. **Cross-Platform File Locking**
- **File**: [jsscanner/core/state_manager.py](../jsscanner/core/state_manager.py)
- **Implementation**:
  ```python
  if sys.platform == 'win32':
      import msvcrt  # Windows file locking
  else:
      import fcntl   # Linux file locking
  ```
- **Tested**: Concurrent writes, atomic check-and-set operations
- **Test**: Run `python test/test_linux_compatibility.py`

### 4. **Linux-Optimized Playwright**
- **File**: [jsscanner/modules/fetcher.py](../jsscanner/modules/fetcher.py)
- **VPS-Required Flags**:
  ```python
  '--no-sandbox',              # Required for Docker/VPS
  '--disable-setuid-sandbox',  # Security bypass for headless
  '--disable-dev-shm-usage',   # Prevent /dev/shm crashes
  '--disable-gpu'              # Headless rendering
  ```

---

## 🐧 Linux VPS Deployment

### Prerequisites
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl
```

### Installation Steps

#### 1. Clone Repository
```bash
cd /opt  # or your preferred directory
git clone <your-repo-url> js-scanner
cd js-scanner
```

#### 2. Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux
# OR
.\venv\Scripts\activate   # Windows
```

#### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install Playwright Browsers
```bash
playwright install chromium
playwright install-deps  # Installs system dependencies (Ubuntu/Debian)
```

#### 5. Install TruffleHog
```bash
# Method 1: Official installer (Recommended)
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

# Method 2: Download to project root
cd /opt/js-scanner
wget https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_linux_amd64
chmod +x trufflehog_linux_amd64
mv trufflehog_linux_amd64 trufflehog

# Verify installation
trufflehog --version
```

#### 6. Configure Application
```bash
cp config.yaml.example config.yaml
nano config.yaml  # or vim, vi, etc.
```

**Key Configuration Changes for Linux**:
```yaml
# Leave empty for auto-detection
trufflehog_path: ""

# Adjust threads based on VPS resources
threads: 25  # 2GB RAM
# OR
threads: 50  # 4GB+ RAM

# Discord webhook (CRITICAL: Never commit this!)
discord_webhook: "YOUR_WEBHOOK_URL"
```

#### 7. Test Installation
```bash
python test/test_linux_compatibility.py
```

**Expected Output**:
```
✅ All Linux compatibility tests PASSED!
Results: 4/4 tests passed
```

#### 8. Run First Scan
```bash
python -m jsscanner -u https://example.com
```

---

## 🔧 Troubleshooting

### Issue: `playwright: command not found`
**Solution**:
```bash
source venv/bin/activate  # Ensure venv is activated
playwright install chromium
```

### Issue: Chromium crashes with `Failed to launch browser`
**Solution**: Add Docker/VPS flags (already implemented):
```bash
# Verify flags in fetcher.py
grep -A 10 "launch_args" jsscanner/modules/fetcher.py
```

### Issue: `trufflehog: not found`
**Solution**:
```bash
# Check PATH
which trufflehog

# If not found, install to project root
cd /opt/js-scanner
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b .
chmod +x ./trufflehog
```

### Issue: `UnicodeDecodeError` on Linux
**Solution**: All file operations now use UTF-8 explicitly. If error persists:
```bash
# Set environment variable
export PYTHONIOENCODING=utf-8

# Or add to ~/.bashrc
echo 'export PYTHONIOENCODING=utf-8' >> ~/.bashrc
source ~/.bashrc
```

### Issue: `Permission denied` on file locking
**Solution**:
```bash
# Ensure output directory is writable
chmod 755 output/
chown $USER:$USER output/
```

---

## 🐳 Docker Deployment (Advanced)

### Dockerfile Example
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN playwright install-deps chromium

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN playwright install chromium

# Install TruffleHog
RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

# Run
CMD ["python", "-m", "jsscanner", "-u", "${TARGET_URL}"]
```

### Build and Run
```bash
docker build -t js-scanner .
docker run -v $(pwd)/output:/app/output js-scanner
```

---

## 📊 Performance Tuning

### VPS Resource Guidelines
| RAM  | threads | playwright.max_concurrent | trufflehog_max_concurrent |
|------|---------|---------------------------|---------------------------|
| 2GB  | 10-15   | 2                         | 3                         |
| 4GB  | 25-30   | 3                         | 5                         |
| 8GB+ | 50-100  | 5                         | 10                        |

### Optimize for Low Memory
```yaml
# config.yaml
threads: 10
playwright:
  max_concurrent: 2
  restart_after: 50  # Restart browser more frequently
trufflehog_max_concurrent: 3
```

---

## 🧪 Testing on WSL (Windows Subsystem for Linux)

Before deploying to VPS, test on WSL:

```bash
# Windows Terminal
wsl --install Ubuntu

# Inside WSL
cd /mnt/d/Automation\ Bug\ Bounty/js-scanner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test/test_linux_compatibility.py
```

---

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] TruffleHog binary available (project root or PATH)
- [ ] config.yaml configured with Discord webhook
- [ ] Linux compatibility tests passed (`test_linux_compatibility.py`)
- [ ] File permissions correct (755 for directories, 644 for files)
- [ ] Test scan completed successfully
- [ ] Discord notifications received

---

## 🚀 Systemd Service (Optional)

Run js-scanner as a background service:

```bash
# Create service file
sudo nano /etc/systemd/system/js-scanner.service
```

```ini
[Unit]
Description=JS Scanner Bug Bounty Tool
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/js-scanner
Environment="PATH=/opt/js-scanner/venv/bin"
ExecStart=/opt/js-scanner/venv/bin/python -m jsscanner -u https://target.com
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable js-scanner
sudo systemctl start js-scanner
sudo systemctl status js-scanner
```

---

## 📚 Related Files
- [README.md](../README.md) - Project overview
- [config.yaml.example](../config.yaml.example) - Configuration template
- [requirements.txt](../requirements.txt) - Python dependencies
- [test/test_linux_compatibility.py](../test/test_linux_compatibility.py) - Compatibility tests

---

## 🆘 Support
- **GitHub Issues**: Report bugs or request features
- **Documentation**: See [docs_for_ai/](../docs_for_ai/) for detailed guides
- **Discord**: Get your webhook from Discord Server Settings → Integrations
