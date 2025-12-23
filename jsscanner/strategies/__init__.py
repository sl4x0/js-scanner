"""Strategy modules - URL discovery methods"""

from .active import ActiveFetcher
from .passive import PassiveFetcher
from .fast import FastFetcher

__all__ = ['ActiveFetcher', 'PassiveFetcher', 'FastFetcher']
