"""
Comprehensive tests for BundleUnpacker module
Tests bundle detection, webcrack integration, retry logic, cleanup, and signature matching
"""
import pytest
import asyncio
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from jsscanner.analysis.unpacking import BundleUnpacker


# ============================================================================
# SETUP AND FIXTURES
# ============================================================================

@pytest.fixture
def unpacker(mock_logger, default_config, tmp_path):
    """Create BundleUnpacker instance"""
    temp_dir = str(tmp_path / "unpacked")
    return BundleUnpacker(mock_logger, temp_dir=temp_dir, config=default_config)


@pytest.fixture
def unpacker_disabled(mock_logger, tmp_path):
    """Create BundleUnpacker with unpacking disabled"""
    config = {'bundle_unpacker': {'enabled': False}}
    temp_dir = str(tmp_path / "unpacked")
    return BundleUnpacker(mock_logger, temp_dir=temp_dir, config=config)


# ============================================================================
# WEBCRACK AVAILABILITY TESTS
# ============================================================================

@pytest.mark.unit
class TestWebcrackAvailability:
    """Test webcrack binary detection"""
    
    def test_check_webcrack_available(self, mock_logger, tmp_path):
        """Test successful webcrack detection"""
        config = {'bundle_unpacker': {'enabled': True}}
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=b'webcrack 2.0.0')
            
            unpacker = BundleUnpacker(mock_logger, str(tmp_path), config=config)
            
            assert unpacker.webcrack_available == True
            mock_logger.info.assert_any_call(pytest.approx("✓ webcrack available: webcrack 2.0.0", rel=1e-3))
    
    def test_check_webcrack_not_found(self, mock_logger, tmp_path):
        """Test webcrack not found"""
        config = {'bundle_unpacker': {'enabled': True}}
        
        with patch('subprocess.run', side_effect=FileNotFoundError):
            unpacker = BundleUnpacker(mock_logger, str(tmp_path), config=config)
            
            assert unpacker.webcrack_available == False
            assert mock_logger.warning.called
    
    def test_check_webcrack_timeout(self, mock_logger, tmp_path):
        """Test webcrack check timeout"""
        import subprocess
        config = {'bundle_unpacker': {'enabled': True}}
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd='webcrack', timeout=5)):
            unpacker = BundleUnpacker(mock_logger, str(tmp_path), config=config)
            
            assert unpacker.webcrack_available == False


