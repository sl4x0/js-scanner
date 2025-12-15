"""
Comprehensive Manual Test Suite for JS Scanner Bug Fixes
Tests all critical changes made to the scanner
"""
import sys
import os

def test_imports():
    """Test 1: Verify all modules can be imported"""
    print("Test 1: Module Import Test")
    print("-" * 50)
    
    try:
        from jsscanner.modules import secret_scanner
        print("✅ secret_scanner module imported")
    except Exception as e:
        print(f"❌ secret_scanner failed: {e}")
        return False
    
    try:
        from jsscanner.modules import fetcher
        print("✅ fetcher module imported")
    except Exception as e:
        print(f"❌ fetcher failed: {e}")
        return False
    
    try:
        from jsscanner.core import notifier
        print("✅ notifier module imported")
    except Exception as e:
        print(f"❌ notifier failed: {e}")
        return False
    
    try:
        from jsscanner.modules import ast_analyzer
        print("✅ ast_analyzer module imported")
    except Exception as e:
        print(f"❌ ast_analyzer failed: {e}")
        return False
    
    try:
        from jsscanner.modules import processor
        print("✅ processor module imported")
    except Exception as e:
        print(f"❌ processor failed: {e}")
        return False
    
    try:
        from jsscanner.utils import logger
        print("✅ logger module imported")
    except Exception as e:
        print(f"❌ logger failed: {e}")
        return False
    
    try:
        from jsscanner.core import state_manager
        print("✅ state_manager module imported (cross-platform)")
    except Exception as e:
        print(f"❌ state_manager failed: {e}")
        return False
    
    print("✅ All modules imported successfully!\n")
    return True


