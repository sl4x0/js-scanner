#!/usr/bin/env python3
"""
Final validation test for batch workflow implementation
"""
import yaml

print("=" * 60)
print("CONFIGURATION FILE VALIDATION")
print("=" * 60)

try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    bp = config.get('batch_processing', {})
    
    print("\n✅ Configuration loaded successfully")
    print("\nBatch Processing Settings:")
    print(f"  ✓ enabled: {bp.get('enabled')}")
    print(f"  ✓ download_threads: {bp.get('download_threads')}")
    print(f"  ✓ process_threads: {bp.get('process_threads')}")
    print(f"  ✓ cleanup_minified: {bp.get('cleanup_minified')}")
    
    # Validate expected values
    assert bp.get('enabled') == True, "batch_processing.enabled should be True"
    assert bp.get('download_threads') == 50, "download_threads should be 50"
    assert bp.get('process_threads') == 50, "process_threads should be 50"
    assert bp.get('cleanup_minified') == True, "cleanup_minified should be True"
    
    print("\n✅ All configuration values are correct!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("ALL VALIDATION TESTS PASSED!")
print("=" * 60)
