![banner](./static/banner.png)

# ⚡ JS Scanner v4.0

> **Blazing-fast JavaScript security scanner for bug bounty hunters**  
> Hunt secrets, extract endpoints, analyze bundles — all in one tool.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)](README.md)
[![Version](https://img.shields.io/badge/Version-4.0-brightgreen.svg)](MASTER_PROTOCOL_v4.md)

---

## ✨ What's New in v4.0 "Stealth & Dashboard"

🎉 **Major upgrade with enterprise-grade features:**

- 🥷 **WAF Bypass** — curl_cffi with Chrome TLS fingerprinting (bypasses Cloudflare/Akamai)
- 📊 **Live Dashboard** — Real-time TUI with progress bars and statistics
- 🧠 **SPA Intelligence** — Predictive webpack chunk discovery for React/Vue apps
- 📂 **Clean Structure** — "Showroom vs. Warehouse" organized output
- 🚀 **Performance** — +30-40% success rate on protected sites

**[📜 Read the full upgrade guide →](MASTER_PROTOCOL_v4.md)**

---

## 🎯 Why Use This?

**Traditional scanners waste time on dead endpoints and slow sites.**  
This scanner is built for **speed and efficiency**:

- ⚡ **Fail-fast** — Skips non-responsive sites instantly (5s timeout)
- 🚫 **No redirects** — Treats redirects as failures (no wasted retries)
- 🎯 **No retries** — Single attempt per URL (skip bad targets immediately)
- 🔥 **Massive concurrency** — 100+ parallel downloads
- 🧠 **Smart filtering** — Ignores CDN noise and known libraries
- 🔒 **Instant alerts** — Verified secrets sent to Discord immediately
- 🥷 **Stealth Mode** — Browser-like fingerprints to bypass WAFs

Perfect for scanning **thousands of domains** in bug bounty programs.

---

## 🚀 Quick Start

```bash
# 1. Setup
pip install -r requirements.txt
playwright install chromium

# 2. Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your Discord webhook

# 3. Scan (with live dashboard!)
python -m jsscanner -t myprogram --subjs -u https://target.com
```

**That's it.** Results saved to `results/myprogram/`

**New in v4.0:** Check the live dashboard while scanning! 📊

---

## 💡 Usage Examples

### Fast Discovery Scan

```bash
# SubJS API only — fastest way to find JS files
python -m jsscanner -t target --subjs-only -u https://example.com --no-beautify
```

### Full Deep Scan

```bash
# Browser crawling + SubJS + source maps + beautification
python -m jsscanner -t target --subjs -u https://example.com --source-maps
```

### Secrets Only (Ultra-Fast)

```bash
# Skip extraction and beautification — just hunt secrets
python -m jsscanner -t target --subjs-only --no-extraction --no-beautify -u https://example.com
```

### Bulk Domain Scan

```bash
# Scan multiple domains from file
python -m jsscanner -t bug-bounty -i domains.txt --subjs --no-beautify
```

---

## 📊 How It Works

## 📊 How It Works

### 🏗️ Architecture: Multi-Stage Hunter

JS-Scanner is not a linear scanner — it's a **coordinated attack** on the target's JavaScript surface using three discovery speeds:

```
┌─────────────────────────────────────────────────────────────────┐
│                     INITIALIZATION & STATE                      │
│  • Load history.json (remember scanned hashes)                  │
│  • Verify dependencies (katana, subjs, trufflehog)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               PHASE 1: HYBRID DISCOVERY (The Funnel)            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   KATANA     │  │    SubJS     │  │   PLAYWRIGHT       │   │
│  │  (Speed)     │  │  (History)   │  │ (Intelligence)     │   │
│  ├──────────────┤  ├──────────────┤  ├────────────────────┤   │
│  │ Go binary    │  │ Wayback/     │  │ Headless Chrome    │   │
│  │ 1000s req/s  │  │ CommonCrawl  │  │ Smart interactions:│   │
│  │ robots.txt   │  │ Orphaned JS  │  │ • Scroll           │   │
│  │ sitemaps     │  │ Old configs  │  │ • Hover menus      │   │
│  │              │  │              │  │ • Click tabs       │   │
│  │ 80% in secs  │  │ Historical   │  │ Lazy-loaded 20%    │   │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬──────────┘   │
│         └──────────────────┴──────────────────────┘             │
│                            │                                    │
│                    ✓ 500-1000 JS URLs                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              PHASE 2: THE FILTER (Data Hygiene)                 │
├─────────────────────────────────────────────────────────────────┤
│  1. Scope Check     → Drop out-of-scope (analytics.google.com) │
│  2. Download        → Parallel fetch (100 threads)              │
│  3. Hash Check      → MD5 fingerprint calculation               │
│     • Known Library? → DROP (jQuery/React/Bootstrap)            │
│     • Scanned Before? → DROP (check history.json)               │
│  4. Result          → Only custom/modified target code          │
│                                                                 │
│                    ✓ 200-400 unique files                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│          PHASE 3: DEEP ANALYSIS (The Recursion)                 │
├─────────────────────────────────────────────────────────────────┤
│  A. AST Recursion (Tree-Sitter)                                │
│     • Parse: import('./admin.js'), require('config')            │
│     • Action: Send new URLs back to Phase 2                     │
│     • Result: Dig deep into app structure (2-3 levels)          │
│                                                                 │
│  B. Bundle Unpacking (Webcrack)                                 │
│     • Detect: app.bundle.js, vendor.chunk.js                    │
│     • Action: Explode into original source files                │
│     • Result: src/components/auth/login.js revealed             │
│                                                                 │
│  C. Source Map Recovery                                         │
│     • Find: .map files                                          │
│     • Action: Reconstruct original TypeScript/unminified code   │
│     • Result: Human-readable source with comments               │
│                                                                 │
│                    ✓ 500-2000 analyzed files                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│         PHASE 4: SECRET SCANNING (The Kill Chain)               │
├─────────────────────────────────────────────────────────────────┤
│  TruffleHog Streaming:                                          │
│  • Pipe clean, unique, un-minified code → TruffleHog            │
│  • Detect:                                                      │
│    - High-Entropy Strings (API Keys)                            │
│    - Specific Patterns (AWS, Stripe, Slack, Private Keys)       │
│    - Hardcoded Credentials (passwords, tokens)                  │
│  • Context: Record file path + line number                      │
│                                                                 │
│                    ✓ 0-50 findings                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│          PHASE 5: INTELLIGENCE REPORTING                        │
├─────────────────────────────────────────────────────────────────┤
│  Discord Alerts:                                                │
│  • 🔴 RED: Verified Secrets (immediate alert)                  │
│  • 🟠 ORANGE: Potential Secrets (manual review)                │
│  • Context: Line of code + file link + domain                   │
│                                                                 │
│  Artifact Generation:                                           │
│  • endpoints.txt     → API routes (feed to Burp/fuzzers)        │
│  • cloud_assets.txt  → S3 buckets, Azure blobs                  │
│  • secrets.json      → Full findings database                   │
│  • domains.txt       → All discovered domains                   │
│                                                                 │
│                    ✓ Actionable intelligence                    │
└─────────────────────────────────────────────────────────────────┘
```

### 🎯 The Result

**Input:** `python -m jsscanner -t target.com`

**Output:**

- 📁 Reconstructed source code (unminified, unpacked)
- 📋 List of hidden API endpoints
- 🔐 Hardcoded credentials with exact file locations
- 🔔 Real-time Discord alerts for verified secrets
- 📊 Organized by domain for easy analysis

**All automated, filtered, and deduplicated.**

---

### ⚡ Performance Comparison

| Method                  | 100 Domains | Files Found | Notes                        |
| ----------------------- | ----------- | ----------- | ---------------------------- |
| Playwright Only         | 15 min      | 450 JS      | Thorough but slow            |
| SubJS + Playwright      | 12 min      | 480 JS      | Good historical coverage     |
| **Katana + Playwright** | **8 min**   | **500 JS**  | **🚀 2x faster**             |
| **Katana + SubJS + PW** | **5 min**   | **550 JS**  | **⚡ Maximum (Recommended)** |

---

## 🎁 Key Features

### 🔐 Secret Detection

- **TruffleHog integration** — Detects 750+ secret types
- **Instant Discord alerts** — Verified secrets sent immediately
- **Smart batching** — Unverified secrets grouped by domain
- **Auto-organized** — Secrets sorted into aws/, github/, stripe/ folders

### ⚡ Performance

- **100 concurrent downloads** — Blazing fast file fetching
- **No wasted retries** — Single attempt per URL
- **5-second timeouts** — Skip slow/dead sites instantly
- **Smart caching** — Never re-download the same file

### 🧠 Intelligent Extraction

- **AST parsing** — Tree-sitter extracts endpoints, domains, links
- **Bundle unpacking** — Webcrack support for Webpack/Vite/Parcel
- **Source map recovery** — Reconstruct original source code
- **Domain organization** — Results auto-grouped by domain

### 🎯 Filtering & Noise Reduction

- **CDN detection** — Skips common CDN files automatically
- **Library filtering** — Ignores jQuery, React, Vue, etc.
- **HTML rejection** — Detects and skips HTML responses
- **Size limits** — Skips oversized files (200MB max)

---

## 📁 Results Structure

**Tiered "Warehouse vs. Showroom" Organization**

```
results/target/
│
├── 📄 REPORT.md              # [TIER 1] Executive summary — start here
│
├── 📂 findings/              # [TIER 2] High-value intelligence (pipeline ready)
│   ├── secrets.json          # → All detected secrets
│   ├── trufflehog.json       # → TruffleHog raw output
│   ├── endpoints.txt         # → API endpoints (ready for nuclei/ffuf)
│   ├── params.txt            # → Parameters for fuzzing
│   └── domains.txt           # → Discovered domains
│
├── 📂 artifacts/             # [TIER 3] Human-readable evidence
│   └── source_code/          # → Beautified JS organized by domain
│
├── 📂 logs/                  # [TIER 4] Audit trail
│   └── scan.log              # → Debug information
│
└── 🔒 .warehouse/            # [TIER 5] Hidden machine data
    ├── raw_js/               # → Original downloaded files
    ├── minified/             # → Processing cache
    └── db/                   # → Scan history & metadata
        ├── history.json      # → Deduplication database
        └── metadata.json     # → Scan statistics
```

**Design Benefits:**

- ⚡ **Instant Triage** — Open `REPORT.md` and see critical findings in 5 seconds
- 🔗 **Pipeline Ready** — Use `findings/*.txt` directly with other tools
- 🧹 **Clean Workspace** — Machine data hidden in `.warehouse/`
- 📊 **Enterprise Ready** — Structured for automation and CI/CD

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete design documentation.

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Discovery Layers (Hybrid Architecture)
katana:
  enabled: false # Fast Go-based crawler (install: go install github.com/projectdiscovery/katana/cmd/katana@latest)
  depth: 2 # Crawl depth
  concurrency: 20 # Concurrent requests

subjs:
  enabled: true # Historical JS file discovery

# Speed vs Completeness
retry:
  http_requests: 1 # No retries (fast)

timeouts:
  http_request: 5 # 5s timeout (fail-fast)
  playwright_page: 15000 # 15s browser timeout

# Concurrency
threads: 100 # Parallel downloads
max_concurrent_domains: 10 # Process 10 domains at once

# Features
discord_webhook: "YOUR_WEBHOOK"
trufflehog_path: "" # Auto-detected
verify_ssl: false # Bypass SSL errors
```

### Optional: Katana Integration

For **2-5x faster discovery**, install Katana:

```bash
# Install Katana (requires Go 1.24+)
CGO_ENABLED=1 go install github.com/projectdiscovery/katana/cmd/katana@latest

# Enable in config.yaml
katana:
  enabled: true
```

**Benefits:**

- ⚡ 10x faster than Playwright for standard JS discovery
- 🌐 Breadth-first crawling (robots.txt, sitemaps, known files)
- 🔗 Works alongside Playwright (Katana for speed, Playwright for depth)

---

## 🔧 Command Reference

### Scan Modes

| Command           | Description                      |
| ----------------- | -------------------------------- |
| `--subjs`         | Use SubJS API + browser crawling |
| `--subjs-only`    | SubJS API only (fastest)         |
| `--source-maps`   | Attempt source map recovery      |
| `--no-extraction` | Skip extraction (secrets only)   |
| `--no-beautify`   | Skip beautification (faster)     |
| `--force`         | Ignore cache, rescan everything  |
| `--resume`        | Resume interrupted scan          |

### Input Options

| Flag           | Description                             |
| -------------- | --------------------------------------- |
| `-t, --target` | Target name (creates `results/[name]/`) |
| `-u, --url`    | Single URL to scan                      |
| `-i, --input`  | File with URLs (one per line)           |

### Examples

```bash
# Fast recon
python -m jsscanner -t recon --subjs-only -i targets.txt --no-beautify

# Deep analysis
python -m jsscanner -t analysis -u https://app.example.com --source-maps

# Secret hunting only
python -m jsscanner -t secrets -i urls.txt --no-extraction --no-beautify

# Resume interrupted scan
python -m jsscanner -t myprogram --resume
```

---

## 🧪 Testing

```bash
# Run all tests
.\tests\run_all_tests.ps1

# Individual tests
python tests/test_comprehensive_suite.py
python tests/test_bundle_unpacker.py
```

---

## 📝 Changelog

### v3.2.1 (Current - Speed Optimized)

- ⚡ **Fail-fast configuration** — 5s timeout, no retries, no redirects
- 🚫 **Redirect blocking** — Treats redirects as failures
- 📁 **Workspace cleanup** — Organized directory structure

### v3.2

- ✅ Config validation with error messages
- 📊 Progress tracking with ETA
- 🔒 Thread-safe browser cleanup
- 🔔 Discord queue limits (1000 messages)

### v3.1

- 🔄 Automatic retry with exponential backoff
- 💾 Checkpoint system for resumable scans
- 📢 Smart Discord notifications (verified immediate)

### v3.0

- ✨ Streamlined extraction (endpoints, domains, links)
- ✨ Bundle detection with webcrack
- ✨ Cross-version tree-sitter compatibility

---

## 💪 Built For Bug Bounty

**Designed for real-world hunting:**

- Scan hundreds of domains in parallel
- Skip dead endpoints instantly (no wasted time)
- Get secret alerts in real-time via Discord
- Organized output for easy analysis
- Handles rate limits, SSL errors, redirects gracefully

**Perfect for:**

- Large bug bounty programs with many subdomains
- Fast reconnaissance on new targets
- Automated secret scanning in CI/CD
- Bulk JavaScript analysis

---

## 📜 License

MIT — Free for bug bounty and security research

---

## � Discord Bot Integration

**Control your VPS scanner remotely from Discord!**

Run scans directly from Discord with slash commands:

```
/scan python3 -m jsscanner -t target --subjs-only -u https://example.com
```

✅ **Features:**

- Execute scans remotely via Discord slash commands
- Runs in screen session on VPS (persistent, detachable)
- Scanner sends notifications via existing webhook system
- Check scan status with `/screen-status`
- List active sessions with `/screen-list`

📖 **Setup Guide:** See [DISCORD_BOT_SETUP.md](DISCORD_BOT_SETUP.md) for full installation instructions  
⚡ **Quick Reference:** See [DISCORD_BOT_QUICKREF.md](DISCORD_BOT_QUICKREF.md) for command examples

---

## �🤝 Contributing

Found a bug? Have an idea? Open an issue or PR!

**Made with ⚡ for bug bounty hunters**
