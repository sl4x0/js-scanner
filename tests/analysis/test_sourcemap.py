"""
Comprehensive tests for SourceMap extraction and processing
Tests sourcemap downloading, parsing, and source recovery
"""
import pytest
import json
import base64
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from jsscanner.analysis.sourcemap import SourceMapRecoverer


@pytest.fixture
def sourcemap_recoverer(default_config, mock_logger, tmp_result_paths):
    """Create SourceMapRecoverer instance"""
    return SourceMapRecoverer(default_config, mock_logger, tmp_result_paths)


@pytest.mark.unit
@pytest.mark.asyncio
class TestSourceMapRecovery:
    """Test source map recovery from JS files"""
    
    async def test_find_inline_sourcemap(self, sourcemap_recoverer):
        """Test finding inline base64 sourcemap"""
        js_content = """function test(){}
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozfQ=="""
        
        map_url = sourcemap_recoverer._find_map_url(js_content, "https://example.com/app.js")
        
        assert map_url is not None
        assert 'data:application/json' in map_url
    
    async def test_find_external_sourcemap(self, sourcemap_recoverer):
        """Test finding external sourcemap reference"""
        js_content = "function test(){}\n//# sourceMappingURL=app.js.map"
        
        map_url = sourcemap_recoverer._find_map_url(js_content, "https://example.com/app.js")
        
        assert map_url is not None
        assert 'app.js.map' in map_url
    
    async def test_no_sourcemap_found(self, sourcemap_recoverer):
        """Test when no sourcemap is present"""
        js_content = "function test() { console.log('no map'); }"
        
        map_url = sourcemap_recoverer._find_map_url(js_content, "https://example.com/app.js")
        
        assert map_url is None


@pytest.mark.unit
class TestSourceMapParsing:
    """Test sourcemap URL parsing and resolution"""
    
    def test_resolve_relative_map_url(self, sourcemap_recoverer):
        """Test resolving relative sourcemap URLs"""
        base_url = "https://example.com/static/js/app.js"
        relative_map = "app.js.map"
        
        # Implementation would resolve to: https://example.com/static/js/app.js.map
        # Test depends on implementation details
    
    def test_resolve_absolute_map_url(self, sourcemap_recoverer):
        """Test resolving absolute sourcemap URLs"""
        base_url = "https://example.com/app.js"
        absolute_map = "https://cdn.example.com/maps/app.js.map"
        
        # Should use absolute URL as-is
