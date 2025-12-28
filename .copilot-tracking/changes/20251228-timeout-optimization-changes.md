<!-- markdownlint-disable-file -->

# Release Changes: Timeout Optimization

**Related Plan**: timeout-handling-optimization
**Implementation Date**: 2025-12-28

## Summary

Optimized timeout handling in JS scanner to reduce failures on slow/unreliable domains while maintaining fast scanning performance. Added domain blacklisting, HEAD request retries with fallback, and faster sourcemap skipping.

## Changes

### Added

- d:\Automation Bug Bounty\js-scanner\jsscanner\core\state.py - Added problematic domains bloom filter for tracking repeatedly timing-out domains, with batched saving to reduce IO lag
- d:\Automation Bug Bounty\js-scanner\jsscanner\strategies\active.py - Added state parameter to ActiveFetcher for domain tracking access
- d:\Automation Bug Bounty\js-scanner\jsscanner\core\engine.py - Updated ActiveFetcher initialization to pass state manager

### Modified

- d:\Automation Bug Bounty\js-scanner\jsscanner\strategies\active.py - Enhanced \_preflight_check with domain blacklist check, HEAD retry logic, and GET fallback on timeout
- d:\Automation Bug Bounty\js-scanner\jsscanner\analysis\sourcemap.py - Reduced sourcemap fetch retries from 2 to 1 for faster optional resource handling
- d:\Automation Bug Bounty\js-scanner\CHANGELOG.md - Added entry for timeout optimization improvements

### Removed

- None

## Release Summary

**Total Files Affected**: 5

### Files Created (0)

- None

### Files Modified (5)

- jsscanner/core/state.py - Added bloom filter methods for problematic domains
- jsscanner/strategies/active.py - Retry logic and domain checking
- jsscanner/core/engine.py - State passing to fetcher
- jsscanner/analysis/sourcemap.py - Reduced retries
- CHANGELOG.md - Documentation update

### Files Removed (0)

- None

### Dependencies & Infrastructure

- **New Dependencies**: None
- **Updated Dependencies**: None
- **Infrastructure Changes**: Added problematic domains bloom filter persistence
- **Configuration Updates**: None

### Deployment Notes

No breaking changes. Scanner will automatically start tracking problematic domains and improve timeout handling on next run.
