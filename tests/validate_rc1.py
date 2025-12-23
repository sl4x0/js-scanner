"""
v4.0 RC1 Final Validation Test
Tests all critical components before production deployment
"""
import sys

print("=" * 80)
print("🚀 JS-Scanner v4.0 RC1 - Final Validation")
print("=" * 80)
print()

all_passed = True

# TEST 1: Python Version Check
print("TEST 1: Python Version (requires 3.11+)")
py_version = sys.version_info
if py_version >= (3, 11):
    print(f"  ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro} - PASS")
else:
    print(f"  ❌ Python {py_version.major}.{py_version.minor}.{py_version.micro} - FAIL (need 3.11+)")
    all_passed = False
print()

# TEST 2: Critical Dependencies
print("TEST 2: Critical Dependencies")
deps_status = []

# curl_cffi (WAF bypass)
try:
    import curl_cffi
    print(f"  ✅ curl_cffi {curl_cffi.__version__} - Stealth networking ready")
    deps_status.append(True)
except ImportError:
    print("  ❌ curl_cffi - NOT INSTALLED (critical for WAF bypass)")
    all_passed = False
    deps_status.append(False)

# rich (Dashboard)
try:
    import rich
    try:
        from importlib.metadata import version
        rich_version = version('rich')
        print(f"  ✅ rich {rich_version} - Live dashboard ready")
    except:
        print(f"  ✅ rich (installed) - Live dashboard ready")
    deps_status.append(True)
except ImportError:
    print("  ❌ rich - NOT INSTALLED (critical for dashboard)")
    all_passed = False
    deps_status.append(False)

# playwright (Browser automation)
try:
    from playwright.async_api import async_playwright
    print(f"  ✅ playwright - Browser automation ready")
    deps_status.append(True)
except ImportError:
    print("  ❌ playwright - NOT INSTALLED")
    all_passed = False
    deps_status.append(False)

# tree-sitter (AST analysis)
try:
    import tree_sitter
    import tree_sitter_javascript
    print(f"  ✅ tree-sitter - AST analysis ready")
    deps_status.append(True)
except ImportError:
    print("  ❌ tree-sitter - NOT INSTALLED")
    all_passed = False
    deps_status.append(False)

# aiofiles (Async I/O)
try:
    import aiofiles
    print(f"  ✅ aiofiles - Async I/O ready")
    deps_status.append(True)
except ImportError:
    print("  ❌ aiofiles - NOT INSTALLED")
    all_passed = False
    deps_status.append(False)

print()

# TEST 3: Module Imports
print("TEST 3: Core Module Imports")
try:
    from jsscanner.core.engine import ScanEngine
    print("  ✅ ScanEngine")
except Exception as e:
    print(f"  ❌ ScanEngine - {e}")
    all_passed = False

try:
    from jsscanner.modules.fetcher import Fetcher
    print("  ✅ Fetcher (curl_cffi)")
except Exception as e:
    print(f"  ❌ Fetcher - {e}")
    all_passed = False

try:
    from jsscanner.core.dashboard import ScanDashboard
    print("  ✅ Dashboard (Rich)")
except Exception as e:
    print(f"  ❌ Dashboard - {e}")
    all_passed = False

try:
    from jsscanner.modules.ast_analyzer import ASTAnalyzer
    print("  ✅ AST Analyzer")
except Exception as e:
    print(f"  ❌ AST Analyzer - {e}")
    all_passed = False

try:
    from jsscanner.utils.file_ops import FileOps
    print("  ✅ FileOps")
except Exception as e:
    print(f"  ❌ FileOps - {e}")
    all_passed = False

print()

