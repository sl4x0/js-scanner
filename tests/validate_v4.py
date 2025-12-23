"""
v4.0 Installation Validator
Tests all Master Protocol phases
"""
import sys

print("=" * 70)
print("🚀 JS-Scanner v4.0 - Installation Validator")
print("=" * 70)
print()

all_passed = True

# PHASE 1: Dependencies
print("📦 PHASE 1: Checking Dependencies...")
try:
    import curl_cffi
    print("  ✅ curl_cffi installed")
except ImportError:
    print("  ❌ curl_cffi NOT installed - run: pip install curl_cffi>=0.5.10")
    all_passed = False

try:
    import rich
    print("  ✅ rich installed")
except ImportError:
    print("  ❌ rich NOT installed - run: pip install rich>=13.7.0")
    all_passed = False

try:
    # Check if aiohttp is still present (should be removed)
    import aiohttp
    print("  ⚠️  WARNING: aiohttp still installed (not needed in v4.0)")
    print("      Run: pip uninstall aiohttp")
except ImportError:
    print("  ✅ aiohttp removed (correct)")

print()

# PHASE 2: Stealth Network Layer
print("⚡ PHASE 2: Validating Stealth Network Layer...")
try:
    from jsscanner.modules.fetcher import Fetcher
    import inspect
    source = inspect.getsource(Fetcher)
    
    if 'curl_cffi' in source and 'AsyncSession' in source:
        print("  ✅ Fetcher using curl_cffi")
    else:
        print("  ❌ Fetcher not using curl_cffi")
        all_passed = False
    
    if 'aiohttp' not in source:
        print("  ✅ aiohttp references removed")
    else:
        print("  ⚠️  WARNING: aiohttp still referenced in fetcher.py")
except Exception as e:
    print(f"  ❌ Error checking fetcher: {e}")
    all_passed = False

print()

# PHASE 3: Dashboard
print("🎨 PHASE 3: Validating Dashboard...")
try:
    from jsscanner.core.dashboard import ScanDashboard
    from jsscanner.utils.logger import console
    print("  ✅ Dashboard module imported")
    print("  ✅ Rich console available")
except ImportError as e:
    print(f"  ❌ Dashboard import failed: {e}")
    all_passed = False

print()

# PHASE 4: File Structure
print("📂 PHASE 4: Validating File Structure...")
try:
    from jsscanner.utils.file_ops import FileOps
    from pathlib import Path
    import tempfile
    import shutil
    
    # Create temporary test structure
    with tempfile.TemporaryDirectory() as tmpdir:
        test_target = Path(tmpdir) / "test-target"
        paths = FileOps.create_result_structure(str(test_target))
        
        # Verify warehouse structure
        if '.warehouse' in str(paths['unique_js']):
            print("  ✅ .warehouse/ structure present")
        else:
            print("  ❌ .warehouse/ structure missing")
            all_passed = False
        
        # Verify tiers
        required_dirs = ['findings', 'artifacts', 'logs', '.warehouse']
        base_path = Path(paths['base'])
        
        for dir_name in required_dirs:
            if (base_path / dir_name).exists():
                print(f"  ✅ {dir_name}/ created")
            else:
                print(f"  ❌ {dir_name}/ missing")
                all_passed = False
                
except Exception as e:
    print(f"  ❌ File structure validation failed: {e}")
    all_passed = False

print()

# PHASE 5: SPA Intelligence
print("🧠 PHASE 5: Validating SPA Intelligence...")
try:
    from jsscanner.modules.ast_analyzer import ASTAnalyzer
    import inspect
    
    # Check if predict_chunks method exists
    if hasattr(ASTAnalyzer, 'predict_chunks'):
        print("  ✅ predict_chunks() method exists")
        
        # Check method signature
        sig = inspect.signature(ASTAnalyzer.predict_chunks)
        params = list(sig.parameters.keys())
        if 'content' in params and 'base_url' in params:
            print("  ✅ Method signature correct")
        else:
            print("  ⚠️  Method signature unexpected")
    else:
        print("  ❌ predict_chunks() method not found")
        all_passed = False
        
except Exception as e:
    print(f"  ❌ AST analyzer validation failed: {e}")
    all_passed = False

print()
print("=" * 70)

if all_passed:
    print("✅ ALL PHASES VALIDATED - v4.0 Installation Complete!")
    print()
    print("Next Steps:")
    print("  1. Run: python -m jsscanner -t example.com")
    print("  2. Check dashboard appears")
    print("  3. Verify .warehouse/ directory hidden")
    print("  4. Test WAF bypass on protected targets")
    sys.exit(0)
else:
    print("❌ VALIDATION FAILED - See errors above")
    print()
    print("To fix:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
