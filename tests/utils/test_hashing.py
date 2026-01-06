"""
Test suite for jsscanner.utils.hashing

Covers:
- MD5 hashing for content and files
- Async and sync consistency
- Large file handling
- Unicode content hashing
- Edge cases (empty content, binary data)
"""
import pytest
import hashlib
import asyncio
from pathlib import Path
from jsscanner.utils.hashing import calculate_hash, calculate_file_hash, calculate_hash_sync


# ============================================================================
# BASIC HASHING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_returns_correct_md5():
    """Test that calculate_hash returns correct MD5 for known input"""
    content = "test"
    expected = hashlib.md5(content.encode('utf-8')).hexdigest()
    
    result = await calculate_hash(content)
    
    assert result == expected
    assert len(result) == 32  # MD5 hex digest is always 32 characters


@pytest.mark.unit
def test_calculate_hash_sync_returns_correct_md5():
    """Test that calculate_hash_sync returns correct MD5 for known input"""
    content = "test"
    expected = hashlib.md5(content.encode('utf-8')).hexdigest()
    
    result = calculate_hash_sync(content)
    
    assert result == expected
    assert len(result) == 32


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_empty_string():
    """Test calculate_hash with empty string"""
    content = ""
    expected = hashlib.md5(content.encode('utf-8')).hexdigest()
    
    result = await calculate_hash(content)
    
    assert result == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_deterministic():
    """Test that calculate_hash produces deterministic results"""
    content = "deterministic test content"
    
    # Calculate hash multiple times
    hash1 = await calculate_hash(content)
    hash2 = await calculate_hash(content)
    hash3 = await calculate_hash(content)
    
    # All should be identical
    assert hash1 == hash2 == hash3


# ============================================================================
# ASYNC VS SYNC CONSISTENCY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_and_sync_produce_identical_results():
    """Test that async and sync versions produce identical hashes"""
    test_strings = [
        "simple test",
        "with numbers 12345",
        "special !@#$%^&*()",
        "multiline\ncontent\nhere",
        "tabs\tand\tspaces",
    ]
    
    for content in test_strings:
        async_result = await calculate_hash(content)
        sync_result = calculate_hash_sync(content)
        
        assert async_result == sync_result, f"Mismatch for content: {content}"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_and_sync_with_unicode():
    """Test async and sync consistency with Unicode content"""
    unicode_strings = [
        "Hello 世界",
        "🎉🔥💻🐛🚀",
        "مرحبا بالعالم",
        "Привет мир",
        "ñüöäß€£¥"
    ]
    
    for content in unicode_strings:
        async_result = await calculate_hash(content)
        sync_result = calculate_hash_sync(content)
        
        assert async_result == sync_result


# ============================================================================
# FILE HASHING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_file_hash_matches_content_hash(tmp_path):
    """Test that calculate_file_hash matches calculate_hash for same content"""
    content = "This is test file content"
    test_file = tmp_path / "test.txt"
    test_file.write_text(content, encoding='utf-8')
    
    # Calculate hash of content
    content_hash = await calculate_hash(content)
    
    # Calculate hash of file
    file_hash = await calculate_file_hash(str(test_file))
    
    assert file_hash == content_hash


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_file_hash_empty_file(tmp_path):
    """Test calculate_file_hash with empty file"""
    test_file = tmp_path / "empty.txt"
    test_file.touch()
    
    file_hash = await calculate_file_hash(str(test_file))
    expected = hashlib.md5(b'').hexdigest()
    
    assert file_hash == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_file_hash_binary_file(tmp_path):
    """Test calculate_file_hash with binary content"""
    test_file = tmp_path / "binary.dat"
    binary_data = bytes([0, 1, 2, 3, 255, 254, 253])
    test_file.write_bytes(binary_data)
    
    file_hash = await calculate_file_hash(str(test_file))
    expected = hashlib.md5(binary_data).hexdigest()
    
    assert file_hash == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_file_hash_with_unicode_content(tmp_path):
    """Test calculate_file_hash with Unicode file content"""
    content = "Hello 世界 🎉 مرحبا Привет ñüöäß€£¥"
    test_file = tmp_path / "unicode.txt"
    test_file.write_text(content, encoding='utf-8')
    
    file_hash = await calculate_file_hash(str(test_file))
    content_hash = await calculate_hash(content)
    
    assert file_hash == content_hash


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_file_hash_missing_file(tmp_path):
    """Test calculate_file_hash raises error for missing file"""
    missing_file = tmp_path / "does_not_exist.txt"
    
    with pytest.raises(FileNotFoundError):
        await calculate_file_hash(str(missing_file))


