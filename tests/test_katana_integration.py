"""
Manual Test: Katana Integration
Test the Katana integration with the actual scanner engine
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jsscanner.core.engine import ScanEngine
from jsscanner.modules.katana_fetcher import KatanaFetcher


async def test_katana_integration():
    """Test Katana integration with mock data"""
    
    print("=" * 70)
    print("🧪 MANUAL TEST: Katana Integration")
    print("=" * 70)
    
    # Test 1: Check if Katana is installed
    print("\n📋 Test 1: Checking Katana Installation")
    print("-" * 70)
    is_installed = KatanaFetcher.is_installed()
    print(f"Katana installed: {is_installed}")
    
    if is_installed:
        print("✅ Katana is available")
        fetcher = KatanaFetcher({'katana': {'enabled': True}}, None)
        version = fetcher.get_version()
        if version:
            print(f"   Version: {version}")
    else:
        print("⚠️  Katana not installed")
        print("   Install with: go install github.com/projectdiscovery/katana/cmd/katana@latest")
    
    # Test 2: Config parsing
    print("\n📋 Test 2: Config Parsing")
    print("-" * 70)
    
    test_config = {
        'katana': {
            'enabled': True,
            'depth': 3,
            'concurrency': 25,
            'rate_limit': 200,
            'timeout': 600,
            'args': '-headless'
        }
    }
    
    fetcher = KatanaFetcher(test_config, None)
    print(f"✓ Enabled: {fetcher.enabled}")
    print(f"✓ Depth: {fetcher.depth}")
    print(f"✓ Concurrency: {fetcher.concurrency}")
    print(f"✓ Rate Limit: {fetcher.rate_limit}/s")
    print(f"✓ Timeout: {fetcher.timeout}s")
    print(f"✓ Custom Args: '{fetcher.custom_args}'")
    
    # Test 3: URL filtering
    print("\n📋 Test 3: URL Filtering")
    print("-" * 70)
    
    test_urls = [
        'https://example.com/app.js',
        'https://example.com/bundle.min.js',
        'https://example.com/page.html',
        'https://example.com/style.css',
        'https://cdn.example.com/vendor.mjs',
        'https://example.com/module.ts',
        'https://js.example.com',  # Domain with 'js' in name
    ]
    
    js_urls = [url for url in test_urls if fetcher._is_js_url(url)]
    print(f"Total URLs: {len(test_urls)}")
    print(f"JS URLs detected: {len(js_urls)}")
    print(f"JS URLs: {js_urls}")
    
    # Test 4: Scope filtering
    print("\n📋 Test 4: Scope Filtering")
    print("-" * 70)
    
    scope_domains = {'example.com', 'test.com'}
    mixed_urls = [
        'https://example.com/app.js',
        'https://api.example.com/api.js',
        'https://test.com/script.js',
        'https://evil.com/malware.js',
    ]
    
    filtered = fetcher._filter_by_scope(mixed_urls, scope_domains)
    print(f"Total URLs: {len(mixed_urls)}")
    print(f"In-scope URLs: {len(filtered)}")
    print(f"Filtered URLs: {filtered}")
    
    # Test 5: Engine integration check
    print("\n📋 Test 5: Engine Integration")
    print("-" * 70)
    
    try:
        # Create a minimal config
        minimal_config = {
            'katana': {'enabled': False},  # Disabled for testing
            'discord_webhook': 'https://example.com/webhook',
            'threads': 10,
            'timeout': 30
        }
        
        # Initialize engine (should not crash)
        engine = ScanEngine(minimal_config, 'test-target')
        await engine._initialize_modules()
        
        # Check that katana_fetcher was initialized
        if hasattr(engine, 'katana_fetcher'):
            print("✅ Katana fetcher initialized in engine")
            print(f"   Enabled: {engine.katana_fetcher.enabled}")
        else:
            print("❌ Katana fetcher NOT found in engine")
        
        # Cleanup
        await engine.fetcher.close()
        
    except Exception as e:
        print(f"❌ Engine integration error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ MANUAL TEST COMPLETE")
    print("=" * 70)
    print("\nNext Steps:")
    if not is_installed:
        print("1. Install Katana: go install github.com/projectdiscovery/katana/cmd/katana@latest")
        print("2. Enable in config.yaml: katana.enabled = true")
    else:
        print("1. Enable in config.yaml: katana.enabled = true")
        print("2. Run a real scan to test Katana discovery")
    print("3. Monitor logs for '⚔️ Katana fast-crawl' messages")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(test_katana_integration())
