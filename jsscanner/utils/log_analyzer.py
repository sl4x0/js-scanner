"""
Log Analyzer
Post-scan log analysis and summary generation
"""
import re
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging


# Regular expressions for log parsing
LOG_LINE_RE = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+-\s+\[(?P<file>[^\]]+)\]\s+-\s+(?P<level>[A-Z]+)\s+-\s+(?P<message>.+)$'
)


def analyze_log_file(path: str) -> Dict:
    """
    Analyze a single log file and extract statistics.

    Parses log file line by line to count log levels, extract timestamps,
    and identify key events (scan start/end, errors, warnings).

    Args:
        path: Path to log file

    Returns:
        Dictionary with statistics:
            - level_counts: Dict[str, int] - Count per log level
            - total_lines: int - Total log entries
            - first_timestamp: str - First log entry time
            - last_timestamp: str - Last log entry time
            - duration_seconds: float - Scan duration in seconds
            - errors: List[str] - List of error messages
            - warnings: List[str] - List of warning messages

    Example:
        >>> stats = analyze_log_file('logs/example.com_2024-01-15.log')
        >>> print(f"Errors: {stats['level_counts']['ERROR']}")
    """
    stats = {
        'level_counts': {},
        'total_lines': 0,
        'first_timestamp': None,
        'last_timestamp': None,
        'duration_seconds': 0.0,
        'errors': [],
        'warnings': [],
        'file_path': path
    }

    if not os.path.exists(path):
        return stats

    first_dt = None
    last_dt = None

    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                match = LOG_LINE_RE.match(line)
                if match:
                    stats['total_lines'] += 1

                    # Extract timestamp
                    timestamp_str = match.group('timestamp')
                    level = match.group('level')
                    message = match.group('message')

                    # Track first and last timestamps
                    try:
                        dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        if first_dt is None:
                            first_dt = dt
                            stats['first_timestamp'] = timestamp_str
                        last_dt = dt
                        stats['last_timestamp'] = timestamp_str
                    except ValueError:
                        pass

                    # Count log levels
                    stats['level_counts'][level] = stats['level_counts'].get(level, 0) + 1

                    # Collect error and warning messages (limited to first 50 each)
                    if level == 'ERROR' and len(stats['errors']) < 50:
                        stats['errors'].append(message)
                    elif level == 'WARNING' and len(stats['warnings']) < 50:
                        stats['warnings'].append(message)

        # Calculate duration
        if first_dt and last_dt:
            duration = last_dt - first_dt
            stats['duration_seconds'] = duration.total_seconds()

    except Exception as e:
        logging.error(f"Failed to analyze log file {path}: {e}")

    return stats


def aggregate_error_logs(log_files: List[str], output_path: str) -> int:
    """
    Extract all ERROR entries from multiple log files and write to single file.

    Args:
        log_files: List of log file paths to process
        output_path: Path to write aggregated error log

    Returns:
        Number of error entries written

    Example:
        >>> count = aggregate_error_logs(
        ...     ['logs/target1.log', 'logs/target2.log'],
        ...     'logs/all_errors.log'
        ... )
    """
    error_count = 0

    try:
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(f"# Aggregated Error Log - Generated {datetime.utcnow().isoformat()}\n")
            out_f.write(f"# Source files: {len(log_files)}\n")
            out_f.write("=" * 80 + "\n\n")

            for log_file in log_files:
                if not os.path.exists(log_file):
                    continue

                out_f.write(f"\n{'='*80}\n")
                out_f.write(f"Source: {log_file}\n")
                out_f.write(f"{'='*80}\n\n")

                with open(log_file, 'r', encoding='utf-8', errors='ignore') as in_f:
                    for line in in_f:
                        if ' - ERROR - ' in line or ' ERROR ' in line:
                            out_f.write(line)
                            error_count += 1

    except Exception as e:
        logging.error(f"Failed to aggregate error logs: {e}")

    return error_count


