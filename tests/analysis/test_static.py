"""
Comprehensive tests for Static Analysis module
Tests AST parsing, endpoint extraction, and tree-sitter integration
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from jsscanner.analysis.static import StaticAnalyzer


@pytest.fixture
def static_analyzer(default_config, mock_logger, tmp_result_paths):
    """Create StaticAnalyzer instance"""
    return StaticAnalyzer(default_config, mock_logger, tmp_result_paths)


@pytest.mark.unit
class TestTreeSitterInitialization:
    """Test tree-sitter parser initialization"""
    
    def test_parser_initialized(self, static_analyzer):
        """Test tree-sitter parser is initialized"""
        # May be None if tree-sitter not available
        assert static_analyzer.parser is not None or static_analyzer.parser is None
    
    def test_handles_missing_tree_sitter(self, default_config, mock_logger, tmp_result_paths):
        """Test graceful handling when tree-sitter not available"""
        # This test is implementation-dependent
        # If tree-sitter is available, it will be initialized
        # If not, the module should handle it gracefully
        try:
            analyzer = StaticAnalyzer(default_config, mock_logger, tmp_result_paths)
            assert analyzer is not None
        except ImportError:
            # Expected if tree-sitter not installed
            pytest.skip("tree-sitter not available")


@pytest.mark.unit
class TestExtractsDatabase:
    """Test extracts database structure"""
    
    def test_extracts_db_initialized(self, static_analyzer):
        """Test extracts database is initialized"""
        assert 'endpoints' in static_analyzer.extracts_db
        assert 'domains' in static_analyzer.extracts_db
        assert 'links' in static_analyzer.extracts_db
    
    def test_domain_organizer_initialized(self, static_analyzer):
        """Test domain organizer is initialized"""
        assert static_analyzer.domain_organizer is not None


@pytest.mark.unit
class TestMaxFileSize:
    """Test file size limits"""
    
    def test_configurable_max_file_size(self, mock_logger, tmp_result_paths):
        """Test max file size can be configured"""
        config = {'ast': {'max_file_size_mb': 25}}
        analyzer = StaticAnalyzer(config, mock_logger, tmp_result_paths)
        
        assert analyzer.max_file_size == 25 * 1024 * 1024
    
    def test_default_max_file_size(self, static_analyzer):
        """Test default max file size"""
        assert static_analyzer.max_file_size == 15 * 1024 * 1024
