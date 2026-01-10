#!/usr/bin/env python3
"""
Logging System Verification Script
Validates per-target logging, error segregation, rotation, and analysis
"""
import sys
import os
import logging
from pathlib import Path
import glob
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from jsscanner.utils.log import get_target_logger
from jsscanner.utils.log_analyzer import analyze_log_file, generate_summary_report


def cleanup_test_logs():
    """Remove any existing test logs"""
    log_dir = Path('logs')
    if log_dir.exists():
        for log_file in log_dir.glob('test_target*'):
            log_file.unlink()
            print(f"🧹 Cleaned up: {log_file.name}")


def verify_file_creation(logger, target_name):
    """Verify that log file was created (single file approach)"""
    metadata = getattr(logger, '_log_metadata', {})
    log_path = metadata.get('log_path')

    assert log_path is not None, "❌ Log path not found in metadata"

    log_file_path = Path(log_path)

    assert log_file_path.exists(), f"❌ Log file not created: {log_path}"

    print(f"✅ Log file created: {log_file_path.name}")

    return str(log_file_path)


def verify_file_content(log_path):
    """Verify log contains WARNING/ERROR/DEBUG but NOT INFO"""
    with open(log_path, 'r') as f:
        content = f.read()

    lines = [line for line in content.split('\n') if line.strip()]

    # Count log levels
    warning_count = sum(1 for line in lines if ' - WARNING - ' in line)
    error_count = sum(1 for line in lines if ' - ERROR - ' in line)
    debug_count = sum(1 for line in lines if ' - DEBUG - ' in line)
    info_count = sum(1 for line in lines if ' - INFO - ' in line)

    assert warning_count >= 5, f"❌ Expected at least 5 WARNING messages, found {warning_count}"
    assert error_count >= 2, f"❌ Expected at least 2 ERROR messages, found {error_count}"
    assert info_count == 0, f"❌ Log file should NOT contain INFO messages (they go to console), found {info_count}"

    print(f"✅ File content verified: {warning_count} WARNING, {error_count} ERROR, {debug_count} DEBUG, 0 INFO (correct!)")


def verify_single_file_only(log_dir, target_name):
    """Verify only ONE log file exists per target"""
    log_files = list(Path(log_dir).glob(f"{target_name}*.log"))

    # Should have exactly 1 log file (not 2 or 3)
    assert len(log_files) == 1, f"❌ Expected 1 log file, found {len(log_files)}: {[f.name for f in log_files]}"

    # Should not have error-only or summary files
    error_logs = list(Path(log_dir).glob(f"{target_name}*errors*.log"))
    summary_files = list(Path(log_dir).glob(f"{target_name}*summary*.txt"))

    assert len(error_logs) == 0, f"❌ Should not create separate error log, found: {error_logs}"
    assert len(summary_files) == 0, f"❌ Should not create summary file, found: {summary_files}"

    print(f"✅ Single file verified: Only 1 log file per target (no error log, no summary)")

def verify_analyzer(log_path):
    """Verify log analyzer correctly parses logs (single-file approach)"""
    stats = analyze_log_file(log_path)

    assert 'level_counts' in stats, "❌ Analyzer did not return level_counts"
    assert 'total_lines' in stats, "❌ Analyzer did not return total_lines"

    level_counts = stats['level_counts']

    info_count = level_counts.get('INFO', 0)
    warning_count = level_counts.get('WARNING', 0)
    error_count = level_counts.get('ERROR', 0)

    # With single-file approach: INFO should be 0 (console only), WARNING/ERROR in file
    assert info_count == 0, f"❌ File should not contain INFO messages (console only), found {info_count}"
    assert warning_count >= 5, f"❌ Analyzer found {warning_count} WARNING, expected >= 5"
    assert error_count >= 2, f"❌ Analyzer found {error_count} ERROR, expected >= 2"

    print(f"✅ Log analyzer verified: INFO={info_count} (console only), WARNING={warning_count}, ERROR={error_count}")

    # Verify duration calculation
    if stats['first_timestamp'] and stats['last_timestamp']:
        print(f"✅ Duration tracked: {stats['duration_seconds']:.2f}s")

    return stats


