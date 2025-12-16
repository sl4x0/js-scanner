# JS Scanner - Bug Bounty Edition

A high-performance JavaScript security scanner designed for bug bounty hunters and security researchers.

## 🚀 Features

- **Multi-domain concurrent scanning** - Process 10+ domains simultaneously with asyncio
- **Live + Wayback Machine discovery** - Find JavaScript files from current sites and historical archives
- **Secret detection** - Integrated TruffleHog scanning for API keys, tokens, and credentials
- **AST-based analysis** - Extract API endpoints, parameters, and sensitive data
- **Intelligent beautification** - Dynamic timeouts based on file size (30s/60s/120s)
- **Discord notifications** - Real-time alerts for verified secrets
- **State management** - Avoid re-scanning duplicate files with hash-based tracking

## 📋 Requirements

- Python 3.12+
- TruffleHog 3.92.3+
- Playwright (Chromium)
- 2GB+ RAM recommended

## 🛠️ Installation

### 1. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 2. Install TruffleHog

**Windows:**
```powershell
# Download trufflehog.exe to project root
# Or place in PATH
```

**Linux/Mac:**
```bash
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
```

### 3. Install Playwright browsers

```powershell
playwright install chromium
```

### 4. Configure settings

```powershell
copy config.yaml.example config.yaml
# Edit config.yaml with your Discord webhook (optional)
```

## 🎯 Usage

### Basic Scanning

**Scan a single JavaScript file:**
```powershell
python -m jsscanner -t myproject -u https://example.com/app.js
```

**Scan with discovery mode (crawl site + Wayback):**
```powershell
python -m jsscanner -t myproject --discovery -u https://example.com
```

**Scan multiple domains from file:**
```powershell
python -m jsscanner -t myproject --discovery -i domains.txt --threads 25
```

**Verbose output (show all HTTP errors):**
```powershell
python -m jsscanner -t myproject -u https://example.com -v
```

### Command-Line Options

```
-t, --target       Project name (creates results/project-name/)
-u, --url          URL(s) to scan (space-separated)
-i, --input        File containing URLs/domains (one per line)
--discovery        Enable Live + Wayback discovery mode
--threads          Concurrent download threads (default: 50)
-v, --verbose      Show detailed output including HTTP errors
```

## ⚙️ Configuration

Edit `config.yaml` for advanced settings:

```yaml
# Discord Integration
discord_webhook: "https://discord.com/api/webhooks/..."
discord_rate_limit: 30
discord_status_enabled: false

# Performance
threads: 50                    # Concurrent downloads (10-50 recommended)
max_concurrent_domains: 10     # Parallel domain processing
trufflehog_max_concurrent: 5   # Limit TruffleHog processes

# Timeouts
timeout: 30                    # HTTP request timeout
trufflehog_timeout: 300        # Secret scanning timeout per file
```

## 📁 Output Structure

```
results/<project-name>/
  ├── files/
  │   ├── minified/           # Original files (deleted after beautification)
  │   └── unminified/         # Beautified JavaScript files
  ├── extracts/
  │   ├── endpoints.txt       # Discovered API endpoints
  │   ├── params.txt          # URL/API parameters
  │   └── words.txt           # Extracted strings/tokens
  ├── logs/
  │   └── scan.log           # Detailed scan logs
  ├── scan_results.json       # Complete results with statistics
  ├── secrets.json            # Verified secrets only (for notifications)
  ├── trufflehog_full.json    # All findings (verified + unverified)
  ├── metadata.json           # Scan metadata and timing
  └── history.json            # File hashes to prevent re-scanning
```

## 🏎️ Performance Optimizations

### Concurrent Processing
- **Domain-level parallelism**: Process up to 10 domains simultaneously
- **File-level parallelism**: Download up to 50 files concurrently per domain
- **Live + Wayback parallelism**: Scan current site and Wayback archive simultaneously