def generate_summary_report(
    log_files: List[str],
    output_path: Optional[str] = None
) -> Dict:
    """
    Generate comprehensive summary report from multiple log files.

    Analyzes all provided log files and produces a unified summary with:
    - Total statistics across all scans
    - Per-file breakdown
    - Error and warning aggregation
    - Duration and performance metrics

    Args:
        log_files: List of log file paths to analyze
        output_path: Optional path to write human-readable summary text file

    Returns:
        Dictionary with complete summary statistics

    Example:
        >>> summary = generate_summary_report(
        ...     ['logs/target1.log', 'logs/target2.log'],
        ...     'logs/summary.txt'
        ... )
        >>> print(f"Total errors: {summary['totals']['ERROR']}")
    """
    summary = {
        'files_analyzed': len(log_files),
        'totals': {
            'ERROR': 0,
            'WARNING': 0,
            'INFO': 0,
            'DEBUG': 0,
            'total_lines': 0,
            'total_duration_seconds': 0.0
        },
        'per_file': [],
        'earliest_start': None,
        'latest_end': None
    }

    earliest_dt = None
    latest_dt = None

    # Analyze each log file
    for log_file in log_files:
        file_stats = analyze_log_file(log_file)
        summary['per_file'].append(file_stats)

        # Aggregate totals
        for level, count in file_stats['level_counts'].items():
            summary['totals'][level] = summary['totals'].get(level, 0) + count

        summary['totals']['total_lines'] += file_stats['total_lines']
        summary['totals']['total_duration_seconds'] += file_stats['duration_seconds']

        # Track earliest and latest timestamps
        if file_stats['first_timestamp']:
            try:
                dt = datetime.strptime(file_stats['first_timestamp'], '%Y-%m-%d %H:%M:%S')
                if earliest_dt is None or dt < earliest_dt:
                    earliest_dt = dt
                    summary['earliest_start'] = file_stats['first_timestamp']
            except ValueError:
                pass

        if file_stats['last_timestamp']:
            try:
                dt = datetime.strptime(file_stats['last_timestamp'], '%Y-%m-%d %H:%M:%S')
                if latest_dt is None or dt > latest_dt:
                    latest_dt = dt
                    summary['latest_end'] = file_stats['last_timestamp']
            except ValueError:
                pass

    # Write human-readable summary if output path provided
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("LOG ANALYSIS SUMMARY\n")
                f.write(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Files Analyzed: {summary['files_analyzed']}\n")
                f.write(f"Total Log Entries: {summary['totals']['total_lines']:,}\n")
                f.write(f"Scan Period: {summary['earliest_start']} to {summary['latest_end']}\n")

                if summary['totals']['total_duration_seconds'] > 0:
                    hours = int(summary['totals']['total_duration_seconds'] // 3600)
                    minutes = int((summary['totals']['total_duration_seconds'] % 3600) // 60)
                    seconds = int(summary['totals']['total_duration_seconds'] % 60)
                    f.write(f"Total Duration: {hours}h {minutes}m {seconds}s\n")

                f.write("\n" + "-" * 80 + "\n")
                f.write("LOG LEVEL BREAKDOWN\n")
                f.write("-" * 80 + "\n")

                for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
                    count = summary['totals'].get(level, 0)
                    if count > 0:
                        percentage = (count / summary['totals']['total_lines'] * 100) if summary['totals']['total_lines'] > 0 else 0
                        f.write(f"  {level:10s}: {count:8,} ({percentage:5.2f}%)\n")

                # Per-file breakdown
                if summary['per_file']:
                    f.write("\n" + "-" * 80 + "\n")
                    f.write("PER-FILE STATISTICS\n")
                    f.write("-" * 80 + "\n\n")

                    for file_stats in summary['per_file']:
                        f.write(f"File: {os.path.basename(file_stats['file_path'])}\n")
                        f.write(f"  Lines: {file_stats['total_lines']:,}\n")
                        f.write(f"  Duration: {file_stats['duration_seconds']:.2f}s\n")

                        errors = file_stats['level_counts'].get('ERROR', 0)
                        warnings = file_stats['level_counts'].get('WARNING', 0)

                        if errors > 0:
                            f.write(f"  ⚠️  Errors: {errors}\n")
                        if warnings > 0:
                            f.write(f"  ⚠️  Warnings: {warnings}\n")

                        f.write("\n")

                # Error samples
                if summary['totals']['ERROR'] > 0:
                    f.write("\n" + "-" * 80 + "\n")
                    f.write("SAMPLE ERRORS (first 10)\n")
                    f.write("-" * 80 + "\n\n")

                    error_count = 0
                    for file_stats in summary['per_file']:
                        for error in file_stats['errors']:
                            if error_count >= 10:
                                break
                            f.write(f"  • {error}\n")
                            error_count += 1
                        if error_count >= 10:
                            break

                f.write("\n" + "=" * 80 + "\n")

        except Exception as e:
            logging.error(f"Failed to write summary report: {e}")

    return summary


def cleanup_old_logs(log_dir: str, retention_days: int, dry_run: bool = False) -> List[str]:
    """
    Remove log files older than specified retention period.

    Args:
        log_dir: Directory containing log files
        retention_days: Number of days to retain logs
        dry_run: If True, only report files that would be deleted without deleting

    Returns:
        List of file paths that were deleted (or would be deleted if dry_run=True)

    Example:
        >>> # Delete logs older than 30 days
        >>> deleted = cleanup_old_logs('logs', retention_days=30)
        >>> print(f"Deleted {len(deleted)} old log files")
    """
    if retention_days <= 0:
        return []

    cutoff_time = datetime.now() - timedelta(days=retention_days)
    deleted_files = []

    try:
        log_path = Path(log_dir)
        if not log_path.exists():
            return deleted_files

        for log_file in log_path.glob('*.log'):
            try:
                # Get file modification time
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                if mtime < cutoff_time:
                    if dry_run:
                        logging.info(f"Would delete: {log_file} (age: {(datetime.now() - mtime).days} days)")
                    else:
                        log_file.unlink()
                        logging.info(f"Deleted old log: {log_file}")
                    deleted_files.append(str(log_file))

            except Exception as e:
                logging.warning(f"Failed to process {log_file}: {e}")

    except Exception as e:
        logging.error(f"Failed to cleanup logs in {log_dir}: {e}")

    return deleted_files