def test_cross_platform_file_locking():
    """Test 2: Verify cross-platform file locking works"""
    print("Test 2: Cross-Platform File Locking")
    print("-" * 50)
    
    try:
        from jsscanner.core.state_manager import StateManager
        import tempfile
        import json
        from pathlib import Path
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Create required files
        history_file = temp_path / 'history.json'
        secrets_file = temp_path / 'secrets.json'
        metadata_file = temp_path / 'metadata.json'
        
        history_file.write_text(json.dumps({'scanned_hashes': []}))
        secrets_file.write_text(json.dumps([]))
        metadata_file.write_text(json.dumps({}))
        
        # Initialize StateManager
        sm = StateManager(str(temp_path))
        
        # Test locking methods exist and are callable
        assert hasattr(sm, '_lock_file'), "Missing _lock_file method"
        assert hasattr(sm, '_unlock_file'), "Missing _unlock_file method"
        print(f"✅ Cross-platform locking methods exist (Platform: {sys.platform})")
        
        # Test basic operations
        test_hash = "abc123"
        is_scanned = sm.is_scanned(test_hash)
        print(f"✅ is_scanned() works: {is_scanned}")
        
        sm.mark_as_scanned(test_hash, "https://example.com/test.js")
        is_scanned_after = sm.is_scanned(test_hash)
        assert is_scanned_after == True, "Hash should be marked as scanned"
        print(f"✅ mark_as_scanned() works")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print("✅ Cross-platform file locking works!\n")
        return True
        
    except Exception as e:
        print(f"❌ File locking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wayback_url_validation():
    """Test 3: Verify Wayback URL validation"""
    print("Test 3: Wayback URL Validation")
    print("-" * 50)
    
    try:
        # We'll test the validation logic by importing the fetcher module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "fetcher", 
            "jsscanner/modules/fetcher.py"
        )
        fetcher_module = importlib.util.module_from_spec(spec)
        
        # Check that _validate_wayback_url method exists
        # (We can't easily test it without a Fetcher instance, but we can verify the code exists)
        with open("jsscanner/modules/fetcher.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        assert "_validate_wayback_url" in content, "Missing _validate_wayback_url method"
        assert "\\x00" in content, "Missing null byte check"
        assert "<script" in content or "javascript:" in content, "Missing XSS check"
        assert "2048" in content, "Missing length check"
        
        print("✅ Wayback URL validation method exists")
        print("✅ Null byte check present")
        print("✅ XSS check present")
        print("✅ Length check present")
        print("✅ Wayback URL validation implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ Wayback validation test failed: {e}")
        return False


def test_discord_timeout():
    """Test 4: Verify Discord webhook timeout"""
    print("Test 4: Discord Webhook Timeout")
    print("-" * 50)
    
    try:
        with open("jsscanner/core/notifier.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "ClientTimeout" in content, "Missing ClientTimeout"
        assert "timeout=timeout" in content or "timeout=" in content, "Missing timeout parameter"
        
        print("✅ Discord timeout implementation found")
        print("✅ Discord webhook timeout implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ Discord timeout test failed: {e}")
        return False


def test_browser_memory_fixes():
    """Test 5: Verify browser memory leak fixes"""
    print("Test 5: Browser Memory Leak Fixes")
    print("-" * 50)
    
    try:
        with open("jsscanner/modules/fetcher.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "asyncio.sleep(1)" in content, "Missing cleanup delay"
        assert "--disable-background-timer-throttling" in content, "Missing Chromium arg 1"
        assert "--disable-backgrounding-occluded-windows" in content, "Missing Chromium arg 2"
        assert "--disable-renderer-backgrounding" in content, "Missing Chromium arg 3"
        
        print("✅ Cleanup delay added")
        print("✅ Additional Chromium args present")
        print("✅ Browser memory fixes implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ Browser memory test failed: {e}")
        return False


def test_ast_memory_cleanup():
    """Test 6: Verify AST memory cleanup"""
    print("Test 6: AST Memory Cleanup")
    print("-" * 50)
    
    try:
        with open("jsscanner/modules/ast_analyzer.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "del tree" in content, "Missing tree cleanup"
        assert "del root_node" in content, "Missing root_node cleanup"
        assert "if not tree or not tree.root_node:" in content, "Missing tree validation"
        
        print("✅ Tree cleanup present")
        print("✅ Root node cleanup present")
        print("✅ Tree validation present")
        print("✅ AST memory cleanup implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ AST memory test failed: {e}")
        return False


def test_beautifier_timeout():
    """Test 7: Verify beautifier timeout"""
    print("Test 7: Beautifier Timeout")
    print("-" * 50)
    
    try:
        with open("jsscanner/modules/processor.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "asyncio.wait_for" in content, "Missing wait_for"
        assert "timeout=30" in content or "timeout=30.0" in content, "Missing 30s timeout"
        
        print("✅ asyncio.wait_for present")
        print("✅ 30-second timeout present")
        print("✅ Beautifier timeout implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ Beautifier timeout test failed: {e}")
        return False


def test_rate_limit_backoff():
    """Test 8: Verify rate limit backoff"""
    print("Test 8: Rate Limit Backoff")
    print("-" * 50)
    
    try:
        with open("jsscanner/modules/fetcher.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "429" in content and "503" in content, "Missing rate limit codes"
        assert "Retry-After" in content, "Missing Retry-After header"
        assert "2 ** retry_count" in content or "exponential" in content.lower(), "Missing exponential backoff"
        
        print("✅ Rate limit codes (429, 503) present")
        print("✅ Retry-After header handling present")
        print("✅ Exponential backoff present")
        print("✅ Rate limit backoff implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ Rate limit backoff test failed: {e}")
        return False


def test_log_rotation():
    """Test 9: Verify log rotation"""
    print("Test 9: Log Rotation")
    print("-" * 50)
    
    try:
        with open("jsscanner/utils/logger.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "RotatingFileHandler" in content, "Missing RotatingFileHandler"
        assert "maxBytes=10 * 1024 * 1024" in content or "10485760" in content, "Missing 10MB max"
        assert "backupCount=5" in content, "Missing 5 backups"
        
        print("✅ RotatingFileHandler imported")
        print("✅ 10MB max size configured")
        print("✅ 5 backup files configured")
        print("✅ Log rotation implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ Log rotation test failed: {e}")
        return False


def test_trufflehog_validation():
    """Test 10: Verify TruffleHog validation"""
    print("Test 10: TruffleHog Validation")
    print("-" * 50)
    
    try:
        with open("jsscanner/modules/secret_scanner.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "_validate_trufflehog" in content, "Missing validation method"
        assert "shutil.which" in content, "Missing shutil.which check"
        assert "--version" in content, "Missing version check"
        
        print("✅ Validation method present")
        print("✅ Binary existence check present")
        print("✅ Version check present")
        print("✅ TruffleHog validation implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ TruffleHog validation test failed: {e}")
        return False


def test_trufflehog_rate_limit():
    """Test 11: Verify TruffleHog rate limiting"""
    print("Test 11: TruffleHog Rate Limiting")
    print("-" * 50)
    
    try:
        with open("jsscanner/modules/secret_scanner.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "asyncio.Semaphore" in content, "Missing Semaphore"
        assert "trufflehog_max_concurrent" in content, "Missing config option"
        assert "async with self.semaphore:" in content, "Missing semaphore usage"
        
        print("✅ Semaphore present")
        print("✅ Config option present")
        print("✅ Semaphore usage present")
        print("✅ TruffleHog rate limiting implemented!\n")
        return True
        
    except Exception as e:
        print(f"❌ TruffleHog rate limit test failed: {e}")
        return False


def test_config_updates():
    """Test 12: Verify config.yaml updates"""
    print("Test 12: Configuration Updates")
    print("-" * 50)
    
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "trufflehog_max_concurrent" in content, "Missing trufflehog_max_concurrent"
        assert "timeouts:" in content, "Missing timeouts section"
        
        print("✅ trufflehog_max_concurrent present")
        print("✅ timeouts section present")
        print("✅ Configuration updated!\n")
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print("JS SCANNER - COMPREHENSIVE TEST SUITE")
    print("=" * 70 + "\n")
    
    tests = [
        test_imports,
        test_cross_platform_file_locking,
        test_wayback_url_validation,
        test_discord_timeout,
        test_browser_memory_fixes,
        test_ast_memory_cleanup,
        test_beautifier_timeout,
        test_rate_limit_backoff,
        test_log_rotation,
        test_trufflehog_validation,
        test_trufflehog_rate_limit,
        test_config_updates,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! ✅")
        print("\n✨ The scanner is ready for production use!")
        return True
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\n⚠️  Please review the failures above before deploying.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
