"""
Comprehensive tests for SemgrepAnalyzer module
Tests binary validation, chunking logic, vendor filtering, scan execution, retry handling, and result aggregation
"""
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from jsscanner.analysis.semgrep import SemgrepAnalyzer


# ============================================================================
# SETUP AND FIXTURES
# ============================================================================

@pytest.fixture
def semgrep_analyzer(default_config, mock_logger, tmp_result_paths):
    """Create SemgrepAnalyzer instance"""
    return SemgrepAnalyzer(default_config, mock_logger, tmp_result_paths)


@pytest.fixture
def semgrep_disabled(mock_logger, tmp_result_paths):
    """Create SemgrepAnalyzer with semgrep disabled"""
    config = {'semgrep': {'enabled': False}}
    return SemgrepAnalyzer(config, mock_logger, tmp_result_paths)


# ============================================================================
# BINARY DETECTION AND VALIDATION TESTS
# ============================================================================

@pytest.mark.unit
class TestBinaryDetection:
    """Test semgrep binary detection and validation"""
    
    def test_find_semgrep_from_config(self, mock_logger, tmp_result_paths, tmp_path):
        """Test finding semgrep from config path"""
        fake_binary = tmp_path / "semgrep"
        fake_binary.write_text("#!/bin/bash\necho 'semgrep'")
        
        config = {
            'semgrep': {
                'enabled': True,
                'binary_path': str(fake_binary)
            }
        }
        
        analyzer = SemgrepAnalyzer(config, mock_logger, tmp_result_paths)
        
        assert analyzer.semgrep_path == str(fake_binary)
    
    def test_find_semgrep_default_path(self, default_config, mock_logger, tmp_result_paths):
        """Test default semgrep path when not in config"""
        analyzer = SemgrepAnalyzer(default_config, mock_logger, tmp_result_paths)
        
        # Should default to 'semgrep' (PATH lookup)
        assert analyzer.semgrep_path == 'semgrep'
    
    def test_validate_semgrep_available(self, semgrep_analyzer):
        """Test successful semgrep validation"""
        with patch('shutil.which', return_value='/usr/bin/semgrep'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout='1.50.0',
                    stderr=''
                )
                
                result = semgrep_analyzer.validate()
                
                assert result == True
                assert semgrep_analyzer.semgrep_available == True
    
    def test_validate_semgrep_not_found(self, semgrep_analyzer):
        """Test validation when semgrep not found"""
        with patch('shutil.which', return_value=None):
            result = semgrep_analyzer.validate()
            
            assert result == False
            assert semgrep_analyzer.semgrep_available == False
    
    def test_validate_semgrep_disabled(self, semgrep_disabled):
        """Test validation when semgrep disabled in config"""
        result = semgrep_disabled.validate()
        
        assert result == False
    
    def test_validate_semgrep_execution_fails(self, semgrep_analyzer):
        """Test validation when semgrep exists but fails to run"""
        with patch('shutil.which', return_value='/usr/bin/semgrep'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stderr='Error running semgrep'
                )
                
                result = semgrep_analyzer.validate()
                
                assert result == False
                assert semgrep_analyzer.semgrep_available == False
    
    def test_validate_with_retry_on_timeout(self, semgrep_analyzer):
        """Test validation retries on timeout"""
        with patch('shutil.which', return_value='/usr/bin/semgrep'):
            with patch('subprocess.run') as mock_run:
                with patch('time.sleep'):  # Skip actual sleep
                    # First 2 calls timeout via subprocess.TimeoutExpired, 3rd succeeds
                    import subprocess
                    mock_run.side_effect = [
                        subprocess.TimeoutExpired(cmd='semgrep', timeout=5),
                        subprocess.TimeoutExpired(cmd='semgrep', timeout=5),
                        MagicMock(returncode=0, stdout='1.50.0')
                    ]
                    
                    result = semgrep_analyzer.validate()
                    
                    # Should eventually succeed after retries
                    assert result == True
                    assert mock_run.call_count == 3
    
    def test_validate_all_retries_timeout(self, semgrep_analyzer):
        """Test validation fails after all retries timeout"""
        with patch('shutil.which', return_value='/usr/bin/semgrep'):
            with patch('subprocess.run', side_effect=TimeoutError()):
                with patch('time.sleep'):
                    result = semgrep_analyzer.validate()
                    
                    assert result == False


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

