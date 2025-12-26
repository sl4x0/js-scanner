import pytest
import asyncio
from jsscanner.utils.net import retry_async, RetryConfig


@pytest.mark.asyncio
async def test_retry_async_succeeds_after_retries():
    calls = {"count": 0}

    @retry_async(max_attempts=3, backoff_base=0.01, backoff_multiplier=1.1, jitter=False)
    async def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise ValueError("transient")
        return "ok"

    result = await flaky()
    assert result == "ok"
    assert calls["count"] == 3


@pytest.mark.asyncio
async def test_retry_async_transient_then_success():
    calls = {"count": 0}

    @retry_async(max_attempts=4, backoff_base=0.01, jitter=False)
    async def flaky_once():
        calls["count"] += 1
        if calls["count"] < 2:
            raise ConnectionError("temporary")
        return "done"

    result = await flaky_once()
    assert result == "done"
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_retry_async_permanent_failure():
    @retry_async(max_attempts=3, backoff_base=0.01, jitter=False)
    async def always_fail():
        raise RuntimeError("permanent")

    with pytest.raises(RuntimeError):
        await always_fail()
