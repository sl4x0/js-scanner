# JS Scanner - Bug Bounty Edition

A high-performance JavaScript security scanner designed for bug bounty hunters and security researchers.

## 🚀 Features

- **Multi-domain concurrent scanning** - Process 10+ domains simultaneously with asyncio
- **SubJS integration** - Fast JavaScript URL discovery using SubJS tool
- **Live browser crawling** - Find JavaScript files from current sites using Playwright
- **Secret detection** - Integrated TruffleHog scanning for API keys, tokens, and credentials
- **AST-based analysis** - Extract API endpoints, parameters, and sensitive data
- **Intelligent beautification** - Dynamic timeouts based on file size (30s/60s/120s)
- **Discord notifications** - Real-time alerts for verified secrets
- **State management** - Avoid re-scanning duplicate files with hash-based tracking
- **Scope filtering** - Automatically filter out-of-scope domains (CDN, third-party JS)

## 📋 Requirements

- Python 3.12+
- TruffleHog 3.92.3+
- Playwright (Chromium)
- SubJS (optional, for enhanced discovery)
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

### 4. Install SubJS (Optional, Recommended)

SubJS is a fast JavaScript URL discovery tool. Install it for enhanced scanning capabilities:

**Prerequisites:** Install Go 1.21+ from https://go.dev/dl/

**Installation:**

```powershell
# Windows/Linux/Mac
go install -v github.com/lc/subjs@latest
```

**Verify installation:**

```powershell
subjs -h
```

If `subjs` is not found, add Go's bin directory to your PATH:

- Windows: `C:\Users\<YourUsername>\go\bin`
- Linux/Mac: `~/go/bin`

### 5. Configure settings

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

**Scan with SubJS discovery (recommended):**

```powershell
python -m jsscanner -t myproject --subjs -u https://example.com
```

**Fast scan with SubJS only (no browser):**

```powershell
python -m jsscanner -t myproject --subjs-only -u https://example.com
```

**Scan multiple domains from file:**

```powershell
# Create input file with one URL/domain per line
# domains.txt:
#   https://example.com
#   https://target.com
#   subdomain.example.com

python -m jsscanner -t myproject --subjs -i domains.txt --threads 25
```

**Include all JS files (CDN, third-party):**

```powershell
python -m jsscanner -t myproject --subjs --no-scope-filter -u https://example.com
```

**Verbose output (show all HTTP errors):**

```powershell
python -m jsscanner -t myproject -u https://example.com -v
```

### Command-Line Options

```
-t, --target          Project name (creates results/project-name/)
-u, --url             URL(s) to scan (space-separated)
-i, --input           File containing URLs/domains (one per line)
--subjs               Use SubJS for additional URL discovery
--subjs-only          Use only SubJS (skip live browser, fastest)
--no-scope-filter     Include CDN and third-party JS files
--threads             Concurrent download threads (default: 50)
-v, --verbose         Show detailed output including HTTP errors
```

### Discovery Modes

| Mode                   | Speed   | Coverage   | Use Case                        |
| ---------------------- | ------- | ---------- | ------------------------------- |
| **Default** (no flags) | Medium  | Low-Medium | Direct URL scanning             |
| **--subjs**            | Fast    | High       | Recommended for most scans      |
| **--subjs-only**       | Fastest | High       | Quick scans, many domains       |
| **--no-scope-filter**  | Any     | Maximum    | Include all JS (CDN, 3rd party) |

## ⚙️ Configuration

Edit `config.yaml` for advanced settings:

