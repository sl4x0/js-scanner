import asyncio
import tracemalloc
import tempfile
from pathlib import Path
import shutil
import pytest

from jsscanner.core.engine import ScanEngine


class DummyState:
    def __init__(self):
        self._seen = set()

    def mark_as_scanned_if_new(self, file_hash, url):
        if file_hash in self._seen:
            return False
        self._seen.add(file_hash)
        return True

    def is_processed(self, url):
        return False


class DummyFetcher:
    def __init__(self, out_dir):
        self.out_dir = Path(out_dir)
        self.last_failure_reason = None

    async def fetch_and_write(self, url: str, out_path: str) -> bool:
        # Simulate writing a small file to disk
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, 'wb') as f:
            f.write(b'console.log("hello")\n' * 10)
        return True


@pytest.mark.asyncio
async def test_memory_usage_small(tmp_path):
    # Minimal config
    config = {
        'threads': 10,
        'retry': {'http_requests': 1},
        'minification_detection': {'sample_size': 1000},
        'max_file_size': 5242880
    }

    engine = ScanEngine(config, 'example.com')

    # Override paths to tmp dir
    base = tmp_path / 'result'
    base.mkdir()
    engine.paths['unique_js'] = str(base / 'unique_js')
    Path(engine.paths['unique_js']).mkdir(parents=True, exist_ok=True)

    # Replace state and fetcher with dummies to avoid network
    engine.state = DummyState()
    engine.fetcher = DummyFetcher(engine.paths['unique_js'])

    # Prepare fake URLs
    urls = [f'https://example.com/file{i}.js' for i in range(100)]

    tracemalloc.start()
    snap1 = tracemalloc.take_snapshot()

    files = await engine._download_all_files(urls)

    snap2 = tracemalloc.take_snapshot()
    stats = snap2.compare_to(snap1, 'lineno')
    total_diff = sum(s.size_diff for s in stats)
    total_mb = total_diff / (1024 * 1024)

    # Ensure memory increase is small (metadata only)
    assert total_mb < 50, f"Memory increased too much: {total_mb} MB"

    # Clean up
    shutil.rmtree(str(base))
