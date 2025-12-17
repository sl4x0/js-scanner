# JS Scanner v3.0

High-performance JavaScript security scanner for bug bounty.

## Quick Start

```bash
pip install -r requirements.txt
playwright install chromium
copy config.yaml.example config.yaml
python -m jsscanner -t target --subjs -u https://example.com
```

## Usage

```bash
# Single URL
python -m jsscanner -t myproject -u https://example.com/app.js

# With SubJS discovery
python -m jsscanner -t myproject --subjs -u https://example.com

# SubJS only (fast)
python -m jsscanner -t myproject --subjs-only -u https://example.com

# Multiple URLs
python -m jsscanner -t myproject -i targets.txt

# Force rescan
python -m jsscanner -t myproject -u https://example.com --force

# Skip beautify (faster)
python -m jsscanner -t myproject -u https://example.com --no-beautify

# Source maps
python -m jsscanner -t myproject -u https://example.com --source-maps
```

## Features

- Multi-domain concurrent scanning
- SubJS integration
- Browser crawling (Playwright)
- Secret detection (TruffleHog)
- AST extraction (endpoints, domains, links)
- Source map recovery
- Discord notifications
- Domain-specific organization

## v3.0 Updates

- Streamlined extraction (endpoints, domains, links only)
- Bundle detection (Webpack/Vite/Parcel)
- Cross-version tree-sitter
- Removed params/wordlist features for better focus

## Results Location

`results/[target]/`

- `extracts/endpoints.txt`
- `extracts/domains.txt`
- `extracts/links.txt`
- `extracts/[domain]/`
- `secrets.json`
- `files/`

## Test

```bash
.\tests\run_all_tests.ps1
```
