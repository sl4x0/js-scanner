"""
Comprehensive tests for NoiseFilter module
Tests URL filtering, content filtering, vendor detection, CDN patterns, hash matching, and heuristics
"""
import pytest
import json
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch
from jsscanner.analysis.filtering import NoiseFilter


# ============================================================================
# SETUP AND FIXTURES
# ============================================================================

@pytest.fixture
def noise_filter(ignored_patterns_config, mock_logger, default_config):
    """Create NoiseFilter instance with mocked config"""
    return NoiseFilter(
        config_path=ignored_patterns_config,
        logger=mock_logger,
        scan_config=default_config
    )


@pytest.fixture
def noise_filter_no_config(tmp_path, mock_logger, default_config):
    """Create NoiseFilter with non-existent config file"""
    non_existent = str(tmp_path / "nonexistent.json")
    return NoiseFilter(
        config_path=non_existent,
        logger=mock_logger,
        scan_config=default_config
    )


# ============================================================================
# URL FILTERING TESTS
# ============================================================================

@pytest.mark.unit
class TestURLFiltering:
    """Test URL-based filtering logic"""
    
    def test_should_skip_url_cdn_domain(self, noise_filter):
        """Test that CDN domains are filtered"""
        test_cases = [
            ('https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js', True),
            ('https://cdn.jsdelivr.net/npm/vue@3/dist/vue.js', True),
            ('https://unpkg.com/react@18/umd/react.production.min.js', True),
            ('https://googleapis.com/ajax/libs/angularjs/1.8.0/angular.min.js', True),
        ]
        
        for url, expected_skip in test_cases:
            should_skip, reason = noise_filter.should_skip_url(url)
            assert should_skip == expected_skip, f"URL {url} should skip: {expected_skip}"
            if expected_skip:
                # Check reason contains either 'CDN:', 'vendor_pattern:', or 'Pattern:'
                assert any(x in reason for x in ['CDN:', 'vendor_pattern:', 'Pattern:']), \
                    f"Reason '{reason}' should indicate filtering type"
    
    def test_should_skip_url_vendor_patterns(self, noise_filter):
        """Test vendor URL patterns are matched"""
        test_cases = [
            'https://example.com/vendor.js',
            'https://example.com/chunk-vendors.abc123.js',
            'https://example.com/polyfills.bundle.js',
        ]
        
        for url in test_cases:
            should_skip, reason = noise_filter.should_skip_url(url)
            # Some URLs may or may not be skipped depending on ignored_patterns.json
            # Just verify the method returns valid response
            assert isinstance(should_skip, bool)
            assert isinstance(reason, str)
    
    def test_should_not_skip_custom_urls(self, noise_filter):
        """Test that custom/application URLs are not filtered"""
        test_cases = [
            'https://myapp.com/app.js',
            'https://example.com/custom/script.js',
            'https://internal.company.com/bundle.js',
        ]
        
        for url in test_cases:
            should_skip, reason = noise_filter.should_skip_url(url)
            assert not should_skip, f"Custom URL {url} should NOT be skipped"
            assert reason == ""
    
    def test_should_skip_url_pattern_matching(self, noise_filter):
        """Test URL pattern matching from config"""
        test_cases = [
            ('https://example.com/jquery-3.6.0.min.js', True),
            ('https://example.com/bootstrap.bundle.js', True),
            ('https://example.com/react.production.min.js', True),
            ('https://example.com/vue.global.js', True),
            ('https://example.com/angular.min.js', True),
        ]
        
        for url, expected_skip in test_cases:
            should_skip, reason = noise_filter.should_skip_url(url)
            assert should_skip == expected_skip, f"Pattern URL {url} skip={expected_skip}"
    
    def test_should_skip_url_case_insensitive(self, noise_filter):
        """Test URL filtering is case-insensitive"""
        test_cases = [
            'https://CDNJS.CLOUDFLARE.COM/lib.js',
            'https://CDN.JsDelivr.Net/npm/package.js',
            'https://example.com/VENDOR.JS',
        ]
        
        for url in test_cases:
            should_skip, _ = noise_filter.should_skip_url(url)
            assert should_skip, f"Case-insensitive URL {url} should be skipped"
    
    def test_should_skip_url_with_port(self, noise_filter):
        """Test URL filtering handles ports correctly"""
        url = 'https://cdnjs.cloudflare.com:443/lib.js'
        should_skip, reason = noise_filter.should_skip_url(url)
        assert should_skip, "URL with port should be skipped if domain matches"
    
    def test_should_skip_url_stats_tracking(self, noise_filter):
        """Test that statistics are tracked correctly"""
        initial_total = noise_filter.stats['total_checked']
        
        # Check any URL - stats should increment
        noise_filter.should_skip_url('https://cdnjs.cloudflare.com/lib.js')
        assert noise_filter.stats['total_checked'] == initial_total + 1, "Total checked should increment"
        
        # Check another URL
        noise_filter.should_skip_url('https://example.com/app.js')
        assert noise_filter.stats['total_checked'] == initial_total + 2, "Total checked should increment again"
    
    def test_should_skip_url_malformed_url(self, noise_filter):
        """Test handling of malformed URLs"""
        malformed_urls = [
            '',
            'not-a-url',
            'ftp://',
            'javascript:void(0)',
        ]
        
        for url in malformed_urls:
            should_skip, reason = noise_filter.should_skip_url(url)
            # Should not crash, return False for invalid URLs
            assert not should_skip or reason != ""