# ============================================================================
# LARGE CONTENT TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_large_string():
    """Test calculate_hash with large string (10MB)"""
    # Generate 10MB of content
    large_content = "x" * (10 * 1024 * 1024)
    
    result = await calculate_hash(large_content)
    expected = hashlib.md5(large_content.encode('utf-8')).hexdigest()
    
    assert result == expected


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.slow
async def test_calculate_file_hash_large_file(tmp_path):
    """Test calculate_file_hash with large file (50MB)"""
    # Create 50MB file
    large_file = tmp_path / "large.dat"
    chunk_size = 1024 * 1024  # 1MB chunks
    num_chunks = 50
    
    # Write in chunks
    with open(large_file, 'wb') as f:
        for i in range(num_chunks):
            f.write(b'x' * chunk_size)
    
    # Calculate hash
    file_hash = await calculate_file_hash(str(large_file))
    
    # Verify hash is valid MD5
    assert len(file_hash) == 32
    assert all(c in '0123456789abcdef' for c in file_hash)
    
    # Verify it matches manual calculation
    md5_hash = hashlib.md5()
    with open(large_file, 'rb') as f:
        while chunk := f.read(8192):
            md5_hash.update(chunk)
    expected = md5_hash.hexdigest()
    
    assert file_hash == expected


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_file_hash_reads_in_chunks(tmp_path):
    """Test that calculate_file_hash reads file in chunks (memory efficient)"""
    # Create file larger than chunk size (8192 bytes)
    content = "y" * 20000  # 20KB
    test_file = tmp_path / "chunked.txt"
    test_file.write_text(content, encoding='utf-8')
    
    file_hash = await calculate_file_hash(str(test_file))
    content_hash = await calculate_hash(content)
    
    assert file_hash == content_hash


# ============================================================================
# UNICODE AND ENCODING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_unicode_consistency():
    """Test that Unicode strings hash consistently"""
    unicode_strings = [
        "Hello 世界",
        "🎉🔥💻",
        "مرحبا بالعالم",
        "Привет мир",
        "你好世界",
        "ñüöäß€£¥"
    ]
    
    # Calculate hash twice for each string
    for content in unicode_strings:
        hash1 = await calculate_hash(content)
        hash2 = await calculate_hash(content)
        assert hash1 == hash2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_different_unicode_produces_different_hashes():
    """Test that different Unicode strings produce different hashes"""
    strings = [
        "Hello",
        "Hello 世界",
        "🎉",
        "مرحبا"
    ]
    
    hashes = [await calculate_hash(s) for s in strings]
    
    # All hashes should be unique
    assert len(set(hashes)) == len(hashes)


# ============================================================================
# EDGE CASES TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_whitespace_variations():
    """Test that different whitespace produces different hashes"""
    variations = [
        "test",
        "test ",
        " test",
        "test\n",
        "test\r\n",
        "test\t"
    ]
    
    hashes = [await calculate_hash(s) for s in variations]
    
    # All should be different (whitespace matters)
    assert len(set(hashes)) == len(variations)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_case_sensitivity():
    """Test that hashing is case-sensitive"""
    content_lower = "hello world"
    content_upper = "HELLO WORLD"
    content_mixed = "Hello World"
    
    hash_lower = await calculate_hash(content_lower)
    hash_upper = await calculate_hash(content_upper)
    hash_mixed = await calculate_hash(content_mixed)
    
    # All should be different
    assert hash_lower != hash_upper
    assert hash_lower != hash_mixed
    assert hash_upper != hash_mixed


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_newline_variations():
    """Test that different newline types produce different hashes"""
    content_unix = "line1\nline2\nline3"
    content_windows = "line1\r\nline2\r\nline3"
    content_mac = "line1\rline2\rline3"
    
    hash_unix = await calculate_hash(content_unix)
    hash_windows = await calculate_hash(content_windows)
    hash_mac = await calculate_hash(content_mac)
    
    # All should be different
    assert len({hash_unix, hash_windows, hash_mac}) == 3