# TEST 4: Fetcher Configuration
print("TEST 4: Fetcher curl_cffi Integration")
try:
    from jsscanner.modules.fetcher import Fetcher
    from jsscanner.utils.logger import setup_logger
    
    logger = setup_logger()
    config = {
        'timeouts': {'http_request': 15},
        'verify_ssl': False,
        'user_agents': ['Mozilla/5.0']
    }
    
    fetcher = Fetcher(config, logger)
    
    # Check critical attributes
    if hasattr(fetcher, 'ssl_verify'):
        print("  ✅ SSL verification config present (for curl_cffi)")
    else:
        print("  ❌ Missing ssl_verify attribute")
        all_passed = False
    
    # Verify no aiohttp imports
    import inspect
    source = inspect.getsource(Fetcher)
    if 'aiohttp' not in source:
        print("  ✅ No aiohttp dependencies (clean migration)")
    else:
        print("  ⚠️  WARNING: aiohttp still referenced")
    
    if 'AsyncSession' in source:
        print("  ✅ curl_cffi AsyncSession used")
    else:
        print("  ❌ curl_cffi AsyncSession not found")
        all_passed = False
        
except Exception as e:
    print(f"  ❌ Fetcher validation failed: {e}")
    all_passed = False

print()

# TEST 5: File Structure
print("TEST 5: Hunter-Architect File Structure")
try:
    from jsscanner.utils.file_ops import FileOps
    from pathlib import Path
    import shutil
    
    paths = FileOps.create_result_structure('rc1-validation-test')
    base = Path(paths['base'])
    
    # Check tier structure
    tiers = {
        'findings': True,
        'artifacts/source_code': True,
        'logs': True,
        '.warehouse/db': True,
        '.warehouse/raw_js': True
    }
    
    all_tiers_ok = True
    for tier, _ in tiers.items():
        exists = (base / tier).exists()
        if exists:
            print(f"  ✅ {tier}/")
        else:
            print(f"  ❌ {tier}/ - NOT CREATED")
            all_tiers_ok = False
            all_passed = False
    
    if all_tiers_ok:
        print("  ✅ All tiers validated")
    
    # Cleanup
    shutil.rmtree(base)
    
except Exception as e:
    print(f"  ❌ Structure validation failed: {e}")
    all_passed = False

print()

# TEST 6: Dashboard
print("TEST 6: Rich Dashboard")
try:
    from jsscanner.core.dashboard import ScanDashboard
    from jsscanner.utils.logger import console
    
    dashboard = ScanDashboard('test.com', console)
    print("  ✅ Dashboard initialized")
    
    dashboard.update_stats(phase='Testing', secrets_found=5)
    print("  ✅ Dashboard stats updated")
    
except Exception as e:
    print(f"  ❌ Dashboard test failed: {e}")
    all_passed = False

print()

# TEST 7: SPA Intelligence
print("TEST 7: SPA Chunk Prediction")
try:
    from jsscanner.modules.ast_analyzer import ASTAnalyzer
    
    # Check if predict_chunks method exists
    if hasattr(ASTAnalyzer, 'predict_chunks'):
        print("  ✅ predict_chunks() method exists")
    else:
        print("  ❌ predict_chunks() method missing")
        all_passed = False
        
except Exception as e:
    print(f"  ❌ SPA intelligence test failed: {e}")
    all_passed = False

print()

# FINAL RESULT
print("=" * 80)
if all_passed:
    print("✅ ALL TESTS PASSED - v4.0 RC1 READY FOR PRODUCTION")
    print()
    print("Next Steps:")
    print("  1. Deploy to VPS: git push origin main")
    print("  2. Install deps: pip install -r requirements.txt")
    print("  3. Test live: python -m jsscanner -t hackerone.com --threads 10")
    print("  4. Monitor: Check .warehouse/ is hidden, dashboard works")
    print()
    print("Status: 🟢 PRODUCTION READY")
    sys.exit(0)
else:
    print("❌ VALIDATION FAILED - Review errors above")
    print()
    print("Common fixes:")
    print("  - Python version: Use Python 3.11+ (pyenv install 3.11)")
    print("  - Dependencies: pip install -r requirements.txt")
    print("  - Playwright: playwright install chromium")
    sys.exit(1)

print("=" * 80)