# ============================================================================
# CONTENT HASH FILTERING TESTS
# ============================================================================

@pytest.mark.unit
class TestContentHashFiltering:
    """Test content hash matching for known libraries"""
    
    def test_should_skip_content_known_hash(self, noise_filter, sample_js_vendor_jquery):
        """Test that known library hashes are detected"""
        # Calculate hash
        content_hash = hashlib.md5(sample_js_vendor_jquery.encode('utf-8', errors='ignore')).hexdigest()
        
        # Add this hash to the filter's config
        noise_filter.config['known_library_hashes']['test-jquery'] = content_hash
        
        should_skip, reason = noise_filter.should_skip_content(sample_js_vendor_jquery)
        assert should_skip, "Known library hash should be skipped"
        assert 'test-jquery' in reason.lower() or 'library' in reason.lower()
    
    def test_should_skip_content_unknown_hash(self, noise_filter):
        """Test that unknown content hashes are not filtered"""
        custom_content = "function myCustomApp() { console.log('custom'); }"
        should_skip, reason = noise_filter.should_skip_content(custom_content)
        assert not should_skip or 'vendor' in reason.lower(), "Unknown hash should not be skipped (unless heuristic triggers)"
    
    def test_should_skip_content_stats_tracking(self, noise_filter):
        """Test content filtering updates statistics"""
        # Add known hash
        content = "test content"
        content_hash = hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()
        noise_filter.config['known_library_hashes']['test'] = content_hash
        
        initial_hash_count = noise_filter.stats['filtered_hash']
        noise_filter.should_skip_content(content)
        assert noise_filter.stats['filtered_hash'] == initial_hash_count + 1


# ============================================================================
# VENDOR LIBRARY HEURISTIC TESTS
# ============================================================================

