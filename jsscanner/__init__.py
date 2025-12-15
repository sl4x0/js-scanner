"""
JS Scanner - Context-Aware JavaScript Secret Hunter
"""

__version__ = '1.0.0'
__author__ = 'Bug Bounty Hunter'
__description__ = 'Context-aware JavaScript scanner for bug bounty hunting'

from .core.engine import ScanEngine
from .core.state_manager import StateManager
from .core.notifier import DiscordNotifier

__all__ = ['ScanEngine', 'StateManager', 'DiscordNotifier']
