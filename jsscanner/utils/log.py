"""
Logger Utility
Colorized console output for the scanner
Enhanced with per-target logging support
"""
import logging
import sys
import io
import os
import re
from datetime import datetime
from typing import Optional, Dict
from colorama import Fore, Style, init
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Initialize colorama for Windows support
init(autoreset=True)

# Fix Windows UTF-8 encoding for console output (must be at module level)
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        # Fallback for older Python or redirected stdout
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except:
            pass  # Keep default if wrapping fails


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str = "jsscanner", log_file: str = None) -> logging.Logger:
    """
    Sets up a logger with console and dual file output (scan.log + errors.log)

    Architecture:
        - Console: INFO level with colors
        - scan.log: DEBUG level (complete telemetry)
        - errors.log: WARNING+ level (error forensics only)

    Args:
        name: Logger name
        log_file: Deprecated. Logs now auto-route to logs/scan.log and logs/errors.log

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # ========== CONSOLE HANDLER ==========
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%y %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # ========== DUAL FILE HANDLERS ==========
    # Define log directory (relative to project root)
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)

    # Detailed formatter for forensic analysis (includes file location)
    detailed_formatter = logging.Formatter(
        '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ========== HANDLER A: Main Log (scan.log) ==========
    # Captures EVERYTHING (DEBUG+) for full scan telemetry
    main_log_path = log_dir / 'scan.log'
    main_handler = RotatingFileHandler(
        str(main_log_path),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    main_handler.setLevel(logging.DEBUG)
    main_handler.setFormatter(detailed_formatter)
    logger.addHandler(main_handler)

    # ========== HANDLER B: Error Log (errors.log) ==========
    # Captures only WARNING+ for error forensics
    error_log_path = log_dir / 'errors.log'
    error_handler = RotatingFileHandler(
        str(error_log_path),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)

    return logger


def log_banner():
    """Prints the scanner banner"""
    banner = f"""
{Fore.CYAN}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              JS SCANNER - Bug Bounty Edition              ║
║                 Context-Aware Secret Hunter               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
    """
    print(banner)


def log_stats(logger: logging.Logger, stats: dict):
    """
    Logs scan statistics

    Args:
        logger: Logger instance
        stats: Dictionary containing scan stats
    """
    logger.info(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
    logger.info(f"{Fore.CYAN}Scan Statistics:{Style.RESET_ALL}")
    logger.info(f"  Files Scanned: {stats.get('total_files', 0)}")

    # Show total findings + verified breakdown (critical for bug bounty triaging)
    total_secrets = stats.get('total_secrets', 0)
    verified_secrets = stats.get('verified_secrets', 0)
    unverified_secrets = total_secrets - verified_secrets

    if total_secrets > 0:
        logger.info(f"  Total Findings: {Fore.RED}{total_secrets}{Style.RESET_ALL} ({verified_secrets} verified, {unverified_secrets} unverified)")
    else:
        logger.info(f"  Secrets Found: {Fore.GREEN}0{Style.RESET_ALL}")

    logger.info(f"  Duration: {stats.get('scan_duration', 0):.2f}s")
    if stats.get('errors'):
        logger.info(f"  Errors: {len(stats['errors'])}")
    logger.info(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """
    Adapter that adds structured context to log messages

    Example:
        logger = StructuredLoggerAdapter(base_logger, {
            'target': 'example.com',
            'scan_id': 'abc123'
        })
        logger.info("File processed", extra={'filename': 'app.js', 'size': 12345})
    """

    def __init__(self, logger: logging.Logger, extra: dict = None):
        """
        Initialize structured logger adapter

        Args:
            logger: Base logger instance
            extra: Dictionary of context fields to add to all log messages
        """
        super().__init__(logger, extra or {})

    def process(self, msg: str, kwargs: dict) -> tuple:
        """
        Process log message and add structured context

        Args:
            msg: Log message
            kwargs: Keyword arguments including 'extra' dict

        Returns:
            Tuple of (message, kwargs)
        """
        # Merge adapter extra with message extra
        extra = self.extra.copy()
        if 'extra' in kwargs:
            extra.update(kwargs['extra'])
        kwargs['extra'] = extra

        # Add structured fields to message for file logging
        if extra and hasattr(self.logger, 'handlers'):
            for handler in self.logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    # Format extra fields as JSON-like string for file logs
                    extra_str = ' | '.join(f"{k}={v}" for k, v in extra.items() if k not in ['color'])
                    if extra_str:
                        msg = f"{msg} [{extra_str}]"
                    break

        return msg, kwargs


def create_structured_logger(name: str, log_file: str = None, context: dict = None) -> StructuredLoggerAdapter:
    """
    Create a structured logger with context

    Args:
        name: Logger name
        log_file: Optional path to log file
        context: Dictionary of context fields to add to all log messages

    Returns:
        Configured StructuredLoggerAdapter instance

    Example:
        logger = create_structured_logger(
            'jsscanner',
            '/path/to/log.txt',
            {'target': 'example.com', 'phase': 'download'}
        )
        logger.info("Processing file", extra={'filename': 'app.js'})
        # Logs: "Processing file [target=example.com | phase=download | filename=app.js]"
    """
    base_logger = setup_logger(name, log_file)
    return StructuredLoggerAdapter(base_logger, context or {})


# ==============================================================================
# PER-TARGET LOGGING SYSTEM (Enhanced)
# ==============================================================================

DEFAULT_LOG_DIR = "logs"
TIMESTAMP_FMT = "%Y-%m-%d_%H-%M-%S"
LOG_FILENAME_FMT = "{target}_{timestamp}.log"
ERROR_FILENAME_FMT = "{target}_errors_{timestamp}.log"


def _sanitize_filename(s: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.

    Removes URL protocols, replaces special characters with underscores,
    and limits length to prevent filesystem issues.

    Args:
        s: String to sanitize (e.g., target name/URL)

    Returns:
        Sanitized filename-safe string

    Examples:
        >>> _sanitize_filename("https://example.com/path")
        'example.com_path'
        >>> _sanitize_filename("api.internal:8080")
        'api.internal_8080'
    """
    # Remove URL protocols
    s = re.sub(r'^https?://', '', s)
    s = re.sub(r'^wss?://', '', s)

    # Replace invalid filesystem characters with underscores
    s = re.sub(r'[<>:"/\\|?*\s]', '_', s)

    # Remove multiple consecutive underscores
    s = re.sub(r'_+', '_', s)

    # Trim leading/trailing underscores and dots
    s = s.strip('_.')

    # Limit length (max 200 chars to leave room for timestamp)
    if len(s) > 200:
        s = s[:200]

    return s or "unknown_target"


