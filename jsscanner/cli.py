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
  # Scan a single target (auto-discover from Wayback + Live)
  python -m jsscanner -t example.com
  
  # Scan with custom config
  python -m jsscanner -t example.com --config custom-config.yaml
  
  # Scan from input file
  python -m jsscanner -t example.com -i urls.txt
  
  # Scan specific URLs
  python -m jsscanner -t example.com -u https://example.com/app.js https://example.com/main.js
        """
    )
    
    # Required arguments
    parser.add_argument(
        '-t', '--target',
        required=True,
        help='Target domain (e.g., example.com)'
    )
    
    # Optional arguments
    parser.add_argument(
        '-i', '--input',
        help='Input file with URLs (one per line)'
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
        '--threads',
        type=int,
        help='Number of concurrent threads (overrides config)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='JS Scanner v1.0.0'
    )
    
    args = parser.parse_args()
    
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
