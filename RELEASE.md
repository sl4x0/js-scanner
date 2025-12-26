# Release v4.2.0

## Summary

Release `v4.2.0` marks the migration of core engine responsibilities into lightweight sub-engines:

- Discovery (Katana/SubJS/Playwright) → `DiscoveryEngine`
- Downloads (stream-to-disk, hashing, dedupe) → `DownloadEngine`
- Analysis (AST, beautify, semgrep) → `AnalysisEngine`

All unit and integration tests pass locally and CI for this tag is configured to run the test workflow.

## Notable Changes

- Reduced memory usage by streaming downloads to disk.
- Clear separation of concerns: discovery, download, analysis are now sub-engines.
- Improved semgrep vendor filtering and Tree-sitter fallback.
- Tests and CI workflow added/updated.

## Deployment Checklist

1. Ensure production config (`config.yaml`) contains correct `discord_webhook` and any secrets.
2. Install runtime dependencies: `pip install -r requirements.txt` and `playwright install chromium`.
3. Run smoke test: `python -m jsscanner --version` and `python -m pytest -q`.
4. Deploy release tag `v4.2.0` (already pushed).

## Rollback Instructions

If an issue is observed in production, roll back to the previous tag (for example `v4.1.0`):

```bash
git fetch --tags origin
git checkout tags/v4.1.0 -b rollback-v4.1.0
# Deploy rollback branch using your deployment mechanism
```

If you need to re-open `main` to a previous commit instead of using tags:

```bash
git checkout main
git reset --hard <commit-sha-of-known-good>
git push --force origin main
```

## Monitoring

- Watch GitHub Actions for test run status: https://github.com/sl4x0/js-scanner/actions
- Monitor disk usage on scanning host and the Discord webhook queue for rate limits.

## Contact

For rollback assistance, contact the release owner or check the repo `CHANGELOG.md` and `ARCHITECTURE.md`.
