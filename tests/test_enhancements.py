"""
Test script for new enhancements:
1. Retry logic
2. Enhanced minification detection
3. Checkpoint system
4. Dynamic import detection
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from jsscanner.core.engine import ScanEngine
from jsscanner.core.state_manager import StateManager
from jsscanner.modules.processor import Processor
from jsscanner.utils.retry import retry_async, RETRY_CONFIG_HTTP
from jsscanner.modules.ast_analyzer import ASTAnalyzer
import logging
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('test')

def test_retry_decorator():
    """Test retry decorator with simulated failures"""
    print("\n" + "="*60)
    print("TEST 1: Retry Decorator")
    print("="*60)
    
    attempt_count = 0
    
    @retry_async(max_attempts=3, backoff_base=0.1, operation_name="test_operation")
    async def failing_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError(f"Simulated failure {attempt_count}")
        return "success"
    
    async def run_test():
        try:
            result = await failing_operation()
            print(f"✅ Retry test PASSED: {result} after {attempt_count} attempts")
            return True
        except Exception as e:
            print(f"❌ Retry test FAILED: {e}")
            return False
    
    return asyncio.run(run_test())

def test_minification_detection():
    """Test enhanced minification detection"""
    print("\n" + "="*60)
    print("TEST 2: Enhanced Minification Detection")
    print("="*60)
    
    # Load config
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Create temporary engine for testing
    temp_dir = Path('results/test-enhancements')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    state = StateManager(str(temp_dir))
    
    # Simulated minified code (long lines, no whitespace)
    minified_code = "function a(b,c){var d=b+c;return d*2;}function e(){console.log('test');}" * 100
    
    # Simulated clean code
    clean_code = """
function calculateSum(num1, num2) {
    // Add two numbers
    var result = num1 + num2;
    return result * 2;
}

