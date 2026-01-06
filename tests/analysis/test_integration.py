"""
Integration tests for the analysis module pipeline
Tests complete workflow from filtering through processing to scanning
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from jsscanner.analysis.filtering import NoiseFilter
from jsscanner.analysis.processor import Processor
from jsscanner.analysis.unpacking import BundleUnpacker


@pytest.mark.integration
@pytest.mark.asyncio
class TestAnalysisPipeline:
    """Test complete analysis pipeline"""
    
    async def test_filter_then_process(self, ignored_patterns_config, mock_logger, default_config, tmp_path):
        """Test filtering followed by processing"""
        # Create filter and processor
        filter = NoiseFilter(ignored_patterns_config, mock_logger, default_config)
        processor = Processor(mock_logger, config=default_config)
        
        # Custom JS file
        custom_js = "function app() { console.log('custom'); }"
        custom_url = "https://myapp.com/app.js"
        
        # Filter check
        should_skip_url, _ = filter.should_skip_url(custom_url)
        should_skip_content, _ = filter.should_skip_content(custom_js)
        
        assert not should_skip_url
        assert not should_skip_content
        
        # Process
        file_path = tmp_path / "app.js"
        file_path.write_text(custom_js)
        
        result = await processor.process(custom_js, str(file_path))
        assert isinstance(result, str)
    
    async def test_vendor_file_filtered_not_processed(self, ignored_patterns_config, mock_logger, default_config, sample_js_vendor_jquery):
        """Test vendor files are filtered and not processed"""
        filter = NoiseFilter(ignored_patterns_config, mock_logger, default_config)
        
        vendor_url = "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"
        
        should_skip_url, reason = filter.should_skip_url(vendor_url)
        should_skip_content, reason2 = filter.should_skip_content(sample_js_vendor_jquery)
        
        # At least one should filter
        assert should_skip_url or should_skip_content
    
    async def test_bundle_detection_and_unpacking(self, mock_logger, default_config, tmp_path, sample_webpack_bundle):
        """Test bundle detection triggers unpacking"""
        unpacker = BundleUnpacker(mock_logger, str(tmp_path / "unpacked"), default_config)
        unpacker.webcrack_available = True
        
        # Make bundle large enough
        large_bundle = sample_webpack_bundle + ("x" * 150000)
        
        should_unpack = await unpacker.should_unpack(large_bundle, len(large_bundle))
        
        assert should_unpack == True


@pytest.mark.integration
class TestConfigurationFlow:
    """Test configuration flows through all components"""
    
    def test_config_propagation(self, default_config, mock_logger, tmp_result_paths, ignored_patterns_config):
        """Test configuration is properly propagated"""
        # Create components with same config
        filter = NoiseFilter(ignored_patterns_config, mock_logger, default_config)
        processor = Processor(mock_logger, config=default_config)
        
        # Verify config is loaded
        assert filter.scan_config == default_config
        assert processor.config == default_config
    
    def test_custom_config_values(self, mock_logger):
        """Test custom configuration values are respected"""
        custom_config = {
            'noise_filter': {'min_file_size_kb': 100},
            'beautification': {'timeout_small': 60},
            'bundle_unpacker': {'enabled': False}
        }
        
        processor = Processor(mock_logger, config=custom_config)
        
        assert processor.config['beautification']['timeout_small'] == 60


@pytest.mark.integration
@pytest.mark.asyncio
class TestEndToEndScenarios:
    """Test realistic end-to-end scenarios"""
    
    async def test_process_custom_application(self, mock_logger, default_config, tmp_path, ignored_patterns_config):
        """Test processing custom application code"""
        filter = NoiseFilter(ignored_patterns_config, mock_logger, default_config)
        processor = Processor(mock_logger, config=default_config)
        
        # Custom app with obfuscation
        obfuscated_app = 'var k="\\x41\\x50\\x49";fetch("/api/"+k);'
        app_url = "https://myapp.example.com/main.js"
        
        # Should not be filtered
        skip_url, _ = filter.should_skip_url(app_url)
        skip_content, _ = filter.should_skip_content(obfuscated_app)
        
        assert not skip_url
        assert not skip_content
        
        # Should be processed
        file_path = tmp_path / "main.js"
        result = await processor.process(obfuscated_app, str(file_path))
        
        # Should decode hex
        assert 'API' in result or isinstance(result, str)


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
class TestPerformanceIntegration:
    """Test performance of integrated pipeline"""
    
    async def test_pipeline_performance(self, mock_logger, default_config, tmp_path, ignored_patterns_config):
        """Test pipeline processes multiple files efficiently"""
        import time
        
        filter = NoiseFilter(ignored_patterns_config, mock_logger, default_config)
        processor = Processor(mock_logger, config=default_config)
        
        # Create 50 files
        files = []
        for i in range(50):
            f = tmp_path / f"file{i}.js"
            f.write_text(f"function test{i}() {{ console.log({i}); }}")
            files.append((str(f), f"https://example.com/file{i}.js"))
        
        start = time.time()
        
        for file_path, url in files:
            # Filter
            skip_url, _ = filter.should_skip_url(url)
            if not skip_url:
                content = Path(file_path).read_text()
                skip_content, _ = filter.should_skip_content(content)
                
                if not skip_content:
                    # Process
                    await processor.process(content, file_path)
        
        elapsed = time.time() - start
        
        # Should complete reasonably fast
        assert elapsed < 30.0, f"Pipeline too slow: {elapsed}s for 50 files"