# ============================================================================
# CONCURRENT HASHING TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_calculate_hash():
    """Test concurrent hash calculations don't interfere"""
    contents = [f"content_{i}" for i in range(100)]
    
    # Calculate hashes concurrently
    tasks = [calculate_hash(content) for content in contents]
    results = await asyncio.gather(*tasks)
    
    # Calculate expected hashes
    expected = [hashlib.md5(c.encode('utf-8')).hexdigest() for c in contents]
    
    assert results == expected


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_file_hash_calculations(tmp_path):
    """Test concurrent file hash calculations"""
    # Create multiple test files
    num_files = 20
    files_and_contents = []
    
    for i in range(num_files):
        test_file = tmp_path / f"file_{i}.txt"
        content = f"content for file {i}"
        test_file.write_text(content, encoding='utf-8')
        files_and_contents.append((str(test_file), content))
    
    # Calculate file hashes concurrently
    file_tasks = [calculate_file_hash(f) for f, _ in files_and_contents]
    file_hashes = await asyncio.gather(*file_tasks)
    
    # Calculate content hashes for verification
    content_tasks = [calculate_hash(c) for _, c in files_and_contents]
    content_hashes = await asyncio.gather(*content_tasks)
    
    # File hashes should match content hashes
    assert file_hashes == content_hashes


# ============================================================================
# PERFORMANCE AND MEMORY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_hash_performance_reasonable():
    """Test that calculate_hash completes in reasonable time for typical content"""
    import time
    
    # Typical JS file size (100KB)
    content = "x" * (100 * 1024)
    
    start = time.time()
    result = await calculate_hash(content)
    elapsed = time.time() - start
    
    # Should complete in less than 100ms for 100KB
    assert elapsed < 0.1
    assert len(result) == 32


@pytest.mark.unit
@pytest.mark.asyncio
async def test_multiple_hash_calculations_same_content():
    """Test that calculating hash multiple times for same content is efficient"""
    content = "test content" * 1000  # 12KB
    
    # Calculate hash 100 times
    results = []
    for _ in range(100):
        result = await calculate_hash(content)
        results.append(result)
    
    # All results should be identical
    assert len(set(results)) == 1


# ============================================================================
# COLLISION DETECTION TESTS (Statistical)
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_hash_collision_unlikely():
    """Test that similar content produces different hashes (collision detection)"""
    # Generate similar but distinct content
    base = "https://example.com/api/v1/users/"
    variants = [base + str(i) for i in range(1000)]
    
    # Calculate hashes
    hashes = [await calculate_hash(v) for v in variants]
    
    # All hashes should be unique (no collisions for this dataset)
    assert len(set(hashes)) == 1000


@pytest.mark.unit
@pytest.mark.asyncio
async def test_hash_avalanche_effect():
    """Test that small change in input produces different hash (avalanche effect)"""
    base = "https://example.com/api"
    variants = [
        base,
        base + "1",
        base + "2",
        base[:-1],  # Remove last char
        base.upper()
    ]
    
    hashes = [await calculate_hash(v) for v in variants]
    
    # All hashes should be different
    assert len(set(hashes)) == len(variants)


# ============================================================================
# INTEGRATION WITH FILESYSTEM TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_hash_file_then_verify_content(tmp_path):
    """Integration test: create file, hash it, verify by content hash"""
    content = "Integration test content with special chars: ñ 世界 🎉"
    test_file = tmp_path / "integration.txt"
    test_file.write_text(content, encoding='utf-8')
    
    # Hash file
    file_hash = await calculate_file_hash(str(test_file))
    
    # Read content and hash it
    read_content = test_file.read_text(encoding='utf-8')
    content_hash = await calculate_hash(read_content)
    
    # Should match
    assert file_hash == content_hash
    
    # Should match original content hash
    original_hash = await calculate_hash(content)
    assert file_hash == original_hash


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deduplication_workflow(tmp_path):
    """Integration test: deduplication workflow using hashes"""
    # Simulate deduplication scenario
    seen_hashes = set()
    duplicates_found = 0
    
    files = [
        ("file1.txt", "unique content 1"),
        ("file2.txt", "unique content 2"),
        ("file3.txt", "unique content 1"),  # duplicate of file1
        ("file4.txt", "unique content 3"),
        ("file5.txt", "unique content 2"),  # duplicate of file2
    ]
    
    for filename, content in files:
        test_file = tmp_path / filename
        test_file.write_text(content, encoding='utf-8')
        
        file_hash = await calculate_file_hash(str(test_file))
        
        if file_hash in seen_hashes:
            duplicates_found += 1
        else:
            seen_hashes.add(file_hash)
    
    # Should find 2 duplicates
    assert duplicates_found == 2
    # Should have 3 unique hashes
    assert len(seen_hashes) == 3
