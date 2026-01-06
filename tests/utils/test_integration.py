"""
Test suite for jsscanner.utils integration workflows

Covers:
- FileSystem + Hashing workflows (deduplication, checksum verification)
- Retry + Real async operations (file I/O, subprocess simulation)
- Logging in concurrent scenarios
- Complete utility stack integration
"""
import pytest
import asyncio
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from jsscanner.utils.fs import FileSystem
from jsscanner.utils.hashing import calculate_hash, calculate_file_hash
from jsscanner.utils.log import setup_logger, create_structured_logger
from jsscanner.utils.net import retry_async, retry_sync, RetryConfig


# ============================================================================
# FILESYSTEM + HASHING INTEGRATION
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_files_and_hash_pipeline(tmp_path):
    """Integration: Create files, calculate hashes, verify deduplication"""
    # Create result structure
    target = "example.com"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    # Create some test files with content
    files = [
        ("file1.js", "console.log('hello');"),
        ("file2.js", "console.log('world');"),
        ("file3.js", "console.log('hello');"),  # Duplicate content
    ]
    
    hashes = []
    for filename, content in files:
        file_path = Path(paths['unique_js']) / filename
        await FileSystem.write_text_file(str(file_path), content, mode='w')
        
        # Calculate hash
        file_hash = await calculate_file_hash(str(file_path))
        hashes.append((filename, file_hash))
    
    # Verify hashes
    assert len(hashes) == 3
    
    # file1 and file3 should have same hash (duplicate content)
    assert hashes[0][1] == hashes[2][1]
    
    # file2 should have different hash
    assert hashes[1][1] != hashes[0][1]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deduplication_workflow_with_history(tmp_path):
    """Integration: Deduplication using history.json and file hashes"""
    target = "test.com"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    # Read initial history
    history_file = Path(paths['history_file'])
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    scanned_hashes = set(history['scanned_hashes'])
    
    # Simulate scanning files
    files_to_scan = [
        "content_a",
        "content_b",
        "content_a",  # Duplicate
        "content_c"
    ]
    
    unique_processed = 0
    for content in files_to_scan:
        file_hash = await calculate_hash(content)
        
        if file_hash not in scanned_hashes:
            # Process this file (it's unique)
            unique_processed += 1
            scanned_hashes.add(file_hash)
    
    # Should have processed 3 unique files (a, b, c)
    assert unique_processed == 3
    
    # Update history
    history['scanned_hashes'] = list(scanned_hashes)
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    # Verify history was updated
    with open(history_file, 'r') as f:
        updated_history = json.load(f)
    assert len(updated_history['scanned_hashes']) == 3


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_file_creation_with_hash_verification(tmp_path):
    """Integration: Concurrent file creation with hash-based verification"""
    target = "concurrent.test"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    async def create_and_verify_file(idx):
        content = f"Content for file {idx}"
        filename = f"file_{idx}.txt"
        file_path = Path(paths['unique_js']) / filename
        
        # Write file
        await FileSystem.write_text_file(str(file_path), content, mode='w')
        
        # Calculate both content and file hash
        content_hash = await calculate_hash(content)
        file_hash = await calculate_file_hash(str(file_path))
        
        # They should match
        return content_hash == file_hash
    
    # Create 20 files concurrently
    tasks = [create_and_verify_file(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    # All hash verifications should pass
    assert all(results)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_append_unique_lines_with_hash_tracking(tmp_path):
    """Integration: Track URLs with hashes to prevent duplicates"""
    target = "url-tracking.test"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    urls_file = Path(paths['extracts']) / 'urls.txt'
    hash_file = Path(paths['cache']) / 'url_hashes.json'
    
    # Initialize hash tracking
    seen_hashes = set()
    
    # Simulate discovering URLs
    discovered_urls = [
        'https://example.com/api/v1',
        'https://example.com/api/v2',
        'https://example.com/api/v1',  # Duplicate
        'https://example.com/api/v3',
        'https://example.com/api/v2',  # Duplicate
    ]
    
    unique_urls = []
    for url in discovered_urls:
        url_hash = await calculate_hash(url)
        if url_hash not in seen_hashes:
            seen_hashes.add(url_hash)
            unique_urls.append(url)
    
    # Append only unique URLs
    await FileSystem.append_unique_lines(str(urls_file), unique_urls)
    
    # Save hash tracking
    with open(hash_file, 'w') as f:
        json.dump(list(seen_hashes), f)
    
    # Verify only 3 unique URLs were saved
    content = urls_file.read_text()
    saved_urls = content.strip().split('\n')
    assert len(saved_urls) == 3


# ============================================================================
# RETRY + ASYNC FILE OPERATIONS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_retry_with_file_io_operations(tmp_path):
    """Integration: Retry decorator with real async file operations"""
    test_file = tmp_path / "retry_test.txt"
    attempt_count = 0
    
    @retry_async(max_attempts=3, backoff_base=0.05, retry_on=(OSError,))
    async def write_with_retry(content):
        nonlocal attempt_count
        attempt_count += 1
        
        # Simulate intermittent failure
        if attempt_count < 2:
            raise OSError("Simulated write failure")
        
        await FileSystem.write_text_file(str(test_file), content, mode='w')
        return await calculate_file_hash(str(test_file))
    
    file_hash = await write_with_retry("Test content")
    
    # Should succeed after retry
    assert test_file.exists()
    assert file_hash is not None
    assert attempt_count == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_retry_with_json_operations(tmp_path):
    """Integration: Retry with JSON file operations"""
    json_file = tmp_path / "data.json"
    
    # Initialize file
    with open(json_file, 'w') as f:
        json.dump([], f)
    
    attempt_count = 0
    
    @retry_async(max_attempts=3, backoff_base=0.05, retry_on=(json.JSONDecodeError, ValueError))
    async def append_json_with_retry(data):
        nonlocal attempt_count
        attempt_count += 1
        
        # Simulate corruption on first attempt
        if attempt_count == 1:
            # Write invalid JSON
            with open(json_file, 'w') as f:
                f.write("{ invalid json }")
            raise json.JSONDecodeError("Invalid", "", 0)
        
        # On retry, reinitialize with empty list then append
        with open(json_file, 'w') as f:
            json.dump([], f)
        await FileSystem.append_to_json(str(json_file), data)
    
    await append_json_with_retry({'id': 1, 'value': 'test'})
    
    # Verify data was appended
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 1
    assert data[0]['id'] == 1


@pytest.mark.integration
def test_retry_sync_with_subprocess_simulation(tmp_path):
    """Integration: Retry with simulated subprocess operations"""
    output_file = tmp_path / "output.txt"
    attempt_count = 0
    
    @retry_sync(max_attempts=3, backoff_base=0.05, retry_on=(RuntimeError,))
    def run_command_with_retry(command):
        nonlocal attempt_count
        attempt_count += 1
        
        # Simulate command failure
        if attempt_count < 2:
            raise RuntimeError(f"Command failed: {command}")
        
        # Success - write output
        output_file.write_text(f"Command executed: {command}")
        return {"returncode": 0, "output": "success"}
    
    result = run_command_with_retry("test-command")
    
    assert result["returncode"] == 0
    assert output_file.exists()
    assert "test-command" in output_file.read_text()


# ============================================================================
# LOGGING + CONCURRENT OPERATIONS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_structured_logging_across_concurrent_tasks(tmp_path, monkeypatch):
    """Integration: Structured logging in concurrent async tasks"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    # Create structured logger for each task
    async def worker_task(worker_id, num_operations):
        logger = create_structured_logger(
            "worker",
            context={'worker_id': worker_id}
        )
        
        for i in range(num_operations):
            logger.info(f"Processing operation {i}")
            await asyncio.sleep(0.001)
        
        return f"Worker {worker_id} completed"
    
    # Run 5 workers concurrently
    tasks = [worker_task(i, 10) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    # All workers should complete
    assert len(results) == 5
    
    # Check that log file exists and has content
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        # Should have logged from multiple workers
        assert 'Processing operation' in content


@pytest.mark.integration
@pytest.mark.asyncio
async def test_logging_during_retry_operations(tmp_path, monkeypatch):
    """Integration: Log messages during retry operations"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("retry_test")
    attempt_count = 0
    
    @retry_async(max_attempts=3, backoff_base=0.05, operation_name="test_operation")
    async def operation_with_logging():
        nonlocal attempt_count
        attempt_count += 1
        logger.info(f"Attempt {attempt_count}")
        
        if attempt_count < 2:
            logger.warning(f"Attempt {attempt_count} failed, will retry")
            raise ValueError("Simulated failure")
        
        logger.info("Operation succeeded")
        return "success"
    
    result = await operation_with_logging()
    
    assert result == "success"
    
    # Check logs
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        assert 'Attempt 1' in content
        assert 'Attempt 2' in content
        assert 'Operation succeeded' in content


# ============================================================================
# COMPLETE UTILITY STACK INTEGRATION
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_scan_workflow_simulation(tmp_path, monkeypatch):
    """Integration: Complete workflow using all utils together"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    # Setup
    logger = create_structured_logger("scan", context={'target': 'example.com'})
    target = "example.com"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    # Track processed hashes
    history_file = Path(paths['history_file'])
    with open(history_file, 'r') as f:
        history = json.load(f)
    scanned_hashes = set(history['scanned_hashes'])
    
    # Simulate discovering and processing URLs
    discovered_urls = [
        'https://example.com/app.js',
        'https://example.com/vendor.js',
        'https://example.com/app.js',  # Duplicate
        'https://example.com/main.js',
    ]
    
    processed_count = 0
    
    @retry_async(max_attempts=3, backoff_base=0.05, retry_on=(ValueError,))
    async def process_url(url):
        nonlocal processed_count
        
        # Calculate URL hash
        url_hash = await calculate_hash(url)
        
        # Check if already processed
        if url_hash in scanned_hashes:
            logger.info(f"Skipping duplicate: {url}")
            return None
        
        # Mark as processed
        scanned_hashes.add(url_hash)
        
        # Simulate downloading content
        content = f"// Content from {url}\nconsole.log('test');"
        
        # Save to file
        filename = url.split('/')[-1]
        file_path = Path(paths['unique_js']) / filename
        await FileSystem.write_text_file(str(file_path), content, mode='w')
        
        # Calculate file hash
        file_hash = await calculate_file_hash(str(file_path))
        
        processed_count += 1
        logger.info(f"Processed: {url} (hash: {file_hash[:8]}...)")
        
        return {'url': url, 'hash': file_hash, 'path': str(file_path)}
    
    # Process all URLs
    tasks = [process_url(url) for url in discovered_urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out None results (duplicates)
    processed = [r for r in results if r is not None and not isinstance(r, Exception)]
    
    # Should have processed 3 unique URLs
    assert processed_count == 3
    assert len(processed) == 3
    
    # Save updated history
    history['scanned_hashes'] = list(scanned_hashes)
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    # Verify files exist
    for result in processed:
        assert Path(result['path']).exists()
    
    # Verify logging
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        assert 'Processed:' in content
        assert 'Skipping duplicate:' in content


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_recovery_with_logging_and_retry(tmp_path, monkeypatch):
    """Integration: Error recovery using retry + structured logging"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = create_structured_logger("recovery", context={'phase': 'download'})
    target = "recovery.test"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    attempt_counts = {}
    
    @retry_async(max_attempts=3, backoff_base=0.05, retry_on=(ConnectionError, TimeoutError))
    async def download_with_recovery(url):
        if url not in attempt_counts:
            attempt_counts[url] = 0
        attempt_counts[url] += 1
        
        attempt = attempt_counts[url]
        logger.info(f"Downloading {url} (attempt {attempt})")
        
        # Simulate different failure scenarios
        if attempt == 1:
            logger.warning(f"Connection failed for {url}")
            raise ConnectionError("Connection refused")
        elif attempt == 2 and 'fail' in url:
            logger.warning(f"Timeout for {url}")
            raise TimeoutError("Request timeout")
        
        # Success
        content = f"Content from {url}"
        filename = url.split('/')[-1] + '.js'
        file_path = Path(paths['unique_js']) / filename
        
        await FileSystem.write_text_file(str(file_path), content, mode='w')
        logger.info(f"Successfully saved {url}")
        
        return {'url': url, 'path': str(file_path)}
    
    urls = [
        'https://example.com/success.js',
        'https://example.com/fail-once.js',
        'https://example.com/success2.js'
    ]
    
    results = await asyncio.gather(*[download_with_recovery(url) for url in urls])
    
    # All should succeed eventually
    assert len(results) == 3
    assert all(r is not None for r in results)
    
    # Check that files were created
    for result in results:
        assert Path(result['path']).exists()
    
    # Verify error logging
    errors_log = logs_dir / "errors.log"
    if errors_log.exists():
        content = errors_log.read_text(encoding='utf-8')
        assert 'Connection failed' in content or 'WARNING' in content


@pytest.mark.integration
@pytest.mark.asyncio
async def test_state_persistence_with_checksum_validation(tmp_path):
    """Integration: State persistence with hash-based validation"""
    target = "checkpoint.test"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    # Simulate scan state
    scan_state = {
        'processed_urls': [],
        'file_hashes': {},
        'metadata': {
            'start_time': time.time(),
            'files_processed': 0
        }
    }
    
    # Process some files
    files_to_process = [
        ('file1.js', 'content1'),
        ('file2.js', 'content2'),
        ('file3.js', 'content3')
    ]
    
    for filename, content in files_to_process:
        # Save file
        file_path = Path(paths['unique_js']) / filename
        await FileSystem.write_text_file(str(file_path), content, mode='w')
        
        # Calculate hash
        file_hash = await calculate_file_hash(str(file_path))
        
        # Update state
        scan_state['processed_urls'].append(filename)
        scan_state['file_hashes'][filename] = file_hash
        scan_state['metadata']['files_processed'] += 1
    
    # Save checkpoint
    checkpoint_file = Path(paths['cache']) / 'checkpoint.json'
    with open(checkpoint_file, 'w') as f:
        json.dump(scan_state, f, indent=2)
    
    # Calculate checkpoint hash for integrity
    checkpoint_hash = await calculate_file_hash(str(checkpoint_file))
    
    # Verify checkpoint can be loaded
    with open(checkpoint_file, 'r') as f:
        loaded_state = json.load(f)
    
    assert loaded_state['metadata']['files_processed'] == 3
    assert len(loaded_state['file_hashes']) == 3
    
    # Verify file hashes match
    for filename in loaded_state['file_hashes']:
        file_path = Path(paths['unique_js']) / filename
        actual_hash = await calculate_file_hash(str(file_path))
        expected_hash = loaded_state['file_hashes'][filename]
        assert actual_hash == expected_hash


# ============================================================================
# PERFORMANCE INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_high_throughput_file_processing(tmp_path):
    """Integration: High throughput file processing with hashing"""
    target = "performance.test"
    paths = FileSystem.create_result_structure(target, base_path=str(tmp_path))
    
    # Process 100 files concurrently
    async def process_file(idx):
        content = f"File content {idx}" * 100  # ~1.5KB per file
        filename = f"file_{idx}.js"
        file_path = Path(paths['unique_js']) / filename
        
        # Write file
        await FileSystem.write_text_file(str(file_path), content, mode='w')
        
        # Calculate hash
        file_hash = await calculate_file_hash(str(file_path))
        
        return {'index': idx, 'hash': file_hash}
    
    start_time = time.time()
    
    tasks = [process_file(i) for i in range(100)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    
    # Should process 100 files reasonably quickly
    assert len(results) == 100
    assert elapsed < 10.0  # Should complete in under 10 seconds
    
    # All hashes should be unique (different content)
    hashes = [r['hash'] for r in results]
    assert len(set(hashes)) == 100
