"""Utility modules for JS Scanner"""

from .file_ops import FileOps
from .hashing import calculate_hash, calculate_file_hash, calculate_hash_sync
from .logger import setup_logger, log_banner, log_stats

__all__ = [
    'FileOps',
    'calculate_hash',
    'calculate_file_hash', 
    'calculate_hash_sync',
    'setup_logger',
    'log_banner',
    'log_stats'
]