def _get_timestamp() -> str:
    """Get current UTC timestamp in standardized format."""
    return datetime.utcnow().strftime(TIMESTAMP_FMT)


def _ensure_log_dir(path: str) -> None:
    """Create log directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def get_target_logger(
    target_name: str,
    log_dir: Optional[str] = None,
    level: int = logging.DEBUG,
    rotation_config: Optional[Dict] = None,
    console_enabled: bool = True
) -> logging.Logger:
    """
    Create a per-target logger - ONE FILE per target + console output.

    This factory creates a logger instance configured with:
    1. Single file handler: WARNING/ERROR/DEBUG only (no INFO - that goes to console)
    2. Console handler: INFO+ for user feedback (scan progress, status updates)

    Architecture:
        - File log: logs/{target}_{timestamp}.log (Level: DEBUG/WARNING/ERROR only, NO INFO)
        - Console: stdout (Level: INFO+, colored, scan progress updates)

    Rationale:
        - INFO = User-facing scan progress → Console only
        - WARNING/ERROR/DEBUG = Technical issues → File only for audit trail
        - Result: ONE log file per target with audit data, console shows scan status

    Args:
        target_name: Target domain/URL (will be sanitized for filename)
        log_dir: Directory to store logs (default: './logs')
        level: Minimum log level for file handler (default: DEBUG)
        rotation_config: Dict with rotation settings:
            - type: 'size' or 'time'
            - For 'size': max_bytes, backup_count
            - For 'time': when, interval, backup_count
            Example: {'type': 'size', 'max_bytes': 10485760, 'backup_count': 5}
        console_enabled: Enable console output (default: True)

    Returns:
        Configured logging.Logger instance with unique name

    Example:
        >>> logger = get_target_logger('example.com')
        >>> logger.info("Scan started")          # → Console only (user sees progress)
        >>> logger.warning("Slow response")      # → File + Console
        >>> logger.error("Failed to fetch URL")  # → File + Console
        # Creates: logs/example.com_2024-01-15_14-30-25.log (warnings/errors only)
    """
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    _ensure_log_dir(log_dir)

    # Sanitize target name for filesystem safety
    safe_target = _sanitize_filename(target_name)
    timestamp = _get_timestamp()

    # Generate single log file path
    log_path = os.path.join(
        log_dir,
        LOG_FILENAME_FMT.format(target=safe_target, timestamp=timestamp)
    )

    # Create unique logger name to avoid conflicts
    logger_name = f"jsscanner.target.{safe_target}.{timestamp}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Capture everything, filter by handlers

    # Prevent duplicate handlers if logger already configured
    if getattr(logger, "_target_configured", False):
        return logger

    # Detailed formatter with file location for forensic analysis
    detailed_formatter = logging.Formatter(
        '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ========== HANDLER 1: File Handler (WARNING/ERROR/DEBUG only, NO INFO) ==========
    # Custom filter to exclude INFO level (user-facing messages go to console only)
    class NoInfoFilter(logging.Filter):
        def filter(self, record):
            return record.levelno != logging.INFO

    if rotation_config and rotation_config.get('type') == 'time':
        # Time-based rotation
        when = rotation_config.get('when', 'midnight')
        interval = rotation_config.get('interval', 1)
        backup_count = rotation_config.get('backup_count', 7)
        file_handler = TimedRotatingFileHandler(
            log_path,
            when=when,
            interval=interval,
            backupCount=backup_count,
            utc=True,
            encoding='utf-8'
        )
    elif rotation_config and rotation_config.get('type') == 'size':
        # Size-based rotation
        max_bytes = rotation_config.get('max_bytes', 10485760)  # 10MB default
        backup_count = rotation_config.get('backup_count', 5)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
    else:
        # No rotation (simple file handler)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')

    file_handler.setLevel(logging.DEBUG)  # Capture DEBUG and above
    file_handler.addFilter(NoInfoFilter())  # Exclude INFO
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # ========== HANDLER 2: Console Handler (INFO+ for user feedback) ==========
    if console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Show INFO+ on console for scan progress
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%m/%d/%y %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Mark as configured to prevent duplicate handlers
    logger._target_configured = True

    # Store metadata for log analyzer
    logger._log_metadata = {
        'target': target_name,
        'safe_target': safe_target,
        'timestamp': timestamp,
        'log_path': log_path
    }

    return logger
