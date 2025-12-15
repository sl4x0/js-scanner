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
    
    # Initialize engine
    engine = ScanEngine(config, args.target)
    
    # Prepare scan parameters
    input_file = args.input
    urls = args.urls
    
    # Run scan
    try:
        await engine.run(input_file=input_file, urls=urls)
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
