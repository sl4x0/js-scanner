"""
Command Line Interface
Handles argument parsing for jsscanner
"""
import argparse
import sys
from pathlib import Path


def parse_args():
    """
    Parses command-line arguments
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='JS Scanner - Context-Aware JavaScript Secret Hunter for Bug Bounty',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan with SubJS discovery
  python -m jsscanner -t example.com --subjs
  
  # Fast scan: SubJS only (no browser)
  python -m jsscanner -t example.com --subjs-only
  
  # Scan from file with SubJS
  python -m jsscanner -t example.com -i subdomains.txt --subjs
  
  # Direct scan of specific JavaScript URLs
  python -m jsscanner -t example.com -u https://example.com/app.js
  
  # Include all JS files (no scope filtering)
  python -m jsscanner -t example.com --subjs --no-scope-filter

Discovery Methods:
  Default (no flags):
    - Live browser crawling only
    - Best for: Single-page apps, exact URLs
  
  --subjs:
    - Uses SubJS for additional URL discovery
    - Combines with live browser scanning
    - Fast and comprehensive
  
  --subjs-only:
    - Uses only SubJS (no browser)
    - Fastest mode
    - Best for: Quick scans, many domains
  
  --no-scope-filter:
    - Include CDN and third-party JS files
    - Use with --subjs for complete coverage

Performance Tips:
  - Use --subjs-only for fastest scans
  - Use --subjs for best coverage
  - Use --threads to control concurrency (default: 50)
        """
    )
    
    # Required arguments
    parser.add_argument(
        '-t', '--target',
        required=True,
        help='Project scope/name (e.g., example.com or "program-name") - used for filtering and output organization'
    )
    
    # Optional arguments
    parser.add_argument(
        '-i', '--input',
        help='Input file containing domains, URLs, or JS files (one per line)'
    )
    
    parser.add_argument(
        '-u', '--urls',
        nargs='+',
        help='Specific URLs to scan'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--subjs',
        action='store_true',
        help='Use SubJS for additional URL discovery (requires SubJS installed)'
    )
    
    parser.add_argument(
        '--subjs-only',
        action='store_true',
        help='Use only SubJS discovery (skip live browser scan, faster)'
    )
    
    parser.add_argument(
        '--no-scope-filter',
        action='store_true',
        help='Disable scope filtering (include CDN and third-party JS files)'
    )
    
    parser.add_argument(
        '--no-live',
        action='store_true',
        help='Skip live site scanning'
    )
    
    parser.add_argument(
        '--no-recursion',
        action='store_true',
        help='Disable recursive crawling'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        help='Number of concurrent threads (overrides config)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Issue #16: Enhanced --version with dependency versions
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information including dependencies'
    )
    
    # Parse args, but check for --version first
    if '--version' in sys.argv:
        # Return early with version flag set, skip validation
        args = argparse.Namespace(version=True)
        return args
    
    args = parser.parse_args()
    
    # Validate conflicting flags
    if args.subjs_only and args.subjs:
        parser.error(
            "Error: Cannot use both --subjs and --subjs-only together.\n"
            "Use --subjs-only for SubJS only, or --subjs to combine with live scanning."
        )
    
    if args.no_live and not args.subjs and not args.subjs_only:
        parser.error(
            "Error: --no-live requires either --subjs or --subjs-only.\n"
            "Cannot disable all scanning methods."
        )
    
    # Check if user accidentally used file path with -t flag
    if args.target and (args.target.startswith('/') or args.target.startswith('./') or args.target.startswith('~')):
        parser.error(
            f"Error: -t flag expects a DOMAIN, not a file path.\n"
            f"You provided: {args.target}\n\n"
            f"Did you mean to use -i flag instead?\n"
            f"Example: python -m jsscanner -t example.com -i {args.target}"
        )
    
    # Validation
    if args.input and not Path(args.input).exists():
        parser.error(f"Input file not found: {args.input}")
    
    if not Path(args.config).exists():
        parser.error(f"Config file not found: {args.config}")
    
    return args


def validate_config(config: dict) -> bool:
    """
    Validates configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['discord_webhook']
    
    for field in required_fields:
        if field not in config or not config[field]:
            print(f"Error: '{field}' not configured in config.yaml")
            return False
    
    # Check if webhook looks valid
    webhook = config['discord_webhook']
    if webhook == "YOUR_WEBHOOK_URL" or not webhook.startswith('https://discord'):
        print("Error: Please configure a valid Discord webhook URL in config.yaml")
        return False
    
    return True
