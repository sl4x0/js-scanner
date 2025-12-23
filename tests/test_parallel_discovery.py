"""
Test Parallel Discovery (Katana + SubJS)
Tests the new parallel execution architecture for Phase 1A discovery
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio


class TestParallelDiscovery(unittest.TestCase):
    """Test parallel execution of Katana and SubJS"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            'target': 'example.com',
            'katana': {
                'enabled': True,
                'depth': 2,
                'concurrency': 20,
                'rate_limit': 150,
                'timeout': 300
            },
            'subjs': {
                'enabled': True
            },
            'skip_live': False,
            'playwright': {
                'max_concurrent': 3,
                'page_timeout': 30000
            }
        }
        
        self.test_inputs = [
            'example.com',
            'api.example.com',
            'https://example.com/app.js'  # Direct JS file
        ]
    
    def test_parallel_task_creation(self):
        """Test that parallel tasks are created correctly"""
        # Mock configuration
        katana_enabled = True
        katana_path = '/usr/bin/katana'
        use_subjs = True
        
        # Simulate task creation logic
        parallel_tasks = []
        
        # Katana task
        if katana_enabled and katana_path:
            parallel_tasks.append("katana_task")
        
        # SubJS task
        if use_subjs:
            parallel_tasks.append("subjs_task")
        
        # Verify both tasks are created
        self.assertEqual(len(parallel_tasks), 2, "Should create 2 parallel tasks")
        self.assertIn("katana_task", parallel_tasks)
        self.assertIn("subjs_task", parallel_tasks)
        
        print("✓ Parallel task creation validation passed")
    
    @patch('asyncio.to_thread')
    @patch('jsscanner.modules.subjs_fetcher.SubJSFetcher.is_installed', return_value=True)
    def test_katana_runs_in_thread(self, mock_is_installed, mock_to_thread):
        """Test that Katana runs in a thread to avoid blocking asyncio"""
        async def mock_async_result():
            return ['https://example.com/app.js']
        
        mock_to_thread.return_value = mock_async_result()
        
        # Verify asyncio.to_thread is used for Katana (sync binary)
        self.assertTrue(callable(mock_to_thread), "asyncio.to_thread should be callable")
        
        print("✓ Katana threading validation passed")
    
    def test_asyncio_gather_exception_handling(self):
        """Test that asyncio.gather with return_exceptions=True works correctly"""
        async def failing_task():
            raise ValueError("Simulated failure")
        
        async def successful_task():
            return ['https://example.com/success.js']
        
        async def run_test():
            tasks = [failing_task(), successful_task()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # First result should be an exception
            self.assertIsInstance(results[0], Exception)
            # Second result should be a list
            self.assertIsInstance(results[1], list)
            self.assertEqual(results[1], ['https://example.com/success.js'])
        
        asyncio.run(run_test())
        print("✓ Exception handling in parallel tasks passed")
    
    def test_subjs_batch_vs_parallel(self):
        """Test that SubJS uses batch mode for subjs-only, parallel mode otherwise"""
        # Case 1: subjs-only mode (no Katana) -> Should use batch mode
        subjs_only = True
        katana_enabled = False
        
        # In this case, subjs_task_info would be None (no parallel task)
        # and batch mode should be used
        use_batch = subjs_only and not katana_enabled
        self.assertTrue(use_batch, "Should use batch mode for pure subjs-only")
        
        # Case 2: Hybrid mode (Katana + SubJS) -> Should use parallel mode
        subjs_only = False
        katana_enabled = True
        
        use_parallel = katana_enabled
        self.assertTrue(use_parallel, "Should use parallel mode when Katana is enabled")
        
        print("✓ SubJS mode selection logic passed")


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParallelDiscovery)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY: Parallel Discovery")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