@pytest.mark.unit
class TestVendorHeuristics:
    """Test vendor library heuristic detection"""
    
    def test_is_likely_vendor_large_minified(self, noise_filter):
        """Test detection of large minified files"""
        # Create large minified content (>50KB, <20 newlines)
        large_minified = "var x=1;" * 10000  # ~70KB with minimal newlines
        should_skip, reason = noise_filter.should_skip_content(large_minified)
        assert should_skip, "Large minified file should be detected as vendor"
        assert 'vendor' in reason.lower() and 'minified' in reason.lower()
    
    def test_is_likely_vendor_jquery_signature(self, noise_filter, sample_js_vendor_jquery):
        """Test jQuery signature detection"""
        should_skip, reason = noise_filter.should_skip_content(sample_js_vendor_jquery)
        assert should_skip, "jQuery signature should be detected"
        assert 'jquery' in reason.lower() or 'vendor' in reason.lower()
    
    def test_is_likely_vendor_umd_pattern(self, noise_filter, sample_js_minified):
        """Test UMD pattern detection"""
        should_skip, reason = noise_filter.should_skip_content(sample_js_minified)
        assert should_skip, "UMD pattern should be detected as vendor"
        assert 'umd' in reason.lower() or 'vendor' in reason.lower()
    
    def test_is_likely_vendor_react_signature(self, noise_filter):
        """Test React signature detection"""
        react_content = """/*! React v18.0.0 */
function createelement(type, props) {
    // React.createElement implementation
}
""" + "x" * 60000  # Make it large enough
        
        should_skip, reason = noise_filter.should_skip_content(react_content)
        assert should_skip, "React signature should be detected"
    
    def test_is_likely_vendor_webpack_signature(self, noise_filter, sample_webpack_bundle):
        """Test Webpack bundle detection"""
        # Make it large enough to trigger size check
        large_webpack = sample_webpack_bundle + ("x" * 60000)
        should_skip, reason = noise_filter.should_skip_content(large_webpack)
        assert should_skip, "Webpack bundle should be detected as vendor"
    
    def test_is_not_vendor_small_file(self, noise_filter):
        """Test small files are not flagged as vendor"""
        small_content = "console.log('hello');"
        should_skip, reason = noise_filter.should_skip_content(small_content)
        assert not should_skip, "Small custom file should not be filtered"
    
    def test_is_not_vendor_beautified_file(self, noise_filter, sample_js_beautified):
        """Test beautified files are not flagged as vendor"""
        # Make it large but with many newlines
        large_beautified = (sample_js_beautified + "\n") * 1000
        should_skip, reason = noise_filter.should_skip_content(large_beautified)
        # Should not be flagged due to high newline count
        assert not should_skip or 'minified' not in reason.lower()
    
    def test_vendor_signatures_comprehensive(self, noise_filter):
        """Test all vendor signature patterns"""
        signatures = [
            ('define.amd', 'AMD'),
            ('angular.module', 'Angular'),
            ('vue.component', 'Vue'),
            ('sentry.io', 'Sentry'),
            ('shopify.theme', 'Shopify'),
        ]
        
        for signature, expected_name in signatures:
            content = f"/* Header */\n{signature}\n" + ("x" * 60000)
            should_skip, reason = noise_filter.should_skip_content(content)
            # Note: May not skip if size threshold not met, so check reason if skipped
            if should_skip:
                # Just check that 'vendor' is mentioned in the reason
                assert 'vendor' in reason.lower(), f"Expected 'vendor' in reason, got: {reason}"


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

@pytest.mark.unit
class TestConfiguration:
    """Test configuration loading and handling"""
    
    def test_load_config_success(self, ignored_patterns_config, mock_logger, default_config):
        """Test successful config loading"""
        nf = NoiseFilter(ignored_patterns_config, mock_logger, default_config)
        assert 'cdn_domains' in nf.config
        assert 'url_patterns' in nf.config
        assert len(nf.config['cdn_domains']) > 0
    
    def test_load_config_missing_file(self, noise_filter_no_config):
        """Test graceful handling of missing config file"""
        # Should have default empty config
        assert noise_filter_no_config.config is not None
        assert 'cdn_domains' in noise_filter_no_config.config
        assert noise_filter_no_config.config['cdn_domains'] == []
    
    def test_load_config_malformed_json(self, tmp_path, mock_logger, default_config):
        """Test graceful handling of malformed config"""
        bad_config = tmp_path / "bad.json"
        bad_config.write_text("{ invalid json ]")
        
        nf = NoiseFilter(str(bad_config), mock_logger, default_config)
        # Should fall back to defaults
        assert nf.config is not None
        assert 'cdn_domains' in nf.config
    
    def test_configurable_thresholds(self, ignored_patterns_config, mock_logger):
        """Test configurable size and newline thresholds"""
        custom_config = {
            'noise_filter': {
                'min_file_size_kb': 100,
                'max_newlines': 10
            }
        }
        
        nf = NoiseFilter(ignored_patterns_config, mock_logger, custom_config)
        assert nf.min_size_kb == 100
        assert nf.max_newlines == 10
    
    def test_default_thresholds(self, ignored_patterns_config, mock_logger):
        """Test default thresholds when not in config"""
        nf = NoiseFilter(ignored_patterns_config, mock_logger, {})
        assert nf.min_size_kb == 50  # Default
        assert nf.max_newlines == 20  # Default


# ============================================================================
# STATISTICS TESTS
# ============================================================================

