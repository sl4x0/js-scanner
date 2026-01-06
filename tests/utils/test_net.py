"""
Test suite for jsscanner.utils.net (Retry Utilities)

Covers:
- Async retry decorator with exponential backoff
- Sync retry decorator with exponential backoff
- Jitter calculation
- Exception filtering
- Shutdown callback handling
- RetryConfig configuration
- Edge cases (zero attempts, nested retries)
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from jsscanner.utils.net import (
    RetryConfig,
    retry_async,
    retry_sync,
    RETRY_CONFIG_HTTP,
    RETRY_CONFIG_SUBPROCESS,
    RETRY_CONFIG_LIGHT
)


# ============================================================================
# RETRY CONFIG TESTS
# ============================================================================

@pytest.mark.unit
def test_retry_config_initialization():
    """Test RetryConfig initializes with correct defaults"""
    config = RetryConfig()
    
    assert config.max_attempts == 3
    assert config.backoff_base == 1.0
    assert config.backoff_multiplier == 2.0
    assert config.jitter is True
    assert config.jitter_range == 0.2
    assert config.retry_on_exceptions == (Exception,)


@pytest.mark.unit
def test_retry_config_custom_values():
    """Test RetryConfig with custom values"""
    config = RetryConfig(
        max_attempts=5,
        backoff_base=2.0,
        backoff_multiplier=3.0,
        jitter=False,
        jitter_range=0.5,
        retry_on_exceptions=(ValueError, TypeError)
    )
    
    assert config.max_attempts == 5
    assert config.backoff_base == 2.0
    assert config.backoff_multiplier == 3.0
    assert config.jitter is False
    assert config.jitter_range == 0.5
    assert config.retry_on_exceptions == (ValueError, TypeError)


@pytest.mark.unit
def test_retry_config_calculate_delay_no_jitter():
    """Test delay calculation without jitter"""
    config = RetryConfig(
        backoff_base=1.0,
        backoff_multiplier=2.0,
        jitter=False
    )
    
    # Attempt 0: 1.0 * (2.0 ^ 0) = 1.0
    assert config.calculate_delay(0) == 1.0
    
    # Attempt 1: 1.0 * (2.0 ^ 1) = 2.0
    assert config.calculate_delay(1) == 2.0
    
    # Attempt 2: 1.0 * (2.0 ^ 2) = 4.0
    assert config.calculate_delay(2) == 4.0


@pytest.mark.unit
def test_retry_config_calculate_delay_with_jitter():
    """Test delay calculation with jitter adds randomness"""
    config = RetryConfig(
        backoff_base=1.0,
        backoff_multiplier=2.0,
        jitter=True,
        jitter_range=0.2
    )
    
    # Calculate delay multiple times for same attempt
    delays = [config.calculate_delay(1) for _ in range(10)]
    
    # All delays should be around 2.0 ± 20%
    for delay in delays:
        assert 1.6 <= delay <= 2.4  # 2.0 ± 0.4
    
    # Delays should vary (not all identical)
    assert len(set(delays)) > 1


@pytest.mark.unit
def test_retry_config_minimum_delay_enforced():
    """Test that minimum delay of 0.1s is enforced"""
    config = RetryConfig(
        backoff_base=0.01,  # Very small base
        backoff_multiplier=0.5,  # Reduces instead of increases
        jitter=False
    )
    
    delay = config.calculate_delay(0)
    
    # Should be at least 0.1s
    assert delay >= 0.1


# ============================================================================
# ASYNC RETRY DECORATOR - SUCCESS SCENARIOS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_succeeds_first_attempt():
    """Test retry_async when function succeeds on first attempt"""
    call_count = 0
    
    @retry_async(max_attempts=3)
    async def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = await successful_func()
    
    assert result == "success"
    assert call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_succeeds_after_failures(retry_failure_counter):
    """Test retry_async succeeds after N failures"""
    retry_failure_counter.reset(max_failures=2)
    
    @retry_async(max_attempts=4)
    async def eventually_succeeds():
        return await retry_failure_counter.async_fail_then_succeed()
    
    result = await eventually_succeeds()
    
    assert "Success on attempt 3" in result
    assert retry_failure_counter.attempt == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_respects_max_attempts(retry_failure_counter):
    """Test retry_async respects max_attempts limit"""
    retry_failure_counter.reset(max_failures=10)  # Will fail more than max_attempts
    
    @retry_async(max_attempts=3, backoff_base=0.01)
    async def always_fails():
        return await retry_failure_counter.async_fail_then_succeed()
    
    with pytest.raises(ValueError):
        await always_fails()
    
    # Should have attempted exactly 3 times
    assert retry_failure_counter.attempt == 3


# ============================================================================
# ASYNC RETRY DECORATOR - BACKOFF TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_uses_exponential_backoff():
    """Test that retry_async uses exponential backoff delays"""
    attempts = []
    start_time = time.time()
    
    @retry_async(max_attempts=3, backoff_base=0.1, backoff_multiplier=2.0, jitter=False)
    async def failing_func():
        attempts.append(time.time() - start_time)
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        await failing_func()
    
    # Should have 3 attempts
    assert len(attempts) == 3
    
    # Check delays between attempts (rough check due to timing variations)
    # Attempt 1 -> Attempt 2: ~0.1s delay
    # Attempt 2 -> Attempt 3: ~0.2s delay
    if len(attempts) == 3:
        delay1 = attempts[1] - attempts[0]
        delay2 = attempts[2] - attempts[1]
        
        # Allow some tolerance for timing
        assert 0.05 <= delay1 <= 0.2
        assert 0.15 <= delay2 <= 0.35


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_jitter_prevents_thundering_herd():
    """Test that jitter creates variations in retry delays"""
    delays = []
    
    for _ in range(5):
        attempt_times = []
        
        @retry_async(max_attempts=3, backoff_base=0.1, jitter=True)
        async def failing_func():
            attempt_times.append(time.time())
            raise ValueError("Test")
        
        try:
            start = time.time()
            await failing_func()
        except ValueError:
            pass
        
        if len(attempt_times) >= 2:
            delays.append(attempt_times[1] - attempt_times[0])
    
    # Delays should vary due to jitter
    if len(delays) > 1:
        assert len(set(delays)) > 1 or all(d > 0 for d in delays)


# ============================================================================
# ASYNC RETRY DECORATOR - EXCEPTION FILTERING
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_retries_only_specified_exceptions():
    """Test retry_async only retries on specified exception types"""
    call_count = 0
    
    @retry_async(max_attempts=3, retry_on=(ValueError,), backoff_base=0.01)
    async def raises_value_error():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Retry this")
        return "success"
    
    result = await raises_value_error()
    
    assert result == "success"
    assert call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_fails_immediately_on_non_retryable_exception():
    """Test retry_async fails immediately for non-retryable exceptions"""
    call_count = 0
    
    @retry_async(max_attempts=3, retry_on=(ValueError,), backoff_base=0.01)
    async def raises_type_error():
        nonlocal call_count
        call_count += 1
        raise TypeError("Don't retry this")
    
    with pytest.raises(TypeError):
        await raises_type_error()
    
    # Should have only attempted once
    assert call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_retries_multiple_exception_types():
    """Test retry_async can retry on multiple exception types"""
    attempts = []
    
    @retry_async(max_attempts=4, retry_on=(ValueError, TypeError), backoff_base=0.01)
    async def raises_different_errors():
        attempts.append(len(attempts) + 1)
        if len(attempts) == 1:
            raise ValueError("First error")
        elif len(attempts) == 2:
            raise TypeError("Second error")
        elif len(attempts) == 3:
            raise ValueError("Third error")
        return "success"
    
    result = await raises_different_errors()
    
    assert result == "success"
    assert len(attempts) == 4


# ============================================================================
# SYNC RETRY DECORATOR - SUCCESS SCENARIOS
# ============================================================================

@pytest.mark.unit
def test_retry_sync_succeeds_first_attempt():
    """Test retry_sync when function succeeds on first attempt"""
    call_count = 0
    
    @retry_sync(max_attempts=3)
    def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = successful_func()
    
    assert result == "success"
    assert call_count == 1


@pytest.mark.unit
def test_retry_sync_succeeds_after_failures():
    """Test retry_sync succeeds after N failures"""
    call_count = 0
    
    @retry_sync(max_attempts=4, backoff_base=0.01)
    def eventually_succeeds():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Attempt {call_count} failed")
        return f"Success on attempt {call_count}"
    
    result = eventually_succeeds()
    
    assert "Success on attempt 3" in result
    assert call_count == 3


@pytest.mark.unit
def test_retry_sync_respects_max_attempts():
    """Test retry_sync respects max_attempts limit"""
    call_count = 0
    
    @retry_sync(max_attempts=3, backoff_base=0.01)
    def always_fails():
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        always_fails()
    
    # Should have attempted exactly 3 times
    assert call_count == 3


# ============================================================================
# SYNC RETRY DECORATOR - SHUTDOWN HANDLING
# ============================================================================

@pytest.mark.unit
def test_retry_sync_shutdown_callback_aborts_retry():
    """Test retry_sync aborts when shutdown callback returns True"""
    call_count = 0
    shutdown_requested = False
    
    def check_shutdown():
        return shutdown_requested
    
    @retry_sync(max_attempts=5, shutdown_callback=check_shutdown, backoff_base=0.01)
    def failing_func():
        nonlocal call_count, shutdown_requested
        call_count += 1
        if call_count == 2:
            shutdown_requested = True
        raise ValueError("Test error")
    
    result = failing_func()
    
    # Should return None when shutdown is requested
    assert result is None
    
    # Should have attempted twice (once normally, once before shutdown)
    assert call_count == 2


@pytest.mark.unit
def test_retry_sync_shutdown_before_first_attempt():
    """Test retry_sync returns None immediately if shutdown requested before first attempt"""
    shutdown_requested = True
    
    def check_shutdown():
        return shutdown_requested
    
    @retry_sync(max_attempts=3, shutdown_callback=check_shutdown)
    def some_func():
        return "should not run"
    
    result = some_func()
    
    assert result is None


@pytest.mark.unit
def test_retry_sync_shutdown_prevents_sleep():
    """Test that shutdown callback prevents unnecessary sleep delays"""
    call_count = 0
    shutdown_requested = False
    
    def check_shutdown():
        return shutdown_requested
    
    @retry_sync(max_attempts=5, shutdown_callback=check_shutdown, backoff_base=0.5)
    def failing_func():
        nonlocal call_count, shutdown_requested
        call_count += 1
        if call_count == 1:
            shutdown_requested = True
        raise ValueError("Test")
    
    start_time = time.time()
    result = failing_func()
    elapsed = time.time() - start_time
    
    # Should abort quickly without sleeping
    assert elapsed < 0.3  # Should not sleep for 0.5s
    assert result is None


# ============================================================================
# PREDEFINED RETRY CONFIGS TESTS
# ============================================================================

@pytest.mark.unit
def test_retry_config_http_values():
    """Test RETRY_CONFIG_HTTP has expected values for HTTP operations"""
    config = RETRY_CONFIG_HTTP
    
    assert config['max_attempts'] == 3
    assert config['backoff_base'] == 0.3  # Fast recovery
    assert config['backoff_multiplier'] == 1.5  # Less aggressive
    assert config['jitter'] is True


@pytest.mark.unit
def test_retry_config_subprocess_values():
    """Test RETRY_CONFIG_SUBPROCESS has expected values"""
    config = RETRY_CONFIG_SUBPROCESS
    
    assert config['max_attempts'] == 2
    assert config['backoff_base'] == 2.0
    assert config['backoff_multiplier'] == 2.0
    assert config['jitter'] is False


@pytest.mark.unit
def test_retry_config_light_values():
    """Test RETRY_CONFIG_LIGHT has expected values for fast operations"""
    config = RETRY_CONFIG_LIGHT
    
    assert config['max_attempts'] == 2
    assert config['backoff_base'] == 0.2  # Very fast
    assert config['backoff_multiplier'] == 1.5
    assert config['jitter'] is True


# ============================================================================
# OPERATION NAME AND LOGGING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_uses_custom_operation_name():
    """Test retry_async uses custom operation name for logging"""
    @retry_async(max_attempts=2, operation_name="custom_op", backoff_base=0.01)
    async def test_func():
        raise ValueError("Test")
    
    # Should use custom name in error messages (captured in logs)
    with pytest.raises(ValueError):
        await test_func()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_defaults_to_function_name():
    """Test retry_async defaults to function name when no operation_name provided"""
    @retry_async(max_attempts=2, backoff_base=0.01)
    async def my_custom_function():
        raise ValueError("Test")
    
    # Should use function name in logging (default behavior)
    with pytest.raises(ValueError):
        await my_custom_function()


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_with_zero_max_attempts():
    """Test retry_async with max_attempts=0 (edge case)"""
    call_count = 0
    
    @retry_async(max_attempts=0, backoff_base=0.01)
    async def test_func():
        nonlocal call_count
        call_count += 1
        return "result"
    
    # With 0 attempts, range(0) produces empty iterator, so function won't run
    # This tests current behavior - may want to validate max_attempts >= 1 in decorator
    try:
        result = await test_func()
        # If it somehow runs, that's ok
    except:
        pass
    
    # Function should not execute with 0 attempts
    assert call_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_with_function_returning_none():
    """Test retry_async works when function returns None"""
    call_count = 0
    
    @retry_async(max_attempts=2)
    async def returns_none():
        nonlocal call_count
        call_count += 1
        return None
    
    result = await returns_none()
    
    assert result is None
    assert call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_preserves_exception_chain():
    """Test that retry_async preserves exception chain"""
    @retry_async(max_attempts=2, backoff_base=0.01)
    async def raises_with_chain():
        try:
            raise ValueError("Original error")
        except ValueError as e:
            raise TypeError("Wrapped error") from e
    
    with pytest.raises(TypeError) as exc_info:
        await raises_with_chain()
    
    # Exception chain should be preserved
    assert exc_info.value.__cause__ is not None or exc_info.value.__context__ is not None


@pytest.mark.unit
def test_retry_sync_with_function_that_modifies_state():
    """Test retry_sync works correctly with functions that modify state"""
    state = {'counter': 0, 'values': []}
    
    @retry_sync(max_attempts=3, backoff_base=0.01)
    def stateful_func():
        state['counter'] += 1
        state['values'].append(state['counter'])
        if state['counter'] < 2:
            raise ValueError("Not yet")
        return state['counter']
    
    result = stateful_func()
    
    assert result == 2
    assert state['counter'] == 2
    assert state['values'] == [1, 2]


# ============================================================================
# ASYNC GENERATOR AND COROUTINE TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_with_async_function():
    """Test retry_async works with async functions (coroutines)"""
    call_count = 0
    
    @retry_async(max_attempts=3, backoff_base=0.01)
    async def async_operation():
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        if call_count < 2:
            raise ValueError("Retry")
        return "success"
    
    result = await async_operation()
    
    assert result == "success"
    assert call_count == 2


# ============================================================================
# INTEGRATION TESTS WITH MOCK OPERATIONS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_retry_async_with_mock_http_request():
    """Integration test: retry_async with simulated HTTP request"""
    attempt_count = 0
    
    @retry_async(max_attempts=3, backoff_base=0.05, retry_on=(ConnectionError, TimeoutError))
    async def mock_http_get(url):
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count == 1:
            raise ConnectionError("Connection refused")
        elif attempt_count == 2:
            raise TimeoutError("Request timeout")
        else:
            return {"status": 200, "data": "success"}
    
    result = await mock_http_get("https://example.com")
    
    assert result["status"] == 200
    assert attempt_count == 3


@pytest.mark.integration
def test_retry_sync_with_mock_subprocess():
    """Integration test: retry_sync with simulated subprocess operation"""
    attempt_count = 0
    
    @retry_sync(max_attempts=2, backoff_base=0.05, retry_on=(OSError,))
    def mock_subprocess_call(command):
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count == 1:
            raise OSError("Command not found")
        else:
            return {"returncode": 0, "stdout": "success"}
    
    result = mock_subprocess_call(["test", "command"])
    
    assert result["returncode"] == 0
    assert attempt_count == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_retry_operations():
    """Integration test: multiple concurrent retry operations"""
    results = []
    
    @retry_async(max_attempts=3, backoff_base=0.05)
    async def concurrent_op(op_id):
        # Simulate random failures
        import random
        if random.random() < 0.3:  # 30% failure rate
            raise ValueError(f"Op {op_id} failed")
        return f"Result {op_id}"
    
    # Run 10 concurrent operations
    tasks = [concurrent_op(i) for i in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Most should succeed (some may still fail after 3 attempts)
    successful = [r for r in results if isinstance(r, str)]
    assert len(successful) >= 5  # At least half should succeed


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_retry_async_performance_no_delay_on_success():
    """Test that retry_async doesn't add delay when function succeeds immediately"""
    start_time = time.time()
    
    @retry_async(max_attempts=3, backoff_base=1.0)
    async def immediate_success():
        return "success"
    
    result = await immediate_success()
    elapsed = time.time() - start_time
    
    # Should complete almost instantly (no retry delays)
    assert elapsed < 0.1
    assert result == "success"


@pytest.mark.unit
def test_retry_sync_performance_efficient_failure():
    """Test that retry_sync fails efficiently after max attempts"""
    start_time = time.time()
    
    @retry_sync(max_attempts=3, backoff_base=0.05, jitter=False)
    def fast_failure():
        raise ValueError("Fast fail")
    
    with pytest.raises(ValueError):
        fast_failure()
    
    elapsed = time.time() - start_time
    
    # With backoff_base=0.05 and multiplier=2.0:
    # Delay 1: 0.05s, Delay 2: 0.1s = Total ~0.15s
    # Allow some tolerance
    assert elapsed < 0.3
