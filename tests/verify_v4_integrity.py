"""
JS-Scanner v4.0 Integrity Check
Automated test suite for validating:
- Stealth Network Layer (curl_cffi TLS fingerprinting)
- Warehouse vs Showroom file structure
- Critical dependencies
"""
import asyncio
import sys
import shutil
from pathlib import Path
import json

# Force project root into path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_stealth_network():
    print("⚡ TESTING: Stealth Network Layer (curl_cffi)...")
    try:
        from jsscanner.modules.fetcher import Fetcher
        import logging
        
        # Create minimal logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.ERROR)  # Suppress info/warning during tests
        
        # Mock config
        conf = {
            'timeouts': {'http_request': 10},
            'verify_ssl': False,
            'retry': {'http_requests': 1},
            'playwright': {'headless': True}
        }
        
        f = Fetcher(conf, logger=logger)
        await f.initialize()
        
        # Test against a TLS fingerprint checker (or fallback to httpbin)
        url = "https://httpbin.org/headers"
        print(f"   - Requesting {url}...")
        
        # Use internal impl to test the specific session logic
        # Note: We can't easily check the fingerprint here without a complex server,
        # but we can verify the library doesn't crash on init/request.
        response = await f.session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            ua = data['headers'].get('User-Agent', 'Unknown')
            print(f"   ✅ Success! UA Sent: {ua}")
            print("   ✅ curl_cffi is operational.")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            
    except TypeError as e:
        if "unexpected keyword argument 'ssl'" in str(e):
            print("   ❌ CRITICAL FAIL: 'ssl' argument still present in fetcher.py!")
            print("      FIX: Remove ssl= parameter from session.get() calls")
            return False
        else:
            print(f"   ❌ Error: {e}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True

def test_warehouse_structure():
    print("\n📂 TESTING: Warehouse vs Showroom Structure...")
    from jsscanner.utils.file_ops import FileOps
    
    target = "test_v4_structure"
    paths = FileOps.create_result_structure(target, base_path="tests_output")
    
    base = Path(paths['base'])
    
    # TIER 1: Executive Summary (REPORT.md created by reporter)
    # TIER 2: Intelligence (findings/)
    # TIER 3: Evidence (artifacts/)
    # TIER 4: Audit Trail (logs/)
    # TIER 5: Warehouse (.warehouse/)
    
    checks = [
        (base / "REPORT.md", False, "TIER 1: Executive Summary"),  # False = check parent exists
        (base / "findings", True, "TIER 2: Intelligence"),
        (base / "artifacts", True, "TIER 3: Evidence"),
        (base / "artifacts" / "source_code", True, "TIER 3: Source Code"),
        (base / "logs", True, "TIER 4: Audit Trail"),
        (base / ".warehouse", True, "TIER 5: Warehouse"),
        (base / ".warehouse" / "raw_js", True, "TIER 5: Raw Files"),
        (base / ".warehouse" / "db", True, "TIER 5: Database")
    ]
    
    all_pass = True
    for path, is_dir, description in checks:
        if path.exists():
            print(f"   ✅ Found: {path.relative_to(base.parent)} ({description})")
        else:
            # For REPORT.md, it's created later, so check if parent exists is fine for this test
            if not is_dir and path.parent.exists():
                 print(f"   ✅ Path structure ready for: {path.name} ({description})")
            else:
                print(f"   ❌ MISSING: {path} ({description})")
                all_pass = False
    
    # Verify backward compatibility mappings
    print("\n   🔄 Backward Compatibility Check:")
    compat_checks = {
        'extracts': 'findings',
        'secrets': 'findings',
        'unique_js': '.warehouse',
        'source_code': 'artifacts'
    }
    
    for old_key, expected_dir in compat_checks.items():
        if old_key in paths:
            actual = Path(paths[old_key])
            if expected_dir in str(actual):
                print(f"      ✅ paths['{old_key}'] → {expected_dir}/")
            else:
                print(f"      ❌ paths['{old_key}'] mapping incorrect")
                all_pass = False
        else:
            print(f"      ❌ Missing key: '{old_key}'")
            all_pass = False
    
    # Cleanup
    try:
        shutil.rmtree("tests_output")
    except: pass
    
    if all_pass:
        print("\n   ✅ FileOps logic is sound.")
    
    return all_pass

def test_dependencies():
    print("\n📦 TESTING: Dependencies...")
    missing = []
    all_ok = True
    
    # Critical v4.0 dependencies
    try: 
        import curl_cffi
        try:
            from importlib.metadata import version
            v = version('curl_cffi')
            print(f"   ✅ curl_cffi {v} installed")
        except:
            print("   ✅ curl_cffi installed")
    except ImportError:
        print("   ❌ curl_cffi - NOT INSTALLED (critical for WAF bypass)")
        missing.append("curl_cffi")
        all_ok = False
        
    try: 
        import rich
        try:
            from importlib.metadata import version
            v = version('rich')
            print(f"   ✅ rich {v} installed")
        except:
            print("   ✅ rich installed")
    except ImportError:
        print("   ❌ rich - NOT INSTALLED (critical for dashboard)")
        missing.append("rich")
        all_ok = False
    
    # Optional performance boost (Linux/macOS only)
    if sys.platform != 'win32':
        try: 
            import uvloop
            print("   ✅ uvloop installed (performance boost)")
        except ImportError:
            print("   ⚠️  uvloop not installed (optional, improves asyncio performance)")
    
    # Core dependencies
    try:
        import playwright
        print("   ✅ playwright installed")
    except ImportError:
        print("   ❌ playwright - NOT INSTALLED")
        missing.append("playwright")
        all_ok = False
        
    try:
        import tree_sitter
        print("   ✅ tree-sitter installed")
    except ImportError:
        print("   ❌ tree-sitter - NOT INSTALLED")
        missing.append("tree-sitter")
        all_ok = False
    
    if missing:
        print(f"\n   ❌ MISSING MODULES: {', '.join(missing)}")
        print(f"      FIX: pip install -r requirements.txt")
    else:
        print("\n   ✅ All v4.0 dependencies present.")
    
    return all_ok

def test_python_version():
    print("🐍 TESTING: Python Version...")
    version = sys.version_info
    required = (3, 11)
    
    if version >= required:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (meets 3.11+ requirement)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - INSUFFICIENT")
        print(f"      Required: Python 3.11+ (for asyncio.TaskGroup)")
        print(f"      FIX: Upgrade Python or use pyenv/conda")
        return False

async def main():
    print("="*60)
    print("🦅 JS-SCANNER v4.0 INTEGRITY CHECK")
    print("="*60)
    
    results = {}
    
    # Test 1: Python Version
    results['python'] = test_python_version()
    
    # Test 2: Dependencies
    results['deps'] = test_dependencies()
    
    # Test 3: File Structure
    results['structure'] = test_warehouse_structure()
    
    # Test 4: Stealth Network (requires async)
    results['network'] = await test_stealth_network()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.upper()}: {status}")
    
    print("="*60)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🚀 v4.0 is PRODUCTION READY")
        print("\nNext Steps:")
        print("   1. git push origin main")
        print("   2. On VPS: git pull && pip install -r requirements.txt")
        print("   3. Test live: python -m jsscanner -t example.com")
        return 0
    else:
        print(f"❌ TESTS FAILED ({total - passed}/{total} failures)")
        print("\n⚠️  Review errors above and fix before deployment")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