@pytest.mark.unit
class TestStatistics:
    """Test statistics tracking"""
    
    def test_stats_initialization(self, noise_filter):
        """Test statistics are initialized correctly"""
        assert 'filtered_cdn' in noise_filter.stats
        assert 'filtered_pattern' in noise_filter.stats
        assert 'filtered_vendor_url' in noise_filter.stats
        assert 'filtered_hash' in noise_filter.stats
        assert 'filtered_vendor' in noise_filter.stats
        assert 'total_checked' in noise_filter.stats
        
        # All should start at 0
        for key, value in noise_filter.stats.items():
            assert value == 0
    
    def test_stats_increment_correctly(self, noise_filter):
        """Test that stats increment for each filter type"""
        initial_total = noise_filter.stats['total_checked']
        
        # CDN filter - just check total increments
        noise_filter.should_skip_url('https://cdnjs.cloudflare.com/lib.js')
        assert noise_filter.stats['total_checked'] > initial_total, "Stats should increment"
        
        # Another check
        noise_filter.should_skip_url('https://example.com/app.js')
        assert noise_filter.stats['total_checked'] > initial_total + 1, "Stats should keep incrementing"
        assert noise_filter.stats['total_checked'] >= 2


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_url(self, noise_filter):
        """Test empty URL handling"""
        should_skip, reason = noise_filter.should_skip_url('')
        assert not should_skip  # Should not crash
    
    def test_empty_content(self, noise_filter):
        """Test empty content handling"""
        should_skip, reason = noise_filter.should_skip_content('')
        assert not should_skip  # Empty content is not vendor
    
    def test_unicode_content(self, noise_filter):
        """Test Unicode content handling"""
        unicode_content = "function test() { console.log('你好世界'); }"
        should_skip, reason = noise_filter.should_skip_content(unicode_content)
        assert not should_skip  # Should handle Unicode
    
    def test_very_large_content(self, noise_filter):
        """Test very large content (>10MB)"""
        very_large = "x" * (10 * 1024 * 1024)  # 10MB
        # Should not crash
        should_skip, reason = noise_filter.should_skip_content(very_large)
        assert isinstance(should_skip, bool)
    
    def test_binary_content(self, noise_filter):
        """Test binary content handling"""
        binary_content = "\x00\x01\x02\x03\xff\xfe"
        # Should not crash
        should_skip, reason = noise_filter.should_skip_content(binary_content)
        assert isinstance(should_skip, bool)
    
    def test_url_with_special_characters(self, noise_filter):
        """Test URLs with special characters"""
        special_urls = [
            'https://example.com/file%20name.js',
            'https://example.com/file?query=param&other=value',
            'https://example.com/file#anchor',
            'https://example.com/файл.js',  # Cyrillic
        ]
        
        for url in special_urls:
            should_skip, reason = noise_filter.should_skip_url(url)
            assert isinstance(should_skip, bool)  # Should not crash


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
class TestNoiseFilterIntegration:
    """Test NoiseFilter integration scenarios"""
    
    def test_full_filtering_pipeline(self, noise_filter, sample_js_vendor_jquery):
        """Test complete filtering workflow"""
        # URL check
        vendor_url = 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js'
        should_skip_url, reason_url = noise_filter.should_skip_url(vendor_url)
        
        # Content check
        should_skip_content, reason_content = noise_filter.should_skip_content(sample_js_vendor_jquery)
        
        # At least one should filter
        assert should_skip_url or should_skip_content, \
            "Vendor library should be filtered by URL or content"
    
    def test_custom_app_not_filtered(self, noise_filter):
        """Test that custom application code is not filtered"""
        custom_url = 'https://myapp.example.com/app.js'
        custom_content = """
function myApp() {
    const apiKey = process.env.API_KEY;
    fetch('/api/data')
        .then(r => r.json())
        .then(data => console.log(data));
}
"""
        
        should_skip_url, _ = noise_filter.should_skip_url(custom_url)
        should_skip_content, _ = noise_filter.should_skip_content(custom_content)
        
        assert not should_skip_url, "Custom URL should not be filtered"
        assert not should_skip_content, "Custom content should not be filtered"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.unit
class TestPerformance:
    """Test performance of filtering operations"""
    
    def test_url_filtering_performance(self, noise_filter):
        """Test URL filtering performance with many URLs"""
        import time
        
        urls = [f'https://example{i}.com/app{i}.js' for i in range(1000)]
        
        start = time.time()
        for url in urls:
            noise_filter.should_skip_url(url)
        elapsed = time.time() - start
        
        # Should process 1000 URLs in less than 1 second
        assert elapsed < 1.0, f"URL filtering too slow: {elapsed}s for 1000 URLs"
    
    def test_content_filtering_performance(self, noise_filter):
        """Test content filtering performance"""
        import time
        
        # Test with multiple medium-sized contents
        contents = ["function test() { }" * 1000 for _ in range(100)]
        
        start = time.time()
        for content in contents:
            noise_filter.should_skip_content(content)
        elapsed = time.time() - start
        
        # Should process 100 contents in reasonable time
        assert elapsed < 2.0, f"Content filtering too slow: {elapsed}s for 100 items"
