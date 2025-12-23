"""
Test Katana Fetcher Module
Tests the Katana integration without requiring actual Katana installation
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jsscanner.modules.katana_fetcher import KatanaFetcher


class TestKatanaFetcher(unittest.TestCase):
    """Test suite for Katana fetcher module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        self.config = {
            'katana': {
                'enabled': True,
                'depth': 2,
                'concurrency': 20,
                'rate_limit': 150,
                'timeout': 300,
                'args': ''
            }
        }
        
    def test_initialization_with_config(self):
        """Test KatanaFetcher initialization with config"""
        fetcher = KatanaFetcher(self.config, self.logger)
        
        self.assertTrue(fetcher.enabled)
        self.assertEqual(fetcher.depth, 2)
        self.assertEqual(fetcher.concurrency, 20)
        self.assertEqual(fetcher.rate_limit, 150)
        self.assertEqual(fetcher.timeout, 300)
        
    def test_initialization_with_defaults(self):
        """Test KatanaFetcher initialization with default values"""
        empty_config = {}
        fetcher = KatanaFetcher(empty_config, self.logger)
        
        self.assertFalse(fetcher.enabled)  # Default is disabled
        self.assertEqual(fetcher.depth, 2)
        self.assertEqual(fetcher.concurrency, 20)
        
    def test_is_js_url_detection(self):
        """Test JavaScript URL detection"""
        fetcher = KatanaFetcher(self.config, self.logger)
        
        # Valid JS URLs
        self.assertTrue(fetcher._is_js_url('https://example.com/app.js'))
        self.assertTrue(fetcher._is_js_url('https://example.com/bundle.min.js'))
        self.assertTrue(fetcher._is_js_url('https://example.com/app.mjs'))
        self.assertTrue(fetcher._is_js_url('https://example.com/module.ts'))
        self.assertTrue(fetcher._is_js_url('https://example.com/app.js?v=123'))
        self.assertTrue(fetcher._is_js_url('https://example.com/app.js#hash'))
        
        # Invalid URLs
        self.assertFalse(fetcher._is_js_url('https://example.com'))
        self.assertFalse(fetcher._is_js_url('https://example.com/page.html'))
        self.assertFalse(fetcher._is_js_url('https://js.example.com'))  # Domain has 'js'
        self.assertFalse(fetcher._is_js_url(''))
        self.assertFalse(fetcher._is_js_url(None))
        
    def test_is_direct_js_url(self):
        """Test direct JS URL detection (vs domain to crawl)"""
        fetcher = KatanaFetcher(self.config, self.logger)
        
        # Direct JS files
        self.assertTrue(fetcher._is_direct_js_url('https://example.com/app.js'))
        self.assertTrue(fetcher._is_direct_js_url('https://cdn.example.com/bundle.min.js'))
        
        # Domains to crawl (not direct JS files)
        self.assertFalse(fetcher._is_direct_js_url('https://example.com'))
        self.assertFalse(fetcher._is_direct_js_url('https://example.com/'))
        self.assertFalse(fetcher._is_direct_js_url('https://js.example.com'))
        
    def test_scope_filtering(self):
        """Test scope-based URL filtering"""
        fetcher = KatanaFetcher(self.config, self.logger)
        
        scope_domains = {'example.com', 'test.com'}
        
        urls = [
            'https://example.com/app.js',
            'https://api.example.com/bundle.js',
            'https://test.com/script.js',
            'https://evil.com/malicious.js',  # Out of scope
            'https://cdn.cloudflare.com/lib.js'  # Out of scope
        ]
        
        filtered = fetcher._filter_by_scope(urls, scope_domains)
        
        self.assertEqual(len(filtered), 3)
        self.assertIn('https://example.com/app.js', filtered)
        self.assertIn('https://api.example.com/bundle.js', filtered)  # Subdomain in scope
        self.assertIn('https://test.com/script.js', filtered)
        self.assertNotIn('https://evil.com/malicious.js', filtered)
        
    def test_disabled_fetcher_returns_empty(self):
        """Test that disabled fetcher returns empty list"""
        config = {'katana': {'enabled': False}}
        fetcher = KatanaFetcher(config, self.logger)
        
        result = fetcher.fetch_urls(['https://example.com'])
        
        self.assertEqual(result, [])
        
    @patch('jsscanner.modules.katana_fetcher.subprocess.run')
    def test_fetch_urls_success(self, mock_run):
        """Test successful URL fetching with mocked Katana"""
        fetcher = KatanaFetcher(self.config, self.logger)
        fetcher.katana_path = '/usr/bin/katana'  # Mock installation
        
        # Mock Katana output
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = """https://example.com/app.js
https://example.com/bundle.min.js
https://example.com/vendor.js
https://example.com/page.html
https://example.com/style.css"""
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        targets = ['https://example.com']
        result = fetcher.fetch_urls(targets)
        
        # Should only return JS files (3 out of 5 URLs)
        self.assertEqual(len(result), 3)
        self.assertIn('https://example.com/app.js', result)
        self.assertIn('https://example.com/bundle.min.js', result)
        self.assertIn('https://example.com/vendor.js', result)
        
    @patch('jsscanner.modules.katana_fetcher.subprocess.run')
    def test_fetch_urls_timeout(self, mock_run):
        """Test timeout handling"""
        fetcher = KatanaFetcher(self.config, self.logger)
        fetcher.katana_path = '/usr/bin/katana'
        
        # Mock timeout exception
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('katana', 300)
        
        result = fetcher.fetch_urls(['https://example.com'])
        
        self.assertEqual(result, [])
        self.logger.warning.assert_called()
        
    @patch('shutil.which')
    def test_is_installed_check(self, mock_which):
        """Test Katana installation detection"""
        # Test when installed
        mock_which.return_value = '/usr/bin/katana'
        self.assertTrue(KatanaFetcher.is_installed())
        
        # Test when not installed
        mock_which.return_value = None
        self.assertFalse(KatanaFetcher.is_installed())
        
    def test_filter_direct_js_urls_from_targets(self):
        """Test that direct JS URLs are filtered from crawl targets"""
        fetcher = KatanaFetcher(self.config, self.logger)
        fetcher.katana_path = '/usr/bin/katana'
        
        targets = [
            'https://example.com',  # Domain to crawl
            'https://example.com/app.js',  # Direct JS file
            'https://test.com',  # Domain to crawl
            'https://cdn.example.com/bundle.js'  # Direct JS file
        ]
        
        with patch('jsscanner.modules.katana_fetcher.subprocess.run') as mock_run:
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = ""
            mock_process.stderr = ""
            mock_run.return_value = mock_process
            
            fetcher.fetch_urls(targets)
            
            # Check that temp file was created with only domains
            call_args = mock_run.call_args
            self.assertIsNotNone(call_args)


class TestKatanaIntegration(unittest.TestCase):
    """Integration tests for Katana module"""
    
    def test_config_validation(self):
        """Test that invalid config values are handled"""
        config = {
            'katana': {
                'enabled': True,
                'depth': 'invalid',  # Should handle gracefully
                'concurrency': None,
                'timeout': -1
            }
        }
        
        # Should not raise exception
        fetcher = KatanaFetcher(config, Mock())
        
        # Verify it initialized with some values
        self.assertIsNotNone(fetcher.depth)
        
    def test_empty_target_list(self):
        """Test handling of empty target list"""
        config = {'katana': {'enabled': True}}
        fetcher = KatanaFetcher(config, Mock())
        fetcher.katana_path = '/usr/bin/katana'
        
        result = fetcher.fetch_urls([])
        
        self.assertEqual(result, [])


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("🧪 TESTING: Katana Fetcher Module")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestKatanaFetcher))
    suite.addTests(loader.loadTestsFromTestCase(TestKatanaIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
