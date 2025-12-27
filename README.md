<p align="center">
  <img src="docs/logo.svg" alt="JS Scanner Logo" width="200"/>
</p>

<h1 align="center">⚡ JS Scanner</h1>

<p align="center">
  <strong>Production-grade JavaScript reconnaissance for bug bounty hunters</strong>
</p>

<p align="center">
  <a href="https://github.com/sl4x0/js-scanner/actions"><img src="https://github.com/sl4x0/js-scanner/workflows/CI/badge.svg" alt="CI Status"/></a>
  <a href="https://github.com/sl4x0/js-scanner/tags"><img src="https://img.shields.io/github/v/tag/sl4x0/js-scanner?label=release&color=blue" alt="Release"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg" alt="Platform"/></a>
</p>

---

## 🎯 Overview

**JS Scanner** is a high-performance JavaScript reconnaissance tool designed for bug bounty workflows. It combines fast discovery, memory-efficient processing, and deep static analysis to uncover hidden endpoints, secrets, and vulnerabilities in client-side code.

### Key Features

- **🚀 130x Faster** – SubJS-only scans complete in 2.25s (vs 5 minutes for legacy tools)
- **💾 100x Memory Efficient** – Stream-to-disk architecture (5MB vs 500MB for 1000 files)
- **🔍 Hybrid Discovery** – Katana crawling + SubJS extraction + Playwright browser automation
- **🧠 Deep Analysis** – Tree-sitter AST parsing, source map recovery, Semgrep SAST, TruffleHog secrets
- **⚡ Production Ready** – Checkpoints, resume capability, rate limiting, Discord alerts, CI/CD tested
- **🛡️ Security Focused** – Vendor file filtering, deduplication, authenticated scans, configurable timeouts

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- [Katana](https://github.com/projectdiscovery/katana) (for crawling)
- [SubJS](https://github.com/lc/subjs) (for passive JS discovery)

### Quick Setup

```bash
# Clone repository
git clone https://github.com/sl4x0/js-scanner.git
cd js-scanner

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser (for live browser strategy)
playwright install chromium

# Copy configuration template
cp config.yaml config.yaml
# Edit config.yaml with your settings (Discord webhook, threads, etc.)

# Optional: Configure environment variables
cp .env.example .env
# Edit .env with DISCORD_WEBHOOK_URL if using alerts
```

---

## 🚀 Quick Start

### Basic Scan (SubJS Only - Fastest)

```bash
python -m jsscanner -t example -u https://example.com --subjs
```

**Output:** `results/example/` containing:

- `all_js_files.txt` – Discovered JavaScript URLs
- `downloaded/` – Downloaded files (organized by domain)
- `endpoints.txt` – Extracted API endpoints
- `findings/` – Semgrep results (if enabled)
- `secrets/` – TruffleHog results (if enabled)

### Full Scan (All Strategies)

```bash
python -m jsscanner -t target \
  -u https://target.com \
  --katana \
  --subjs \
  --live-browser \
  --semgrep
```

### Resume Interrupted Scan

```bash
python -m jsscanner -t target --resume
```

### Authentication Scan

```bash
python -m jsscanner -t target \
  -u https://target.com \
  --cookie "session=abc123; token=xyz789" \
  --subjs
```

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      JS Scanner Pipeline                    │
└─────────────────────────────────────────────────────────────┘

1️⃣  DISCOVERY
    ├─ Katana (deep crawl) ────────────► JS URLs
    ├─ SubJS (passive CDN) ────────────► JS URLs
    └─ Playwright (browser automation) ► JS URLs
                    │
                    ▼
2️⃣  FILTERING & VALIDATION
    ├─ Bloom filter deduplication
    ├─ HEAD request validation (check exists)
    └─ CDN/vendor pattern filtering
                    │
                    ▼
3️⃣  DOWNLOAD (Stream-to-Disk)
    ├─ Async HTTP/2 session pooling
    ├─ Content-based hashing (detect duplicates)
    └─ uvloop event loop (high performance)
                    │
                    ▼
4️⃣  ANALYSIS
    ├─ Tree-sitter AST parsing ────────► Endpoints, secrets
    ├─ Source map recovery ────────────► Original code
    ├─ Semgrep SAST (optional) ────────► Vulnerabilities
    └─ TruffleHog (optional) ──────────► Hardcoded secrets
                    │
                    ▼
5️⃣  REPORTING
    ├─ Markdown report generation
    ├─ Discord webhook alerts
    └─ Checkpoint state (resume support)
```

---

## ⚙️ Configuration

### `config.yaml` Structure

```yaml
# Performance tuning
threads: 10 # Concurrent workers
timeout_seconds: 20 # HTTP request timeout
retries: 3 # Failed request retries

# Discovery strategies (enable/disable)
katana_enabled: true
subjs_enabled: true
live_browser_enabled: false # Resource-intensive

# Analysis modules
semgrep_enabled: true # SAST scanning
trufflehog_enabled: true # Secret detection
source_map_enabled: true # Recover original code

# Filtering
skip_vendor_files: true # Ignore jQuery, React, etc.
cdn_patterns: # Skip CDNs
  - "cdn.jsdelivr.net"
  - "unpkg.com"

# Notifications
discord_webhook: "https://discord.com/api/webhooks/..."
discord_rate_limit: 2 # Messages per second
```

---

### New configuration options

The scanner adds a few new runtime knobs useful for low-RAM VPS deployments and unstable SPAs:

- `download.chunk_size` (int): Number of URLs processed per batch during downloads. Lower to reduce memory/task churn (default: 250).
- `playwright.enable_interactions` (bool): Disable in-page smart interactions (scroll/hover/tabs) if a site is unstable or causes frequent browser crashes (default: true).

## 🎓 Usage Examples

### Bug Bounty Recon Workflow

```bash
# Step 1: Fast passive discovery
python -m jsscanner -t acme -u https://acme.com --subjs

# Step 2: Review endpoints.txt for interesting APIs
cat results/acme/endpoints.txt | grep -i "api\|admin\|internal"

# Step 3: Deep scan interesting domains
python -m jsscanner -t acme-deep \
  -u https://api.acme.com \
  --katana \
  --live-browser \
  --semgrep

# Step 4: Check findings
ls results/acme-deep/findings/     # Semgrep vulnerabilities
ls results/acme-deep/secrets/      # Hardcoded secrets
```

### Authenticated Scan with Custom Headers

```bash
python -m jsscanner -t app \
  -u https://app.example.com \
  --cookie "session=abc123" \
  --header "Authorization: Bearer token123" \
  --header "X-API-Key: secret" \
  --subjs
```

### Resume After Network Failure

```bash
# Scan interrupted due to network issue
python -m jsscanner -t example -u https://example.com --katana
# ^C (interrupted)

# Resume from checkpoint
python -m jsscanner -t example --resume
```

---

## 📈 Performance Benchmarks

| Metric                        | Legacy Tool | JS Scanner   | Improvement             |
| ----------------------------- | ----------- | ------------ | ----------------------- |
| **SubJS-only scan**           | 5 min       | 2.25s        | **130x faster**         |
| **Memory usage (1000 files)** | 500MB       | 5MB          | **100x reduction**      |
| **Concurrent downloads**      | 5           | 50+          | **10x throughput**      |
| **Deduplication**             | None        | Bloom filter | **60% fewer downloads** |

### Tested Environments

- ✅ Windows 11 (Python 3.11)
- ✅ Ubuntu 24.04 (Python 3.11, 3.12)
- ✅ VPS (Debian 12, 2GB RAM)
- ✅ GitHub Actions CI/CD

---

## ⚡ CLI Reference

### Core Commands

```bash
# Basic scan
python -m jsscanner -t <target> -u <url> [options]

# Resume scan
python -m jsscanner -t <target> --resume

# Show version
python -m jsscanner --version

# Show help
python -m jsscanner --help
```

### Discovery Options

| Flag             | Description                          |
| ---------------- | ------------------------------------ |
| `--katana`       | Enable Katana crawling               |
| `--subjs`        | Enable SubJS passive discovery       |
| `--live-browser` | Enable Playwright browser automation |

### Analysis Options

| Flag        | Description               |
| ----------- | ------------------------- |
| `--semgrep` | Run Semgrep SAST analysis |

**Semgrep notes**

- `semgrep.chunk_size` (config.yaml): number of files processed per Semgrep subprocess. Default `100`. Increase to `200-500` on larger machines to improve throughput; decrease on low-RAM VPS.
- `semgrep.timeout` is applied per-chunk (default `120s`). If many batches still time out, raise this value or reduce `chunk_size`.
- Recommended run for large lists: `python -m jsscanner -t example.com --subjs --no-live --semgrep`
  | `--secrets` | Run TruffleHog secret detection |
  | `--source-maps` | Attempt source map recovery |
  | `--no-vendor` | Skip vendor/library files |

### Authentication Options

| Flag                    | Description                    |
| ----------------------- | ------------------------------ |
| `--cookie "key=val"`    | Set cookie header              |
| `--header "Key: Value"` | Add custom HTTP header         |
| `--auth-token <token>`  | Set Authorization Bearer token |

### Performance Tuning

| Flag            | Description                              |
| --------------- | ---------------------------------------- |
| `--threads <n>` | Override config threads (default: 10)    |
| `--timeout <n>` | Request timeout in seconds (default: 20) |
| `--retries <n>` | Failed request retries (default: 3)      |

---

## 📊 Output Structure

```
results/
└── <target>/
    ├── all_js_files.txt           # All discovered JS URLs
    ├── endpoints.txt              # Extracted API endpoints
    ├── state.json                 # Checkpoint state
    ├── scan_report.md             # Markdown summary
    ├── downloaded/                # Downloaded JS files
    │   ├── example.com/
    │   │   ├── app.js
    │   │   └─ vendor.min.js
    │   └── cdn.example.com/
    │       └── bundle.js
    ├── findings/                  # Semgrep results
    │   ├── sql-injection.json
    │   └── xss-dom.json
    ├── secrets/                   # TruffleHog results
    │   ├── api-keys.json
    │   └── credentials.json
    └── logs/
        └── scan.log              # Detailed logs
```

---

## 💡 Pro Tips

### 1. Two-Phase Reconnaissance

```bash
# Phase 1: Fast discovery (2-5 seconds)
python -m jsscanner -t recon -u https://target.com --subjs --no-live

# Phase 2: Deep dive on interesting findings
python -m jsscanner -t deep \
  -u https://api.target.com \
  --katana --live-browser --semgrep
```

### 2. Filter for High-Value Targets

```bash
# Find admin/internal endpoints
grep -iE "(admin|internal|api|v[0-9])" results/target/endpoints.txt

# Find authentication endpoints
grep -iE "(auth|login|token|session)" results/target/endpoints.txt

# Find data endpoints
grep -iE "(user|profile|account|data)" results/target/endpoints.txt
```

### 3. Combine with Other Tools

```bash
# Export URLs for manual review
cat results/target/all_js_files.txt | httpx -silent > live_js.txt

# Feed endpoints to fuzzer
cat results/target/endpoints.txt | ffuf -w - -u FUZZ

# Check for exposed source maps
cat results/target/endpoints.txt | grep "\.map$"
```

### 4. Monitor Progress in Real-Time

```bash
# Watch log file
tail -f results/target/logs/scan.log

# Monitor Discord channel for alerts
# Configure webhook in config.yaml
```

---

## 🎬 Demo

### Example Scan Output

```bash
$ python -m jsscanner -t example -u https://example.com --subjs

⚡ JS Scanner v4.2.0 - Production Ready
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Target: example
🌐 URL: https://example.com
📋 Strategies: SubJS

[1/5] 🔍 Discovery Phase
  ├─ SubJS: Found 47 JS files (2.1s)
  └─ Total unique URLs: 47

[2/5] 🧹 Filtering & Validation
  ├─ CDN filtered: 12 files
  ├─ Vendor filtered: 8 files
  └─ Ready to download: 27 files

[3/5] 📥 Download Phase
  ├─ Downloaded: 27/27 files
  ├─ Duplicates skipped: 5 files
  └─ Total size: 3.2 MB (2.8s)

[4/5] 🧠 Analysis Phase
  ├─ Endpoints extracted: 142
  ├─ Unique domains: 8
  └─ API patterns: 23

[5/5] 📊 Reporting
  ├─ Report: results/example/scan_report.md
  ├─ Endpoints: results/example/endpoints.txt
  └─ Discord: ✅ Sent

✅ Scan completed in 5.2 seconds
```
