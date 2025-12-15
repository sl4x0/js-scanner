# JS Scanner - The Ultimate Bug Bounty Edition

> Context-Aware JavaScript Secret Hunter for Private Bug Bounty Programs

## 🎯 Overview

**JS Scanner** is a powerful, production-ready tool designed for bug bounty hunters running on VPS environments. Unlike traditional regex-based scanners, JS Scanner uses **Abstract Syntax Tree (AST)** parsing with Tree-sitter to understand JavaScript code contextually, providing more accurate results with fewer false positives.

### Key Features

- 🧠 **Context-Aware**: AST parsing with Tree-sitter for intelligent code analysis
- ⚡ **Instant Alerts**: Streaming secret detection with immediate Discord notifications
- 💾 **No Database**: JSON-based state management with file locking
- 🔄 **Hybrid Discovery**: Combines Wayback Machine, Live Site, and Recursive scanning
- 🎯 **Deduplication**: SHA256 hash-based file tracking to avoid rescanning
- 🚀 **Memory Efficient**: Proper resource management for long-running VPS deployments

## 📁 Project Structure

```
js-scanner/
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
├── jsscanner/                  # Main package
│   ├── __init__.py
│   ├── __main__.py            # Entry point
│   ├── cli.py                 # CLI argument parser
│   ├── core/                  # Core functionality
│   │   ├── engine.py          # Main orchestrator
│   │   ├── state_manager.py   # JSON state with file locking
│   │   └── notifier.py        # Discord rate-limited alerts
│   ├── modules/               # Worker modules
│   │   ├── fetcher.py         # Playwright + Wayback fetching
│   │   ├── processor.py       # JS beautification + source maps
│   │   ├── secret_scanner.py  # TruffleHog integration
│   │   ├── ast_analyzer.py    # Tree-sitter AST parsing
│   │   └── crawler.py         # Recursive JS discovery
│   └── utils/                 # Utilities
│       ├── file_ops.py        # File operations
│       ├── hashing.py         # SHA256 hashing
│       └── logger.py          # Colorized logging
└── results/                   # Output directory
    └── {target_name}/
        ├── secrets.json       # Verified secrets
        ├── history.json       # Scanned file hashes
        ├── metadata.json      # Scan statistics
        ├── files/
        │   ├── minified/      # Original JS files
        │   └── unminified/    # Beautified JS files
        ├── extracts/
        │   ├── endpoints.txt  # API endpoints
        │   ├── params.txt     # Parameters
        │   ├── links.txt      # Document links
        │   ├── domains.txt    # External domains
        │   └── wordlist.txt   # Custom wordlist
        └── logs/
            └── scan.log       # Detailed logs
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- TruffleHog v3+
- Git (for Playwright installation)

### Step 1: Clone the Repository

```bash
cd /path/to/js-scanner
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 4: Install TruffleHog

```bash
# macOS/Linux
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

# Or download from: https://github.com/trufflesecurity/trufflehog/releases
```

### Step 5: Configure

Edit `config.yaml`:

```yaml
discord_webhook: "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"
discord_rate_limit: 30

trufflehog_path: "/usr/local/bin/trufflehog" # Update if different
threads: 10

playwright:
  headless: true
  max_concurrent_contexts: 3
  page_timeout: 30000

wayback:
  rate_limit: 15

recursion:
  enabled: true
  depth: 2

ast:
  min_word_length: 4
```

## 📖 Usage

### Understanding Discovery Mode

JS Scanner now separates **scope definition** (`-t`) from **discovery behavior** (`--discovery`):

- **Scope (`-t`)**: Defines the project name and filters results to matching domains
- **Discovery Mode (`--discovery`)**: Controls whether to actively discover JS files via Wayback Machine + Live crawling

| Mode              | Flag          | Wayback | Live Crawl | Use Case                            |
| ----------------- | ------------- | ------- | ---------- | ----------------------------------- |
| **OFF** (default) | `-i file.txt` | ❌      | ✅         | Fast scanning of known URLs/domains |
| **ON**            | `--discovery` | ✅      | ✅         | Full discovery from Wayback + Live  |

### Basic Examples

#### 1. Full Discovery for a Single Domain

```bash
python -m jsscanner -t example.com --discovery
```

**Behavior:**

- ✅ Fetch all `*.example.com` JavaScript files from Wayback Machine
- ✅ Crawl live site with Playwright
- ✅ Scan all discovered JS files
- ✅ Filter results to match scope `example.com`