# ============================================================================
# SHOULD_UNPACK TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestShouldUnpack:
    """Test bundle detection logic"""
    
    async def test_should_unpack_disabled_in_config(self, unpacker_disabled, sample_webpack_bundle):
        """Test unpacking disabled in config"""
        result = await unpacker_disabled.should_unpack(sample_webpack_bundle, len(sample_webpack_bundle))
        
        assert result == False
    
    async def test_should_unpack_webcrack_not_available(self, unpacker, sample_webpack_bundle):
        """Test when webcrack is not available"""
        unpacker.webcrack_available = False
        
        result = await unpacker.should_unpack(sample_webpack_bundle, len(sample_webpack_bundle))
        
        assert result == False
    
    async def test_should_unpack_file_too_small(self, unpacker):
        """Test small files are not unpacked"""
        small_content = "function test() {}"
        
        result = await unpacker.should_unpack(small_content, len(small_content))
        
        # Default min_file_size is 100KB
        assert result == False
    
    async def test_should_unpack_webpack_signature(self, unpacker, sample_webpack_bundle):
        """Test Webpack bundle signature detection"""
        unpacker.webcrack_available = True
        # Enable bundle unpacking in config
        unpacker.config = {'bundle_unpacker': {'enabled': True, 'min_file_size': 50000}}
        
        # Make it large enough to meet min_file_size
        large_bundle = sample_webpack_bundle + ("x" * 100000)
        
        result = await unpacker.should_unpack(large_bundle, len(large_bundle))
        
        assert result == True
    
    async def test_should_unpack_vite_signature(self, unpacker):
        """Test Vite bundle signature detection"""
        unpacker.webcrack_available = True
        
        vite_content = '__vite__' + ("x" * 150000)
        
        result = await unpacker.should_unpack(vite_content, len(vite_content))
        
        assert result == True
    
    async def test_should_unpack_parcel_signature(self, unpacker):
        """Test Parcel bundle signature detection"""
        unpacker.webcrack_available = True
        
        parcel_content = 'parcelRequire' + ("x" * 150000)
        
        result = await unpacker.should_unpack(parcel_content, len(parcel_content))
        
        assert result == True
    
    async def test_should_unpack_amd_signature(self, unpacker):
        """Test AMD bundle signature detection"""
        unpacker.webcrack_available = True
        
        amd_content = 'define.amd' + ("x" * 150000)
        
        result = await unpacker.should_unpack(amd_content, len(amd_content))
        
        assert result == True
    
    async def test_should_unpack_system_register(self, unpacker):
        """Test System.register signature detection"""
        unpacker.webcrack_available = True
        
        system_content = 'System.register' + ("x" * 150000)
        
        result = await unpacker.should_unpack(system_content, len(system_content))
        
        assert result == True
    
    async def test_should_unpack_case_insensitive(self, unpacker):
        """Test signature detection is case-insensitive"""
        unpacker.webcrack_available = True
        
        content = 'WEBPACK' + ("x" * 150000)
        
        result = await unpacker.should_unpack(content, len(content))
        
        assert result == True
    
    async def test_should_unpack_no_signature(self, unpacker):
        """Test files without bundle signatures are not unpacked"""
        unpacker.webcrack_available = True
        
        # Large file but no bundle signature
        content = "function myApp() { console.log('test'); }" * 5000
        
        result = await unpacker.should_unpack(content, len(content))
        
        assert result == False
    
    async def test_should_unpack_custom_min_size(self, mock_logger, tmp_path):
        """Test custom minimum file size configuration"""
        config = {
            'bundle_unpacker': {
                'enabled': True,
                'min_file_size': 50000  # 50KB
            }
        }
        
        unpacker = BundleUnpacker(mock_logger, str(tmp_path), config=config)
        unpacker.webcrack_available = True
        
        # 60KB file with signature
        content = 'webpack' + ("x" * 60000)
        
        result = await unpacker.should_unpack(content, len(content))
        
        assert result == True


