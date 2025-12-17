#!/usr/bin/env python3
"""Test bundle unpacking functionality"""
import asyncio
from pathlib import Path

async def test_bundle_detection():
    """Test bundle signature detection"""
    
    from jsscanner.modules.bundle_unpacker import BundleUnpacker
    from jsscanner.utils.logger import setup_logger
    
    logger = setup_logger('test')
    unpacker = BundleUnpacker(logger, 'test_output/unpacked')
    
    print("Testing bundle detection...")
    print(f"{'='*70}")
    
    # Test webpack bundle
    webpack_content = '''
    (function(modules) { // webpackBootstrap
        var installedModules = {};
        function __webpack_require__(moduleId) {
            // webpack module loading
        }
    })({
        "./src/app.js": function(module, exports) {
            console.log("Hello from app");
        }
    });
    '''
    # Pad to make it large enough (>100KB)
    webpack_content = webpack_content + ('// padding comment\n' * 10000)
    
    print(f"Webpack content size: {len(webpack_content)} bytes")
    should_unpack = await unpacker.should_unpack(webpack_content, len(webpack_content))
    print(f"✅ Webpack bundle detection: {should_unpack}")
    assert should_unpack, "Should detect webpack bundle"
    
    # Test Vite bundle
    vite_content = '''
    var __vite__ = {};
    (function() {
        const modules = {
            "./src/main.js": function() {
                console.log("Vite app");
            }
        };
    })();
    '''
    # Pad to make it large enough
    vite_content = vite_content + ('// padding comment\n' * 10000)
    
    should_unpack = await unpacker.should_unpack(vite_content, len(vite_content))
    print(f"✅ Vite bundle detection: {should_unpack}")
    assert should_unpack, "Should detect vite bundle"
    
    # Test regular file (should NOT unpack)
    regular_content = 'const x = 1; console.log(x);'
    should_unpack = await unpacker.should_unpack(regular_content, len(regular_content))
    print(f"✅ Regular file detection: {should_unpack} (correctly rejected)")
    assert not should_unpack, "Should not flag regular file"
    
    # Test small file with webpack signature (should NOT unpack - too small)
    small_webpack = 'webpack' * 10  # Only 70 bytes
    should_unpack = await unpacker.should_unpack(small_webpack, len(small_webpack))
    print(f"✅ Small file rejection: {should_unpack} (correctly rejected)")
    assert not should_unpack, "Should not unpack small files"
    
    print(f"{'='*70}")
    print("✅ All bundle detection tests passed")
    return True

if __name__ == '__main__':
    success = asyncio.run(test_bundle_detection())
    exit(0 if success else 1)
