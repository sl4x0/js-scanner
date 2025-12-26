# ⚡ JS Scanner

![CI](https://github.com/sl4x0/js-scanner/workflows/CI/badge.svg)
![Release](https://img.shields.io/github/v/tag/sl4x0/js-scanner?label=release)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)

<p align="left"><img src="docs/logo.svg" alt="logo" width="140"/></p>

A compact, automation-friendly JavaScript reconnaissance tool for bug bounty hunters. Fast discovery, disk-streamed downloads, AST/source-map analysis, and optional Semgrep/TruffleHog integrations.

Key points:
- Streams downloads to disk to avoid memory pressure
- Hybrid discovery: Katana | SubJS | Playwright
- Pluggable analysis: AST, source maps, Semgrep, secrets

---

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Copy and edit config
copy config.yaml.example config.yaml
# Set `discord_webhook` and tune `threads`

# Run a scan
python -m jsscanner -t mytarget -u https://example.com --subjs
```

Results are written to `results/<target>/`.

---

## Minimal Workflow

1. Discovery — Katana/SubJS/Browser
2. Filter & Download — stream → disk, hash, dedupe
3. Analyze — AST, source maps, Semgrep, secrets
4. Report — findings, endpoints, Discord alerts

---

## Useful Links
- Changelog: CHANGELOG.md
- Architecture: ARCHITECTURE.md
- Config example: config.yaml.example

---

If you'd like, I can (a) add a CI badge and small logo, or (b) expand Quick Start with example outputs — tell me which.

## �🤝 Contributing

Found a bug? Have an idea? Open an issue or PR!

**Made with ⚡ for bug bounty hunters**

