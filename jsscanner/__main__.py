"""
Main Entry Point
Launches the JS Scanner
"""
import asyncio
import sys
import yaml
from pathlib import Path
from .cli import parse_args, validate_config
from .core.engine import ScanEngine
from .utils.logger import log_banner


async def main():
    """Main execution function"""
    # Display banner
    log_banner()
    
    # Parse arguments
    args = parse_args()
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in config file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        raise
    
    # Apply CLI overrides
    if args.threads:
        config['threads'] = args.threads
    
    if args.no_recursion:
        config.setdefault('recursion', {})['enabled'] = False
    
    # Validate config
    if not validate_config(config):
        sys.exit(1)
    
    # Apply CLI overrides
    if args.no_wayback:
        config['skip_wayback'] = True
    if args.no_live:
        config['skip_live'] = True
    
    # Parse multiple targets (comma-separated)
    targets = [t.strip() for t in args.target.split(',') if t.strip()]
    
    if len(targets) > 1:
        print(f"\n🎯 Targets detected: {len(targets)}")
        print("="*60)
    
    # === NEW: Determine Input List and Discovery Mode ===
    targets_to_scan = []
    discovery_mode = args.discovery  # Start with user's explicit flag
    
    if args.input:
        # Read from input file
        with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
            targets_to_scan = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Validate that we got valid targets from the file
        if not targets_to_scan:
            print(f"Error: Input file '{args.input}' contains no valid targets.")
            print("Make sure the file contains at least one URL or domain (non-comment, non-empty line).")
            sys.exit(1)
    elif args.urls:
        # Use provided URLs
        targets_to_scan = args.urls
    else:
        # If no input file or URLs provided, the target(s) ARE the input
        # Force discovery mode ON in this case
        targets_to_scan = targets
        discovery_mode = True
    
    # Log the scan configuration
    primary_scope = targets[0] if targets else args.target
    print(f"\n🎯 Project Scope: {args.target}")
    print(f"📂 Input Items: {len(targets_to_scan)}")
    print(f"🔍 Discovery Mode: {'ON (Wayback + Live)' if discovery_mode else 'OFF (Direct scan only)'}")
    print("="*60)
    
    # Run scan for each target sequentially
    try:
        for idx, target in enumerate(targets, 1):
            if len(targets) > 1:
                print(f"\n{'='*60}")
                print(f"🚀 STARTING SCAN {idx}/{len(targets)}: {target}")
                print("="*60)
            
            # Initialize engine for this target
            engine = ScanEngine(config, target)
            
            # Run scan with new parameters
            await engine.run(targets_to_scan, discovery_mode=discovery_mode)
            
            if len(targets) > 1 and idx < len(targets):
                print(f"\n✓ Completed scan {idx}/{len(targets)} for {target}")
                print(f"\n{'='*60}")
                print(f"Preparing next target...")
                await asyncio.sleep(1)  # Brief pause between scans
        
        if len(targets) > 1:
            print(f"\n{'='*60}")
            print(f"✅ ALL SCANS COMPLETED ({len(targets)} targets)")
            print("="*60)
            
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)


def run():
    """Entry point wrapper"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)


if __name__ == '__main__':
    run()
