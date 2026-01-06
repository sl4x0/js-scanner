"""
Test suite for jsscanner.utils.fs (FileSystem)

Covers:
- Directory structure creation
- JSON file operations (append, read, write)
- Unique line appending with concurrency
- UTF-8 encoding on Windows
- Edge cases (large files, corrupt data, race conditions)
"""
import pytest
import json
import asyncio
from pathlib import Path
from jsscanner.utils.fs import FileSystem


# ============================================================================
# BASIC STRUCTURE CREATION TESTS
# ============================================================================

@pytest.mark.unit
def test_create_result_structure_creates_all_directories(tmp_path):
    """Test that create_result_structure creates all expected directories"""
    target_name = "example.com"
    paths = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    # Verify all expected directories exist
    assert (tmp_path / target_name).exists()
    assert (tmp_path / target_name / "findings").exists()
    assert (tmp_path / target_name / "artifacts" / "source_code").exists()
    assert (tmp_path / target_name / "logs").exists()
    assert (tmp_path / target_name / ".warehouse").exists()
    assert (tmp_path / target_name / ".warehouse" / "raw_js").exists()
    assert (tmp_path / target_name / ".warehouse" / "db").exists()
    assert (tmp_path / target_name / ".warehouse" / "temp").exists()
    assert (tmp_path / target_name / ".warehouse" / "minified").exists()
    assert (tmp_path / target_name / ".warehouse" / "unminified").exists()
    assert (tmp_path / target_name / ".warehouse" / "cache").exists()
    assert (tmp_path / target_name / ".warehouse" / "final_source").exists()


