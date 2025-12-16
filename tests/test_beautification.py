#!/usr/bin/env python3
"""
Beautification Tests
Validates JavaScript beautification and processing
"""
from pathlib import Path


class BeautificationValidator:
    """Validates beautification functionality"""
    
    def __init__(self):
        self.test_results = []
    
    def test_minification_detection(self, content: str) -> bool:
        """
        Test if minified code is detected correctly
        
        Args:
            content: JavaScript content
            
        Returns:
            True if detected as minified
        """
        # Simple heuristic: avg line length > 500 chars = minified
        lines = content.split('\n')
        if not lines:
            return False
        
        avg_length = sum(len(line) for line in lines) / len(lines)
        return avg_length > 500
    
    def test_beautification_quality(self, original: str, beautified: str) -> dict:
        """
        Test beautification quality
        
        Args:
            original: Original minified content
            beautified: Beautified content
            
        Returns:
            Quality metrics
        """
        metrics = {
            'original_lines': len(original.split('\n')),
            'beautified_lines': len(beautified.split('\n')),
            'expansion_ratio': 0,
            'avg_line_length_original': 0,
            'avg_line_length_beautified': 0,
            'quality_score': 0
        }
        
        if metrics['original_lines'] > 0:
            orig_lines = original.split('\n')
            metrics['avg_line_length_original'] = sum(len(l) for l in orig_lines) / len(orig_lines)
        
        if metrics['beautified_lines'] > 0:
            beau_lines = beautified.split('\n')
            metrics['avg_line_length_beautified'] = sum(len(l) for l in beau_lines) / len(beau_lines)
            
            if metrics['original_lines'] > 0:
                metrics['expansion_ratio'] = metrics['beautified_lines'] / metrics['original_lines']
        
        # Quality score: good beautification should have:
        # - More lines (expansion ratio > 2)
        # - Shorter average line length
        if metrics['expansion_ratio'] > 2 and metrics['avg_line_length_beautified'] < 100:
            metrics['quality_score'] = 100
        elif metrics['expansion_ratio'] > 1.5:
            metrics['quality_score'] = 75
        elif metrics['expansion_ratio'] > 1:
            metrics['quality_score'] = 50
        else:
            metrics['quality_score'] = 25
        
        return metrics
    
    def verify_results_directory(self, target_dir: Path) -> dict:
        """
        Verify beautification results
        
        Args:
            target_dir: Target results directory
            
        Returns:
            Verification results
        """
        results = {
            'has_minified': False,
            'has_unminified': False,
            'minified_count': 0,
            'unminified_count': 0,
            'files_processed': []
        }
        
        minified_dir = target_dir / 'files' / 'minified'
        unminified_dir = target_dir / 'files' / 'unminified'
        
        if minified_dir.exists():
            results['has_minified'] = True
            minified_files = list(minified_dir.glob('*.js'))
            results['minified_count'] = len(minified_files)
        
        if unminified_dir.exists():
            results['has_unminified'] = True
            unminified_files = list(unminified_dir.glob('*.js'))
            results['unminified_count'] = len(unminified_files)
            results['files_processed'] = [f.name for f in unminified_files]
        
        return results
    
    def print_report(self, results: dict):
        """Print beautification report"""
        print("\n" + "="*80)
        print("BEAUTIFICATION VALIDATION REPORT")
        print("="*80)
        
        print(f"\n✨ BEAUTIFICATION RESULTS")
        print(f"   Minified files: {results['minified_count']}")
        print(f"   Unminified files: {results['unminified_count']}")
        
        if results['files_processed']:
            print(f"\n   Processed files ({len(results['files_processed'])}):")
            for filename in results['files_processed'][:5]:
                print(f"      - {filename}")
            if len(results['files_processed']) > 5:
                print(f"      ... and {len(results['files_processed']) - 5} more")
        
        print("\n" + "="*80)
        success = results['has_minified'] or results['has_unminified']
        print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
        print("="*80 + "\n")
        
        return success


def test_sample_beautification():
    """Test beautification with sample code"""
    minified = 'function test(){var a=1;var b=2;return a+b;}console.log(test());'
    
    # Expected beautified output (simplified)
    expected = """function test() {
    var a = 1;
    var b = 2;
    return a + b;
}
console.log(test());"""
    
    validator = BeautificationValidator()
    
    # Test detection
    is_minified = validator.test_minification_detection(minified)
    print(f"Minification detection: {'✅' if is_minified else '❌'}")
    
    # Test quality (would need actual beautifier output)
    # This is a simplified test
    print("\nNote: Full quality test requires actual scan results")


if __name__ == '__main__':
    test_sample_beautification()