#### 2. Scan Subdomains from httpx (Live Only - Fast! ⚡)

```bash
# Fast scan: Only checks live pages, no Wayback queries
python -m jsscanner -t example.com -i subdomains.txt
```

**Input (`subdomains.txt`):**

```
https://app.example.com
https://api.example.com
https://cdn.example.com
```

**Behavior:**

- ✅ Open each URL in Playwright
- ✅ Extract JavaScript files from the live page
- ❌ **Does NOT** query Wayback Machine (fast!)
- ❌ **Does NOT** perform additional discovery

#### 3. Scan Subdomains with Full Discovery

```bash
# Add --discovery to enable Wayback for each subdomain
python -m jsscanner -t example.com -i subdomains.txt --discovery
```

**Behavior:**

- ✅ Query Wayback Machine for each subdomain
- ✅ Crawl each live page
- ⚠️ Slower but more comprehensive

#### 4. Scan Specific JavaScript URLs Directly

```bash
python -m jsscanner -t example.com -i js-urls.txt
```

**Input (`js-urls.txt`):**

```
https://example.com/static/app.js
https://example.com/vendor/bundle.min.js
https://cdn.example.com/main.js
```

**Behavior:**

- ✅ Download and scan each JS file directly
- ❌ No Wayback queries
- ❌ No live page crawling

#### 5. Scan Specific URLs via Command Line

```bash
python -m jsscanner -t example.com -u https://example.com/app.js https://example.com/main.js
```

**Behavior:**

- ✅ Download and scan the 2 specified files only
- ❌ No discovery

### Advanced Options

```bash
# Enable full discovery (Wayback + Live)
python -m jsscanner -t example.com --discovery

# Custom config file
python -m jsscanner -t example.com --config prod-config.yaml

# Skip Wayback scanning (even in discovery mode)
python -m jsscanner -t example.com --discovery --no-wayback

# Skip live site scanning (use Wayback only)
python -m jsscanner -t example.com --discovery --no-live

# Disable recursive crawling
python -m jsscanner -t example.com --discovery --no-recursion

# Override thread count
python -m jsscanner -t example.com --threads 20

# Verbose output
python -m jsscanner -t example.com -v
```

### Multi-Domain Scanning

```bash
# Scan multiple domains with full discovery
python -m jsscanner -t "bug-bounty-program" -i domains.txt --discovery
```

**Input (`domains.txt`):**

```
google.com
youtube.com
gmail.com
```

**Behavior:**

- Uses "bug-bounty-program" as the scope/project name
- Performs full discovery (Wayback + Live) for each domain
- Results organized under `results/bug-bounty-program/`

## 🔧 How It Works

### 1. Input Processing

JS Scanner determines what to scan based on your input:

- **Direct JS URLs**: `.js` files are downloaded and scanned immediately
- **Domains/Page URLs**: JavaScript files are extracted via:
  - **Live Crawl** (always enabled unless `--no-live`)
  - **Wayback Machine** (only if `--discovery` flag is set)

### 2. Discovery Phase (When `--discovery` is enabled)

- **Wayback Machine**: Queries the CDX API for historical JavaScript files
- **Live Site**: Uses Playwright to render the page and extract `<script>` tags
- **Recursive Crawling**: Parses JS imports/requires to find linked files (if enabled)

### 3. Processing Phase

- **Deduplication**: Calculates SHA256 hash and checks `history.json`
- **Source Map Extraction**: Extracts inline or referenced source maps
- **Beautification**: Uses jsbeautifier to format minified code
- **File Storage**: Saves both original and processed versions

### 4. Analysis Phase

- **Secret Scanning**: Streams TruffleHog output line-by-line
  - Only alerts on **verified** secrets
  - Immediately queues Discord notifications
- **AST Parsing**: Uses Tree-sitter to extract:
  - API endpoints (`/api/`, `/v1/`, etc.)
  - Parameter names (object properties)
  - External domains (for subdomain takeover checks)
  - Custom wordlists (identifiers for fuzzing)

### 5. Alerting Phase

- **Rate-Limited Queue**: Max 30 Discord messages/minute
- **Rich Embeds**: Color-coded with detector info, file location, and timestamps

## 🎯 Discovery Mode Quick Reference