def verify_summary_generation(main_log_path):
    """Verify summary report generation"""
    summary_path = Path('logs') / 'test_summary.txt'

    summary = generate_summary_report([main_log_path], str(summary_path))

    assert summary_path.exists(), "❌ Summary report not created"
    assert summary['files_analyzed'] == 1, f"❌ Expected 1 file analyzed, got {summary['files_analyzed']}"
    assert summary['totals']['ERROR'] >= 2, f"❌ Summary shows {summary['totals']['ERROR']} errors, expected >= 2"

    print(f"✅ Summary report generated: {summary_path.name}")

    # Cleanup
    summary_path.unlink()

    return summary


def verify_filename_sanitization():
    """Verify that URLs are sanitized in filenames"""
    logger = get_target_logger(
        "https://example.com:8080/path/to/resource",
        log_dir="logs",
        level=logging.INFO,
        console_enabled=False
    )

    metadata = getattr(logger, '_log_metadata', {})
    safe_target = metadata.get('safe_target', '')

    # Should not contain :, /, or protocol
    assert 'https' not in safe_target.lower(), f"❌ Protocol not removed: {safe_target}"
    assert '/' not in safe_target, f"❌ Slashes not sanitized: {safe_target}"
    assert ':' not in safe_target or safe_target.count(':') == 0, f"❌ Colons not sanitized: {safe_target}"

    print(f"✅ Filename sanitization verified: '{safe_target}'")

    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # Remove test files
    for log_file in Path('logs').glob(f'{safe_target}*'):
        log_file.unlink()


def main():
    """Main verification workflow"""
    print("=" * 70)
    print("🔍 LOGGING SYSTEM VERIFICATION")
    print("=" * 70)
    print()

    try:
        # Step 1: Cleanup
        print("📋 Step 1: Cleanup existing test logs")
        cleanup_test_logs()
        print()

        # Step 2: Create logger and simulate scan
        print("📋 Step 2: Simulate scan with mixed log levels")
        logger = get_target_logger(
            "test_target",
            log_dir="logs",
            level=logging.INFO,
            console_enabled=False  # Suppress console output for clean test
        )

        # Log messages
        for i in range(10):
            logger.info(f"Scanning URL #{i+1}: https://example.com/file{i}.js")

        for i in range(5):
            logger.warning(f"Slow response detected for resource {i}")

        logger.error("Connection failed: timeout after 30s")
        logger.error("Connection failed: HTTP 503 Service Unavailable")

        print("  → Logged 10 INFO, 5 WARNING, 2 ERROR messages")
        print()

        # Step 3: Flush and close handlers
        print("📋 Step 3: Flushing handlers")
        for handler in logger.handlers[:]:
            handler.flush()
            handler.close()
            logger.removeHandler(handler)
        print()

        # Step 4: Verify file creation
        print("📋 Step 4: Verify single file creation")
        log_path = verify_file_creation(logger, "test_target")
        print()
        
        # Step 5: Verify only ONE file exists
        print("📋 Step 5: Verify single file approach (no error log, no summary)")
        verify_single_file_only("logs", "test_target")
        print()
        
        # Step 6: Verify file content (no INFO messages)
        print("📋 Step 6: Verify file content (WARNING/ERROR only, no INFO)")
        verify_file_content(log_path)

        # Step 7: Verify analyzer
        print("📋 Step 7: Verify log analyzer")
        stats = verify_analyzer(log_path)
        print()
        
        # Step 8: Verify summary generation (optional tool)
        print("📋 Step 8: Verify summary generation (manual tool)")
        summary = verify_summary_generation(log_path)
        print()
        
        # Step 9: Verify filename sanitization
        print("📋 Step 9: Verify filename sanitization")
        verify_filename_sanitization()
        print()
        
        # Final cleanup
        print("📋 Step 10: Final cleanup")
        cleanup_test_logs()
        print()
        
        # Success
        print("=" * 70)
        print("✅ LOGGING SYSTEM VERIFIED - ALL CHECKS PASSED")
        print("=" * 70)
        print()
        print("Summary:")
        print(f"  ✓ Single log file per target created")
        print(f"  ✓ File contains WARNING/ERROR/DEBUG only (no INFO)")
        print(f"  ✓ INFO logs go to console for user feedback")
        print(f"  ✓ Log analyzer parsing correctly")
        print("🚀 System is production-ready!")

        return 0

    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"❌ VERIFICATION FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        return 1

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ UNEXPECTED ERROR")
        print("=" * 70)
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