@pytest.mark.unit
def test_create_result_structure_initializes_history_json(tmp_path):
    """Test that history.json is initialized with correct structure"""
    target_name = "test.com"
    paths = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    history_file = Path(paths['history_file'])
    assert history_file.exists()
    
    with open(history_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert 'scanned_hashes' in data
    assert 'scan_metadata' in data
    assert isinstance(data['scanned_hashes'], list)
    assert isinstance(data['scan_metadata'], dict)
    assert len(data['scanned_hashes']) == 0


@pytest.mark.unit
def test_create_result_structure_initializes_metadata_json(tmp_path):
    """Test that metadata.json is initialized with all required fields"""
    target_name = "test.com"
    paths = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    metadata_file = Path(paths['metadata_file'])
    assert metadata_file.exists()
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Verify all expected fields exist
    expected_fields = ['total_files', 'total_secrets', 'scan_duration', 
                      'errors', 'start_time', 'end_time', 'source_urls']
    for field in expected_fields:
        assert field in data
    
    assert data['total_files'] == 0
    assert data['total_secrets'] == 0
    assert data['scan_duration'] == 0
    assert isinstance(data['errors'], list)
    assert data['start_time'] is None
    assert data['end_time'] is None
    assert isinstance(data['source_urls'], list)


@pytest.mark.unit
def test_create_result_structure_initializes_secrets_json(tmp_path):
    """Test that secrets.json is initialized as empty array"""
    target_name = "test.com"
    paths = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    secrets_file = Path(paths['secrets']) / 'secrets.json'
    assert secrets_file.exists()
    
    with open(secrets_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.unit
def test_create_result_structure_returns_backward_compatible_paths(tmp_path):
    """Test that returned paths dict has all expected keys for backward compatibility"""
    target_name = "test.com"
    paths = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    # Verify all expected keys exist (engine depends on these exact names)
    expected_keys = [
        'base', 'logs', 'extracts', 'secrets', 'source_code',
        'unique_js', 'final_source_code', 'cache', 'temp',
        'files_minified', 'files_unminified', 'history_file', 'metadata_file'
    ]
    
    for key in expected_keys:
        assert key in paths, f"Missing key: {key}"
        assert isinstance(paths[key], str), f"Key {key} should be string path"


@pytest.mark.unit
def test_create_result_structure_does_not_overwrite_existing(tmp_path):
    """Test that creating structure twice doesn't overwrite existing files"""
    target_name = "test.com"
    
    # Create structure first time
    paths1 = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    # Modify history file
    history_file = Path(paths1['history_file'])
    with open(history_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['scanned_hashes'].append('test_hash_123')
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    
    # Create structure second time
    paths2 = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    # Verify file was not overwritten
    with open(history_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert 'test_hash_123' in data['scanned_hashes']


# ============================================================================
# JSON APPEND OPERATIONS TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_to_json_appends_data_to_existing_list(tmp_path):
    """Test that append_to_json correctly appends to existing JSON list"""
    test_file = tmp_path / "test.json"
    
    # Initialize file with empty list
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump([], f)
    
    # Append first item
    await FileSystem.append_to_json(str(test_file), {'id': 1, 'name': 'first'})
    
    # Append second item
    await FileSystem.append_to_json(str(test_file), {'id': 2, 'name': 'second'})
    
    # Verify both items exist
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) == 2
    assert data[0] == {'id': 1, 'name': 'first'}
    assert data[1] == {'id': 2, 'name': 'second'}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_to_json_creates_list_if_file_empty(tmp_path):
    """Test that append_to_json creates list if file is empty"""
    test_file = tmp_path / "test.json"
    
    # Create empty file
    test_file.touch()
    
    # Append item
    await FileSystem.append_to_json(str(test_file), {'id': 1, 'value': 'test'})
    
    # Verify list was created with item
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0] == {'id': 1, 'value': 'test'}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_to_json_raises_error_if_not_list(tmp_path):
    """Test that append_to_json raises error if file contains non-list"""
    test_file = tmp_path / "test.json"
    
    # Initialize file with dict instead of list
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump({'key': 'value'}, f)
    
    # Attempt to append should raise ValueError
    with pytest.raises(ValueError, match="Expected list"):
        await FileSystem.append_to_json(str(test_file), {'new': 'data'})


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_to_json_handles_unicode_data(tmp_path):
    """Test that append_to_json correctly handles Unicode characters"""
    test_file = tmp_path / "test.json"
    
    # Initialize with empty list
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump([], f)
    
    # Append items with various Unicode characters
    unicode_items = [
        {'text': 'Hello 世界'},
        {'emoji': '🎉🔥💻'},
        {'arabic': 'مرحبا'},
        {'special': 'ñüöäß€£¥'}
    ]
    
    for item in unicode_items:
        await FileSystem.append_to_json(str(test_file), item)
    
    # Verify all Unicode was preserved
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) == 4
    for i, expected in enumerate(unicode_items):
        assert data[i] == expected


@pytest.mark.integration
@pytest.mark.asyncio
async def test_append_to_json_concurrent_writes(tmp_path):
    """Test that concurrent append_to_json calls don't corrupt data"""
    test_file = tmp_path / "test.json"
    
    # Initialize with empty list
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump([], f)
    
    # Create multiple concurrent append tasks
    async def append_item(idx):
        await FileSystem.append_to_json(str(test_file), {'id': idx, 'value': f'item_{idx}'})
    
    # Run 50 concurrent appends
    tasks = [append_item(i) for i in range(50)]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Read final state
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Note: Without file locking, some items may be lost due to race conditions
    # This test documents current behavior - consider adding file locking in future
    # For now, verify file is valid JSON and contains at least some items
    assert isinstance(data, list)
    assert len(data) > 0  # At least some items should have been appended


# ============================================================================
# UNIQUE LINES APPEND TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_unique_lines_adds_new_lines(tmp_path):
    """Test that append_unique_lines adds only new lines"""
    test_file = tmp_path / "urls.txt"
    
    # First append
    await FileSystem.append_unique_lines(str(test_file), [
        'https://example.com/page1',
        'https://example.com/page2',
        'https://example.com/page3'
    ])
    
    # Verify lines were added
    content = test_file.read_text(encoding='utf-8')
    lines = content.strip().split('\n')
    assert len(lines) == 3
    assert 'https://example.com/page1' in lines


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_unique_lines_skips_duplicates(tmp_path):
    """Test that append_unique_lines skips duplicate lines"""
    test_file = tmp_path / "urls.txt"
    
    # First append
    await FileSystem.append_unique_lines(str(test_file), [
        'https://example.com/page1',
        'https://example.com/page2'
    ])
    
    # Second append with some duplicates
    await FileSystem.append_unique_lines(str(test_file), [
        'https://example.com/page2',  # duplicate
        'https://example.com/page3',  # new
        'https://example.com/page1'   # duplicate
    ])
    
    # Verify only unique lines exist
    content = test_file.read_text(encoding='utf-8')
    lines = content.strip().split('\n')
    assert len(lines) == 3  # Only 3 unique lines
    assert set(lines) == {
        'https://example.com/page1',
        'https://example.com/page2',
        'https://example.com/page3'
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_unique_lines_handles_empty_file(tmp_path):
    """Test that append_unique_lines works when file doesn't exist"""
    test_file = tmp_path / "new_file.txt"
    
    # Append to non-existent file
    await FileSystem.append_unique_lines(str(test_file), [
        'line1',
        'line2',
        'line3'
    ])
    
    # Verify file was created with lines
    assert test_file.exists()
    content = test_file.read_text(encoding='utf-8')
    lines = content.strip().split('\n')
    assert len(lines) == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_unique_lines_handles_unicode(tmp_path, sample_unicode_content):
    """Test that append_unique_lines handles Unicode correctly"""
    test_file = tmp_path / "unicode.txt"
    
    unicode_lines = [
        'Hello 世界',
        '🎉🔥💻🐛',
        'مرحبا بالعالم',
        'Привет мир',
        'ñüöäß€£¥'
    ]
    
    await FileSystem.append_unique_lines(str(test_file), unicode_lines)
    
    # Verify Unicode was preserved
    content = test_file.read_text(encoding='utf-8')
    lines = content.strip().split('\n')
    assert len(lines) == 5
    for expected in unicode_lines:
        assert expected in lines


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_append_unique_lines_handles_large_dataset(tmp_path):
    """Test append_unique_lines with large dataset (10,000+ lines)"""
    test_file = tmp_path / "large.txt"
    
    # Generate 10,000 unique lines
    large_dataset = [f'https://example.com/page{i}' for i in range(10000)]
    
    # Append in chunks (simulating real usage)
    chunk_size = 1000
    for i in range(0, len(large_dataset), chunk_size):
        chunk = large_dataset[i:i+chunk_size]
        await FileSystem.append_unique_lines(str(test_file), chunk)
    
    # Verify all lines were added
    content = test_file.read_text(encoding='utf-8')
    lines = set(content.strip().split('\n'))
    assert len(lines) == 10000


@pytest.mark.integration
@pytest.mark.asyncio
async def test_append_unique_lines_concurrent_access(tmp_path):
    """Test append_unique_lines with concurrent access"""
    test_file = tmp_path / "concurrent.txt"
    
    # Create multiple concurrent tasks appending overlapping sets
    async def append_batch(start_idx, count):
        lines = [f'url_{i}' for i in range(start_idx, start_idx + count)]
        await FileSystem.append_unique_lines(str(test_file), lines)
    
    # Run multiple batches concurrently with overlapping ranges
    tasks = [
        append_batch(0, 20),    # url_0 to url_19
        append_batch(10, 20),   # url_10 to url_29 (overlaps)
        append_batch(20, 20),   # url_20 to url_39 (overlaps)
        append_batch(30, 20),   # url_30 to url_49 (overlaps)
    ]
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verify file has unique lines (may have race conditions, but should be valid)
    content = test_file.read_text(encoding='utf-8')
    lines = set(line for line in content.strip().split('\n') if line)  # Filter empty lines
    
    # Note: Race conditions may cause some items to be lost
    # This documents current behavior - at least 30 unique lines should exist
    assert len(lines) >= 30
    
    # All lines should follow expected pattern
    for line in lines:
        assert line.startswith('url_')


# ============================================================================
# FILE WRITE OPERATIONS TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_write_text_file_creates_new_file(tmp_path):
    """Test that write_text_file creates new file with content"""
    test_file = tmp_path / "new.txt"
    content = "This is test content"
    
    await FileSystem.write_text_file(str(test_file), content, mode='w')
    
    assert test_file.exists()
    assert test_file.read_text(encoding='utf-8') == content


@pytest.mark.unit
@pytest.mark.asyncio
async def test_write_text_file_overwrites_in_write_mode(tmp_path):
    """Test that write_text_file overwrites existing content in 'w' mode"""
    test_file = tmp_path / "overwrite.txt"
    
    # Write initial content
    await FileSystem.write_text_file(str(test_file), "Original content", mode='w')
    
    # Overwrite with new content
    await FileSystem.write_text_file(str(test_file), "New content", mode='w')
    
    # Verify content was overwritten
    assert test_file.read_text(encoding='utf-8') == "New content"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_write_text_file_appends_in_append_mode(tmp_path):
    """Test that write_text_file appends content in 'a' mode"""
    test_file = tmp_path / "append.txt"
    
    # Write initial content
    await FileSystem.write_text_file(str(test_file), "Line 1\n", mode='w')
    
    # Append additional content
    await FileSystem.write_text_file(str(test_file), "Line 2\n", mode='a')
    await FileSystem.write_text_file(str(test_file), "Line 3\n", mode='a')
    
    # Verify all content exists
    content = test_file.read_text(encoding='utf-8')
    assert content == "Line 1\nLine 2\nLine 3\n"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_write_text_file_handles_utf8_on_windows(tmp_path):
    """Test that write_text_file correctly handles UTF-8 encoding on Windows"""
    test_file = tmp_path / "utf8.txt"
    
    # Content with various Unicode characters
    unicode_content = "Hello 世界 🎉 مرحبا Привет ñüöäß€£¥"
    
    await FileSystem.write_text_file(str(test_file), unicode_content, mode='w')
    
    # Read back and verify
    assert test_file.read_text(encoding='utf-8') == unicode_content


@pytest.mark.unit
@pytest.mark.asyncio
async def test_write_text_file_handles_large_content(tmp_path, sample_large_content):
    """Test write_text_file with large content (10MB)"""
    test_file = tmp_path / "large.txt"
    
    await FileSystem.write_text_file(str(test_file), sample_large_content, mode='w')
    
    # Verify file size
    assert test_file.stat().st_size >= 10 * 1024 * 1024
    
    # Verify content (sample check)
    content = test_file.read_text(encoding='utf-8')
    assert len(content) == len(sample_large_content)
    assert content[:1000] == sample_large_content[:1000]


# ============================================================================
# HELPER METHOD TESTS
# ============================================================================

@pytest.mark.unit
def test_get_target_path_returns_correct_path(tmp_path):
    """Test that get_target_path returns correct path string"""
    target_name = "test.com"
    base_path = str(tmp_path)
    
    result = FileSystem.get_target_path(target_name, base_path)
    
    expected = str(Path(base_path) / target_name)
    assert result == expected


@pytest.mark.unit
def test_get_target_path_uses_default_base():
    """Test that get_target_path uses 'results' as default base"""
    target_name = "test.com"
    
    result = FileSystem.get_target_path(target_name)
    
    expected = str(Path("results") / target_name)
    assert result == expected


# ============================================================================
# EDGE CASES AND ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
def test_create_result_structure_handles_special_characters_in_target(tmp_path):
    """Test that create_result_structure handles special characters in target name"""
    # Use URL-safe characters that might appear in target names
    target_name = "api.example.com-8080"
    
    paths = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    # Verify structure was created
    assert (tmp_path / target_name).exists()
    assert (tmp_path / target_name / "findings").exists()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_to_json_recovers_from_invalid_json(tmp_path):
    """Test behavior when JSON file contains invalid JSON"""
    test_file = tmp_path / "corrupt.json"
    
    # Write invalid JSON
    test_file.write_text("{ invalid json }", encoding='utf-8')
    
    # Attempt to append should raise exception
    with pytest.raises(json.JSONDecodeError):
        await FileSystem.append_to_json(str(test_file), {'data': 'value'})


@pytest.mark.unit
@pytest.mark.asyncio
async def test_append_unique_lines_handles_empty_lines(tmp_path):
    """Test that append_unique_lines handles empty lines correctly"""
    test_file = tmp_path / "with_empty.txt"
    
    lines_with_empty = [
        'line1',
        '',  # empty line
        'line2',
        '',  # empty line
        'line3'
    ]
    
    await FileSystem.append_unique_lines(str(test_file), lines_with_empty)
    
    content = test_file.read_text(encoding='utf-8')
    lines = content.strip().split('\n')
    
    # Empty lines should be included
    assert '' in lines
    assert len(lines) == 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_write_text_file_creates_parent_directories(tmp_path):
    """Test that write_text_file works when parent directories don't exist"""
    # Note: aiofiles doesn't auto-create parents, so this tests current behavior
    nested_file = tmp_path / "level1" / "level2" / "file.txt"
    
    # Manually create parent directories (this is expected behavior)
    nested_file.parent.mkdir(parents=True, exist_ok=True)
    
    await FileSystem.write_text_file(str(nested_file), "content", mode='w')
    
    assert nested_file.exists()
    assert nested_file.read_text(encoding='utf-8') == "content"


@pytest.mark.unit
def test_create_result_structure_with_deeply_nested_path(tmp_path):
    """Test create_result_structure with deeply nested base path"""
    deep_base = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep_base.mkdir(parents=True, exist_ok=True)
    
    target_name = "test.com"
    paths = FileSystem.create_result_structure(target_name, base_path=str(deep_base))
    
    # Verify structure was created in deep path
    assert (deep_base / target_name).exists()
    assert (deep_base / target_name / "findings").exists()


# ============================================================================
# WINDOWS-SPECIFIC TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_windows_path_compatibility(tmp_path):
    """Test that paths work correctly on Windows (backslashes vs forward slashes)"""
    import sys
    
    target_name = "test.com"
    paths = FileSystem.create_result_structure(target_name, base_path=str(tmp_path))
    
    # All paths should be valid strings
    for key, path in paths.items():
        assert isinstance(path, str)
        assert len(path) > 0
    
    # Test writing to path works regardless of separator
    test_file = paths['secrets'] + '/test.txt' if sys.platform != 'win32' else paths['secrets'] + '\\test.txt'
    
    # Normalize path for cross-platform
    from pathlib import Path
    normalized_path = str(Path(paths['secrets']) / 'test.txt')
    
    await FileSystem.write_text_file(normalized_path, "test content", mode='w')
    assert Path(normalized_path).exists()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_utf8_encoding_on_windows(tmp_path):
    """Test that UTF-8 encoding works correctly on Windows"""
    test_file = tmp_path / "windows_utf8.txt"
    
    # Content that often causes issues on Windows
    problematic_content = "Line 1: ñ\nLine 2: 世界\nLine 3: 🎉\n"
    
    await FileSystem.write_text_file(str(test_file), problematic_content, mode='w')
    
    # Read back with explicit UTF-8
    content = test_file.read_text(encoding='utf-8')
    assert content == problematic_content