| Command                                  | Discovery | Wayback | Live   | Best For                      |
| ---------------------------------------- | --------- | ------- | ------ | ----------------------------- |
| `-t domain.com --discovery`              | ON        | ✅      | ✅     | Initial comprehensive scan    |
| `-t domain.com -i httpx.txt`             | OFF       | ❌      | ✅     | Fast live-only subdomain scan |
| `-t domain.com -i httpx.txt --discovery` | ON        | ✅      | ✅     | Deep subdomain discovery      |
| `-t domain.com -i urls.txt`              | OFF       | ❌      | Direct | Direct JS file scanning       |
| `-t domain.com -u url1 url2`             | OFF       | ❌      | Direct | Quick test of specific files  |
| `-t domain.com` (no input)               | AUTO-ON   | ✅      | ✅     | Auto-discovery mode           |

**💡 Pro Tip:** Use discovery mode OFF (`-i` without `--discovery`) when scanning httpx output for maximum speed!

## 🔐 State Management

JS Scanner uses **fcntl file locking** for thread-safe JSON operations:

```python
# Example from state_manager.py
with open(self.history_file, 'r+') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
    try:
        data = json.load(f)
        # ... modify data ...
        json.dump(data, f, indent=2)
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock
```

This prevents corruption when multiple threads try to write simultaneously.

## 📊 Output Files

### secrets.json

```json
[
  {
    "DetectorName": "AWS",
    "DecoderName": "PLAIN",
    "Verified": true,
    "Raw": "AKIAIOSFODNN7EXAMPLE",
    "SourceMetadata": {
      "file": "/path/to/file.js",
      "url": "https://example.com/app.js"
    },
    "timestamp": "2025-12-15T10:30:45Z"
  }
]
```

### history.json

```json
{
  "scanned_hashes": ["a1b2c3d4e5f6...", "b2c3d4e5f6a7..."],
  "scan_metadata": {
    "a1b2c3d4e5f6...": {
      "url": "https://example.com/app.js",
      "timestamp": "2025-12-15T10:30:00Z"
    }
  }
}
```

### metadata.json

```json
{
  "total_files": 42,
  "total_secrets": 3,
  "scan_duration": 187.5,
  "errors": [],
  "last_updated": "2025-12-15T10:35:00Z"
}
```

## ⚠️ Important Notes

### Memory Management

- **Always close Playwright contexts**: Each context consumes ~50-100MB
- Use `max_concurrent_contexts` to limit parallel browser sessions
- The scanner automatically closes contexts in `finally` blocks

### Rate Limiting

- **Wayback Machine**: 15 requests/second (configurable)
- **Discord Webhooks**: 30 messages/minute (hard limit)
- Built-in queuing system prevents bans

### File Locking (Windows vs Linux)

- **Linux/macOS**: Uses `fcntl` (POSIX file locking)
- **Windows**: `fcntl` is not available natively
  - Consider using `msvcrt.locking()` or
  - Run in WSL (Windows Subsystem for Linux)

## 🐛 Troubleshooting

### TruffleHog Not Found

```bash
# Verify installation
which trufflehog

# Update path in config.yaml
trufflehog_path: "/path/to/trufflehog"
```

### Playwright Fails to Launch

```bash
# Reinstall browsers
playwright install chromium --with-deps
```

### Discord Webhooks Not Working

```bash
# Test webhook manually
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"Test from JS Scanner"}' \
  YOUR_WEBHOOK_URL
```

### High Memory Usage

- Reduce `max_concurrent_contexts` in config
- Reduce `threads` count
- Enable `--no-recursion` for shallow scans

## 🔄 Continuous Monitoring

For 24/7 VPS monitoring, use systemd or supervisor:

### systemd Service Example

```ini
[Unit]
Description=JS Scanner for example.com
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/js-scanner
ExecStart=/usr/bin/python3 -m jsscanner -t example.com
Restart=on-failure
RestartSec=300

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable jsscanner-example.service
sudo systemctl start jsscanner-example.service
```

## 📝 License

This tool is provided for educational and authorized bug bounty purposes only. Always ensure you have permission before scanning any targets.

## 🤝 Contributing

This is a private bug bounty tool, but suggestions and improvements are welcome!

## 🎓 Credits

Built with:

- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Secret scanning
- [Playwright](https://playwright.dev/) - Browser automation
- [Tree-sitter](https://tree-sitter.github.io/) - AST parsing
- [jsbeautifier](https://github.com/beautifier/js-beautify) - Code formatting

---

**Happy Hunting! 🎯**