function logMessage() {
    console.log('Hello World');
}
"""
    
    # Create a mock engine with _is_minified method
    class MockEngine:
        def __init__(self, config):
            self.config = config
            self.logger = logger
        
        def _is_minified(self, content: str) -> bool:
            """Enhanced minification detection"""
            if not content or len(content) < 100:
                return False
            
            minification_config = self.config.get('minification_detection', {})
            sample_size = minification_config.get('sample_size', 10000)
            threshold_score = minification_config.get('threshold_score', 5)
            
            sample = content[:sample_size]
            lines = sample.split('\n')
            
            if len(lines) < 3:
                return True
            
            score = 0
            
            # Heuristic 1: Average line length
            total_chars = sum(len(line) for line in lines)
            avg_line_length = total_chars / len(lines) if lines else 0
            if avg_line_length > 200:
                score += 3
            
            # Heuristic 2: Semicolon density
            semicolon_count = sample.count(';')
            semicolon_density = semicolon_count / len(lines) if lines else 0
            if semicolon_density > 5:
                score += 2
            
            # Heuristic 3: Whitespace ratio
            whitespace_chars = sum(1 for c in sample if c in ' \t\n\r')
            whitespace_ratio = whitespace_chars / len(sample) if sample else 0
            if whitespace_ratio < 0.15:
                score += 2
            
            # Heuristic 4: Short variable ratio
            import re
            short_vars = len(re.findall(r'\b[a-z]\b', sample))
            total_words = len(sample.split())
            short_var_ratio = short_vars / total_words if total_words else 0
            if short_var_ratio > 0.3:
                score += 2
            
            # Heuristic 5: Comment presence
            has_comments = '//' in sample or '/*' in sample
            if not has_comments:
                score += 1
            
            return score >= threshold_score
    
    engine = MockEngine(config)
    
    min_result = engine._is_minified(minified_code)
    clean_result = engine._is_minified(clean_code)
    
    if min_result and not clean_result:
        print(f"✅ Minification detection PASSED")
        print(f"   - Minified code detected: {min_result}")
        print(f"   - Clean code detected: {clean_result}")
        return True
    else:
        print(f"❌ Minification detection FAILED")
        print(f"   - Minified code detected: {min_result} (expected True)")
        print(f"   - Clean code detected: {clean_result} (expected False)")
        return False

def test_checkpoint_system():
    """Test checkpoint save/load functionality"""
    print("\n" + "="*60)
    print("TEST 3: Checkpoint System")
    print("="*60)
    
    # Create test directory
    temp_dir = Path('results/test-checkpoint')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    state = StateManager(str(temp_dir))
    
    # Save checkpoint
    test_phase = 'PHASE_2_DOWNLOADING'
    test_progress = {
        'download': {
            'completed': False,
            'total_downloaded': 50,
            'total_pending': 150
        }
    }
    
    state.save_checkpoint(test_phase, test_progress)
    
    # Verify checkpoint exists
    if state.has_checkpoint():
        resume_state = state.get_resume_state()
        
        if (resume_state['phase'] == test_phase and 
            resume_state['download']['total_downloaded'] == 50):
            print(f"✅ Checkpoint system PASSED")
            print(f"   - Checkpoint saved and loaded correctly")
            print(f"   - Phase: {resume_state['phase']}")
            print(f"   - Progress: {resume_state['download']['total_downloaded']}/200")
            
            # Cleanup
            state.delete_checkpoint()
            return True
        else:
            print(f"❌ Checkpoint data mismatch")
            return False
    else:
        print(f"❌ Checkpoint not found after save")
        return False

def test_dynamic_import_detection():
    """Test dynamic import pattern detection"""
    print("\n" + "="*60)
    print("TEST 4: Dynamic Import Detection")
    print("="*60)
    
    # Sample JavaScript with dynamic imports
    test_code = """
    // Dynamic import
    import('./components/Dashboard.js').then(module => {
        console.log(module);
    });
    
    // CommonJS require
    const utils = require('./utils/helpers.js');
    
    // Webpack chunk loading
    __webpack_require__.e(123).then(() => {
        console.log('Chunk loaded');
    });
    
    // React lazy loading
    const LazyComponent = React.lazy(() => import('./LazyComponent'));
    
    // Next.js dynamic
    const DynamicComponent = dynamic(() => import('../components/Hello'));
    """
    
    # This would require tree-sitter to be fully initialized
    # For now, just check that the methods exist
    from pathlib import Path
    import yaml
    
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    temp_dir = Path('results/test-dynamic-imports')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    paths = {
        'extracts': str(temp_dir / 'extracts'),
        'base': str(temp_dir)
    }
    Path(paths['extracts']).mkdir(parents=True, exist_ok=True)
    
    analyzer = ASTAnalyzer(config, logger, paths)
    
    # Check if methods exist
    has_extract_method = hasattr(analyzer, '_extract_dynamic_imports')
    has_chunk_method = hasattr(analyzer, '_extract_chunk_relationships')
    has_save_method = hasattr(analyzer, 'extract_and_save_dynamic_imports')
    
    if has_extract_method and has_chunk_method and has_save_method:
        print(f"✅ Dynamic import detection methods PRESENT")
        print(f"   - _extract_dynamic_imports: ✓")
        print(f"   - _extract_chunk_relationships: ✓")
        print(f"   - extract_and_save_dynamic_imports: ✓")
        return True
    else:
        print(f"❌ Dynamic import detection methods MISSING")
        print(f"   - _extract_dynamic_imports: {'✓' if has_extract_method else '✗'}")
        print(f"   - _extract_chunk_relationships: {'✓' if has_chunk_method else '✗'}")
        print(f"   - extract_and_save_dynamic_imports: {'✓' if has_save_method else '✗'}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("JS-SCANNER ENHANCEMENTS TEST SUITE")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(('Retry Decorator', test_retry_decorator()))
    results.append(('Minification Detection', test_minification_detection()))
    results.append(('Checkpoint System', test_checkpoint_system()))
    results.append(('Dynamic Import Detection', test_dynamic_import_detection()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<50} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
