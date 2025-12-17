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
- AST extraction (endpoints, params, wordlists)
- Source map recovery
- Discord notifications
- Domain-specific organization

## v3.0 Updates

- 70% better wordlists (fragment filtering)
- Bundle detection (Webpack/Vite/Parcel)
- Cross-version tree-sitter

## Results Location

`results/[target]/`
- `extracts/endpoints.txt`
- `extracts/params.txt`
- `extracts/wordlist.txt`
- `extracts/[domain]/`
- `secrets.json`
- `files/`

## Test

```bash
.\tests\run_all_tests.ps1
```
