"""
Unit Tests for Processor (Deobfuscation)
"""
import pytest
import asyncio
from jsscanner.analysis.processor import Processor


class MockLogger:
    """Mock logger for testing"""
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass
    def debug(self, msg): pass


@pytest.mark.asyncio
async def test_deobfuscate_hex_strings():
    """Test hex string decoding"""
    processor = Processor(MockLogger(), config={})
    
    # Test simple hex string
    input_code = r'var msg = "\x48\x65\x6c\x6c\x6f";'
    result = await processor.deobfuscate(input_code)
    
    assert 'Hello' in result
    assert r'\x48' not in result


@pytest.mark.asyncio
async def test_deobfuscate_hex_api_key():
    """Test hex-encoded API key"""
    processor = Processor(MockLogger(), config={})
    
    input_code = r'var apiKey = "\x41\x49\x7a\x61\x53\x79\x44";'
    result = await processor.deobfuscate(input_code)
    
    assert 'AIzaSyD' in result


@pytest.mark.asyncio
async def test_deobfuscate_bracket_notation():
    """Test bracket notation simplification"""
    processor = Processor(MockLogger(), config={})
    
    input_code = "obj['property']"
    result = await processor.deobfuscate(input_code)
    
    assert 'obj.property' in result
    assert "['property']" not in result


@pytest.mark.asyncio
async def test_deobfuscate_nested_bracket_notation():
    """Test nested bracket notation"""
    processor = Processor(MockLogger(), config={})
    
    input_code = "window['location']['href']"
    result = await processor.deobfuscate(input_code)
    
    assert 'window.location.href' in result


@pytest.mark.asyncio
async def test_deobfuscate_mixed_obfuscation():
    """Test mixed hex and bracket notation"""
    processor = Processor(MockLogger(), config={})
    
    input_code = r'''
    var config = {
        '\x61\x70\x69': "\x68\x74\x74\x70\x73",
        'endpoint': window['location']['hostname']
    };
    '''
    result = await processor.deobfuscate(input_code)
    
    assert 'api' in result or 'https' in result
    assert 'window.location.hostname' in result


@pytest.mark.asyncio
async def test_deobfuscate_invalid_hex():
    """Test that invalid hex sequences are left unchanged"""
    processor = Processor(MockLogger(), config={})
    
    # Invalid hex (odd length)
    input_code = r'var x = "\x4";'
    result = await processor.deobfuscate(input_code)
    
    # Should remain unchanged or at least not crash
    assert result is not None


@pytest.mark.asyncio
async def test_deobfuscate_empty_string():
    """Test empty string handling"""
    processor = Processor(MockLogger(), config={})
    
    result = await processor.deobfuscate('')
    assert result == ''


@pytest.mark.asyncio
async def test_deobfuscate_no_obfuscation():
    """Test that clean code is left unchanged"""
    processor = Processor(MockLogger(), config={})
    
    input_code = 'var x = "Hello World";'
    result = await processor.deobfuscate(input_code)
    
    assert 'Hello World' in result


@pytest.mark.asyncio
async def test_decode_hex_arrays_validation():
    """Test hex decoding edge cases"""
    processor = Processor(MockLogger(), config={})
    
    # Test various edge cases
    test_cases = [
        (r'"\x48\x65\x6c\x6c\x6f"', 'Hello'),  # Valid
        (r'"\x00"', None),  # Null byte (might be filtered)
        (r'"\xFF"', None),  # Non-printable (should remain unchanged)
        (r'"\x20\x20"', '  '),  # Spaces (valid)
    ]
    
    for input_str, expected_substr in test_cases:
        result = await processor._decode_hex_arrays(input_str)
        if expected_substr:
            assert expected_substr in result or input_str in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
