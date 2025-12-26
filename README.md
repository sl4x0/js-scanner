# ⚡ JS Scanner

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)

A fast, focused JavaScript reconnaissance tool for bug bounty hunters — discovers JS, extracts endpoints, and hunts secrets with minimal configuration.

- Small, portable, and automation-friendly
- Streams downloads to disk to avoid memory pressure
- Hybrid discovery: Katana | SubJS | Playwright
- Optional Semgrep + TruffleHog integrations

---

**Quick Start**

```powershell
# 1. Install deps
pip install -r requirements.txt
playwright install chromium

# 2. Copy config
copy config.yaml.example config.yaml
# edit config.yaml (add discord_webhook, tune threads)

# 3. Run a quick scan
python -m jsscanner -t mytarget -u https://example.com --subjs
```

Results are saved under `results/<target>/`.

---

**Minimal Workflow**

1. Discovery — Katana/SubJS/Browser find JS files
2. Filter & Download — stream-to-disk, hash, dedupe
3. Analyze — AST, source-maps, semgrep, secrets
4. Report — findings, endpoints, Discord alerts

Simple ASCII flow:

```
inputs -> [Discovery (Katana / SubJS / Playwright)]
  -> [Filter & Download (stream -> disk)]
  -> [Analysis (AST / Semgrep / Secrets)]
  -> [Report (files/, findings/, discord)]
```

---

Why this README is short:

- This repo focuses on tools and automation; detailed design and examples live in `ARCHITECTURE.md` and `CHANGELOG.md`.

Helpful links

- Changelog: CHANGELOG.md
- Architecture: ARCHITECTURE.md
- Config example: config.yaml.example

---

Want me to (a) add a small project logo image and CI badge, or (b) expand the Quick Start with example outputs? Reply with your choice.

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
├── 📄 REPORT.md # [TIER 1] Executive summary — start here
│
├── 📂 findings/ # [TIER 2] High-value intelligence (pipeline ready)
│ ├── secrets.json # → All detected secrets
│ ├── trufflehog.json # → TruffleHog raw output
│ ├── semgrep.json # → Semgrep security patterns (if enabled)
│ ├── endpoints.txt # → API endpoints (ready for nuclei/ffuf)
│ ├── params.txt # → Parameters for fuzzing
│ └── domains.txt # → Discovered domains
│
├── 📂 artifacts/ # [TIER 3] Human-readable evidence
│ └── source_code/ # → Beautified JS organized by domain
│
├── 📂 logs/ # [TIER 4] Audit trail
│ └── scan.log # → Debug information
│
└── 🔒 .warehouse/ # [TIER 5] Hidden machine data
├── raw_js/ # → Original downloaded files
├── minified/ # → Processing cache
└── db/ # → Scan history & metadata
├── history.json # → Deduplication database
└── metadata.json # → Scan statistics

````

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

# Static Analysis (Optional)
semgrep:
  enabled: false # Semgrep security pattern detection (install: pip install semgrep && semgrep login)
  timeout: 600 # 10 minutes
  max_target_bytes: 5000000 # 5MB max per file
  jobs: 4 # Parallel scanning

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
````

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

### Optional: Semgrep Static Analysis

For **security pattern detection** in downloaded JavaScript files:

```bash
# Install Semgrep
pip install semgrep

# Login to access registry rules (free account)
semgrep login
# Follow the browser link and authorize

# Enable in config.yaml
semgrep:
  enabled: true
  timeout: 600
  jobs: 4  # Parallel scanning for speed
```

**What it detects:**

- 🔴 **XSS Sinks** — innerHTML, eval, document.write patterns
- 🔐 **Insecure Crypto** — MD5, weak random, hardcoded salts
- 📂 **Path Traversal** — Unsafe file path operations
- 🗃️ **SQL Injection** — String concatenation in queries
- 🌐 **SSRF Patterns** — User-controlled URLs in fetch/axios
- 🔑 **Authentication Issues** — Weak JWT, missing validation

**Performance Tips:**

- Uses `--config=auto` to leverage Semgrep registry rules
- Runs on **deduplicated, beautified** JS files (Phase 5.5)
- Parallel processing with configurable `jobs` (default: 4)
- `max_target_bytes` prevents hanging on large files (5MB default)
- Results saved to `findings/semgrep.json` for manual review

**Note:** This is for **investigation purposes only** — no Discord notifications sent. Review findings manually to identify patterns worth deeper investigation.

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
