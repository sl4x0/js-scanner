"""
Logger Utility
Colorized console output for the scanner
"""
import logging
import sys
import io
from datetime import datetime
from colorama import Fore, Style, init
from pathlib import Path
from logging.handlers import RotatingFileHandler

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
    Sets up a logger with console and optional file output
    
    Args:
        name: Logger name
        log_file: Optional path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified) - Issue #17: Use rotating file handler
    if log_file:
        # Create logs directory if needed
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Issue #17: Use RotatingFileHandler with 10MB max size and 5 backup files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        # Only log WARNING and above to file (exclude INFO to reduce file size)
        file_handler.setLevel(logging.WARNING)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
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
