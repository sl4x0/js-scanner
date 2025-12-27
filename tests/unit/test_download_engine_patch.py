import asyncio
import tempfile
import shutil
import os
from pathlib import Path

from jsscanner.core.subengines import DownloadEngine


class FakeState:
    def __init__(self):
        self.seen = set()

    def mark_as_scanned_if_new(self, file_hash, url):
        if file_hash in self.seen:
            return False
        self.seen.add(file_hash)
        return True


class FakeFetcher:
    def __init__(self):
        self.last_failure_reason = None

    async def fetch_and_write(self, url, out_path):
        # Create a small JS file to simulate download
        try:
            Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(b"// test js content\nconsole.log('hello')\n")
            return True
        except Exception:
            self.last_failure_reason = 'write_error'
            return False


class DummyEngine:
    def __init__(self, unique_dir):
        self.config = {'verbose': False}
        self.logger = self
        self.paths = {'unique_js': unique_dir}
        self.fetcher = FakeFetcher()
        self.state = FakeState()
        self.stats = {
            'network_errors': {'timeouts':0,'dns_errors':0,'connection_refused':0,'ssl_errors':0,'rate_limits':0,'http_errors':0},
            'failures': {'timeout':0,'http_error':0,'duplicates':0},
            'total_files': 0
        }
        self.shutdown_requested = False
        self._manifests = []

    def info(self, *args, **kwargs):
        pass

    def debug(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def _is_valid_js_url(self, url):
        return url.startswith('http') and '.js' in url

    def _is_target_domain(self, url):
        return True

    def _save_file_manifest(self, url, file_hash, hash_filename, is_minified):
        self._manifests.append({'url': url, 'hash': file_hash, 'filename': hash_filename, 'is_minified': is_minified})

    def _log_progress(self, *args, **kwargs):
        pass

    def _is_minified(self, sample: str) -> bool:
        # Simple heuristic for tests
        return False


def test_download_all_basic_flow(tmp_path):
    unique_dir = str(tmp_path / 'unique_js')
    engine = DummyEngine(unique_dir)

    dl = DownloadEngine(engine)

    urls = ['https://example.com/app.js']

    results = asyncio.run(dl.download_all(urls))

    # One file should be downloaded and present in manifests
    assert isinstance(results, list)
    assert len(engine._manifests) == 1
    manifest = engine._manifests[0]
    stored_path = Path(engine.paths['unique_js']) / manifest['filename']
    assert stored_path.exists()
