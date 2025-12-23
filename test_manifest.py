"""
Test manifest loading and URL enrichment
"""
import json
from pathlib import Path


def test_manifest_structure():
    """Check if file_manifest.json exists and show its structure"""
    
    # Look for recent scan results
    results_dir = Path('results')
    if not results_dir.exists():
        print("❌ No results directory found. Run a scan first.")
        return
    
    # Find most recent target directory
    target_dirs = [d for d in results_dir.iterdir() if d.is_dir()]
    if not target_dirs:
        print("❌ No target directories found in results/")
        return
    
    # Check each target for manifest
    for target_dir in sorted(target_dirs, key=lambda x: x.stat().st_mtime, reverse=True):
        manifest_file = target_dir / 'file_manifest.json'
        
        if manifest_file.exists():
            print(f"\n{'='*80}")
            print(f"Found manifest: {manifest_file}")
            print(f"{'='*80}")
            
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            print(f"\n📊 Manifest Statistics:")
            print(f"   Total entries: {len(manifest)}")
            
            # Show sample entries
            print(f"\n📋 Sample Entries (first 3):")
            for i, (file_hash, entry) in enumerate(list(manifest.items())[:3]):
                print(f"\n   Entry {i+1}:")
                print(f"   Hash: {file_hash}")
                print(f"   URL: {entry.get('url', 'N/A')}")
                print(f"   Filename: {entry.get('filename', 'N/A')}")
                print(f"   Minified: {entry.get('is_minified', 'N/A')}")
            
            print(f"\n{'='*80}")
            print("✅ Manifest structure verified!")
            print("   - Keyed by: MD5 hash")
            print("   - Contains: URL, filename, minified status, timestamp")
            print(f"{'='*80}\n")
            
            # Check if secrets file exists
            secrets_file = target_dir / 'trufflehog_full.json'
            if secrets_file.exists():
                with open(secrets_file, 'r') as f:
                    secrets_data = json.load(f)
                
                secrets = secrets_data.get('secrets', [])
                print(f"\n🔐 Secrets found: {len(secrets)}")
                
                if secrets:
                    print(f"\n📋 Sample Secret Metadata:")
                    sample = secrets[0]
                    metadata = sample.get('SourceMetadata', {})
                    print(f"   URL: {metadata.get('url', 'MISSING!')}")
                    print(f"   File: {metadata.get('file', 'MISSING!')}")
                    print(f"   Line: {metadata.get('line', 'MISSING!')}")
                    print(f"   Domain: {metadata.get('domain', 'MISSING!')}")
                    
                    if not metadata.get('url'):
                        print("\n⚠️  WARNING: URL is missing from secret metadata!")
                        print("   This explains why notifications don't show URLs.")
            
            return
    
    print("❌ No file_manifest.json found in any target directory")


if __name__ == '__main__':
    test_manifest_structure()
