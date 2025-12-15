"""
Logger Utility
Colorized console output for the scanner
"""
import logging
import sys
from datetime import datetime
from colorama import Fore, Style, init
from pathlib import Path

# Initialize colorama for Windows support
init(autoreset=True)


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
    
    # File handler (if specified)
    if log_file:
        # Create logs directory if needed
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
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
    logger.info(f"  Secrets Found: {Fore.RED}{stats.get('total_secrets', 0)}{Style.RESET_ALL}")
    logger.info(f"  Duration: {stats.get('scan_duration', 0):.2f}s")
    if stats.get('errors'):
        logger.info(f"  Errors: {len(stats['errors'])}")
    logger.info(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