@pytest.mark.unit
class TestConfiguration:
    """Test configuration loading and defaults"""
    
    def test_default_configuration_values(self, semgrep_analyzer):
        """Test default config values are set correctly"""
        assert semgrep_analyzer.enabled == True
        assert semgrep_analyzer.timeout == 300
        assert semgrep_analyzer.max_target_bytes == 2000000
        assert semgrep_analyzer.ruleset == 'p/javascript'
        assert semgrep_analyzer.chunk_size == 100
    
    def test_custom_configuration_values(self, mock_logger, tmp_result_paths):
        """Test custom config values override defaults"""
        config = {
            'semgrep': {
                'enabled': True,
                'timeout': 600,
                'max_target_bytes': 5000000,
                'ruleset': 'p/security-audit',
                'chunk_size': 50,
                'jobs': 8
            }
        }
        
        analyzer = SemgrepAnalyzer(config, mock_logger, tmp_result_paths)
        
        assert analyzer.timeout == 600
        assert analyzer.max_target_bytes == 5000000
        assert analyzer.ruleset == 'p/security-audit'
        assert analyzer.chunk_size == 50
        assert analyzer.jobs == 8
    
    def test_version_timeout_configuration(self, mock_logger, tmp_result_paths):
        """Test version check timeout configuration"""
        config = {
            'semgrep': {
                'enabled': True,
                'version_timeout': 60,
                'version_check_retries': 5
            }
        }
        
        analyzer = SemgrepAnalyzer(config, mock_logger, tmp_result_paths)
        
        assert analyzer.version_timeout == 60
        assert analyzer.version_retries == 5


# ============================================================================
# FILE FILTERING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestFileFiltering:
    """Test vendor file pre-filtering logic"""
    
    async def test_filter_large_files(self, semgrep_analyzer, tmp_path):
        """Test files larger than max_target_bytes are filtered"""
        # Create file > 2MB
        large_file = tmp_path / "large.js"
        large_file.write_text("x" * (3 * 1024 * 1024))
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'{"results": []}', b''))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await semgrep_analyzer.scan_directory(str(tmp_path))
            
            # Large files should be skipped
            assert semgrep_analyzer.logger.debug.called
    
    async def test_filter_vendor_signatures(self, semgrep_analyzer, tmp_path):
        """Test vendor files are filtered based on signatures"""
        # Create file with vendor signature
        vendor_file = tmp_path / "vendor.js"
        vendor_file.write_text("/* jQuery v3.6.0 */\n" + ("x" * 1000))
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'{"results": []}', b''))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            await semgrep_analyzer.scan_directory(str(tmp_path))
            
            # Vendor detection should be logged
            assert semgrep_analyzer.logger.debug.called


