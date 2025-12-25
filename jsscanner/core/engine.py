"""
Engine
Main orchestrator that routes input to appropriate modules
"""
import asyncio
import json
import time
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from ..utils.fs import FileSystem
from ..utils.log import setup_logger, log_stats
from .state import State
from ..output.discord import Discord
from ..output.reporter import generate_report


class ScanEngine:
    """Main scanning engine that orchestrates all modules"""
    
    def __init__(self, config: dict, target: str) -> None:
        """
        Initialize the scan engine
        
        Args:
            config: Configuration dictionary
            target: Target domain or URL
        """
        self.config = config
        self.target = target
        self.target_name = self._sanitize_target_name(target)
        
        # Setup directories
        self.paths = FileSystem.create_result_structure(self.target_name)
        
        # Initialize logger
        log_file = Path(self.paths['logs']) / 'scan.log'
        self.logger = setup_logger(log_file=str(log_file))
        
        # Initialize state manager
        self.state = State(self.paths['base'])
        
        # Initialize Discord notifier
        webhook_url = config.get('discord_webhook')
        rate_limit = config.get('discord_rate_limit', 30)
        max_queue_size = config.get('discord_max_queue', 1000)
        self.notifier = Discord(webhook_url, rate_limit, max_queue_size, self.logger)
        
        # Modules will be initialized when needed
        self.fetcher = None
        self.processor = None
        self.secret_scanner = None
        self.ast_analyzer = None
        self.semgrep_analyzer = None
        
        # Shutdown flag for graceful exit
        self.shutdown_requested = False
        
        # Track allowed domains from input file
        self.allowed_domains = set()
        
        # Progress tracking for _log_progress
        self.current_phase = None
        self.phase_start_time = None
        self.phase_progress = {'current': 0, 'total': 0}
        
        # Statistics
        self.start_time = None
        self._last_progress_update = 0
        self.stats = {
            'total_files': 0,
            'total_secrets': 0,
            'semgrep_findings': 0,
            'errors': [],
            'failures': {
                'fetch_failed': 0,
                'empty_content': 0,
                'html_not_js': 0,
                'too_short': 0,
                'too_large': 0,
                'timeout': 0,
                'http_error': 0,
                'duplicates': 0,
                'invalid_url': 0
            },
            'network_errors': {
                'dns_errors': 0,
                'connection_refused': 0,
                'ssl_errors': 0,
                'timeouts': 0,
                'rate_limits': 0,
                'http_errors': 0
            }
        }
    
    def _log_progress(self, phase_name: str, current: int, total: int, extra_info: str = ""):
        """
        Log progress with ETA calculation and dashboard update
        
        Args:
            phase_name: Name of current phase
            current: Current progress count
            total: Total items to process
            extra_info: Additional information to display
        """
        if total == 0:
            return
        
        # Update phase if changed
        if phase_name != self.current_phase:
            self.current_phase = phase_name
            self.phase_start_time = time.time()
            self.phase_progress = {'current': 0, 'total': total}
        
        # Update progress
        self.phase_progress = {'current': current, 'total': total}
        
        # Calculate progress percentage
        progress_pct = (current / total) * 100
        
        # Calculate ETA (only after processing a few items)
        eta_str = ""
        if current > 0 and self.phase_start_time:
            elapsed = time.time() - self.phase_start_time
            if elapsed > 0:
                rate = current / elapsed
                if rate > 0:
                    remaining = total - current
                    eta_seconds = remaining / rate
                    
                    # Format ETA nicely
                    if eta_seconds < 60:
                        eta_str = f", ETA: {int(eta_seconds)}s"
                    elif eta_seconds < 3600:
                        minutes = int(eta_seconds / 60)
                        seconds = int(eta_seconds % 60)
                        eta_str = f", ETA: {minutes}m {seconds}s"
                    else:
                        hours = int(eta_seconds / 3600)
                        minutes = int((eta_seconds % 3600) / 60)
                        eta_str = f", ETA: {hours}h {minutes}m"
                    
                    # Add throughput
                    if rate >= 1:
                        eta_str += f" ({rate:.1f} items/s)"
                    else:
                        eta_str += f" ({1/rate:.1f}s/item)"
        
        # Build progress bar
        bar_width = 30
        filled = int(bar_width * current / total)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # Log only every 5% or on completion to avoid spam
        progress_key = int(progress_pct / 5) * 5
        current_time = time.time()
        
        # Throttle updates to once per 2 seconds, except for milestones
        should_log = (
            current == total or  # Always log completion
            current == 1 or  # Always log first item
            progress_key % 10 == 0 or  # Log every 10%
            (current_time - self._last_progress_update) >= 2  # Or every 2 seconds
        )
        
        if should_log:
            extra = f" - {extra_info}" if extra_info else ""
            self.logger.info(f"📊 {phase_name}: [{bar}] {current}/{total} ({progress_pct:.1f}%){eta_str}{extra}")
            self._last_progress_update = current_time
    
    async def run(self, inputs: List[str], use_subjs: bool = False, subjs_only: bool = False, resume: bool = False):
        """
        Main execution method with BATCH PROCESSING and checkpoint support
        
        Args:
            inputs: List of URLs or domains to scan
            use_subjs: If True, use SubJS for additional URL discovery
            subjs_only: If True, only use SubJS (skip live browser scan)
            resume: If True, resume from last checkpoint if available
        """
        self.start_time = time.time()
        
        # Check for resumable checkpoint
        checkpoint_enabled = self.config.get('checkpoint', {}).get('enabled', True)
        resume_state = None
        
        if resume and checkpoint_enabled and self.state.has_checkpoint():
            # Check if config has changed
            config_changed = self.state.check_config_changed(self.config)
            if config_changed:
                self.logger.warning("\n⚠️  WARNING: Configuration has changed since last scan!")
                self.logger.warning("   Resuming with modified config may produce inconsistent results.")
                self.logger.warning("   Consider starting a fresh scan instead.")
                self.logger.warning("   Continuing anyway in 3 seconds... (Ctrl+C to cancel)\n")
                
                import asyncio
                await asyncio.sleep(3)
            
            resume_state = self.state.get_resume_state()
            self.logger.info(f"\n{'='*60}")
            self.logger.info("📂 RESUMING FROM CHECKPOINT")
            self.logger.info(f"{'='*60}")
            self.logger.info(f"Last checkpoint: {resume_state.get('timestamp', 'unknown')}")
            self.logger.info(f"Phase: {resume_state.get('phase', 'unknown')}")
            self.logger.info(f"Progress: Phase {resume_state['phase_progress']['current_phase']}/{resume_state['phase_progress']['total_phases']}")
            if config_changed:
                self.logger.warning("⚠️  Config modified - results may be inconsistent")
            self.logger.info(f"{'='*60}\n")
        elif resume and checkpoint_enabled:
            self.logger.warning("⚠️  --resume specified but no checkpoint found, starting fresh scan")
            resume = False
        
        # Update metadata with start time
        self.state.update_metadata({
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'use_subjs': use_subjs,
            'subjs_only': subjs_only,
            'resumed': resume
        })
        
        # Setup signal handlers for graceful shutdown with timeout
        def signal_handler(signum, frame):
            if not self.shutdown_requested:
                self.shutdown_requested = True
                self.logger.warning("\n⚠️  Shutdown requested (Ctrl+C). Saving data and exiting...")
                
                # Start cleanup with timeout in background
                import threading
                cleanup_thread = threading.Thread(target=self._emergency_shutdown, daemon=True)
                cleanup_thread.start()
                cleanup_thread.join(timeout=30)  # 30-second timeout for VPS (was 5s)
                
                # Force exit if cleanup takes too long
                if cleanup_thread.is_alive():
                    self.logger.error("⏱️  Cleanup timeout (30s) - forcing exit")
                    import os
                    os._exit(1)
                else:
                    self.logger.info("✅ Graceful shutdown complete")
                    import sys
                    sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Start Discord notifier
            await self.notifier.start()
            
            # Only send status if enabled in config
            if self.config.get('discord_status_enabled', False):
                await self.notifier.send_status(
                    f"🚀 Starting scan for **{self.target}**",
                    status_type='info'
                )
            
            self.logger.info(f"Starting scan for target: {self.target}")
            
            # Initialize modules
            await self._initialize_modules()
            
            # Check dependencies
            await self._check_dependencies()
            
            # ============================================================
            # PHASE 1: DISCOVERY & URL COLLECTION (CONCURRENT)
            # ============================================================
            self.logger.info(f"\n{'═'*70}")
            self.logger.info("📡 PHASE 1: DISCOVERY & URL COLLECTION (CONCURRENT)")
            self.logger.info(f"{'═'*70}")
            
            # Extract domains for scope filtering
            from urllib.parse import urlparse
            for item in inputs:
                try:
                    parsed = urlparse(item if item.startswith('http') else f'https://{item}')
                    domain = parsed.netloc
                    if domain:
                        # Keep port for localhost, remove www
                        clean_domain = domain.lower().replace('www.', '')
                        self.allowed_domains.add(clean_domain)
                except:
                    pass
            
            # Resume logic: Skip discovery if already completed
            if resume_state and resume_state.get('discovery', {}).get('completed'):
                urls_to_scan = resume_state['discovery']['urls_discovered']
                self.logger.info(f"➩ Skipping Phase 1 (already completed) - loaded {len(urls_to_scan)} URLs from checkpoint")
            else:
                # Process domains concurrently
                urls_to_scan = await self._discover_all_domains_concurrent(inputs, use_subjs, subjs_only)
                
                # Save checkpoint after Phase 1
                if checkpoint_enabled:
                    self.state.save_checkpoint('PHASE_1_COMPLETE', {
                        'discovery': {
                            'completed': True,
                            'urls_discovered': urls_to_scan,
                            'total_urls': len(urls_to_scan)
                        }
                    })
            
            if not urls_to_scan:
                self.logger.warning("No JavaScript files found to scan")
                return
            
            # ============================================================
            # PHASE 2: DOWNLOADING ALL FILES (Parallel)
            # ============================================================
            self.logger.info(f"\n{'═'*70}")
            self.logger.info("⬇️  PHASE 2: DOWNLOADING ALL FILES")
            self.logger.info(f"{'═'*70}")
            
            # Resume logic: Skip download if already completed
            if resume_state and resume_state.get('download', {}).get('completed'):
                downloaded_files = resume_state['download'].get('downloaded_files', [])
                self.logger.info(f"➩ Skipping Phase 2 (already completed) - loaded {len(downloaded_files)} files from checkpoint")
            else:
                downloaded_files = await self._download_all_files(urls_to_scan)
                
                # Save checkpoint after Phase 2
                if checkpoint_enabled:
                    self.state.save_checkpoint('PHASE_2_COMPLETE', {
                        'download': {
                            'completed': True,
                            'downloaded_files': [str(f) for f in downloaded_files],
                            'total_downloaded': len(downloaded_files)
                        }
                    })
            
            self.logger.info(f"✅ Downloaded {len(downloaded_files)} files\n")
            
            if not downloaded_files:
                self.logger.warning("No files were successfully downloaded")
                return
            
            # ============================================================
            # PHASE 2.1: RECURSIVE JS DISCOVERY (Optional, NEW)
            # ============================================================
            recursion_config = self.config.get('recursion', {})
            if recursion_config.get('enabled', True) and recursion_config.get('max_depth', 2) > 0:
                self.logger.info(f"\n{'═'*70}")
                self.logger.info("🔍 PHASE 2.1: RECURSIVE JS DISCOVERY")
                self.logger.info(f"{'═'*70}")
                
                additional_files = await self._discover_js_recursively(
                    downloaded_files, 
                    recursion_config.get('max_depth', 2),
                    recursion_config.get('validate_with_head', True)
                )
                
                if additional_files:
                    self.logger.info(f"✅ Found {len(additional_files)} additional JS files via recursive discovery")
                    self.logger.info("📦 Adding to processing pipeline (already downloaded)...")
                    
                    # Files are already downloaded - add directly to pipeline
                    downloaded_files.extend(additional_files)
                    
                    self.logger.info(f"✅ Total files after recursive discovery: {len(downloaded_files)}\n")
                else:
                    self.logger.info("ℹ️  No additional JS files found via recursive discovery\n")
            
            # ============================================================
            # PHASE 2.5: SOURCE MAP RECOVERY (Optional)
            # ============================================================
            if self.shutdown_requested:
                self.logger.warning("⚠️  Shutdown requested before source map recovery")
                await self._save_current_progress()
                return
            
            if self.config.get('recover_source_maps', False):
                self.logger.info(f"\n{'═'*70}")
                self.logger.info("🗺️  PHASE 2.5: RECOVERING SOURCE MAPS")
                self.logger.info(f"{'═'*70}")
                
                await self._recover_source_maps(downloaded_files)
                
                # Report stats
                recovery_stats = self.source_map_recoverer.get_stats()
                if recovery_stats['maps_found'] > 0:
                    self.logger.info(f"✅ Source Map Recovery:")
                    self.logger.info(f"  • Maps found: {recovery_stats['maps_found']}")
                    self.logger.info(f"  • Maps downloaded: {recovery_stats['maps_downloaded']}")
                    self.logger.info(f"  • Sources recovered: {recovery_stats['sources_recovered']}")
                    self.logger.info(f"  • Recovery rate: {recovery_stats['recovery_rate']}")
                else:
                    self.logger.info("ℹ️  No source maps found")
                self.logger.info("")
            
            # ============================================================
            # PHASE 3: SCANNING FOR SECRETS (TruffleHog)
            # ============================================================
            if self.shutdown_requested:
                self.logger.warning("⚠️  Shutdown requested before secret scanning")
                await self._save_current_progress()
                return
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info("🔍 PHASE 3: SCANNING FOR SECRETS (TruffleHog)")
            self.logger.info(f"{'='*60}")
            
            # NEW: Scan unique_js directory (MD5-based content deduplication)
            unique_js_dir = str(Path(self.paths['unique_js']))
            
            # Scan unique JS files
            verified_secrets = await self.secret_scanner.scan_directory(unique_js_dir)
            total_findings = self.secret_scanner.secrets_count  # Total findings counter (v4.1 fix)
            self.stats['total_secrets'] = total_findings
            self.stats['verified_secrets'] = len(verified_secrets)
            
            # Save organized secrets (domain-specific + full results)
            await self.secret_scanner.save_organized_secrets()
            
            # Get secrets summary for reporting
            secrets_summary = self.secret_scanner.get_secrets_summary()
            self.stats['secrets_summary'] = secrets_summary
            
            # Export TruffleHog results to JSON (legacy - for backward compatibility)
            trufflehog_output = Path(self.paths['base']) / 'trufflehog_full.json'
            self.secret_scanner.export_results(str(trufflehog_output))
            
            # Save checkpoint after Phase 3
            if checkpoint_enabled:
                self.state.save_checkpoint('PHASE_3_COMPLETE', {
                    'scanning': {
                        'completed': True,
                        'total_findings': total_findings,
                        'verified_secrets': len(verified_secrets)
                    }
                })
            
            if total_findings > 0:
                self.logger.info(f"\n🎯 Secret Findings Summary:")
                self.logger.info(f"  ├─ Total Findings: {total_findings}")
                self.logger.info(f"  ├─ Verified: {len(verified_secrets)}")
                self.logger.info(f"  └─ Unverified: {total_findings - len(verified_secrets)}")
                
                # Show domain breakdown if available
                if secrets_summary:
                    self.logger.info(f"\n📊 Findings by Domain:")
                    # Extract domains dict from summary (structure: {'domains': {'domain': {'total': int, 'verified': int}, ...}, ...})
                    domains = secrets_summary.get('domains', {})
                    if domains:
                        # Sort by total count (descending)
                        sorted_domains = sorted(domains.items(), key=lambda x: x[1].get('total', 0), reverse=True)
                        for i, (domain, stats) in enumerate(sorted_domains[:10], 1):  # Top 10
                            total = stats.get('total', 0)
                            verified = stats.get('verified', 0)
                            status = f"✅ {verified}" if verified > 0 else f"⚠️ {total}"
                            self.logger.info(f"  {i:2d}. {domain}: {total} total ({status})")
                        if len(domains) > 10:
                            self.logger.info(f"  ... and {len(domains) - 10} more domains")
                    else:
                        self.logger.info(f"  No domain breakdown available")
                self.logger.info("")
            else:
                self.logger.info(f"\n✅ No secrets found\n")
            
            # Flush Discord notifications immediately (verified + unverified findings)
            await self.notifier.flush_queue(timeout=90)
            
            # ============================================================
            # PHASE 4: EXTRACTING DATA (Parallel)
            # ============================================================
            # Skip if --no-extraction flag is set
            if not self.config.get('skip_extraction', False):
                self.logger.info(f"\n{'═'*70}")
                self.logger.info("⚙️  PHASE 4: EXTRACTING DATA (Parallel)")
                self.logger.info(f"{'═'*70}")
                
                await self._process_all_files_parallel(downloaded_files)
                
                # Save checkpoint after Phase 4
                if checkpoint_enabled:
                    self.state.save_checkpoint('PHASE_4_COMPLETE', {
                        'extraction': {
                            'completed': True,
                            'processed_files': len(downloaded_files)
                        }
                    })
            else:
                self.logger.info(f"\n{'═'*70}")
                self.logger.info("⏭️  PHASE 4: SKIPPED (--no-extraction enabled)")
                self.logger.info(f"{'═'*70}")
            
            # ============================================================
            # PHASE 5: BEAUTIFYING FILES
            # ============================================================
            if self.shutdown_requested:
                self.logger.warning("⚠️  Shutdown requested before beautification")
                await self._save_current_progress()
                return
            
            # Skip if --no-beautify flag is set
            if not self.config.get('skip_beautification', False):
                self.logger.info(f"\n{'═'*70}")
                self.logger.info("✨ PHASE 5: BEAUTIFYING FILES")
                self.logger.info(f"{'═'*70}")
                
                await self._unminify_all_files(downloaded_files)
                
                # Save checkpoint after Phase 5
                if checkpoint_enabled:
                    self.state.save_checkpoint('PHASE_5_COMPLETE', {
                        'beautification': {
                            'completed': True,
                            'beautified_files': len(downloaded_files)
                        }
                    })
            else:
                self.logger.info(f"\n{'='*60}")
                self.logger.info("⏭️  PHASE 5: SKIPPED (--no-beautify enabled)")
                self.logger.info(f"{'='*60}")
            
            # ============================================================
            # PHASE 5.5: SEMGREP STATIC ANALYSIS (Optional)
            # ============================================================
            if self.shutdown_requested:
                self.logger.warning("⚠️  Shutdown requested before Semgrep analysis")
                await self._save_current_progress()
                return
            
            # Run Semgrep if enabled
            if self.config.get('semgrep', {}).get('enabled', False):
                self.logger.info(f"\n{'═'*70}")
                self.logger.info("🔬 PHASE 5.5: SEMGREP STATIC ANALYSIS")
                self.logger.info(f"{'═'*70}")
                
                await self._run_semgrep_analysis(unique_js_dir)
            else:
                self.logger.debug("ℹ️  Semgrep analysis disabled in config")
            
            # ============================================================
            # PHASE 6: CLEANUP
            # ============================================================
            if self.shutdown_requested:
                self.logger.warning("⚠️  Shutdown requested before cleanup")
                await self._save_current_progress()
                return
            
            if self.config.get('batch_processing', {}).get('cleanup_minified', True):
                self.logger.info(f"\n{'='*60}")
                self.logger.info("🗑️  PHASE 6: CLEANUP")
                self.logger.info(f"{'='*60}")
                
                await self._cleanup_minified_files()
            
            # ============================================================
            # PHASE 6.5: MINIMAL STORAGE CLEANUP (DISABLED FOR BUG BOUNTY)
            # ============================================================
            # NOTE: Cleanup disabled to preserve all JS files for manual analysis
            # if self.config.get('minimal_storage', False):
            #     self.logger.info(f"\n{'='*60}")
            #     self.logger.info("🗑️  MINIMAL STORAGE CLEANUP")
            #     self.logger.info(f"{'='*60}")
            #     
            #     # Call the cleanup method to remove files without secrets
            #     cleaned_count = await self._cleanup_files_without_secrets()
            #     self.logger.info(f"✅ Cleaned up {cleaned_count} uninteresting files")
            #     self.logger.info("")
            
            # ============================================================
            # FINAL STATISTICS
            # ============================================================
            duration = time.time() - self.start_time
            self.stats['scan_duration'] = duration
            
            # Update metadata with final stats
            self.state.update_metadata({
                'scan_duration': duration,
                'end_time': datetime.utcnow().isoformat() + 'Z',
                'total_files': self.stats['total_files'],
                'total_secrets': self.stats['total_secrets']
            })
            
            # Mark scan as complete and cleanup checkpoint
            if checkpoint_enabled:
                self.state.save_checkpoint('PHASE_6_COMPLETE', {
                    'stats': {
                        'elapsed_time': duration,
                        'total_files': self.stats['total_files'],
                        'total_secrets': self.stats['total_secrets']
                    }
                })
                
                # Auto cleanup checkpoint on success
                if self.config.get('checkpoint', {}).get('auto_cleanup', True):
                    self.state.delete_checkpoint()
                    self.logger.debug("🧹 Checkpoint cleaned up after successful scan")
            
            # Log and send final stats
            log_stats(self.logger, self.stats)
            
            # Generate Hunter's Report (instant triage summary)
            try:
                generate_report(self.target_name, str(self.paths['base']), self.stats)
            except Exception as e:
                self.logger.warning(f"Report generation failed: {e}")
            
            # NEW: Report noise filtering statistics
            if hasattr(self.fetcher, 'noise_filter'):
                noise_stats = self.fetcher.noise_filter.get_stats()
                if noise_stats['total_checked'] > 0:
                    self.logger.info(f"\n{'='*80}")
                    self.logger.info(f"📊 Noise Filtering Statistics:")
                    self.logger.info(f"{'='*80}")
                    self.logger.info(f"  • Total URLs checked: {noise_stats['total_checked']}")
                    self.logger.info(f"  • Filtered (CDN): {noise_stats['filtered_cdn']}")
                    self.logger.info(f"  • Filtered (Pattern): {noise_stats['filtered_pattern']}")
                    self.logger.info(f"  • Filtered (Known libs): {noise_stats['filtered_hash']}")
                    self.logger.info(f"  • Total filtered: {noise_stats['total_filtered']}")
                    self.logger.info(f"  • Filter rate: {noise_stats['filter_rate']}")
                    self.logger.info(f"  • Passed through: {noise_stats['passed']}")
            self.logger.info(f"{'═'*80}\n")
            # Log detailed failure breakdown (exclude duplicates)
            actual_failures = {k: v for k, v in self.stats['failures'].items() if k != 'duplicates'}
            total_actual_failures = sum(actual_failures.values())
            
            if total_actual_failures > 0:
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"📊 Failure Breakdown ({total_actual_failures} total):")
                self.logger.info(f"{'='*80}")
                for failure_type, count in sorted(actual_failures.items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        self.logger.info(f"  {failure_type}: {count}")
                self.logger.info(f"{'='*80}\n")
            
            # Log duplicates separately as info, not failure
            if self.stats['failures'].get('duplicates', 0) > 0:
                self.logger.info(f"ℹ️  Skipped {self.stats['failures']['duplicates']} files (already scanned in previous run)")
            
            # Log error summary if there were errors
            if self.stats.get('errors'):
                error_count = len(self.stats['errors'])
                self.logger.warning(f"\n{'='*80}")
                self.logger.warning(f"⚠️  Error Summary: {error_count} error(s) occurred during scan")
                self.logger.warning(f"{'='*80}")
                
                # Show first 5 errors
                for i, error in enumerate(self.stats['errors'][:5], 1):
                    self.logger.warning(f"  {i}. {error}")
                
                # Indicate if there are more errors
                if error_count > 5:
                    self.logger.warning(f"  ... and {error_count - 5} more error(s)")
                
                self.logger.warning(f"{'='*80}\n")
            
            # Export results as JSON
            results_json = {
                'target': self.target,
                'scan_date': datetime.utcnow().isoformat() + 'Z',
                'statistics': self.stats,
                'files_scanned': urls_to_scan,
                'secrets_found': self.state.get_total_secrets(),
            }
            
            # Only include extraction data if extraction was performed
            if not self.config.get('skip_extraction', False):
                results_json['extracts'] = self.stats.get('extracts_detailed', {})  # NEW: Detailed extracts with source tracking
                results_json['extracts_legacy'] = {  # OLD: For backwards compatibility
                    'endpoints': self._read_extract_file('endpoints.txt'),
                    'params': self._read_extract_file('params.txt'),
                    'domains': self._read_extract_file('domains.txt')
                }
            else:
                results_json['extraction_skipped'] = True
            
            json_output = Path(self.paths['base']) / 'scan_results.json'
            with open(json_output, 'w') as f:
                json.dump(results_json, f, indent=2)
            
            self.logger.info(f"📄 Results exported to: {json_output}")
            
            # Finalize state for incremental scanning
            self.state.finalize_scan()
            
            # Only send completion status if enabled
            if self.config.get('discord_status_enabled', False):
                await self.notifier.send_status(
                    f"✅ Scan completed for **{self.target}**\n"
                    f"Files: {self.stats['total_files']} | "
                    f"Secrets: {self.stats['total_secrets']} | "
                    f"Duration: {duration:.2f}s",
                    status_type='success'
                )
            
        except Exception as e:
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"❌ Scan failed: {str(e)}")
            self.logger.debug("Full scan failure traceback:", exc_info=True)
            
            # Only send error status if enabled
            if self.config.get('discord_status_enabled', False):
                await self.notifier.send_status(
                    f"❌ Scan failed for **{self.target}**: {str(e)}",
                    status_type='error'
                )
        finally:
            # Cleanup
            await self._cleanup()
            await self.notifier.stop()
    
    async def _check_dependencies(self):
        """Verify all required external dependencies are available before starting scan."""
        import shutil
        
        # TruffleHog is always required for secret scanning
        required_tools = ['trufflehog']
        # SubJS and webcrack are optional (warnings only)
        optional_tools = ['subjs', 'webcrack']
        
        missing_required = []
        missing_optional = []
        
        for tool in required_tools:
            if not shutil.which(tool):
                missing_required.append(tool)
        
        for tool in optional_tools:
            if not shutil.which(tool):
                missing_optional.append(tool)
        
        if missing_required:
            self.logger.error(f"❌ Missing required dependencies: {', '.join(missing_required)}")
            self.logger.error("Please install missing tools before running the scanner.")
            raise RuntimeError(f"Missing dependencies: {', '.join(missing_required)}")
        
        if missing_optional:
            self.logger.warning(f"⚠️  Optional tools not found: {', '.join(missing_optional)}")
            self.logger.warning("Some features may be limited (SubJS discovery, bundle unpacking)")
        
        self.logger.info("✅ Core dependencies verified")
    
    async def _initialize_modules(self):
        """Initializes all scanning modules"""
        from ..strategies.active import ActiveFetcher
        from ..analysis.processor import Processor
        from ..analysis.secrets import SecretScanner
        from ..analysis.static import StaticAnalyzer
        from ..analysis.sourcemap import SourceMapRecoverer
        from ..strategies.fast import FastFetcher
        from ..analysis.semgrep import SemgrepAnalyzer
        
        self.fetcher = ActiveFetcher(self.config, self.logger)
        skip_beautify = self.config.get('skip_beautification', False)
        self.processor = Processor(self.logger, skip_beautification=skip_beautify, config=self.config)
        self.secret_scanner = SecretScanner(
            self.config, 
            self.logger, 
            self.state, 
            self.notifier,
            shutdown_callback=lambda: self.shutdown_requested
        )
        self.ast_analyzer = StaticAnalyzer(self.config, self.logger, self.paths)
        self.source_map_recoverer = SourceMapRecoverer(self.config, self.logger, self.paths)
        self.katana_fetcher = FastFetcher(self.config, self.logger)
        self.semgrep_analyzer = SemgrepAnalyzer(self.config, self.logger, self.paths)
        
        # Initialize secrets organizer
        self.secret_scanner.initialize_organizer(self.paths['base'])
        
        await self.fetcher.initialize()
    
    async def _strategy_katana(self, inputs: List[str]) -> List[str]:
        """
        Strategy 1: Katana-based URL discovery (isolated logic)
        
        Args:
            inputs: List of target URLs/domains
            
        Returns:
            List of discovered JavaScript URLs
        """
        targets = [item for item in inputs if not self._is_valid_js_url(item)]
        if not targets:
            return []
        
        scope_domains = self._get_scope_domains() if not self.config.get('no_scope_filter', False) else None
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info("⚡ STRATEGY: KATANA FAST-PASS (Speed Layer)")
        self.logger.info(f"{'='*70}")
        
        katana_urls = await asyncio.to_thread(
            self.katana_fetcher.fetch_urls,
            targets,
            scope_domains
        )
        
        if katana_urls:
            self.logger.info(f"✓ Katana complete: {len(katana_urls)} JS files discovered\n")
        
        return katana_urls or []
    
    async def _strategy_subjs(self, inputs: List[str]) -> List[str]:
        """
        Strategy 2: SubJS-based URL discovery (isolated logic)
        
        Args:
            inputs: List of target URLs/domains
            
        Returns:
            List of discovered JavaScript URLs
        """
        from ..strategies.passive import PassiveFetcher
        
        targets = [item for item in inputs if not self._is_valid_js_url(item)]
        if not targets:
            return []
        
        subjs_fetcher = PassiveFetcher(self.config, self.logger)
        if not PassiveFetcher.is_installed():
            self.logger.warning("⚠️  SubJS not installed, skipping SubJS strategy")
            return []
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info("📚 STRATEGY: SUBJS HISTORICAL SCAN (History Layer)")
        self.logger.info(f"{'='*70}")
        
        subjs_urls = await subjs_fetcher.fetch_batch(targets)
        
        if subjs_urls:
            self.logger.info(f"✓ SubJS complete: {len(subjs_urls)} JS files discovered\n")
        
        return subjs_urls or []
    
    async def _strategy_live_browser(self, inputs: List[str]) -> List[str]:
        """
        Strategy 3: Live browser-based URL discovery (isolated logic)
        
        Args:
            inputs: List of target URLs/domains
            
        Returns:
            List of discovered JavaScript URLs
        """
        self.logger.info(f"\n{'='*70}")
        self.logger.info("🌐 STRATEGY: LIVE BROWSER SCAN")
        self.logger.info(f"{'='*70}")
        
        all_urls = []
        max_concurrent = self.config.get('max_concurrent_domains', 10)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scan_one(item: str) -> List[str]:
            async with semaphore:
                if self._is_valid_js_url(item):
                    return [item]
                
                is_valid, reason = await self.fetcher.validate_domain(item)
                if not is_valid:
                    return []
                
                result = await self.fetcher.fetch_live(item)
                return result if isinstance(result, list) else []
        
        tasks = [scan_one(item) for item in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_urls.extend(result)
        
        if all_urls:
            self.logger.info(f"✓ Live browser complete: {len(all_urls)} JS files discovered\n")
        
        return all_urls
    
    async def _discover_all_domains_concurrent(self, inputs: List[str], use_subjs: bool, subjs_only: bool) -> List[str]:
        """
        PHASE 1: Concurrent domain discovery using strategy pattern
        
        Args:
            inputs: List of URLs or domains to scan
            use_subjs: If True, use SubJS for URL discovery
            subjs_only: If True, only use SubJS (skip live browser scan)
            
        Returns:
            List of discovered JavaScript URLs
        """
        all_urls = []
        strategies = []
        
        # Strategy 1: Katana (if enabled)
        if self.katana_fetcher.enabled and self.katana_fetcher.katana_path:
            strategies.append(self._strategy_katana(inputs))
        elif self.katana_fetcher.enabled and not self.katana_fetcher.katana_path:
            self.logger.warning("⚠️  Katana enabled but not installed. Install with: go install github.com/projectdiscovery/katana/cmd/katana@latest\n")
        
        # Strategy 2: SubJS (if enabled)
        if use_subjs:
            strategies.append(self._strategy_subjs(inputs))
        
        # Strategy 3: Live Browser (if not disabled)
        if not subjs_only and not self.config.get('skip_live', False):
            strategies.append(self._strategy_live_browser(inputs))
        
        # Execute all strategies in parallel
        if strategies:
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"🚀 LAUNCHING {len(strategies)} PARALLEL DISCOVERY STRATEGIES")
            self.logger.info(f"{'='*70}\n")
            
            results = await asyncio.gather(*strategies, return_exceptions=True)
            
            # Collect results
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"❌ Strategy {idx+1} failed: {str(result)}")
                    self.logger.debug(f"Full strategy traceback:", exc_info=result)
                elif isinstance(result, list):
                    all_urls.extend(result)
        
        # Deduplicate and return
        all_urls = self._deduplicate_urls(all_urls)
        
        self.logger.info(f"{'='*60}")
        self.logger.info(f"📊 Total unique files to process: {len(all_urls)}")
        self.logger.info(f"{'='*60}\n")
        
        # Store source URLs in metadata
        self.state.update_metadata({
            'source_urls': all_urls[:100]
        })
        
        return all_urls
    
    async def _download_all_files(self, urls: List[str]) -> List[dict]:
        """
        PHASE 2: Download all files in parallel using TaskGroup for structured concurrency
        
        Args:
            urls: List of URLs to download
            
        Returns:
            List of downloaded file info dictionaries containing:
            - url: Original URL
            - hash: File content hash
            - filename: Readable filename
            - minified_path: Path to minified file
            - content: File content
        """
        downloaded_files = []
        semaphore = asyncio.Semaphore(self.config.get('threads', 50))
        total_urls = len(urls)
        completed = 0
        failed_breakdown = {
            'invalid_url': 0,
            'out_of_scope': 0,
            'fetch_failed': 0,
            'filtered': 0,
            'duplicate': 0
        }
        lock = asyncio.Lock()  # For thread-safe counter updates
        
        async def download_one(url: str) -> Optional[dict]:
            nonlocal completed
            async with semaphore:
                try:
                    # 🔍 DIAGNOSTIC: Log every URL being processed in verbose mode
                    verbose_mode = self.config.get('verbose', False)
                    if verbose_mode:
                        self.logger.info(f"📥 Download: {url[:80]}")
                    
                    # Validate URL
                    if not self._is_valid_js_url(url):
                        if verbose_mode:
                            self.logger.info(f"❌ Invalid URL: {url[:80]}")
                        else:
                            self.logger.debug(f"Invalid URL: {url}")
                        async with lock:
                            failed_breakdown['invalid_url'] += 1
                        return None
                    
                    if not self._is_target_domain(url):
                        if verbose_mode:
                            self.logger.info(f"❌ Out of scope: {url[:80]}")
                        else:
                            self.logger.debug(f"Out of scope: {url}")
                        async with lock:
                            failed_breakdown['out_of_scope'] += 1
                        return None
                    
                    # Fetch content
                    content = await self.fetcher.fetch_content(url)
                    if not content:
                        # Classify failure using fetcher's last_failure_reason to avoid "untracked failures"
                        reason = getattr(self.fetcher, 'last_failure_reason', None)
                        async with lock:
                            if reason and str(reason).startswith('filtered'):
                                # Noise-filtered URLs should not be treated as fetch failures
                                failed_breakdown['filtered'] += 1
                            else:
                                failed_breakdown['fetch_failed'] += 1

                        # Update engine-level network error counters where applicable
                        if reason:
                            # Map common fetcher reasons to engine stats
                            if reason in ('timeout',):
                                self.stats['network_errors']['timeouts'] += 1
                                self.stats['failures']['timeout'] += 1
                            elif reason in ('dns_errors', 'dns'):
                                self.stats['network_errors']['dns_errors'] += 1
                            elif reason in ('connection_refused',):
                                self.stats['network_errors']['connection_refused'] += 1
                            elif reason in ('ssl_errors',):
                                self.stats['network_errors']['ssl_errors'] += 1
                            elif reason in ('rate_limit', 'rate_limits'):
                                self.stats['network_errors']['rate_limits'] += 1
                            elif reason in ('not_found',) or str(reason).startswith('http_') or reason in ('http_errors','non_retryable_error'):
                                self.stats['network_errors']['http_errors'] += 1
                                self.stats['failures']['http_error'] += 1

                        # Verbose log for quick triage
                        if verbose_mode:
                            self.logger.info(f"❌ Fetch failed ({reason}) {url[:80]}")

                        return None
                    
                    # Calculate hash
                    from ..utils.hashing import calculate_hash
                    file_hash = await calculate_hash(content)
                    
                    # Check if already scanned (UNLESS force flag is set)
                    force_rescan = self.config.get('force_rescan', False)
                    if not force_rescan:
                        if not self.state.mark_as_scanned_if_new(file_hash, url):
                            self.logger.debug(f"Duplicate (already scanned): {url}")
                            self.stats['failures']['duplicates'] += 1
                            async with lock:
                                failed_breakdown['duplicate'] += 1
                            return None
                    else:
                        # Force mode: still mark as scanned but don't skip
                        self.state.mark_as_scanned_if_new(file_hash, url)
                    
                    # NEW: Save to unique_js/{md5}.js for content-based deduplication
                    hash_filename = f"{file_hash}.js"
                    file_path = Path(self.paths['unique_js']) / hash_filename
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Detect if file is minified (for metadata only)
                    is_minified = self._is_minified(content)
                    
                    # Update progress AND Save manifest (THREAD-SAFE)
                    async with lock:
                        # Save hash -> URL mapping for notifications
                        self._save_file_manifest(url, file_hash, hash_filename, is_minified)
                        
                        self.stats['total_files'] += 1
                        completed += 1
                        success_count = len(downloaded_files) + 1  # +1 for current
                        
                        # Show detailed progress every 50 files or at completion
                        if completed % 50 == 0 or completed == total_urls:
                            total_skipped = sum(failed_breakdown.values())
                            extra = f"{success_count} saved, {total_skipped} skipped"
                            if total_skipped > 0 and failed_breakdown['duplicate'] > total_skipped * 0.9:
                                extra += " (mostly cached)"
                            self._log_progress("Download Files", completed, total_urls, extra)
                        else:
                            self._log_progress("Download Files", completed, total_urls, f"{success_count} saved")
                    
                    return {
                        'url': url,
                        'hash': file_hash,
                        'filename': hash_filename,
                        'file_path': str(file_path),
                        'is_minified': is_minified,
                        'content': content
                    }
                
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"❌ Download failed for {url[:100]}: {str(e)}")
                    self.logger.debug("Full download error traceback:", exc_info=True)
                    return None
        
        # Wrapper to append results to shared list (TaskGroup doesn't return results)
        async def task_wrapper(url: str):
            try:
                result = await download_one(url)
                if result:
                    downloaded_files.append(result)
            except Exception as e:
                # Catch any uncaught exceptions to prevent TaskGroup failure
                self.logger.error(f"Task wrapper exception for {url}: {e}")
        
        # Check shutdown before downloading
        if self.shutdown_requested:
            self.logger.warning("⚠️  Download interrupted - shutting down")
            return []
        
        # Download all files using TaskGroup (structured concurrency)
        try:
            async with asyncio.TaskGroup() as tg:
                for url in urls:
                    tg.create_task(task_wrapper(url))
        except* Exception as eg:
            # TaskGroup raises ExceptionGroup if tasks fail critically
            # Since download_one handles its own errors, this catches system errors
            self.logger.error(f"Critical batch download error: {eg}")
        
        # Check shutdown after downloads complete
        if self.shutdown_requested:
            self.logger.warning("⚠️  Download processing interrupted - shutting down")
            return downloaded_files
        
        # Show clean summary
        total_filtered = sum(failed_breakdown.values())
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"✅ Downloaded {len(downloaded_files)} files (skipped {total_filtered})")
        
        # Always show breakdown if many files were skipped
        if total_filtered > 0:
            self.logger.info(f"   📊 Breakdown:")
            if failed_breakdown['invalid_url'] > 0:
                self.logger.info(f"      • Invalid URLs: {failed_breakdown['invalid_url']}")
            if failed_breakdown['out_of_scope'] > 0:
                self.logger.info(f"      • Out of scope: {failed_breakdown['out_of_scope']}")
            if failed_breakdown['fetch_failed'] > 0:
                self.logger.info(f"      • Fetch failed: {failed_breakdown['fetch_failed']}")
            if failed_breakdown['duplicate'] > 0:
                self.logger.info(f"      • Duplicates (cached): {failed_breakdown['duplicate']}")
        
        # 🔍 DIAGNOSTIC: Show fetcher error stats to diagnose failures
        if hasattr(self.fetcher, 'error_stats') and failed_breakdown['fetch_failed'] > 0:
            error_stats = self.fetcher.error_stats
            total_errors = sum(error_stats.values())
            
            self.logger.info(f"\n   🔍 Fetch Failure Analysis:")
            
            # Show all error categories (even if 0, for transparency)
            if error_stats['http_errors'] > 0:
                self.logger.info(f"      • HTTP errors (403/404/etc): {error_stats['http_errors']}")
                
                # Show HTTP status code breakdown
                if hasattr(self.fetcher, 'http_status_breakdown') and self.fetcher.http_status_breakdown:
                    status_summary = ", ".join([f"{code}: {count}" for code, count in sorted(self.fetcher.http_status_breakdown.items())])
                    self.logger.info(f"        └─ Status codes: {status_summary}")
            
            if error_stats['timeouts'] > 0:
                self.logger.info(f"      • Timeouts: {error_stats['timeouts']}")
            if error_stats['rate_limits'] > 0:
                self.logger.info(f"      • Rate limited: {error_stats['rate_limits']}")
            if error_stats['dns_errors'] > 0:
                self.logger.info(f"      • DNS errors: {error_stats['dns_errors']}")
            if error_stats['ssl_errors'] > 0:
                self.logger.info(f"      • SSL errors: {error_stats['ssl_errors']}")
            if error_stats['connection_refused'] > 0:
                self.logger.info(f"      • Connection refused: {error_stats['connection_refused']}")
            
            # Show unaccounted failures (failures that didn't increment any error stat)
            unaccounted = failed_breakdown['fetch_failed'] - total_errors
            if unaccounted > 0:
                self.logger.info(f"      • ⚠️  Untracked failures: {unaccounted}")
                self.logger.info(f"        └─ These failed before HTTP request or weren't logged")
            
            # Show tip about verbose mode
            verbose_mode = self.config.get('verbose', False)
            if verbose_mode or unaccounted > 0:
                self.logger.info(f"      💡 Run with --verbose to see each failure as it happens")
        
        self.logger.info(f"{'='*60}\n")
        
        return downloaded_files
    
    async def _recover_source_maps(self, files: List[dict]):
        """
        PHASE 2.5: Recover source maps from downloaded JavaScript files
        
        Args:
            files: List of file info dictionaries from _download_all_files()
        """
        semaphore = asyncio.Semaphore(self.config.get('threads', 50))
        recovered_count = 0
        
        async def recover_one(file_info: dict):
            nonlocal recovered_count
            async with semaphore:
                try:
                    url = file_info['url']
                    content = file_info['content']
                    
                    # Attempt to recover source map
                    sources = await self.source_map_recoverer.recover_from_file(url, content)
                    
                    if sources:
                        # Save recovered sources
                        await self.source_map_recoverer.save_sources(url, sources)
                        recovered_count += 1
                        return True
                    
                    return False
                
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"Source map recovery failed for {file_info.get('url', 'unknown')}: {str(e)}")
                    self.logger.debug("Full source map recovery traceback:", exc_info=True)
                    return False
        
        # Process all files in parallel
        self.logger.info(f"Processing {len(files)} files for source maps...")
        tasks = [recover_one(file_info) for file_info in files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        if recovered_count > 0:
            self.logger.info(f"✅ Recovered sources from {recovered_count} files")
    
    async def _process_all_files_parallel(self, files: List[dict]):
        """
        PHASE 4: Process all files in parallel using TaskGroup (AST analysis on minified files)
        
        Args:
            files: List of file info dictionaries from _download_all_files()
        """
        semaphore = asyncio.Semaphore(self.config.get('threads', 50))
        processed_count = 0
        total_files = len(files)
        progress_lock = asyncio.Lock()
        
        async def process_one(file_info: dict):
            nonlocal processed_count
            async with semaphore:
                try:
                    content = file_info['content']
                    url = file_info['url']
                    
                    # OPTIMIZATION: Skip vendor libraries by hash before expensive AST analysis
                    should_skip, reason = self.fetcher.noise_filter.should_skip_content(content, url)
                    if should_skip:
                        self.logger.debug(f"⏭️  Skipping AST analysis for vendor lib: {url} ({reason})")
                        async with progress_lock:
                            processed_count += 1
                        return
                    
                    # Run AST analysis on MINIFIED content (faster!)
                    await self.ast_analyzer.analyze(content, url)
                    
                    # PHASE 5: Predict webpack/vite chunks for SPA intelligence
                    if self.config.get('spa_intelligence', {}).get('enabled', True):
                        try:
                            predicted_chunks = self.ast_analyzer.predict_chunks(content, url)
                            if predicted_chunks:
                                # Queue predicted chunks for download (will be deduplicated by state manager)
                                for chunk_url in predicted_chunks:
                                    # Add to discovered URLs (will be fetched in next iteration if not already)
                                    if not self.state.is_processed(chunk_url):
                                        self.logger.debug(f"🧩 Queued chunk: {chunk_url}")
                                        # Note: In a real implementation, you'd add these to a queue
                                        # For now, just log them as they'll be picked up in next scan
                        except Exception as e:
                            self.logger.debug(f"Chunk prediction failed for {url}: {e}")
                    
                    # Update progress counter and log periodically
                    async with progress_lock:
                        processed_count += 1
                        # Log every 30 files to show progress without spam
                        if processed_count % 30 == 0 or processed_count == total_files:
                            percent = (processed_count / total_files * 100) if total_files > 0 else 0
                            self.logger.info(f"⚙️  Extracting: {processed_count}/{total_files} files ({percent:.1f}%)")
                    
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"❌ Processing failed {file_info['url']}: {str(e)}")
                    self.logger.debug("Full processing error traceback:", exc_info=True)
        
        # Check shutdown before extraction
        if self.shutdown_requested:
            self.logger.warning("⚠️  Extraction interrupted - shutting down")
            return
        
        # Process all files using TaskGroup (structured concurrency)
        try:
            async with asyncio.TaskGroup() as tg:
                for f in files:
                    tg.create_task(process_one(f))
        except* Exception as eg:
            # TaskGroup raises ExceptionGroup if tasks fail critically
            # Since process_one handles its own errors, this catches system errors
            self.logger.error(f"Critical batch processing error: {eg}")
        
        # Check shutdown before saving extracts
        if self.shutdown_requested:
            self.logger.warning("⚠️  Skipping extract save - shutting down")
            return
        
        # Save organized extracts (domain-specific + legacy format)
        await self.ast_analyzer.save_organized_extracts()
        
        # Get extracts with source tracking
        extracts_with_sources = self.ast_analyzer.get_extracts_with_sources()
        self.stats['extracts_detailed'] = extracts_with_sources
        
        # Get domain summary for reporting
        domain_summary = self.ast_analyzer.get_domain_summary()
        self.stats['domain_summary'] = domain_summary
        
        self.logger.info(f"✅ Processed {len(files)} files")
    
    async def _unminify_all_files(self, files: List[dict]):
        """
        PHASE 5: Beautify all files in parallel
        
        Args:
            files: List of file info dictionaries from _download_all_files()
        """
        timeout_count = 0  # Track timeouts
        max_timeout_logs = 3  # Only log first 3 timeouts
        semaphore = asyncio.Semaphore(self.config.get('threads', 50))
        
        async def unminify_one(file_info: dict):
            async with semaphore:
                try:
                    # Skip if already unminified
                    if not file_info.get('is_minified', True):
                        return
                    
                    content = file_info['content']
                    minified_path = file_info.get('minified_path')
                    filename = file_info['filename']
                    
                    # Skip if no minified path (shouldn't happen)
                    if not minified_path:
                        return
                    
                    # Process (beautify)
                    processed = await self.processor.process(content, minified_path)
                    
                    # Save unminified version
                    unminified_path = Path(self.paths['files_unminified']) / filename
                    with open(unminified_path, 'w', encoding='utf-8') as f:
                        f.write(processed)
                    
                except asyncio.TimeoutError:
                    nonlocal timeout_count
                    timeout_count += 1
                    if timeout_count <= max_timeout_logs:
                        self.logger.warning(f"Beautification timed out after 30s, using original content")
                    elif timeout_count == max_timeout_logs + 1:
                        self.logger.warning(f"... suppressing further timeout warnings ...")
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"❌ Unminify failed {file_info['url']}: {str(e)}")
                    self.logger.debug("Full beautification error traceback:", exc_info=True)
        
        # Check shutdown before beautification
        if self.shutdown_requested:
            self.logger.warning("⚠️  Beautification interrupted - shutting down")
            return
        
        tasks = [unminify_one(f) for f in files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info(f"✅ Beautified {len(files)} files")
        
        if timeout_count > 0:
            self.logger.info(f"ℹ️  {timeout_count} files timed out during beautification (using original)")
    
    async def _run_semgrep_analysis(self, directory_path: str):
        """
        PHASE 5.5: Run Semgrep static analysis on JS files
        
        Args:
            directory_path: Path to directory containing deduplicated JS files (unique_js/)
        """
        # Validate Semgrep is available
        if not self.semgrep_analyzer.validate():
            self.logger.warning("⚠️  Semgrep validation failed, skipping static analysis")
            return
        
        self.logger.info("🔍 Running Semgrep static analysis...")
        self.logger.info(f"📂 Target: {directory_path}")
        
        # Run Semgrep scan
        findings = await self.semgrep_analyzer.scan_directory(directory_path)
        
        # Update stats
        self.stats['semgrep_findings'] = len(findings)
        
        # Save findings to file
        if findings:
            findings_path = Path(self.paths['base']) / 'findings' / 'semgrep.json'
            self.semgrep_analyzer.save_findings(findings, str(findings_path))
            
            self.logger.info(f"✅ Semgrep analysis complete: {len(findings)} findings")
            self.logger.info(f"💾 Results saved to: {findings_path}")
        else:
            self.logger.info("✅ Semgrep analysis complete: No findings")
        
        self.logger.info("")
    
    async def _cleanup_minified_files(self):
        """
        PHASE 6: Delete all minified files to save disk space
        """
        import shutil
        
        minified_dir = Path(self.paths['files_minified'])
        
        if minified_dir.exists():
            files = list(minified_dir.glob('*'))
            file_count = len(files)
            
            if file_count > 0:
                # Log each file being deleted for verification
                self.logger.debug(f"Deleting {file_count} minified files from {minified_dir}")
                for f in files[:5]:  # Show first 5 files
                    self.logger.debug(f"  - {f.name}")
                if file_count > 5:
                    self.logger.debug(f"  ... and {file_count - 5} more")
                
                shutil.rmtree(minified_dir)
                minified_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"✅ Deleted {file_count} minified files (freed ~{file_count * 200}KB)")
            else:
                self.logger.debug("No minified files to delete")
    
    def _is_minified(self, content: str) -> bool:
        """
        Detect if JavaScript file is minified using multi-heuristic scoring system.
        
        Uses 5 heuristics with weighted scoring:
        1. Average line length (weight: 3)
        2. Semicolon density (weight: 2)
        3. Whitespace ratio (weight: 2)
        4. Short variable ratio (weight: 2)
        5. Comment presence (weight: 1)
        
        Args:
            content: JavaScript content
            
        Returns:
            True if file appears to be minified (score >= threshold)
        """
        # Skip empty files
        if not content or len(content) < 100:
            return False
        
        # Get configuration
        minification_config = self.config.get('minification_detection', {})
        sample_size = minification_config.get('sample_size', 10000)
        threshold_score = minification_config.get('threshold_score', 5)
        
        # Sample for performance (increased from 5000 to 10000)
        sample = content[:sample_size]
        lines = sample.split('\n')
        
        # Very few lines strongly suggests minification
        if len(lines) < 3:
            return True
        
        # Initialize score
        score = 0
        
        # Heuristic 1: Average line length (weight: 3)
        total_chars = sum(len(line) for line in lines)
        avg_line_length = total_chars / len(lines) if lines else 0
        if avg_line_length > 200:
            score += 3
        
        # Heuristic 2: Semicolon density - minified has more semicolons per line (weight: 2)
        semicolon_count = sample.count(';')
        semicolon_density = semicolon_count / len(lines) if lines else 0
        if semicolon_density > 5:
            score += 2
        
        # Heuristic 3: Whitespace ratio - minified has less whitespace (weight: 2)
        whitespace_chars = sum(1 for c in sample if c in ' \t\n\r')
        whitespace_ratio = whitespace_chars / len(sample) if sample else 0
        if whitespace_ratio < 0.15:
            score += 2
        
        # Heuristic 4: Short variable ratio - minified uses short vars (weight: 2)
        import re
        # Match single-letter variables (common in minified code)
        short_vars = len(re.findall(r'\b[a-z]\b', sample))
        total_words = len(sample.split())
        short_var_ratio = short_vars / total_words if total_words else 0
        if short_var_ratio > 0.3:
            score += 2
        
        # Heuristic 5: Comment presence - minified removes comments (weight: 1)
        has_comments = '//' in sample or '/*' in sample
        if not has_comments:
            score += 1
        
        # Debug logging
        self.logger.debug(
            f"Minification detection score: {score}/{threshold_score} "
            f"(avg_line: {avg_line_length:.0f}, semicolon_density: {semicolon_density:.1f}, "
            f"whitespace: {whitespace_ratio:.2f}, short_vars: {short_var_ratio:.2f}, comments: {has_comments})"
        )
        
        # Threshold: default 5+ points = minified
        return score >= threshold_score
    
    def _is_in_scope(self, url: str) -> bool:
        """
        Check if a URL is in scope for the current target
        
        Args:
            url: URL to check
            
        Returns:
            True if URL matches target domain
        """
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            url_domain = parsed.netloc.lower()
            
            # Remove port if present
            if ':' in url_domain:
                url_domain = url_domain.split(':')[0]
            
            # Remove www. prefix for comparison
            url_domain = url_domain.replace('www.', '')
            target_clean = self.target.lower().replace('www.', '')
            
            # Match if URL domain ends with target (supports subdomains)
            return url_domain == target_clean or url_domain.endswith('.' + target_clean)
        except:
            return False
    
    def _read_extract_file(self, filename: str) -> List[str]:
        """Read lines from an extract file
        
        Args:
            filename: Name of the extract file (e.g., 'endpoints.txt')
            
        Returns:
            List of lines from the file, or empty list if file doesn't exist
        """
        extract_path = Path(self.paths['extracts']) / filename
        if extract_path.exists():
            try:
                with open(extract_path, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            except Exception as e:
                # Traceback Pattern: Clean console + forensic log
                self.logger.error(f"Could not read {filename}: {str(e)}")
                self.logger.debug(f"Full extract read traceback:", exc_info=True)
                return []
        return []
    
    async def _cleanup(self):
        """Cleanup resources with proper error handling"""
        # Cleanup fetcher with timeout protection
        if self.fetcher:
            try:
                await asyncio.wait_for(self.fetcher.cleanup(), timeout=5.0)
            except asyncio.TimeoutError:
                self.logger.warning("⏱️  Fetcher cleanup timeout - forcing shutdown")
            except Exception as e:
                self.logger.debug(f"Fetcher cleanup error: {e}")
    
    def _deduplicate_urls(self, urls: List[str]) -> List[str]:
        """
        Deduplicate URLs by base path (ignore query parameters)
        Keeps the shortest URL for each unique base path
        
        Args:
            urls: List of URLs
            
        Returns:
            Deduplicated list of URLs
        """
        from urllib.parse import urlparse, urlunparse
        
        unique_urls = {}  # base_url -> full_url
        invalid_urls = []
        
        for url in urls:
            try:
                # Fix common URL corruption: backslashes instead of forward slashes
                # e.g., "https://example.com/file.js\\" -> "https://example.com/file.js"
                url = url.replace('\\', '/').rstrip('/')
                
                # Basic validation - reject obviously corrupted URLs
                if not url.startswith(('http://', 'https://')):
                    invalid_urls.append(url)
                    continue
                
                # Check for corruption indicators
                if ' ' in url or len(url) > 2000:
                    invalid_urls.append(url)
                    self.logger.debug(f"Invalid URL (corrupted): {url[:100]}")
                    continue
                
                # Check if it looks like a valid domain
                parsed = urlparse(url)
                if not parsed.netloc:
                    invalid_urls.append(url)
                    self.logger.debug(f"Invalid URL (no domain): {url[:100]}")
                    continue
                
                # Reject malformed paths (e.g., ending with /.js or just .js)
                if not parsed.path or parsed.path == '/':
                    continue
                path_parts = parsed.path.split('/')
                if path_parts and path_parts[-1].startswith('.') and '.' not in path_parts[-1][1:]:
                    invalid_urls.append(url)
                    self.logger.debug(f"Invalid URL (malformed path): {url}")
                    continue
                
                # Create base URL without query params
                base_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                
                # Keep the URL, prefer one without query params
                if base_url not in unique_urls:
                    unique_urls[base_url] = url
                else:
                    # If current URL has no query params, prefer it
                    if not parsed.query and '?' in unique_urls[base_url]:
                        unique_urls[base_url] = url
                        
            except Exception as e:
                # Traceback Pattern: Clean console + forensic log
                self.logger.error(f"Failed to parse URL {url[:100]}: {str(e)}")
                self.logger.debug("Full URL parsing traceback:", exc_info=True)
                invalid_urls.append(url)
        
        if invalid_urls:
            self.logger.warning(f"Filtered out {len(invalid_urls)} invalid URLs")
        
        original_count = len(urls)
        deduplicated = list(unique_urls.values())
        
        if original_count > len(deduplicated):
            self.logger.info(f"Deduplicated {original_count} URLs to {len(deduplicated)} unique files (removed {original_count - len(deduplicated)} duplicates)")
        
        return deduplicated
    
    @staticmethod
    def _extract_root_domain(domain: str) -> str:
        """
        Extract root domain handling multi-part TLDs
        
        Examples:
            'example.com' -> 'example.com'
            'api.example.com' -> 'example.com'
            'api.cdn.example.co.uk' -> 'example.co.uk'
        
        Args:
            domain: Domain to extract from
            
        Returns:
            Root domain (e.g., example.co.uk for multi-part TLDs, example.com for standard TLDs)
        """
        # Known multi-part TLDs (set for O(1) lookup performance)
        multi_part_tlds = {
            'co.uk', 'com.au', 'co.jp', 'co.za', 'com.br',
            'co.in', 'co.nz', 'com.mx', 'co.il', 'com.ar',
            'com.tr', 'net.tr', 'co.kr', 'ne.kr'
        }
        
        parts = domain.split('.')
        
        # Check for multi-part TLD (e.g., co.uk, com.au)
        if len(parts) >= 3:
            potential_tld = '.'.join(parts[-2:])
            if potential_tld in multi_part_tlds:
                # Return domain + multi-part TLD (last 3 parts)
                # e.g., 'example.co.uk' from 'api.cdn.example.co.uk'
                return '.'.join(parts[-3:])
        
        # Standard single-part TLD (e.g., .com, .org)
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        
        return domain
    
    @staticmethod
    def _sanitize_target_name(target: str) -> str:
        """
        Sanitizes target name for use as directory name
        
        Args:
            target: Target domain/URL
            
        Returns:
            Sanitized name
        """
        # Remove protocol
        target = target.replace('https://', '').replace('http://', '')
        # Remove trailing slashes
        target = target.rstrip('/')
        # Replace invalid characters
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            target = target.replace(char, '_')
        return target
    
    def _is_target_domain(self, url: str) -> bool:
        """Check if URL belongs to allowed domains from input file
        
        Only checks domain.tld - ignores paths, query params, ports, and scheme.
        Respects ALL domains provided in the -i input file.
        """
        from urllib.parse import urlparse
        
        try:
            if not url.startswith(('http://', 'https://')):
                return False
            
            domain = urlparse(url).netloc.lower()
            
            # Remove port to get clean domain
            domain_no_port = domain.split(':')[0]
            
            # Remove www. prefix for comparison
            domain_clean = domain_no_port.replace('www.', '')
            
            # Check against all allowed domains
            for allowed in self.allowed_domains:
                # Remove port and www. from allowed domain for comparison
                allowed_no_port = allowed.split(':')[0]
                allowed_clean = allowed_no_port.replace('www.', '')
                
                # Exact match or subdomain match
                if domain_clean == allowed_clean or domain_clean.endswith('.' + allowed_clean):
                    return True
            
            # Debug: log rejected URLs to help diagnose scope issues
            self.logger.debug(f"❌ OUT OF SCOPE: {url[:100]} | Domain: {domain_clean} | Allowed: {list(self.allowed_domains)[:5]}")
            return False
        except Exception as e:
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"Domain check error for {url[:80]}: {str(e)}")
            self.logger.debug("Full domain check traceback:", exc_info=True)
            return False
    
    @staticmethod
    def _is_valid_js_url(url: str) -> bool:
        """
        Validates if URL is a valid JS/TS file
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid JS/TS/JSX URL
        """
        from urllib.parse import urlparse
        
        try:
            # Must start with http/https
            if not url.startswith(('http://', 'https://')):
                return False
            
            parsed = urlparse(url)
            
            # Must have domain
            if not parsed.netloc:
                return False
            
            # Must have path
            if not parsed.path or parsed.path == '/':
                return False
            
            # Check for obvious invalid patterns
            if ' ' in url:  # Spaces in URL
                return False
            
            # Reject malformed paths like '/.js', '.js', or ending with only extension
            path_parts = parsed.path.split('/')
            if not path_parts or not path_parts[-1]:  # Empty filename
                return False
            
            filename = path_parts[-1]
            # Reject if filename is ONLY an extension (e.g., '.js', '.ts')
            if filename.startswith('.') and '.' not in filename[1:]:
                return False
            if parsed.path.endswith(('/.js', '/.ts', '/.jsx', '/.tsx', '/.mjs', '/.cts', '/.mts')):
                return False
                
            # Must be JS/TS file (.js, .mjs, .ts, .tsx, .jsx, or with query params)
            path_lower = parsed.path.lower()
            full_url_lower = url.lower()
            
            # Check for supported extensions
            if (path_lower.endswith('.js') or 
                path_lower.endswith('.mjs') or
                path_lower.endswith('.ts') or
                path_lower.endswith('.tsx') or
                path_lower.endswith('.jsx') or
                path_lower.endswith('.cts') or
                path_lower.endswith('.mts') or
                '.js?' in full_url_lower or
                '.js#' in full_url_lower or
                '.ts?' in full_url_lower or
                '.ts#' in full_url_lower or
                '.tsx?' in full_url_lower or
                '.tsx#' in full_url_lower or
                '.jsx?' in full_url_lower or
                '.jsx#' in full_url_lower or
                '.mjs?' in full_url_lower or
                '.mjs#' in full_url_lower or
                '.cts?' in full_url_lower or
                '.cts#' in full_url_lower or
                '.mts?' in full_url_lower or
                '.mts#' in full_url_lower):
                return True
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def _get_readable_filename(url: str, file_hash: str) -> str:
        """
        Creates human-readable filename from URL and hash
        
        Args:
            url: Source URL
            file_hash: SHA256 hash
            
        Returns:
            Readable filename like: subdomain.domain.com-filename-abc123.js
        """
        from urllib.parse import urlparse
        import re
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            path = parsed.path
            
            # Extract filename from path
            filename = path.split('/')[-1] if path else 'script'
            
            # Remove query string from filename
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # Remove all supported file extensions
            for ext in ['.js', '.mjs', '.ts', '.tsx', '.jsx', '.cts', '.mts']:
                if filename.endswith(ext):
                    filename = filename[:-len(ext)]
                    break
            
            # Clean filename: keep only alphanumeric, dash, underscore
            filename = re.sub(r'[^a-zA-Z0-9\-_.]', '-', filename)
            
            # Remove consecutive dashes
            filename = re.sub(r'-+', '-', filename)
            
            # Trim to reasonable length
            if len(filename) > 50:
                filename = filename[:50]
            
            # Remove trailing/leading dashes
            filename = filename.strip('-')
            
            # If filename is empty, use 'script'
            if not filename:
                filename = 'script'
            
            # Short hash (first 7 chars)
            short_hash = file_hash[:7]
            
            # Clean domain: replace colon with dash (Windows compatibility)
            clean_domain = domain.replace(':', '-')
            
            # Build final name: domain-filename-hash.js
            final_name = f"{clean_domain}-{filename}-{short_hash}.js"
            
            # Final cleanup
            final_name = final_name.replace('..', '.')
            
            return final_name
            
        except Exception:
            # Fallback to just hash
            return f"{file_hash}.js"
    
    def _save_file_manifest(self, url: str, file_hash: str, filename: str, is_minified: bool = False):
        """
        Saves file manifest mapping for easy reference and Discord notifications
        
        Args:
            url: Source URL
            file_hash: MD5 hash (32 characters)
            filename: Hash-based filename ({md5}.js)
            is_minified: Whether file is minified
        """
        import json
        
        manifest_file = Path(self.paths['base']) / 'file_manifest.json'
        
        # Load existing manifest
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = {}
        
        # Add entry: hash -> {url, filename, timestamp, minified}
        manifest[file_hash] = {
            'url': url,
            'filename': filename,
            'is_minified': is_minified,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Save manifest
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
    
    def _get_scope_domains(self) -> set:
        """Get set of in-scope domains for filtering"""
        domains = set()
        
        # Extract domains from allowed_domains
        for domain in self.allowed_domains:
            # Remove protocol
            clean = domain.replace('http://', '').replace('https://', '')
            # Remove path
            clean = clean.split('/')[0]
            # Remove port
            clean = clean.split(':')[0]
            # Remove www
            if clean.startswith('www.'):
                clean = clean[4:]
            domains.add(clean.lower())
        
        return domains if domains else None
    
    async def _cleanup_files_without_secrets(self) -> int:
        """
        Minimal storage mode: Delete files that have no secrets or findings
        
        Returns:
            Count of files deleted
        """
        deleted_count = 0
        
        try:
            # Get all secret source filenames from scanner
            files_with_secrets = set()
            # Check secrets from disk (streamed mode)
            secret_count = 0
            if self.secret_scanner.secrets_organizer:
                secrets_file = self.secret_scanner.secrets_organizer.streaming_file
                if secrets_file.exists():
                    try:
                        with open(secrets_file, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)
                            # Handle both list (old format) and dict (new format)
                            if isinstance(raw_data, list):
                                secrets = raw_data
                            elif isinstance(raw_data, dict):
                                secrets = raw_data.get('secrets', [])
                            else:
                                secrets = []
                            for secret in secrets:
                                filename = secret.get('filename')
                                if filename:
                                    files_with_secrets.add(filename)
                    except Exception as e:
                        self.logger.error(f"Error reading secrets for cleanup: {e}")
            
            # Get all endpoint/interesting finding filenames from AST analyzer
            files_with_findings = set()
            if hasattr(self.ast_analyzer, 'extracts'):
                for source_url, extracts_list in self.ast_analyzer.extracts.items():
                    if extracts_list:  # Has findings
                        # Extract filename from URL or manifest
                        manifest_file = Path(self.paths['base']) / 'file_manifest.json'
                        if manifest_file.exists():
                            import json
                            with open(manifest_file, 'r') as f:
                                manifest = json.load(f)
                                for filename, entry in manifest.items():
                                    if entry.get('url') == source_url:
                                        files_with_findings.add(filename)
                                        break
            
            # Combine files to keep
            files_to_keep = files_with_secrets | files_with_findings
            
            # Scan both minified and unminified directories
            for dir_path in [self.paths['files_minified'], self.paths['files_unminified']]:
                dir_path = Path(dir_path)
                if not dir_path.exists():
                    continue
                
                for file_path in dir_path.glob('*.js'):
                    filename = file_path.name
                    
                    # Skip vendor libraries (already filtered by hash)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    should_skip, reason = self.fetcher.noise_filter.should_skip_content(content, str(file_path))
                    if should_skip:
                        # Delete vendor library
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.debug(f"🗑️  Deleted vendor lib: {filename} ({reason})")
                        continue
                    
                    # Delete if no secrets or findings
                    if filename not in files_to_keep:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.debug(f"🗑️  Deleted file with no findings: {filename}")
            
            return deleted_count
            
        except Exception as e:
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"⚠️  Error during cleanup: {str(e)}")
            self.logger.debug("Full cleanup error traceback:", exc_info=True)
            return deleted_count
    
    async def _save_current_progress(self):
        """
        Save current scan progress and data before shutdown
        Ensures no data loss when Ctrl+C is pressed
        """
        try:
            self.logger.info("💾 Saving current progress...")
            
            # Save secrets if any were found
            # Save organized secrets (reads from disk)
            secret_count = 0
            if self.secret_scanner.secrets_organizer:
                secrets_file = self.secret_scanner.secrets_organizer.streaming_file
                if secrets_file.exists():
                    try:
                        with open(secrets_file, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)
                            # Handle both list (old format) and dict (new format)
                            if isinstance(raw_data, list):
                                secret_count = len(raw_data)
                            elif isinstance(raw_data, dict):
                                secret_count = len(raw_data.get('secrets', []))
                    except:
                        pass
            
            if secret_count > 0:
                try:
                    await self.secret_scanner.save_organized_secrets()
                    trufflehog_output = Path(self.paths['base']) / 'trufflehog_full.json'
                    self.secret_scanner.export_results(str(trufflehog_output))
                    self.logger.info(f"  ✓ Saved {secret_count} secrets")
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"  ✗ Failed to save secrets: {str(e)}")
                    self.logger.debug("Full secret save traceback:", exc_info=True)
            
            # Save extracts if any were found
            if hasattr(self.ast_analyzer, 'extracts') and self.ast_analyzer.extracts:
                try:
                    await self.ast_analyzer.save_organized_extracts()
                    extract_count = sum(len(v) for v in self.ast_analyzer.extracts.values())
                    self.logger.info(f"  ✓ Saved {extract_count} extracts")
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"  ✗ Failed to save extracts: {str(e)}")
                    self.logger.debug("Full extract save traceback:", exc_info=True)
            
            # Update metadata with shutdown info
            try:
                duration = time.time() - self.start_time
                
                # Include error stats in metadata
                metadata_update = {
                    'scan_duration': duration,
                    'end_time': datetime.utcnow().isoformat() + 'Z',
                    'shutdown_type': 'interrupted',
                    'total_files': self.stats.get('total_files', 0),
                    'total_secrets': self.stats.get('total_secrets', 0)
                }
                
                if self.fetcher and hasattr(self.fetcher, 'error_stats'):
                    metadata_update['network_errors'] = self.fetcher.error_stats
                
                self.state.update_metadata(metadata_update)
                self.logger.info(f"  ✓ Updated metadata (duration: {duration:.1f}s)")
            except Exception as e:
                # Traceback Pattern: Clean console + forensic log
                self.logger.error(f"  ✗ Failed to update metadata: {str(e)}")
                self.logger.debug("Full metadata update traceback:", exc_info=True)
            
            # Display error summary
            self._display_error_summary()
            
            self.logger.info("💾 Progress saved successfully")
            
        except Exception as e:
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"❌ Failed to save progress: {str(e)}")
            self.logger.debug("Full progress save traceback:", exc_info=True)
    
    def _display_error_summary(self):
        """Display categorized error summary at scan completion"""
        if not self.fetcher:
            return
            
        error_stats = self.fetcher.error_stats
        total_errors = sum(error_stats.values())
        
        if total_errors == 0:
            return
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info("⚠️  ERROR SUMMARY")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total Network Errors: {total_errors}")
        self.logger.info("")
        
        if error_stats['dns_errors'] > 0:
            self.logger.info(f"  🔴 DNS Resolution Failed: {error_stats['dns_errors']}")
            self.logger.info("     → Dead domains or invalid DNS records")
        
        if error_stats['connection_refused'] > 0:
            self.logger.info(f"  🔴 Connection Refused: {error_stats['connection_refused']}")
            self.logger.info("     → Servers not accepting connections")
        
        if error_stats['ssl_errors'] > 0:
            self.logger.info(f"  🔴 SSL/Certificate Errors: {error_stats['ssl_errors']}")
            self.logger.info("     → Invalid or self-signed certificates")
        
        if error_stats['timeouts'] > 0:
            self.logger.info(f"  ⏱️  Timeouts: {error_stats['timeouts']}")
            self.logger.info("     → Slow servers or rate limiting")
        
        if error_stats['rate_limits'] > 0:
            self.logger.info(f"  🚦 Rate Limited: {error_stats['rate_limits']}")
            self.logger.info("     → HTTP 429/503 responses")
        
        if error_stats['http_errors'] > 0:
            self.logger.info(f"  ❌ HTTP Errors: {error_stats['http_errors']}")
            self.logger.info("     → 4xx/5xx status codes")
        
        self.logger.info(f"{'='*60}\n")
    
    def _emergency_shutdown(self):
        """
        Emergency shutdown handler - runs in separate thread with timeout
        Saves critical data synchronously before exit
        """
        try:
            # Get the current event loop (where tasks are running)
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no loop exists, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Cancel all pending tasks in the ORIGINAL loop first
            # This prevents "Future exception was never retrieved" spam
            try:
                pending_tasks = asyncio.all_tasks(loop)
                self.logger.debug(f"Cancelling {len(pending_tasks)} pending tasks...")
                
                for task in pending_tasks:
                    if not task.done():
                        task.cancel()
                
                # Wait for all tasks to acknowledge cancellation
                if pending_tasks:
                    loop.run_until_complete(
                        asyncio.gather(*pending_tasks, return_exceptions=True)
                    )
                self.logger.debug("All tasks cancelled successfully")
            except Exception as e:
                self.logger.debug(f"Task cancellation error (expected): {e}")
            
            # Force cleanup browser if it exists (prevents Playwright TargetClosedError)
            if hasattr(self, 'fetcher') and self.fetcher:
                try:
                    loop.run_until_complete(self.fetcher.cleanup())
                    self.logger.info("Browser cleanup completed")
                except Exception as e:
                    self.logger.debug(f"Browser cleanup error: {e}")
            
            # Now save progress
            try:
                loop.run_until_complete(self._save_current_progress())
            except Exception as e:
                self.logger.debug(f"Progress save error: {e}")
            
            # Stop Discord notifier
            if hasattr(self, 'notifier') and self.notifier:
                try:
                    loop.run_until_complete(self.notifier.stop(drain_queue=False))
                except Exception as e:
                    self.logger.debug(f"Notifier cleanup error: {e}")
            
            # Close the loop
            try:
                loop.close()
            except Exception as e:
                self.logger.debug(f"Loop close error: {e}")
            
            # Force kill any remaining playwright processes (with verification)
            try:
                import subprocess
                import sys
                import time
                
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/IM', 'chromium.exe'], 
                                   stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                                   stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    time.sleep(0.5)  # Give Windows time to kill processes
                else:
                    subprocess.run(['pkill', '-9', 'chromium'], 
                                   stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    subprocess.run(['pkill', '-9', 'chrome'], 
                                   stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                    time.sleep(0.3)  # Give Linux time to kill processes
                
                # Verify cleanup
                if sys.platform != 'win32':
                    result = subprocess.run(['pgrep', '-f', 'chromium|chrome'], 
                                          capture_output=True, text=True)
                    if result.stdout.strip():
                        self.logger.warning("⚠️  Some browser processes may still be running")
                    else:
                        self.logger.debug("✓ All browser processes terminated")
            except Exception:
                pass  # Ignore errors - best effort cleanup
                
        except Exception as e:
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"❌ Emergency shutdown failed: {str(e)}")
            self.logger.debug("Full emergency shutdown traceback:", exc_info=True)
    
    def get_url_from_filename(self, filename: str) -> Optional[str]:
        """
        Get original URL from readable filename
        
        Args:
            filename: Readable filename
            
        Returns:
            Original URL or None if not found
        """
        import json
        
        manifest_file = Path(self.paths['base']) / 'file_manifest.json'
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                entry = manifest.get(filename, {})
                return entry.get('url')
        return None
    
    async def _discover_js_recursively(self, downloaded_files: List[dict], max_depth: int, validate_with_head: bool) -> List[dict]:
        """
        Recursively discover JS files referenced within other JS files
        
        Implements depth-limited recursive discovery to find 2nd/3rd level JS files.
        Prevents infinite loops via seen_urls tracking and enforces in-scope validation.
        
        Args:
            downloaded_files: List of initially downloaded file dictionaries
            max_depth: Maximum recursion depth (1=direct references only, 2=2nd level, etc.)
            validate_with_head: If True, use HEAD requests to validate URLs before downloading
            
        Returns:
            List of newly discovered file objects (already downloaded, ready for pipeline)
        """
        seen_urls = set()  # Track all URLs we've seen to prevent duplicates
        all_discovered_files = []  # All file objects downloaded during recursion
        all_discovered_urls = set()  # Track all discovered URLs for reporting
        
        # Initialize seen_urls with all initially downloaded URLs
        for file_info in downloaded_files:
            seen_urls.add(file_info['url'])
        
        current_depth = 0
        current_files = downloaded_files
        
        self.logger.info(f"Starting recursive discovery (max_depth={max_depth})")
        
        while current_depth < max_depth:
            current_depth += 1
            self.logger.info(f"  🔍 Depth {current_depth}/{max_depth}: Analyzing {len(current_files)} files...")
            
            discovered_at_depth = set()
            
            # Extract JS URLs from all files at current depth
            for file_info in current_files:
                try:
                    content = file_info.get('content', '')
                    if not content:
                        # Read from disk if content not in memory
                        file_path = file_info.get('file_path')
                        if file_path and Path(file_path).exists():
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                    
                    if content:
                        # Extract JS URLs using AST analyzer
                        js_urls = await self.ast_analyzer.extract_js_urls(content, file_info['url'])
                        
                        for url in js_urls:
                            # Skip if already seen
                            if url in seen_urls:
                                continue
                            
                            # In-scope validation
                            if not self._is_target_domain(url):
                                self.logger.debug(f"Skipping out-of-scope URL: {url}")
                                continue
                            
                            # Mark as seen
                            seen_urls.add(url)
                            discovered_at_depth.add(url)
                            all_discovered_urls.add(url)
                
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"Error extracting JS URLs from {file_info.get('url', 'unknown')}: {str(e)}")
                    self.logger.debug("Full URL extraction traceback:", exc_info=True)
            
            self.logger.info(f"  ✓ Depth {current_depth}: Found {len(discovered_at_depth)} new URLs")
            
            # If no new URLs found, stop early
            if not discovered_at_depth:
                self.logger.info(f"  ℹ️  No more JS files found at depth {current_depth}, stopping recursion")
                break
            
            # Validate URLs with HEAD requests if enabled
            if validate_with_head and discovered_at_depth:
                self.logger.info(f"  🔎 Validating {len(discovered_at_depth)} URLs with HEAD requests...")
                validated_urls = await self._validate_urls_with_head(list(discovered_at_depth))
                self.logger.info(f"  ✓ {len(validated_urls)} URLs validated (200 OK)")
                discovered_at_depth = set(validated_urls)
            
            # Download files for next depth iteration AND add to results
            if discovered_at_depth:
                self.logger.info(f"  ⬇️  Downloading {len(discovered_at_depth)} files for depth {current_depth + 1} analysis...")
                current_files = await self._download_all_files(list(discovered_at_depth))
                
                # Add downloaded files to results (these are ready for pipeline)
                all_discovered_files.extend(current_files)
                
                # If we've reached max depth, stop here (don't analyze deeper)
                if current_depth >= max_depth:
                    break
            else:
                break
        
        self.logger.info(f"✅ Recursive discovery complete: {len(all_discovered_files)} total new files downloaded")
        return all_discovered_files
    
    async def _validate_urls_with_head(self, urls: List[str]) -> List[str]:
        """
        Validate URLs using HEAD requests to check existence before downloading
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of URLs that returned 200 OK
        """
        validated_urls = []
        semaphore = asyncio.Semaphore(20)  # Limit concurrent HEAD requests
        
        async def validate_one(url: str) -> Optional[str]:
            async with semaphore:
                try:
                    exists, status_code = await self.fetcher.validate_url_exists(url)
                    if exists:
                        return url
                    else:
                        self.logger.debug(f"HEAD validation failed: {url} (status {status_code})")
                        return None
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"HEAD request error for {url}: {str(e)}")
                    self.logger.debug("Full HEAD validation traceback:", exc_info=True)
                    return None
        
        tasks = [validate_one(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, str):
                validated_urls.append(result)
        
        return validated_urls