### Smart Resource Management
- **Dynamic timeouts**: Beautification timeout scales with file size
  - <0.5MB: 30 seconds
  - 0.5-1MB: 60 seconds
  - 1-2MB: 120 seconds
  - >2MB: Skip (too slow)
- **Retry logic**: Automatic retry for Wayback Machine timeouts (3 attempts)
- **Memory optimization**: Clean up minified files after beautification

### Noise Reduction
- **Verbose mode toggle**: Hide HTTP errors by default, show with `-v`
- **Progress indicators**: Real-time progress tracking for multi-domain scans
- **Smart filtering**: Automatic duplicate detection, scope validation

## 🔒 Security Features

### Secret Detection
- **TruffleHog integration**: Scan for 800+ secret types
- **Verification**: Distinguish verified vs unverified secrets
- **Full export**: Save all findings for manual review (`trufflehog_full.json`)
- **Notifications**: Discord alerts for verified secrets only

### Extraction Capabilities
- **API endpoints**: `/api/v1/users`, `/admin/dashboard`, etc.
- **Parameters**: Query strings, POST parameters, API fields
- **Sensitive patterns**: Tokens, keys, connection strings
- **Custom regex**: Fallback when AST parsing unavailable

## 🧪 Testing

See [docs/TESTING.md](TESTING.md) for comprehensive testing guide.

**Quick test:**
```powershell
python -m jsscanner -t test -u https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js
```

## 📊 Example Output

```
╔═══════════════════════════════════════════════════════════╗
║              JS SCANNER - Bug Bounty Edition              ║
║                 Context-Aware Secret Hunter               ║
╚═══════════════════════════════════════════════════════════╝

🎯 Project Scope: myproject
📂 Input Items: 3
🔍 Discovery Mode: ON (Wayback + Live)

📡 PHASE 1: DISCOVERY & URL COLLECTION (CONCURRENT)
🚀 Processing 3 domains with concurrency level: 10
[1/3] 📍 Processing: https://example.com
  ├─ Live scan: Found 14 JS files
  ├─ Wayback scan: Found 23 JS files
  └─ Total discovered: 37 JS files

⬇️  PHASE 2: DOWNLOADING ALL FILES
✅ Downloaded 25 files (filtered 12 invalid/duplicate)

🔍 PHASE 3: SCANNING FOR SECRETS (TruffleHog)
✅ No secrets found

⚙️  PHASE 4: EXTRACTING DATA (Parallel)
✅ Processed 25 files
   • Endpoints: 127
   • Parameters: 451
   • Words: 2,341

✨ PHASE 5: BEAUTIFYING FILES
✅ Beautified 25 files

🗑️  PHASE 6: CLEANUP
✅ Deleted 20 minified files (freed ~15MB)

Scan Statistics:
  Files Scanned: 25
  Secrets Found: 0
  Duration: 48.47s
```

## 🐛 Troubleshooting

### Tree-sitter errors
If you see "Tree-sitter initialization failed", the scanner will use regex fallback (slightly less accurate but functional).

### Wayback timeout
Wayback Machine can be slow. The scanner automatically retries up to 3 times with exponential backoff.

### Discord notifications not working
1. Check `discord_webhook` in `config.yaml`
2. Verify webhook is valid (test in Discord)
3. Secrets must be **verified** to trigger notifications

### High memory usage
Reduce `threads` and `max_concurrent_domains` in `config.yaml`:
```yaml
threads: 25                # Lower for 2-4GB RAM
max_concurrent_domains: 5  # Lower for slower VPS
```

## 📚 Documentation

- **[README.md](README.md)** - Main documentation (this file)
- **[TESTING.md](TESTING.md)** - Testing guide and test files
- **[config.yaml.example](../config.yaml.example)** - Configuration template
- **[TRUFFLEHOG_README.md](TRUFFLEHOG_README.md)** - TruffleHog documentation

## 🤝 Contributing

Contributions welcome! Please submit issues and pull requests.

## 📄 License

MIT License
