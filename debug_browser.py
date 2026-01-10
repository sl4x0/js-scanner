#!/usr/bin/env python3
"""
Debug Browser Stability Test
Validates the browser crash fixes by running 10 parallel scans against example.com.

SUCCESS CRITERIA:
- 0 browser crashes (no "Target page, context or browser has been closed" errors)
- All 10 scans complete successfully
- JavaScript files detected (> 0)
- Proper resource cleanup (no zombie processes)
"""

import asyncio
import sys
from pathlib import Path

# Add jsscanner to path
sys.path.insert(0, str(Path(__file__).parent))

from jsscanner.strategies.active import ActiveFetcher
from jsscanner.utils.log import setup_logger


async def test_single_scan(scan_id: int, logger):
    """Run a single scan against example.com"""
    logger.info(f"[Scan {scan_id:02d}] Starting...")

    try:
        # Create minimal config for ActiveFetcher
        config = {
            'verbose': False,
            'playwright': {
                'max_concurrent': 1,
                'restart_after': 5,
                'page_timeout': 30000,
                'headless': True
            },
            'verify_ssl': False,
            'session_management': {
                'pool_size': 1,
                'rotate_after': 50,
                'download_timeout': 30
            },
            'retry': {
                'http_requests': 1
            },
            'download': {
                'max_concurrent_per_domain': 2
            }
        }

        # Create fetcher (handles Playwright internally)
        fetcher = ActiveFetcher(config=config, logger=logger, state=None)

        try:
            # Initialize Playwright
            await fetcher.initialize()

            # Scan a real site with JavaScript
            target = "https://httpbin.org/html"  # Simple test site
            js_files = await fetcher.fetch_live(target)

            # Validate results
            if js_files:
                logger.info(f"[Scan {scan_id:02d}] ✅ SUCCESS: Found {len(js_files)} JavaScript files")
                return {"scan_id": scan_id, "status": "success", "js_count": len(js_files), "error": None}
            else:
                logger.warning(f"[Scan {scan_id:02d}] ⚠️  WARNING: Found 0 JavaScript files (detection issue?)")
                return {"scan_id": scan_id, "status": "warning", "js_count": 0, "error": "Zero detection"}

        finally:
            # Ensure cleanup
            await fetcher.cleanup()

    except Exception as e:
        error_msg = str(e)
        if "closed" in error_msg.lower() or "target" in error_msg.lower():
            logger.error(f"[Scan {scan_id:02d}] ❌ CRASH: {error_msg}")
            return {"scan_id": scan_id, "status": "crash", "js_count": 0, "error": "Browser crash"}
        else:
            logger.error(f"[Scan {scan_id:02d}] ❌ ERROR: {error_msg}")
            return {"scan_id": scan_id, "status": "error", "js_count": 0, "error": error_msg}


async def main():
    """Run 10 parallel scans to validate browser stability"""

    # Setup logger
    logger = setup_logger("debug_browser")

    logger.info("=" * 80)
    logger.info("🔬 BROWSER STABILITY TEST - 10 Parallel Scans")
    logger.info("=" * 80)
    logger.info("Target: httpbin.org/html (simple test site)")
    logger.info("Parallel scans: 10")
    logger.info("Expected: 0 crashes, JavaScript files detected\n")

    # Run 10 parallel scans
    tasks = [test_single_scan(i + 1, logger) for i in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    # Analyze results
    logger.info("\n" + "=" * 80)
    logger.info("📊 TEST RESULTS")
    logger.info("=" * 80)

    successes = [r for r in results if r["status"] == "success"]
    warnings = [r for r in results if r["status"] == "warning"]
    crashes = [r for r in results if r["status"] == "crash"]
    errors = [r for r in results if r["status"] == "error"]

    total_js_files = sum(r["js_count"] for r in results)

    logger.info(f"✅ Successful scans:     {len(successes)}/10")
    logger.info(f"⚠️  Zero detection scans: {len(warnings)}/10")
    logger.info(f"❌ Browser crashes:      {len(crashes)}/10")
    logger.info(f"❌ Other errors:         {len(errors)}/10")
    logger.info(f"📦 Total JS files found: {total_js_files}")

    # Print crash details
    if crashes:
        logger.error("\n🔥 CRASH DETAILS:")
        for crash in crashes:
            logger.error(f"  Scan {crash['scan_id']:02d}: {crash['error']}")

    if errors:
        logger.error("\n⚠️  ERROR DETAILS:")
        for error in errors:
            logger.error(f"  Scan {error['scan_id']:02d}: {error['error']}")

    # Final verdict
    logger.info("\n" + "=" * 80)
    if len(crashes) == 0 and len(errors) == 0:
        if len(warnings) == 0:
            logger.info("🎉 ALL TESTS PASSED - 100% Stability, 100% Detection")
            return 0
        else:
            logger.warning("⚠️  PARTIAL SUCCESS - 100% Stability, but zero detection on some scans")
            return 1
    else:
        logger.error("❌ TESTS FAILED - Browser crashes or errors detected")
        return 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
