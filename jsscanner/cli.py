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
        '--katana',
        action='store_true',
        help='Enable Katana fast crawler (overrides config)'
    )
    
    parser.add_argument(
        '--no-katana',
        action='store_true',
        help='Disable Katana fast crawler (overrides config)'
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
        '--no-beautify',
        action='store_true',
        help='Skip file beautification (faster scans, runs extraction on minified files)'
    )
    
    parser.add_argument(
        '--no-extraction',
        action='store_true',
        help='Skip data extraction (endpoints, params, domains) - only scan for secrets'
    )
    
    parser.add_argument(
        '--no-discord',
        action='store_true',
        help='Disable Discord notifications (quiet mode, results saved locally only)'
    )
    
    parser.add_argument(
        '--discord-verified-only',
        action='store_true',
        help='Send only verified secrets to Discord (reduce noise, unverified saved locally)'
    )
    
    parser.add_argument(
        '--discord-batch-size',
        type=int,
        default=15,
        help='Maximum secrets per batched Discord message (1-25, default: 15)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force rescan all files (ignore incremental scan state/cache)'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint if available (skips completed phases)'
    )
    
    parser.add_argument(
        '--source-maps',
        action='store_true',
        help='Attempt to recover original source code from source maps'
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
    
    if args.katana and args.no_katana:
        parser.error(
            "Error: Cannot use both --katana and --no-katana together.\n"
            "Use one flag to override config.yaml setting."
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
    
    # Discord batch size validation
    if hasattr(args, 'discord_batch_size') and args.discord_batch_size:
        if args.discord_batch_size < 1 or args.discord_batch_size > 25:
            parser.error(
                f"Error: --discord-batch-size must be between 1 and 25.\n"
                f"Discord embed field limit is 25. You provided: {args.discord_batch_size}"
            )
    
    return args


def validate_config(config: dict) -> bool:
    """
    Validates configuration with comprehensive checks
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    errors = []
    warnings = []
    
    # 1. Discord webhook validation
    webhook = config.get('discord_webhook', '')
    if not webhook:
        errors.append("❌ Discord webhook not configured")
        errors.append("   → Set 'discord_webhook' in config.yaml")
        errors.append("   → Get webhook from: Discord Server > Settings > Integrations > Webhooks")
    elif webhook == "YOUR_DISCORD_WEBHOOK_URL_HERE" or not webhook.startswith('https://discord.com/api/webhooks/'):
        errors.append("❌ Invalid Discord webhook URL")
        errors.append("   → Must start with: https://discord.com/api/webhooks/")
        errors.append("   → Example: https://discord.com/api/webhooks/123456789/abcdefg")
    
    # 2. Numeric range validations
    numeric_validations = {
        'threads': (1, 200, "Concurrent threads"),
        'timeout': (5, 300, "HTTP timeout (seconds)"),
        'max_file_size': (1024, 1073741824, "Max file size (1KB - 1GB)"),
        'discord_rate_limit': (1, 60, "Discord messages per minute"),
    }
    
    for field, (min_val, max_val, desc) in numeric_validations.items():
        value = config.get(field)
        if value is not None:
            if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                errors.append(f"❌ Invalid {desc}: {value}")
                errors.append(f"   → Must be between {min_val} and {max_val}")
    
    # 3. TruffleHog path validation (if specified)
    trufflehog_path = config.get('trufflehog_path', '')
    if trufflehog_path:  # Only validate if user specified custom path
        from pathlib import Path
        import shutil
        
        path = Path(trufflehog_path)
        if not path.exists() and not shutil.which(trufflehog_path):
            warnings.append(f"⚠️  TruffleHog not found at: {trufflehog_path}")
            warnings.append("   → Will attempt auto-detection")
    
    # 4. Retry configuration validation
    retry_config = config.get('retry', {})
    if retry_config.get('http_requests', 2) < 1:
        errors.append("❌ retry.http_requests must be >= 1")
    if retry_config.get('backoff_base', 1.0) < 0.1:
        errors.append("❌ retry.backoff_base must be >= 0.1")
    
    # 5. Checkpoint configuration validation
    checkpoint_config = config.get('checkpoint', {})
    if checkpoint_config.get('frequency', 10) < 1:
        errors.append("❌ checkpoint.frequency must be >= 1")
    
    # 6. Notification batching validation
    batch_config = config.get('notification_batching', {})
    batch_size = batch_config.get('batch_size', 10)
    if batch_size < 1 or batch_size > 25:
        errors.append("❌ notification_batching.batch_size must be 1-25")
        errors.append("   → Discord embed limit is 25 fields")
    
    # 7. Playwright configuration
    playwright_config = config.get('playwright', {})
    max_concurrent = playwright_config.get('max_concurrent', 10)
    if max_concurrent < 1 or max_concurrent > 50:
        warnings.append(f"⚠️  playwright.max_concurrent ({max_concurrent}) is unusual")
        warnings.append("   → Recommended: 3-10 for optimal performance")
    
    # Print results
    if errors:
        print("\n" + "="*70)
        print("❌ CONFIGURATION VALIDATION FAILED")
        print("="*70)
        for error in errors:
            print(error)
        print("\n💡 Fix these errors in config.yaml and try again")
        print("="*70 + "\n")
        return False
    
    if warnings:
        print("\n" + "="*70)
        print("⚠️  CONFIGURATION WARNINGS")
        print("="*70)
        for warning in warnings:
            print(warning)
        print("="*70 + "\n")
    
    return True
