"""
Engine
Main orchestrator that routes input to appropriate modules
"""
import asyncio
import aiohttp
import json
import time
import signal
from pathlib import Path
from typing import Optional, List
from ..utils.file_ops import FileOps
from ..utils.logger import setup_logger, log_stats
from .state_manager import StateManager
from .notifier import DiscordNotifier


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
        self.paths = FileOps.create_result_structure(self.target_name)
        
        # Initialize logger
        log_file = Path(self.paths['logs']) / 'scan.log'
        self.logger = setup_logger(log_file=str(log_file))
        
        # Initialize state manager
        self.state = StateManager(self.paths['base'])
        
        # Initialize Discord notifier
        webhook_url = config.get('discord_webhook')
        rate_limit = config.get('discord_rate_limit', 30)
        self.notifier = DiscordNotifier(webhook_url, rate_limit, self.logger)
        
        # Modules will be initialized when needed
        self.fetcher = None
        self.processor = None
        self.secret_scanner = None
        self.ast_analyzer = None
        
        # Shutdown flag for graceful exit
        self.shutdown_requested = False
        
        # Track allowed domains from input file
        self.allowed_domains = set()
        
        # Statistics
        self.start_time = None
        self.stats = {
            'total_files': 0,
            'total_secrets': 0,
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
            }
        }
    
    async def run(self, inputs: List[str], use_subjs: bool = False, subjs_only: bool = False):
        """
        Main execution method with BATCH PROCESSING
        
        Args:
            inputs: List of URLs or domains to scan
            use_subjs: If True, use SubJS for additional URL discovery
            subjs_only: If True, only use SubJS (skip live browser scan)
        """
        self.start_time = time.time()
        
        # Update metadata with start time
        from datetime import datetime
        self.state.update_metadata({
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'use_subjs': use_subjs,
            'subjs_only': subjs_only
        })
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            if not self.shutdown_requested:
                self.shutdown_requested = True
                self.logger.warning("\n⚠️  Shutdown requested (Ctrl+C). Cleaning up...")
        
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
            
            # ============================================================
            # PHASE 1: DISCOVERY & URL COLLECTION (CONCURRENT)
            # ============================================================
            self.logger.info(f"\n{'='*60}")
            self.logger.info("📡 PHASE 1: DISCOVERY & URL COLLECTION (CONCURRENT)")
            self.logger.info(f"{'='*60}")
            
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
            
            # Process domains concurrently
            urls_to_scan = await self._discover_all_domains_concurrent(inputs, use_subjs, subjs_only)
            
            if not urls_to_scan:
                self.logger.warning("No JavaScript files found to scan")
                return
            
            # ============================================================
            # PHASE 2: DOWNLOADING ALL FILES (Parallel)
            # ============================================================
            self.logger.info(f"\n{'='*60}")
            self.logger.info("⬇️  PHASE 2: DOWNLOADING ALL FILES")
            self.logger.info(f"{'='*60}")
            
            downloaded_files = await self._download_all_files(urls_to_scan)
            self.logger.info(f"✅ Downloaded {len(downloaded_files)} files\n")
            
            if not downloaded_files:
                self.logger.warning("No files were successfully downloaded")
                return
            
            # ============================================================
            # PHASE 2.5: SOURCE MAP RECOVERY (Optional)
            # ============================================================
            if self.config.get('recover_source_maps', False):
                self.logger.info(f"\n{'='*60}")
                self.logger.info("🗺️  PHASE 2.5: RECOVERING SOURCE MAPS")
                self.logger.info(f"{'='*60}")
                
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
            self.logger.info(f"\n{'='*60}")
            self.logger.info("🔍 PHASE 3: SCANNING FOR SECRETS (TruffleHog)")
            self.logger.info(f"{'='*60}")
            
            # Reset all_secrets before scanning (in case of multiple scan_directory calls)
            self.secret_scanner.all_secrets = []
            
            # Scan BOTH minified AND unminified directories
            # (files are saved to different directories based on minification detection)
            minified_dir = str(Path(self.paths['files_minified']))
            unminified_dir = str(Path(self.paths['files_unminified']))
            
            # Scan minified files
            secrets_minified = await self.secret_scanner.scan_directory(minified_dir)
            
            # Scan unminified files
            secrets_unminified = await self.secret_scanner.scan_directory(unminified_dir)
            
            # Combine results (secret_scanner tracks all in self.all_secrets)
            secrets = secrets_minified + secrets_unminified
            self.stats['total_secrets'] = len(secrets)
            
            # Save organized secrets (domain-specific + full results)
            await self.secret_scanner.save_organized_secrets()
            
            # Get secrets summary for reporting
            secrets_summary = self.secret_scanner.get_secrets_summary()
            self.stats['secrets_summary'] = secrets_summary
            
            # Export TruffleHog results to JSON (legacy - for backward compatibility)
            trufflehog_output = Path(self.paths['base']) / 'trufflehog_full.json'
            self.secret_scanner.export_results(str(trufflehog_output))
            
            if secrets:
                self.logger.info(f"✅ Found {len(secrets)} secrets\n")
            else:
                self.logger.info(f"✅ No secrets found\n")
            
            # ============================================================
            # PHASE 4: EXTRACTING DATA (Parallel)
            # ============================================================
            self.logger.info(f"\n{'='*60}")
            self.logger.info("⚙️  PHASE 4: EXTRACTING DATA (Parallel)")
            self.logger.info(f"{'='*60}")
            
            await self._process_all_files_parallel(downloaded_files)
            
            # ============================================================
            # PHASE 5: BEAUTIFYING FILES
            # ============================================================
            self.logger.info(f"\n{'='*60}")
            self.logger.info("✨ PHASE 5: BEAUTIFYING FILES")
            self.logger.info(f"{'='*60}")
            
            await self._unminify_all_files(downloaded_files)
            
            # ============================================================
            # PHASE 6: CLEANUP
            # ============================================================
            if self.config.get('batch_processing', {}).get('cleanup_minified', True):
                self.logger.info(f"\n{'='*60}")
                self.logger.info("🗑️  PHASE 6: CLEANUP")
                self.logger.info(f"{'='*60}")
                
                await self._cleanup_minified_files()
            
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
            
            # Log and send final stats
            log_stats(self.logger, self.stats)
            
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
                    self.logger.info(f"{'='*80}\n")
            
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
                'extracts': self.stats.get('extracts_detailed', {}),  # NEW: Detailed extracts with source tracking
                'extracts_legacy': {  # OLD: For backwards compatibility
                    'endpoints': self._read_extract_file('endpoints.txt'),
                    'params': self._read_extract_file('params.txt'),
                    'domains': self._read_extract_file('domains.txt')
                }
            }
            
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
            self.logger.error(f"Scan failed: {e}", exc_info=True)
            
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
    
    async def _initialize_modules(self):
        """Initializes all scanning modules"""
        from ..modules.fetcher import Fetcher
        from ..modules.processor import Processor
        from ..modules.secret_scanner import SecretScanner
        from ..modules.ast_analyzer import ASTAnalyzer
        from ..modules.crawler import Crawler
        from ..modules.source_map_recovery import SourceMapRecoverer
        
        self.fetcher = Fetcher(self.config, self.logger)
        skip_beautify = self.config.get('skip_beautification', False)
        self.processor = Processor(self.logger, skip_beautification=skip_beautify)
        self.secret_scanner = SecretScanner(self.config, self.logger, self.state, self.notifier)
        self.ast_analyzer = ASTAnalyzer(self.config, self.logger, self.paths)
        self.crawler = Crawler(self.config, self.logger)
        self.source_map_recoverer = SourceMapRecoverer(self.config, self.logger, self.paths)
        
        # Initialize secrets organizer
        self.secret_scanner.initialize_organizer(self.paths['base'])
        
        await self.fetcher.initialize()
    
    async def _discover_all_domains_concurrent(self, inputs: List[str], use_subjs: bool, subjs_only: bool) -> List[str]:
        """
        PHASE 1: Concurrent domain discovery with SubJS and/or Live scanning
        
        Args:
            inputs: List of URLs or domains to scan
            use_subjs: If True, use SubJS for URL discovery
            subjs_only: If True, only use SubJS (skip live browser scan)
            
        Returns:
            List of discovered JavaScript URLs
        """
        all_urls = []
        
        # Initialize SubJS if enabled
        from ..modules.subjs_fetcher import SubJSFetcher
        subjs_fetcher = SubJSFetcher(self.config, self.logger)
        
        # Configure concurrency level
        max_concurrent_domains = self.config.get('max_concurrent_domains', 10)
        semaphore = asyncio.Semaphore(max_concurrent_domains)
        
        self.logger.info(f"🚀 Processing {len(inputs)} domains with concurrency level: {max_concurrent_domains}")
        
        async def discover_one_domain(index: int, item: str) -> List[str]:
            """Discover JS files for a single domain/URL"""
            async with semaphore:
                discovered = []
                
                try:
                    # Check if shutdown was requested
                    if self.shutdown_requested:
                        self.logger.warning("Shutdown requested, stopping input processing")
                        return []
                    
                    # CASE A: It's already a full JS URL (scan immediately)
                    if self._is_valid_js_url(item):
                        self.logger.info(f"[{index+1}/{len(inputs)}] ✓ Direct JS URL: {item}")
                        return [item]
                    
                    # CASE B: It's a Domain/Page URL (needs JS extraction)
                    self.logger.info(f"[{index+1}/{len(inputs)}] 📍 Processing: {item}")
                    
                    # Determine which discovery methods to use
                    tasks = []
                    
                    # SubJS scan
                    if use_subjs or subjs_only:
                        if SubJSFetcher.is_installed():
                            # Get scope domains for filtering
                            scope_domains = self._get_scope_domains() if not self.config.get('no_scope_filter', False) else None
                            tasks.append(('subjs', asyncio.to_thread(subjs_fetcher.fetch_urls, item, scope_domains)))
                        else:
                            self.logger.warning(f"  ⚠️  SubJS not installed, skipping SubJS scan")
                    
                    # Live browser scan (unless subjs_only mode)
                    if not subjs_only and not self.config.get('skip_live', False):
                        tasks.append(('live', self.fetcher.fetch_live(item)))
                    
                    # Execute discovery methods concurrently
                    if tasks:
                        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
                        
                        for i, result in enumerate(results):
                            source_type = tasks[i][0]
                            if isinstance(result, Exception):
                                self.logger.error(f"  ├─ {source_type.capitalize()} scan error: {result}")
                            elif isinstance(result, list):
                                discovered.extend(result)
                                self.logger.info(f"  ├─ {source_type.capitalize()} scan: Found {len(result)} JS files")
                            else:
                                self.logger.warning(f"  ├─ {source_type.capitalize()} scan: Unexpected result type")
                    
                    self.logger.info(f"  └─ Total discovered for {item}: {len(discovered)} JS files")
                    
                except Exception as e:
                    self.logger.error(f"[{index+1}/{len(inputs)}] Error processing {item}: {e}", exc_info=True)
                
                return discovered
        
        # Process all domains concurrently
        tasks = [discover_one_domain(i, item) for i, item in enumerate(inputs)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all URLs
        for result in results:
            if isinstance(result, list):
                all_urls.extend(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Task exception during discovery: {result}")
        
        # Deduplicate URLs
        all_urls = self._deduplicate_urls(all_urls)
        
        self.logger.info(f"{'='*60}")
        self.logger.info(f"📊 Total unique files to process: {len(all_urls)}")
        self.logger.info(f"{'='*60}\n")
        
        # Store source URLs in metadata
        self.state.update_metadata({
            'source_urls': all_urls[:100]  # Store first 100 to avoid bloat
        })
        
        return all_urls
    
    async def _download_all_files(self, urls: List[str]) -> List[dict]:
        """
        PHASE 2: Download all files in parallel
        
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
            'duplicate': 0
        }
        lock = asyncio.Lock()  # For thread-safe counter updates
        
        async def download_one(url: str) -> Optional[dict]:
            nonlocal completed
            async with semaphore:
                try:
                    # Validate URL
                    if not self._is_valid_js_url(url):
                        self.logger.debug(f"Invalid URL: {url}")
                        async with lock:
                            failed_breakdown['invalid_url'] += 1
                        return None
                    
                    if not self._is_target_domain(url):
                        self.logger.debug(f"Out of scope: {url}")
                        async with lock:
                            failed_breakdown['out_of_scope'] += 1
                        return None
                    
                    # Fetch content
                    content = await self.fetcher.fetch_content(url)
                    if not content:
                        async with lock:
                            failed_breakdown['fetch_failed'] += 1
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
                    
                    # Generate filename
                    readable_name = self._get_readable_filename(url, file_hash)
                    
                    # Detect if file is minified
                    is_minified = self._is_minified(content)
                    
                    # Save to appropriate directory based on minification
                    if is_minified:
                        file_path = Path(self.paths['files_minified']) / readable_name
                    else:
                        file_path = Path(self.paths['files_unminified']) / readable_name
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Save manifest
                    self._save_file_manifest(url, file_hash, readable_name)
                    
                    self.stats['total_files'] += 1
                    
                    # Update progress
                    async with lock:
                        completed += 1
                        if completed % 10 == 0 or completed == total_urls:
                            success_count = len(downloaded_files) + 1  # +1 for current
                            self.logger.info(f"🔄 Progress: {completed}/{total_urls} processed, {success_count} downloaded")
                    
                    return {
                        'url': url,
                        'hash': file_hash,
                        'filename': readable_name,
                        'minified_path': str(file_path) if is_minified else None,
                        'unminified_path': str(file_path) if not is_minified else None,
                        'is_minified': is_minified,
                        'content': content
                    }
                
                except Exception as e:
                    # Only log specific error types, not every download failure
                    if 'timeout' in str(e).lower() or 'connection' in str(e).lower():
                        self.logger.debug(f"Network error for {url}: {str(e)}")
                    return None
        
        # Download all files in parallel
        tasks = [download_one(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful downloads
        for result in results:
            if isinstance(result, dict):
                downloaded_files.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Task exception: {result}")
        
        # Show clean summary
        total_filtered = sum(failed_breakdown.values())
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"✅ Downloaded {len(downloaded_files)} files (skipped {total_filtered} invalid/cached)")
        if self.config.get('verbose', False) and total_filtered > 0:
            self.logger.info(f"  Breakdown: {failed_breakdown}")
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
                    self.logger.debug(f"Error recovering source map for {file_info.get('url', 'unknown')}: {e}")
                    return False
        
        # Process all files in parallel
        self.logger.info(f"Processing {len(files)} files for source maps...")
        tasks = [recover_one(file_info) for file_info in files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        if recovered_count > 0:
            self.logger.info(f"✅ Recovered sources from {recovered_count} files")
    
    async def _process_all_files_parallel(self, files: List[dict]):
        """
        PHASE 4: Process all files in parallel (AST analysis on minified files)
        
        Args:
            files: List of file info dictionaries from _download_all_files()
        """
        semaphore = asyncio.Semaphore(self.config.get('threads', 50))
        
        async def process_one(file_info: dict):
            async with semaphore:
                try:
                    content = file_info['content']
                    url = file_info['url']
                    
                    # Run AST analysis on MINIFIED content (faster!)
                    await self.ast_analyzer.analyze(content, url)
                    
                except Exception as e:
                    self.logger.error(f"Processing failed {file_info['url']}: {e}")
        
        tasks = [process_one(f) for f in files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
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
                    self.logger.error(f"Unminify failed {file_info['url']}: {e}")
        
        tasks = [unminify_one(f) for f in files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info(f"✅ Beautified {len(files)} files")
        
        if timeout_count > 0:
            self.logger.info(f"ℹ️  {timeout_count} files timed out during beautification (using original)")
    
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
        Detect if JavaScript file is minified
        
        Args:
            content: JavaScript content
            
        Returns:
            True if file appears to be minified
        """
        # Skip empty files
        if not content or len(content) < 100:
            return False
        
        # Sample first 5000 characters for performance
        sample = content[:5000]
        lines = sample.split('\n')
        
        # Calculate average line length
        if len(lines) < 3:
            # Very few lines suggests minification
            return True
        
        total_chars = sum(len(line) for line in lines)
        avg_line_length = total_chars / len(lines) if lines else 0
        
        # Minified files typically have very long lines (>200 chars average)
        if avg_line_length > 200:
            return True
        
        # Check for common minification patterns
        # - Very long lines (>500 chars)
        # - Lack of whitespace
        # - Few newlines relative to length
        long_lines = sum(1 for line in lines if len(line) > 500)
        newline_ratio = sample.count('\n') / len(sample) if sample else 0
        
        if long_lines > len(lines) * 0.3 or newline_ratio < 0.01:
            return True
        
        return False
    
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
                self.logger.debug(f"Could not read {filename}: {e}")
                return []
        return []
    
    async def _cleanup(self):
        """Cleanup resources"""
        if self.fetcher:
            await self.fetcher.cleanup()
    
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
                # If parsing fails, skip the URL
                self.logger.debug(f"Failed to parse URL {url[:100]}: {e}")
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
        """Check if URL belongs to allowed domains from input file"""
        from urllib.parse import urlparse
        
        try:
            if not url.startswith(('http://', 'https://')):
                return False
            
            domain = urlparse(url).netloc.lower()
            
            # Remove www but keep port
            clean_domain = domain.replace('www.', '')
            
            # Check if domain (with or without port) is in allowed list
            for allowed in self.allowed_domains:
                # Exact match (with port)
                if clean_domain == allowed:
                    return True
                # Match without port
                domain_no_port = clean_domain.split(':')[0] if ':' in clean_domain else clean_domain
                allowed_no_port = allowed.split(':')[0] if ':' in allowed else allowed
                if domain_no_port == allowed_no_port or domain_no_port.endswith('.' + allowed_no_port):
                    return True
            
            return False
        except:
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
    
    def _save_file_manifest(self, url: str, file_hash: str, filename: str):
        """
        Saves file manifest mapping for easy reference
        
        Args:
            url: Source URL
            file_hash: SHA256 hash
            filename: Readable filename
        """
        import json
        from datetime import datetime
        
        manifest_file = Path(self.paths['base']) / 'file_manifest.json'
        
        # Load existing manifest
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = {}
        
        # Add entry
        manifest[filename] = {
            'url': url,
            'hash': file_hash,
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