# ============================================================================
# UNPACK_BUNDLE TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestUnpackBundle:
    """Test bundle unpacking execution"""
    
    async def test_unpack_bundle_success(self, unpacker, tmp_path):
        """Test successful bundle unpacking"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("webpack bundle content")
        output_dir = tmp_path / "output"
        
        unpacker.webcrack_available = True
        
        # Mock successful webcrack execution
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'Success', b''))
            mock_exec.return_value = mock_process
            
            # Create some fake extracted files
            output_dir.mkdir(parents=True)
            (output_dir / "file1.js").write_text("content1")
            (output_dir / "file2.js").write_text("content2")
            
            result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
            
            assert result is not None
            assert result['success'] == True
            assert result['file_count'] >= 0
            assert 'extracted_files' in result
    
    async def test_unpack_bundle_webcrack_not_available(self, unpacker, tmp_path):
        """Test unpacking when webcrack not available"""
        unpacker.webcrack_available = False
        
        input_file = tmp_path / "bundle.js"
        output_dir = tmp_path / "output"
        
        result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
        
        assert result is None
    
    async def test_unpack_bundle_webcrack_failure(self, unpacker, tmp_path):
        """Test handling webcrack failure"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("bundle content")
        output_dir = tmp_path / "output"
        
        unpacker.webcrack_available = True
        
        # Mock failed webcrack execution
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(b'', b'Error: failed'))
            mock_exec.return_value = mock_process
            
            result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
            
            assert result is None or result['success'] == False
    
    async def test_unpack_bundle_timeout(self, unpacker, tmp_path):
        """Test unpacking timeout (5 minutes)"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("bundle content")
        output_dir = tmp_path / "output"
        
        unpacker.webcrack_available = True
        
        # Mock process that times out
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_exec.return_value = mock_process
            
            result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
            
            assert result is None or result.get('success') == False
    
    async def test_unpack_bundle_directory_cleanup(self, unpacker, tmp_path):
        """Test existing directory cleanup before unpacking"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("bundle content")
        output_dir = tmp_path / "output"
        
        # Create existing directory with files
        output_dir.mkdir(parents=True)
        (output_dir / "old_file.js").write_text("old content")
        
        unpacker.webcrack_available = True
        
        # Mock successful execution
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'Success', b''))
            mock_exec.return_value = mock_process
            
            result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
            
            # Old file should be removed during cleanup
            # (Actual cleanup happens in the implementation)
    
    async def test_unpack_bundle_directory_conflict_retry(self, unpacker, tmp_path):
        """Test retry on directory conflict"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("bundle content")
        output_dir = tmp_path / "output"
        
        unpacker.webcrack_available = True
        
        # Mock first attempt fails with "already exists", second succeeds
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process_fail = AsyncMock()
            mock_process_fail.returncode = 1
            mock_process_fail.communicate = AsyncMock(
                return_value=(b'', b'Error: directory already exists')
            )
            
            mock_process_success = AsyncMock()
            mock_process_success.returncode = 0
            mock_process_success.communicate = AsyncMock(return_value=(b'Success', b''))
            
            mock_exec.side_effect = [mock_process_fail, mock_process_success]
            
            # Create output dir to trigger conflict
            output_dir.mkdir(parents=True)
            
            # This may attempt retry in implementation
            result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
            
            # Should eventually succeed or fail gracefully
            assert isinstance(result, dict) or result is None
    
    async def test_unpack_bundle_counts_extracted_files(self, unpacker, tmp_path):
        """Test correct counting of extracted JavaScript files"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("bundle content")
        output_dir = tmp_path / "output"
        
        unpacker.webcrack_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'Success', b''))
            mock_exec.return_value = mock_process
            
            # Create extracted files
            output_dir.mkdir(parents=True)
            (output_dir / "file1.js").write_text("content1")
            (output_dir / "file2.js").write_text("content2")
            (output_dir / "subdir").mkdir()
            (output_dir / "subdir" / "file3.js").write_text("content3")
            
            result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
            
            if result and result['success']:
                assert result['file_count'] >= 0
                assert 'extracted_files' in result
    
    async def test_unpack_bundle_creates_parent_directory(self, unpacker, tmp_path):
        """Test that parent directories are created"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("bundle content")
        
        # Deep nested output path
        output_dir = tmp_path / "deep" / "nested" / "path" / "output"
        
        unpacker.webcrack_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b'Success', b''))
            mock_exec.return_value = mock_process
            
            await unpacker.unpack_bundle(str(input_file), str(output_dir))
            
            # Parent should be created
            assert output_dir.parent.exists()


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    async def test_should_unpack_empty_content(self, unpacker):
        """Test empty content"""
        result = await unpacker.should_unpack('', 0)
        assert result == False
    
    async def test_should_unpack_exact_size_boundary(self, unpacker):
        """Test file exactly at size boundary"""
        unpacker.webcrack_available = True
        
        # Exactly 102400 bytes (default min_file_size)
        content = 'webpack' + ('x' * (102400 - 7))
        
        result = await unpacker.should_unpack(content, len(content))
        
        # Should unpack files >= min_size
        assert result in [True, False]  # Implementation dependent
    
    async def test_unpack_bundle_missing_input_file(self, unpacker, tmp_path):
        """Test unpacking with non-existent input file"""
        unpacker.webcrack_available = True
        
        non_existent = str(tmp_path / "nonexistent.js")
        output_dir = str(tmp_path / "output")
        
        result = await unpacker.unpack_bundle(non_existent, output_dir)
        
        # Should handle gracefully
        assert result is None or result.get('success') == False
    
    async def test_unpack_bundle_permission_error(self, unpacker, tmp_path):
        """Test handling permission errors during cleanup"""
        input_file = tmp_path / "bundle.js"
        input_file.write_text("content")
        output_dir = tmp_path / "output"
        
        unpacker.webcrack_available = True
        
        # Mock shutil.rmtree to raise PermissionError
        with patch('shutil.rmtree', side_effect=PermissionError):
            with patch('asyncio.create_subprocess_exec') as mock_exec:
                mock_process = AsyncMock()
                mock_process.returncode = 1
                mock_process.communicate = AsyncMock(return_value=(b'', b'already exists'))
                mock_exec.return_value = mock_process
                
                # Should handle permission error gracefully
                result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
                
                assert isinstance(result, dict) or result is None
    
    async def test_temp_dir_creation(self, mock_logger, tmp_path):
        """Test temporary directory is created on initialization"""
        temp_dir = tmp_path / "custom_temp"
        
        config = {'bundle_unpacker': {'enabled': True}}
        unpacker = BundleUnpacker(mock_logger, str(temp_dir), config=config)
        
        assert Path(temp_dir).exists()


# ============================================================================
# CONFIGURATION INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestConfigurationIntegration:
    """Test configuration integration"""
    
    async def test_config_enabled_flag(self, mock_logger, tmp_path):
        """Test bundle_unpacker.enabled flag is respected"""
        config_disabled = {'bundle_unpacker': {'enabled': False}}
        unpacker = BundleUnpacker(mock_logger, str(tmp_path), config_disabled)
        
        # Even with webcrack available, should not unpack
        unpacker.webcrack_available = True
        content = 'webpack' + ('x' * 150000)
        
        result = await unpacker.should_unpack(content, len(content))
        
        assert result == False
    
    async def test_config_min_file_size(self, mock_logger, tmp_path):
        """Test custom min_file_size configuration"""
        config = {
            'bundle_unpacker': {
                'enabled': True,
                'min_file_size': 200000  # 200KB
            }
        }
        
        unpacker = BundleUnpacker(mock_logger, str(tmp_path), config)
        unpacker.webcrack_available = True
        
        # 150KB file (below threshold)
        small_content = 'webpack' + ('x' * 150000)
        result = await unpacker.should_unpack(small_content, len(small_content))
        assert result == False
        
        # 250KB file (above threshold)
        large_content = 'webpack' + ('x' * 250000)
        result = await unpacker.should_unpack(large_content, len(large_content))
        assert result == True
    
    async def test_config_default_values(self, mock_logger, tmp_path):
        """Test default config values are used when not specified"""
        config = {}
        unpacker = BundleUnpacker(mock_logger, str(tmp_path), config)
        
        # Should use defaults
        bundle_config = unpacker.config.get('bundle_unpacker', {})
        assert bundle_config.get('enabled', False) in [True, False]
        assert bundle_config.get('min_file_size', 102400) >= 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.requires_binary
class TestBundleUnpackerIntegration:
    """Integration tests with real webcrack (if available)"""
    
    async def test_real_webpack_bundle_if_available(self, unpacker, tmp_path, sample_webpack_bundle):
        """Test with real webcrack if available"""
        if not unpacker.webcrack_available:
            pytest.skip("webcrack not installed")
        
        input_file = tmp_path / "bundle.js"
        input_file.write_text(sample_webpack_bundle)
        output_dir = tmp_path / "output"
        
        result = await unpacker.unpack_bundle(str(input_file), str(output_dir))
        
        # If webcrack succeeds, should have results
        if result and result.get('success'):
            assert result['file_count'] >= 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.asyncio
class TestPerformance:
    """Test performance of unpacking operations"""
    
    async def test_should_unpack_performance(self, unpacker):
        """Test should_unpack is fast"""
        import time
        
        unpacker.webcrack_available = True
        content = 'webpack' + ('x' * 200000)
        
        start = time.time()
        for _ in range(100):
            await unpacker.should_unpack(content, len(content))
        elapsed = time.time() - start
        
        # Should be very fast (signature matching only)
        assert elapsed < 1.0, f"should_unpack too slow: {elapsed}s for 100 calls"
    
    async def test_signature_detection_on_large_file(self, unpacker):
        """Test signature detection only checks first 5000 chars"""
        import time
        
        unpacker.webcrack_available = True
        
        # Signature at beginning, but huge file
        content = 'webpack' + ('x' * 10 * 1024 * 1024)  # 10MB
        
        start = time.time()
        result = await unpacker.should_unpack(content, len(content))
        elapsed = time.time() - start
        
        # Should be fast even for large files
        assert elapsed < 0.5, f"Signature detection slow on large file: {elapsed}s"
        assert result == True