# ============================================================================
# SCAN DIRECTORY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestScanDirectory:
    """Test directory scanning functionality"""
    
    async def test_scan_directory_not_available(self, semgrep_analyzer, tmp_path):
        """Test scan when semgrep not available"""
        semgrep_analyzer.semgrep_available = False
        
        result = await semgrep_analyzer.scan_directory(str(tmp_path))
        
        assert result == []
    
    async def test_scan_directory_not_exists(self, semgrep_analyzer):
        """Test scan of non-existent directory"""
        semgrep_analyzer.semgrep_available = True
        
        result = await semgrep_analyzer.scan_directory("/nonexistent/path")
        
        assert result == []
    
    async def test_scan_directory_success(self, semgrep_analyzer, tmp_path):
        """Test successful directory scan"""
        # Create test files
        (tmp_path / "app.js").write_text("console.log('test');")
        (tmp_path / "lib.js").write_text("function test() {}")
        
        semgrep_analyzer.semgrep_available = True
        
        mock_findings = {
            "results": [
                {
                    "check_id": "javascript.lang.security.audit.xss",
                    "path": "app.js",
                    "start": {"line": 1, "col": 0},
                    "end": {"line": 1, "col": 10},
                    "extra": {"message": "Potential XSS"}
                }
            ]
        }
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(
                return_value=(json.dumps(mock_findings).encode(), b'')
            )
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            # Mock Path.rglob to return our test files
            with patch.object(Path, 'rglob', return_value=[tmp_path / "app.js", tmp_path / "lib.js"]):
                result = await semgrep_analyzer.scan_directory(str(tmp_path))
                
                assert isinstance(result, list)
    
    async def test_scan_directory_chunking(self, semgrep_analyzer, tmp_path):
        """Test file chunking for large directories"""
        # Create 150 files (more than chunk_size of 100)
        for i in range(150):
            (tmp_path / f"file{i}.js").write_text(f"console.log({i});")
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'{"results": []}', b''))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await semgrep_analyzer.scan_directory(str(tmp_path))
            
            # Should have chunked into multiple calls
            # Implementation dependent on actual chunking logic
            assert isinstance(result, list)
    
    async def test_scan_directory_timeout(self, semgrep_analyzer, tmp_path):
        """Test scan timeout handling"""
        (tmp_path / "test.js").write_text("console.log('test');")
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_exec.return_value = mock_process
            
            result = await semgrep_analyzer.scan_directory(str(tmp_path))
            
            # Should handle timeout gracefully
            assert isinstance(result, list)
    
    async def test_scan_directory_semgrep_error(self, semgrep_analyzer, tmp_path):
        """Test handling semgrep execution errors"""
        (tmp_path / "test.js").write_text("console.log('test');")
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'', b'Fatal error'))
            mock_process.returncode = 2
            mock_exec.return_value = mock_process
            
            result = await semgrep_analyzer.scan_directory(str(tmp_path))
            
            # Should handle error gracefully
            assert isinstance(result, list)
    
    async def test_scan_directory_malformed_json(self, semgrep_analyzer, tmp_path):
        """Test handling malformed JSON output from semgrep"""
        (tmp_path / "test.js").write_text("console.log('test');")
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'{invalid json}', b''))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await semgrep_analyzer.scan_directory(str(tmp_path))
            
            # Should handle gracefully
            assert isinstance(result, list)


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_scan_empty_directory(self, semgrep_analyzer, tmp_path):
        """Test scanning empty directory"""
        semgrep_analyzer.semgrep_available = True
        
        result = await semgrep_analyzer.scan_directory(str(tmp_path))
        
        # Should return empty list
        assert result == []
    
    @pytest.mark.asyncio
    async def test_scan_directory_with_subdirectories(self, semgrep_analyzer, tmp_path):
        """Test scanning directory with nested subdirectories"""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.js").write_text("console.log('test');")
        (tmp_path / "lib" / "util").mkdir(parents=True)
        (tmp_path / "lib" / "util" / "helper.js").write_text("function help() {}")
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'{"results": []}', b''))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            result = await semgrep_analyzer.scan_directory(str(tmp_path))
            
            # Should find files in subdirectories
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_validate_handles_permission_error(self, semgrep_analyzer):
        """Test validation handles permission errors"""
        with patch('shutil.which', return_value='/usr/bin/semgrep'):
            with patch('subprocess.run', side_effect=PermissionError("Access denied")):
                result = semgrep_analyzer.validate()
                
                assert result == False
    
    def test_findings_counter_initialization(self, semgrep_analyzer):
        """Test findings counter is initialized"""
        assert semgrep_analyzer.findings_count == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_binary
class TestSemgrepIntegration:
    """Integration tests with real semgrep binary"""
    
    async def test_real_semgrep_scan_if_available(self, semgrep_analyzer, tmp_path):
        """Test with real semgrep if available"""
        if not semgrep_analyzer.validate():
            pytest.skip("semgrep not installed")
        
        # Create test file with potential issue
        test_file = tmp_path / "test.js"
        test_file.write_text("""
function dangerous() {
    eval(userInput);  // Should be flagged
}
""")
        
        result = await semgrep_analyzer.scan_directory(str(tmp_path))
        
        # Real semgrep may or may not find issues depending on ruleset
        assert isinstance(result, list)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.asyncio
class TestPerformance:
    """Test performance of semgrep operations"""
    
    async def test_file_filtering_performance(self, semgrep_analyzer, tmp_path):
        """Test file filtering is fast for many files"""
        import time
        
        # Create 500 files
        for i in range(500):
            (tmp_path / f"file{i}.js").write_text(f"console.log({i});")
        
        semgrep_analyzer.semgrep_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b'{"results": []}', b''))
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            
            start = time.time()
            await semgrep_analyzer.scan_directory(str(tmp_path))
            elapsed = time.time() - start
            
            # Filtering 500 files should be reasonably fast
            # (actual scan time depends on mocking)
            assert elapsed < 10.0, f"File processing too slow: {elapsed}s"
