#!/usr/bin/env python3
"""
Quick Integration Test - Verify dashboard doesn't flicker with logging
Run this before deploying to production
"""
import sys
import asyncio
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🧪 Dashboard + Logging Integration Test\n")
print("="*60)

from jsscanner.utils.logger import setup_logger, console
from jsscanner.core.dashboard import ScanDashboard
import time

print("\n✅ Test: Dashboard with Active Logging")
print("   Expected: Dashboard stable, no console logs visible\n")

# Setup logger
logger = setup_logger()

# Create dashboard with logger
dashboard = ScanDashboard("test.com", console=console, logger=logger)
dashboard.start()

# Simulate scan with logging
for i in range(10):
    # These logs should NOT appear (console handler disabled)
    logger.info(f"Phase {i+1}: Processing items...")
    logger.warning(f"Warning at step {i+1}")
    
    # Update dashboard stats
    dashboard.update_stats(
        phase=f"Phase {i+1}/10",
        files_processed=i+1,
        secrets_found=i,
        errors=0
    )
    dashboard.update_progress("discovery", i+1, 10)
    
    time.sleep(0.3)

# Stop dashboard (console logging should resume)
dashboard.stop()

print("\n✓ Dashboard test complete")
print("\nExpected behavior:")
print("  1. Dashboard updated smoothly without flickering")
print("  2. No console log messages appeared during dashboard")
print("  3. Dashboard had exclusive terminal control")
print("  4. Logs were still written to files (check logs/)")
print("\n" + "="*60)
print("✅ If dashboard appeared stable, integration test PASSED")
print("🚀 Ready for production deployment!")
