"""
State Migration Script
Migrate existing JSON state to Bloom filter format
"""
import json
import sys
from pathlib import Path


def migrate_state_to_bloom(state_path: Path):
    """
    Migrate JSON state to Bloom filter format
    
    Args:
        state_path: Path to .warehouse/db directory
    """
    try:
        from pybloom_live import ScalableBloomFilter
    except ImportError:
        print("❌ pybloom-live not installed. Install with: pip install pybloom-live")
        sys.exit(1)
    
    history_file = state_path / 'history.json'
    bloom_file = state_path / 'state.bloom'
    
    if not history_file.exists():
        print(f"❌ History file not found: {history_file}")
        sys.exit(1)
    
    if bloom_file.exists():
        response = input(f"⚠️  Bloom filter already exists at {bloom_file}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            sys.exit(0)
    
    # Load existing history
    print(f"📖 Loading history from {history_file}...")
    with open(history_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    scanned_hashes = data.get('scanned_hashes', [])
    print(f"✓ Found {len(scanned_hashes)} scanned hashes")
    
    # Create Bloom filter
    print("🔧 Creating Bloom filter...")
    bloom = ScalableBloomFilter(
        initial_capacity=max(len(scanned_hashes), 100000),
        error_rate=0.001
    )
    
    # Add all hashes
    for hash_value in scanned_hashes:
        bloom.add(hash_value)
    
    # Save Bloom filter
    print(f"💾 Saving Bloom filter to {bloom_file}...")
    bloom_file.parent.mkdir(parents=True, exist_ok=True)
    with open(bloom_file, 'wb') as f:
        bloom.tofile(f)
    
    print(f"\n✅ Migration complete!")
    print(f"   - Migrated {len(scanned_hashes)} hashes")
    print(f"   - Bloom filter size: {bloom_file.stat().st_size / 1024:.2f} KB")
    print(f"   - Original JSON size: {history_file.stat().st_size / 1024:.2f} KB")
    print(f"   - Compression ratio: {(1 - bloom_file.stat().st_size / history_file.stat().st_size) * 100:.1f}%")


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python migrate_state.py <path-to-.warehouse/db>")
        print("\nExample:")
        print("  python scripts/migrate_state.py results/example.com/.warehouse/db")
        sys.exit(1)
    
    state_path = Path(sys.argv[1])
    if not state_path.exists():
        print(f"❌ Path does not exist: {state_path}")
        sys.exit(1)
    
    migrate_state_to_bloom(state_path)


if __name__ == '__main__':
    main()
