import asyncio
import hashlib
from jsscanner.utils.hashing import calculate_hash_sync, calculate_hash
from jsscanner.utils.hashing import calculate_file_hash
import tempfile
from pathlib import Path


def test_calculate_hash_sync():
    s = "hello world"
    assert calculate_hash_sync(s) == hashlib.md5(s.encode('utf-8')).hexdigest()


import pytest

@pytest.mark.asyncio
async def test_calculate_hash_async():
    s = "async hello"
    expected = hashlib.md5(s.encode('utf-8')).hexdigest()
    got = await calculate_hash(s)
    assert got == expected


def test_calculate_file_hash(tmp_path):
    content = b"file content for hashing"
    p = tmp_path / "test.bin"
    p.write_bytes(content)
    # calculate_file_hash is async - run in event loop
    import asyncio

    got = asyncio.run(calculate_file_hash(str(p)))
    expected = hashlib.md5(content).hexdigest()
    assert got == expected
