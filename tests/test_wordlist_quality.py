#!/usr/bin/env python3
"""Test wordlist fragment filtering"""
import asyncio
import re
from pathlib import Path

async def test_wordlist_filtering():
    """Test that fragments are properly filtered"""
    
    # Import here to ensure module loads
    from jsscanner.modules.ast_analyzer import ASTAnalyzer
    from jsscanner.utils.logger import setup_logger
    
    logger = setup_logger('test')
    config = {'ast': {'min_word_length': 4}}
    paths = {'base': '.', 'extracts': 'test_output'}
    
    analyzer = ASTAnalyzer(config, logger, paths)
    
    # Test cases: (word, should_pass, reason)
    test_cases = [
        # Fragments (should FAIL)
        ('ndicat', False, 'Low vowel ratio'),
        ('eAlignm', False, 'Low vowel ratio + no suffix'),
        ('tsplatformpaym', False, 'Consonant cluster'),
        ('abcd', False, 'Low vowel ratio'),
        ('xyzw', False, 'No vowels'),
        ('tstst', False, 'Consonant cluster'),
        ('bcdfg', False, 'No vowels'),
        
        # Valid words (should PASS)
        ('button', True, 'Programming term'),
        ('indicator', True, 'Valid suffix + good ratio'),
        ('alignment', True, 'Valid suffix'),
        ('platform', True, 'Valid word'),
        ('payment', True, 'Valid suffix'),
        ('testing', True, 'Valid suffix'),
        ('component', True, 'Valid suffix'),
        ('navigation', True, 'Valid suffix'),
        ('undefined', True, 'Valid prefix'),
        ('enable', True, 'Programming term'),
        ('container', True, 'Programming term'),
        ('handler', True, 'Programming term'),
    ]
    
    print("Testing wordlist filtering...")
    print(f"{'='*70}")
    passed = 0
    failed = 0
    
    for word, should_pass, reason in test_cases:
        # Create a test set with just this word
        test_set = {word}
        filtered = analyzer._filter_wordlist(test_set)
        result = word in filtered
        
        if result == should_pass:
            print(f"✅ {word:20s} → {str(result):5} (expected {should_pass}) - {reason}")
            passed += 1
        else:
            print(f"❌ {word:20s} → {str(result):5} (expected {should_pass}) - {reason}")
            failed += 1
    
    print(f"{'='*70}")
    print(f"Results: {passed}/{len(test_cases)} passed")
    print(f"{'='*70}")
    
    return failed == 0

if __name__ == '__main__':
    success = asyncio.run(test_wordlist_filtering())
    exit(0 if success else 1)