```yaml
# Discord Integration
discord_webhook: "https://discord.com/api/webhooks/..."
discord_rate_limit: 30 # Messages per minute
discord_status_enabled: false # Only send secret alerts, not status updates

# Performance Tuning
threads: 50 # Concurrent downloads (10-50 recommended based on RAM)
max_concurrent_domains: 10 # Parallel domain processing
trufflehog_max_concurrent: 5 # Limit concurrent TruffleHog processes

# Discovery Options
skip_live: false # Skip live site crawling
verbose: false # Show all HTTP errors and debug info
no_scope_filter: false # Include CDN and third-party JS files

# Timeouts
timeout: 30 # HTTP request timeout (seconds)
trufflehog_timeout: 300 # Secret scanning timeout per file (seconds)
max_file_size: 10485760 # 10MB max per JS file

# Playwright Browser
playwright:
  headless: true # Run browser in headless mode
  max_concurrent: 3 # Max concurrent browser instances
  page_timeout: 30000 # Page load timeout (milliseconds)

# SubJS Configuration
subjs:
  enabled: true # Enable SubJS for URL discovery
  timeout: 60 # Timeout per domain (seconds)

# AST Analysis
ast:
  enabled: true # Enable Tree-sitter AST parsing
  min_word_length: 4 # Minimum word length for wordlist extraction

# Batch Processing
batch_processing:
  cleanup_minified: true # Delete minified files after beautification
```

## 📁 Output Structure

```
results/<project-name>/
  ├── files/
  │   ├── minified/           # Original files (deleted if cleanup enabled)
  │   └── unminified/         # Beautified JavaScript files
  ├── extracts/
  │   ├── example.com/        # Domain-specific extracts (NEW)
  │   │   ├── endpoints.json  # Endpoints with metadata
  │   │   ├── params.txt      # Parameters found
  │   │   └── words.txt       # Custom wordlist
  │   ├── another-domain.com/
  │   │   └── ...
  │   ├── endpoints.txt       # Legacy: All endpoints (backward compatibility)
  │   ├── params.txt          # Legacy: All parameters
  │   └── words.txt           # Legacy: All words
  ├── secrets/
  │   ├── example.com/        # Domain-specific secrets (NEW)
  │   │   └── secrets.json    # Secrets found in this domain
  │   ├── another-domain.com/
  │   │   └── secrets.json
  │   └── trufflehog_full.json # All findings (verified + unverified)
  ├── logs/
  │   └── scan.log            # Detailed scan logs
  ├── scan_results.json       # Complete results with statistics
  ├── metadata.json           # Scan metadata and timing
  └── history.json            # File hashes to prevent re-scanning
```

**New Features:**

- **Domain-specific organization**: Extracts and secrets are now organized by domain for easier analysis
- **Backward compatibility**: Legacy flat files (endpoints.txt, params.txt) are still created
- **Enhanced metadata**: scan_results.json includes domain_summary and secrets_summary fields

## 🏎️ Performance Optimizations

### Concurrent Processing

- **Domain-level parallelism**: Process up to 10 domains simultaneously
- **File-level parallelism**: Download up to 50 files concurrently per domain
- **SubJS integration**: Fast URL discovery without browser overhead

### Smart Resource Management

- **Dynamic timeouts**: Beautification timeout scales with file size
  - <0.5MB: 30 seconds
  - 0.5-1MB: 60 seconds
  - 1-2MB: 120 seconds
  - \> 2MB: Skip (too slow)
- **Scope filtering**: Automatically filter out-of-scope domains (CDN, third-party)
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

Comprehensive test suite for validation and quality assurance:

### Integration Tests

```bash
# Run all integration tests (10+ domains, extraction, beautification)
python tests/integration_tests.py
```

### Discord Notification Tests

```bash
# Start test server
cd test_notifications
python test_server.py

# Validate webhook (in another terminal)
python webhook_validator.py "YOUR_WEBHOOK_URL"

# Run scanner against test files
cd ..
python -m jsscanner -t test-notifications -i test_notifications/test_urls.txt
```

### Test Documentation

- **[tests/README.md](tests/README.md)** - Integration test suite documentation
- **[test_notifications/README.md](test_notifications/README.md)** - Notification testing guide

**Test Coverage:**

