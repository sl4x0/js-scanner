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
  # Full discovery for a single domain (Wayback + Live)
  python -m jsscanner -t example.com --discovery
  
  # Fast scan: httpx subdomains (live pages only, no Wayback)
  python -m jsscanner -t example.com -i subdomains.txt
  
  # Deep scan: httpx subdomains with full discovery
  python -m jsscanner -t example.com -i subdomains.txt --discovery
  
  # Scan multiple domains with discovery
  python -m jsscanner -t "program-name" -i domains.txt --discovery
  
  # Direct scan of specific JavaScript URLs (no discovery)
  python -m jsscanner -t example.com -i js-files.txt
  python -m jsscanner -t example.com -u https://example.com/app.js https://example.com/main.js

Discovery Mode:
  --discovery flag controls whether to actively discover JS files:
  
  OFF (default with -i/-u):
    - Scans only the URLs/domains provided in input
    - Live page crawling only (fast)
    - No Wayback Machine queries
    - Best for: httpx output, known URL lists
  
  ON (with --discovery flag):
    - Queries Wayback Machine for historical files
    - Crawls live site with Playwright
    - Comprehensive discovery
    - Best for: initial recon, full coverage
  
  AUTO-ON (no -i or -u):
    - Discovery automatically enabled when scanning a bare domain
    - Example: python -m jsscanner -t example.com

Performance Tips:
  - Use -i without --discovery for fast httpx subdomain scans
  - Use --discovery for comprehensive initial reconnaissance
  - Use --no-wayback to skip Wayback (keeps live crawling)
  - Use --threads to control concurrency (default: 10)
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
        help='Input file containing domains, URLs, or JS files (one per line). Without --discovery, only live pages are scanned'
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
        '--no-wayback',
        action='store_true',
        help='Skip Wayback Machine scanning'
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
        '--discovery',
        action='store_true',
        help='Enable full discovery mode (Wayback Machine + Live crawling). Default: OFF when using -i or -u, AUTO-ON for bare domains'
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
    if args.no_wayback and args.no_live:
        parser.error(
            "Error: Cannot use both --no-wayback and --no-live together.\n"
            "This would disable all scanning methods. Please use only one or neither."
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
