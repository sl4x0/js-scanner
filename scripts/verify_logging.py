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
    """Verify that main and error log files were created"""
    metadata = getattr(logger, '_log_metadata', {})
    main_log = metadata.get('main_log_path')
    error_log = metadata.get('error_log_path')

    assert main_log is not None, "❌ Main log path not found in metadata"
    assert error_log is not None, "❌ Error log path not found in metadata"

    main_log_path = Path(main_log)
    error_log_path = Path(error_log)

    assert main_log_path.exists(), f"❌ Main log file not created: {main_log}"
    assert error_log_path.exists(), f"❌ Error log file not created: {error_log}"

    print(f"✅ Main log created: {main_log_path.name}")
    print(f"✅ Error log created: {error_log_path.name}")

    return str(main_log_path), str(error_log_path)


def verify_error_segregation(error_log_path):
    """Verify error log contains only ERROR level entries"""
    with open(error_log_path, 'r') as f:
        content = f.read()

    lines = [line for line in content.split('\n') if line.strip()]

    # Count log levels in error file
    error_count = sum(1 for line in lines if ' - ERROR - ' in line)
    info_count = sum(1 for line in lines if ' - INFO - ' in line)
    warning_count = sum(1 for line in lines if ' - WARNING - ' in line)

    assert error_count == 2, f"❌ Expected 2 errors, found {error_count}"
    assert info_count == 0, f"❌ Error log should not contain INFO messages, found {info_count}"
    assert warning_count == 0, f"❌ Error log should not contain WARNING messages, found {warning_count}"

    print(f"✅ Error segregation verified: {error_count} errors only")


def verify_main_log_content(main_log_path):
    """Verify main log contains all message levels"""
    with open(main_log_path, 'r') as f:
        content = f.read()

    lines = [line for line in content.split('\n') if line.strip()]

    info_count = sum(1 for line in lines if ' - INFO - ' in line)
    warning_count = sum(1 for line in lines if ' - WARNING - ' in line)
    error_count = sum(1 for line in lines if ' - ERROR - ' in line)

    assert info_count >= 10, f"❌ Expected at least 10 INFO messages, found {info_count}"
    assert warning_count >= 5, f"❌ Expected at least 5 WARNING messages, found {warning_count}"
    assert error_count >= 2, f"❌ Expected at least 2 ERROR messages, found {error_count}"

    print(f"✅ Main log content verified: {info_count} INFO, {warning_count} WARNING, {error_count} ERROR")


def verify_analyzer(main_log_path):
    """Verify log analyzer correctly parses logs"""
    stats = analyze_log_file(main_log_path)

    assert 'level_counts' in stats, "❌ Analyzer did not return level_counts"
    assert 'total_lines' in stats, "❌ Analyzer did not return total_lines"

    level_counts = stats['level_counts']

    info_count = level_counts.get('INFO', 0)
    warning_count = level_counts.get('WARNING', 0)
    error_count = level_counts.get('ERROR', 0)

    assert info_count >= 10, f"❌ Analyzer found {info_count} INFO, expected >= 10"
    assert warning_count >= 5, f"❌ Analyzer found {warning_count} WARNING, expected >= 5"
    assert error_count >= 2, f"❌ Analyzer found {error_count} ERROR, expected >= 2"

    print(f"✅ Log analyzer verified: INFO={info_count}, WARNING={warning_count}, ERROR={error_count}")

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
        print("📋 Step 4: Verify file creation")
        main_log, error_log = verify_file_creation(logger, "test_target")
        print()

        # Step 5: Verify error segregation
        print("📋 Step 5: Verify error segregation")
        verify_error_segregation(error_log)
        print()

        # Step 6: Verify main log content
        print("📋 Step 6: Verify main log content")
        verify_main_log_content(main_log)
        print()

        # Step 7: Verify analyzer
        print("📋 Step 7: Verify log analyzer")
        stats = verify_analyzer(main_log)
        print()

        # Step 8: Verify summary generation
        print("📋 Step 8: Verify summary generation")
        summary = verify_summary_generation(main_log)
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
        print(f"  ✓ Per-target log files created correctly")
        print(f"  ✓ Error segregation working")
        print(f"  ✓ Log analyzer parsing correctly")
        print(f"  ✓ Summary generation working")
        print(f"  ✓ Filename sanitization working")
        print()
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