- ✅ Multi-domain scanning (10+ domains)
- ✅ Domain-specific organization
- ✅ Extraction accuracy validation
- ✅ Beautification quality tests
- ✅ Discord webhook validation
- ✅ Backward compatibility verification

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
🔍 Discovery Mode: Hybrid (SubJS + Live Browser)

📡 PHASE 1: DISCOVERY & URL COLLECTION (CONCURRENT)
🚀 Processing 3 domains with concurrency level: 10
[1/3] 📍 Processing: https://example.com
  ├─ Live scan: Found 14 JS files
  ├─ Subjs scan: Found 23 JS files
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

If you see "Tree-sitter initialization failed", the scanner will use regex fallback (slightly less accurate but functional). This is normal and doesn't affect secret scanning or file processing.

### SubJS not installed

If you see "SubJS not installed" warnings:

1. Install Go from https://go.dev/dl/
2. Run: `go install -v github.com/lc/subjs@latest`
3. Add Go's bin directory to your PATH
4. Verify with: `subjs -h`

The scanner will work without SubJS using live browser scanning only.

### Discord notifications not working

1. Check `discord_webhook` in `config.yaml` is a valid webhook URL
2. Verify webhook works by testing in Discord
3. Secrets must be **verified** by TruffleHog to trigger notifications
4. Check `discord_status_enabled` if you want scan status updates (not recommended - too noisy)

### High memory usage

Reduce concurrency settings in `config.yaml`:

```yaml
threads: 10 # Lower for 2GB RAM systems
max_concurrent_domains: 3 # Lower for slower connections
trufflehog_max_concurrent: 2 # Reduce if TruffleHog crashes
playwright:
  max_concurrent: 1 # Single browser instance
```

### TruffleHog not found

The scanner auto-detects TruffleHog in this order:

1. Path specified in `trufflehog_path` config
2. Project root directory (trufflehog.exe on Windows, trufflehog on Linux)
3. System PATH

Download from: https://github.com/trufflesecurity/trufflehog/releases

### No files downloaded

Common causes:

- **Invalid URLs**: Ensure URLs point to .js files or pages containing JS
- **CORS/403 errors**: Some sites block automated requests (normal)
- **Scope filtering**: Scanner only downloads files from target domains
- **Duplicates**: Files already scanned are skipped (check history.json)

Use `--verbose` flag to see detailed error messages:

```powershell
python -m jsscanner -t test -u https://example.com --verbose
```

## 💡 Best Practices

### For Large Scans (100+ domains)

```yaml
# config.yaml - Optimized for bulk scanning
threads: 50 # High concurrency
max_concurrent_domains: 20 # Process many domains in parallel
batch_processing:
  cleanup_minified: true # Save disk space
```

**Command:**

```powershell
python -m jsscanner -t bulk-scan --subjs-only -i domains.txt --threads 50
```

### For Deep Analysis (Single Target)

```yaml
# config.yaml - Optimized for thorough analysis
threads: 25 # Moderate concurrency
max_concurrent_domains: 3 # Focus on quality
recursion:
  max_depth: 5 # Deeper crawling
```

**Command:**

```powershell
python -m jsscanner -t deep-scan --subjs -u https://example.com
```

### For Limited Resources (VPS/Low RAM)

```yaml
# config.yaml - Optimized for 1-2GB RAM
threads: 10 # Low concurrency
max_concurrent_domains: 2 # Process few domains at once
trufflehog_max_concurrent: 2 # Limit secret scanning
playwright:
  max_concurrent: 1 # Single browser
batch_processing:
  cleanup_minified: true # Save disk space
```

### Command-Line Quick Tips

```powershell
# Quick scan without Wayback (fast)
python -m jsscanner -t quick -u https://example.com

# Deep scan with Wayback (thorough)
python -m jsscanner -t deep --discovery -u https://example.com

# Bulk scan from file (efficient)
python -m jsscanner -t bulk --discovery -i targets.txt --threads 50

# Debug mode (troubleshooting)
python -m jsscanner -t debug -u https://example.com --verbose
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
