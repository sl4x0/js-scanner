"""
Retry utilities for handling transient failures in network and subprocess operations.

Provides async retry decorators with exponential backoff, jitter, and configurable strategies.
"""

import asyncio
import random
from typing import Callable, Type, Tuple, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        backoff_base: float = 1.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        jitter_range: float = 0.2,
        retry_on_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts (including initial)
            backoff_base: Base delay in seconds for first retry
            backoff_multiplier: Multiplier for exponential backoff (2.0 = double each time)
            jitter: Whether to add random jitter to backoff delays
            jitter_range: Range for jitter as fraction of delay (0.2 = ±20%)
            retry_on_exceptions: Tuple of exception types to retry on
        """
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.jitter_range = jitter_range
        self.retry_on_exceptions = retry_on_exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay before next retry attempt.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: base * (multiplier ^ attempt)
        delay = self.backoff_base * (self.backoff_multiplier ** attempt)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            jitter_amount = delay * self.jitter_range
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0.1, delay)  # Minimum 100ms delay


def retry_async(
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    backoff_multiplier: float = 2.0,
    jitter: bool = True,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    operation_name: Optional[str] = None
):
    """
    Decorator for async functions to add retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts (including initial)
        backoff_base: Base delay in seconds for first retry
        backoff_multiplier: Multiplier for exponential backoff
        jitter: Whether to add random jitter to prevent thundering herd
        retry_on: Tuple of exception types to retry on (None = all exceptions)
        operation_name: Name for logging (defaults to function name)
    
    Example:
        @retry_async(max_attempts=3, backoff_base=1.0, retry_on=(TimeoutError, ConnectionError))
        async def fetch_data(url):
            # Network operation that may fail
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Determine which exceptions to retry on
            exceptions_to_retry = retry_on if retry_on else (Exception,)
            
            # Get operation name for logging
            op_name = operation_name or func.__name__
            
            # Create config
            config = RetryConfig(
                max_attempts=max_attempts,
                backoff_base=backoff_base,
                backoff_multiplier=backoff_multiplier,
                jitter=jitter,
                retry_on_exceptions=exceptions_to_retry
            )
            
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    # Try to execute the function
                    result = await func(*args, **kwargs)
                    
                    # If we're retrying, log success
                    if attempt > 0:
                        logger.info(f"✓ {op_name} succeeded on attempt {attempt + 1}/{max_attempts}")
                    
                    return result
                    
                except exceptions_to_retry as e:
                    last_exception = e
                    
                    # Check if we have more attempts left
                    if attempt < max_attempts - 1:
                        delay = config.calculate_delay(attempt)
                        logger.warning(
                            f"⚠ {op_name} failed (attempt {attempt + 1}/{max_attempts}): {str(e)[:100]} "
                            f"- retrying in {delay:.1f}s"
                        )
                        await asyncio.sleep(delay)
                    else:
                        # Final attempt failed
                        logger.error(
                            f"✗ {op_name} failed after {max_attempts} attempts: {str(e)[:200]}"
                        )
                
                except Exception as e:
                    # Exception not in retry list - fail immediately
                    logger.error(f"✗ {op_name} failed with non-retryable error: {str(e)[:200]}")
                    raise
            
            # All attempts exhausted - raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    backoff_multiplier: float = 2.0,
    jitter: bool = True,
    retry_on: Optional[Tuple[Type[Exception], ...]] = None,
    operation_name: Optional[str] = None,
    shutdown_callback: Optional[Callable[[], bool]] = None
):
    """
    Decorator for synchronous functions to add retry logic with exponential backoff.
    
    Similar to retry_async but for non-async functions.
    
    Args:
        shutdown_callback: Optional callable that returns True if shutdown is requested
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine which exceptions to retry on
            exceptions_to_retry = retry_on if retry_on else (Exception,)
            
            # Get operation name for logging
            op_name = operation_name or func.__name__
            
            # Create config
            config = RetryConfig(
                max_attempts=max_attempts,
                backoff_base=backoff_base,
                backoff_multiplier=backoff_multiplier,
                jitter=jitter,
                retry_on_exceptions=exceptions_to_retry
            )
            
            last_exception = None
            
            for attempt in range(max_attempts):
                # Check for shutdown before each attempt
                if shutdown_callback and shutdown_callback():
                    logger.debug(f"⚠️ {op_name} aborted - shutdown requested")
                    return None  # Return None instead of retrying
                
                try:
                    # Try to execute the function
                    result = func(*args, **kwargs)
                    
                    # If we're retrying, log success
                    if attempt > 0:
                        logger.info(f"✓ {op_name} succeeded on attempt {attempt + 1}/{max_attempts}")
                    
                    return result
                    
                except exceptions_to_retry as e:
                    last_exception = e
                    
                    # Check if we have more attempts left
                    if attempt < max_attempts - 1:
                        # Check shutdown before sleeping
                        if shutdown_callback and shutdown_callback():
                            logger.debug(f"⚠️ {op_name} aborted - shutdown requested")
                            return None
                        
                        delay = config.calculate_delay(attempt)
                        logger.warning(
                            f"⚠ {op_name} failed (attempt {attempt + 1}/{max_attempts}): {str(e)[:100]} "
                            f"- retrying in {delay:.1f}s"
                        )
                        import time
                        time.sleep(delay)
                    else:
                        # Final attempt failed
                        logger.error(
                            f"✗ {op_name} failed after {max_attempts} attempts: {str(e)[:200]}"
                        )
                
                except Exception as e:
                    # Exception not in retry list - fail immediately
                    logger.error(f"✗ {op_name} failed with non-retryable error: {str(e)[:200]}")
                    raise
            
            # All attempts exhausted - raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


# Common retry configurations for different use cases
RETRY_CONFIG_HTTP = {
    'max_attempts': 3,
    'backoff_base': 1.0,
    'backoff_multiplier': 2.0,
    'jitter': True
}

RETRY_CONFIG_SUBPROCESS = {
    'max_attempts': 2,
    'backoff_base': 2.0,
    'backoff_multiplier': 2.0,
    'jitter': False  # Subprocess failures less likely to benefit from jitter
}

RETRY_CONFIG_LIGHT = {
    'max_attempts': 2,
    'backoff_base': 0.5,
    'backoff_multiplier': 2.0,
    'jitter': True
}
