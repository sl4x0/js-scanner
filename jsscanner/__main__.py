"""
Main Entry Point
Launches the JS Scanner
"""
import asyncio
import sys
import yaml
from pathlib import Path
from .cli import parse_args, validate_config
from .utils.config_validator import ConfigValidator
from .core.engine import ScanEngine
from .utils.log import log_banner


def show_version_info():
    """Issue #16: Show enhanced version information with dependencies"""
    print("JS Scanner v4.0.0 'Stealth & Dashboard'")
    print("\nDependencies:")
    
    # Python version
    py_version = sys.version.split()[0]
    status = "✅" if sys.version_info >= (3, 11) else "❌"
    print(f"  Python: {py_version} {status} (v4.0 requires 3.11+)")
    
    # Key dependencies
    try:
        import curl_cffi
        print(f"  curl_cffi: {curl_cffi.__version__} ✅ (WAF bypass)")
    except (ImportError, AttributeError):
        print("  curl_cffi: Not installed ❌")
    
    try:
        import rich
        print(f"  rich: {rich.__version__} ✅ (Live dashboard)")
    except (ImportError, AttributeError):
        print("  rich: Not installed ❌")
    
    try:
        from playwright import __version__ as pw_version
        print(f"  playwright: {pw_version}")
    except (ImportError, AttributeError):
        try:
            import playwright
            print("  playwright: installed (version unknown)")
        except ImportError:
            print("  playwright: Not installed")
    
    try:
        import tree_sitter
        try:
            # Try getting version from metadata (newer approach)
            from importlib.metadata import version
            ts_version = version('tree-sitter')
            print(f"  tree-sitter: {ts_version}")
        except:
            print("  tree-sitter: installed (version unknown)")
    except ImportError:
        print("  tree-sitter: Not installed")
    
    try:
        import jsbeautifier
        print(f"  jsbeautifier: {jsbeautifier.__version__}")
    except (ImportError, AttributeError):
        print("  jsbeautifier: Not installed")
    
    try:
        import yaml as yaml_mod
        print(f"  PyYAML: {yaml_mod.__version__ if hasattr(yaml_mod, '__version__') else 'installed'}")
    except ImportError:
        print("  PyYAML: Not installed")


async def main():
    """Main execution function"""
    # Display banner
    log_banner()
    
    # Parse arguments
    args = parse_args()
    
    # Issue #16: Handle --version flag with enhanced output
    if args.version:
        show_version_info()
        sys.exit(0)
    
    # Load configuration
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
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
    
    if args.no_beautify:
        config['skip_beautification'] = True
    
    if args.no_extraction:
        config['skip_extraction'] = True
    
    if args.force:
        config['force_rescan'] = True
    
    if args.source_maps:
        config['recover_source_maps'] = True
    
    # Add verbose flag to config
    if hasattr(args, 'verbose') and args.verbose:
        config['verbose'] = True
    
    # Validate config
    # Run structured config validation (additional to CLI-level checks)
    is_valid_cfg, cfg_errors = ConfigValidator.validate_all(config)
    if not is_valid_cfg:
        print(ConfigValidator.format_errors(cfg_errors))
        sys.exit(1)

    if not validate_config(config):
        sys.exit(1)
    
    # Apply CLI overrides for SubJS
    if args.subjs or args.subjs_only:
        config.setdefault('subjs', {})['enabled'] = True
    
    if args.subjs_only:
        config['skip_live'] = True
        config.setdefault('katana', {})['enabled'] = False  # Disable Katana in SubJS-only mode
    
    # Apply CLI overrides for Katana
    if args.katana:
        config.setdefault('katana', {})['enabled'] = True
    
    if args.no_katana:
        config.setdefault('katana', {})['enabled'] = False
    
    if args.no_scope_filter:
        config['no_scope_filter'] = True
    
    if args.no_live:
        config['skip_live'] = True
    
    # Parse multiple targets (comma-separated)
    targets = [t.strip() for t in args.target.split(',') if t.strip()]
    
    if len(targets) > 1:
        print(f"\n🎯 Targets detected: {len(targets)}")
        print("="*60)
    
    # === NEW: Determine Input List ===
    targets_to_scan = []
    
    # SubJS: Respect config file setting unless explicitly overridden by CLI
    if args.subjs or args.subjs_only:
        # Explicit CLI flag - enable SubJS
        use_subjs = True
        subjs_only = args.subjs_only
    elif args.no_live:
        # --no-live implies SubJS only mode
        use_subjs = True
        subjs_only = True
    else:
        # No explicit CLI flag - use config file setting (defaults to true)
        use_subjs = config.get('subjs', {}).get('enabled', True)
        subjs_only = False
    
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
        targets_to_scan = targets
    
    # Log the scan configuration
    primary_scope = targets[0] if targets else args.target
    print(f"\n🎯 Project Scope: {args.target}")
    print(f"📂 Input Items: {len(targets_to_scan)}")
    
    if subjs_only:
        print(f"🔍 Discovery Mode: SubJS Only (no browser)")
    elif use_subjs:
        print(f"🔍 Discovery Mode: Hybrid (SubJS + Live Browser)")
    else:
        print(f"🔍 Discovery Mode: Live Browser Only")
    
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
            
            # Run scan with new parameters (including resume)
            await engine.run(targets_to_scan, use_subjs=use_subjs, subjs_only=subjs_only, resume=args.resume)
            
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
    # PHASE 0: Check Python version for TaskGroup support (requires 3.11+)
    if sys.version_info < (3, 11):
        print("❌ Error: JS-Scanner v4.0 requires Python 3.11+ (needed for asyncio.TaskGroup)")
        print(f"   Current version: {sys.version.split()[0]}")
        print("\n   Upgrade with: pip install --upgrade python (or use pyenv/conda)")
        sys.exit(1)
    
    # PHASE 1: Enable high-performance uvloop (Linux/macOS only)
    if sys.platform != 'win32':
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("🚀 High-Performance uvloop enabled")
        except ImportError:
            pass  # Silently fall back to standard asyncio
    
    # Suppress "Future exception was never retrieved" warnings during shutdown
    # This prevents Playwright TargetClosedError spam when pressing Ctrl+C
    import warnings
    import logging
    
    # Suppress asyncio warnings about uncollected futures
    warnings.filterwarnings('ignore', message='.*Future exception was never retrieved.*')
    
    # Suppress Playwright TargetClosedError in asyncio logger
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.CRITICAL)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except BrokenPipeError:
        # Gracefully handle broken pipe (e.g., when output is piped to `head` or `tail`)
        # This prevents crash when the reading end of a pipe closes
        import os
        # Close stdout and stderr to prevent further write attempts
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)


if __name__ == '__main__':
    run()
