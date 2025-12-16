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
        self.crawler = None
        
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
    
    async def run(self, inputs: List[str], discovery_mode: bool = False):
        """
        Main execution method with BATCH PROCESSING
        
        Args:
            inputs: List of URLs or domains to scan
            discovery_mode: If True, perform active discovery (Wayback + Live crawling).
                          If False, scan only the exact URLs/domains provided.
        """
        self.start_time = time.time()
        
        # Update metadata with start time
        from datetime import datetime
        self.state.update_metadata({
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'discovery_mode': discovery_mode
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
            # PHASE 1: DISCOVERY & URL COLLECTION
            # ============================================================
            self.logger.info(f"\n{'='*60}")
            self.logger.info("📡 PHASE 1: DISCOVERY & URL COLLECTION")
            self.logger.info(f"{'='*60}")
            
            urls_to_scan = []
            
            for item in inputs:
                # Extract domain for scope filtering
                from urllib.parse import urlparse
                try:
                    domain = urlparse(item if item.startswith('http') else f'https://{item}').netloc
                    if domain:
                        self.allowed_domains.add(domain.lower().replace('www.', ''))
                except:
                    pass
                
                # Check if shutdown was requested
                if self.shutdown_requested:
                    self.logger.warning("Shutdown requested, stopping input processing")
                    break
                
                # CASE A: It's already a full JS URL (scan immediately)
                if self._is_valid_js_url(item):
                    self.logger.info(f"✓ Direct JS URL: {item}")
                    urls_to_scan.append(item)
                    continue
                
                # CASE B: It's a Domain/Page URL (needs JS extraction)
                self.logger.info(f"📍 Processing input: {item}")
                
                # Always fetch LIVE JS from this page/domain (unless --no-live)
                if not self.config.get('skip_live', False):
                    live_js = await self.fetcher.fetch_live(item)
                    self.logger.info(f"  ├─ Live scan: Found {len(live_js)} JS files")
                    urls_to_scan.extend(live_js)
                
                # ONLY if Discovery Mode is ON, query Wayback
                if discovery_mode and not self.config.get('skip_wayback', False):
                    wb_js = await self.fetcher.fetch_wayback(item)
                    self.logger.info(f"  └─ Wayback scan: Found {len(wb_js)} JS files")
                    urls_to_scan.extend(wb_js)
                elif discovery_mode:
                    self.logger.info(f"  └─ Wayback scan: Skipped (--no-wayback flag)")
                else:
                    self.logger.info(f"  └─ Wayback scan: Skipped (discovery mode OFF)")
            
            # Deduplicate URLs
            urls_to_scan = self._deduplicate_urls(urls_to_scan)
            
            self.logger.info(f"{'='*60}")
            self.logger.info(f"📊 Total unique files to process: {len(urls_to_scan)}")
            self.logger.info(f"{'='*60}\n")
            
            # Store source URLs in metadata
            self.state.update_metadata({
                'source_urls': urls_to_scan[:100]  # Store first 100 to avoid bloat
            })
            
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
            # PHASE 3: SCANNING FOR SECRETS (TruffleHog)
            # ============================================================
            self.logger.info(f"\n{'='*60}")
            self.logger.info("🔍 PHASE 3: SCANNING FOR SECRETS (TruffleHog)")
            self.logger.info(f"{'='*60}")
            
            # Scan entire minified directory at once
            minified_dir = str(Path(self.paths['files_minified']))
            secrets = await self.secret_scanner.scan_directory(minified_dir)
            self.stats['total_secrets'] = len(secrets)
            
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
            
            # Log detailed failure breakdown
            total_failures = sum(self.stats['failures'].values())
            if total_failures > 0:
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"📊 Failure Breakdown ({total_failures} total):")
                self.logger.info(f"{'='*80}")
                for failure_type, count in self.stats['failures'].items():
                    if count > 0:
                        self.logger.info(f"  {failure_type}: {count}")
                self.logger.info(f"{'='*80}\n")
            
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
                'extracts': {
                    'endpoints': self._read_extract_file('endpoints.txt'),
                    'params': self._read_extract_file('params.txt'),
                    'domains': self._read_extract_file('domains.txt')
                }
            }
            
            json_output = Path(self.paths['base']) / 'scan_results.json'
            with open(json_output, 'w') as f:
                json.dump(results_json, f, indent=2)
            
            self.logger.info(f"📄 Results exported to: {json_output}")
            
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
        
        self.fetcher = Fetcher(self.config, self.logger)
        self.processor = Processor(self.logger)
        self.secret_scanner = SecretScanner(self.config, self.logger, self.state, self.notifier)
        self.ast_analyzer = ASTAnalyzer(self.config, self.logger, self.paths)
        self.crawler = Crawler(self.config, self.logger)
        
        await self.fetcher.initialize()
    
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
        
        async def download_one(url: str) -> Optional[dict]:
            async with semaphore:
                try:
                    # Validate URL
                    if not self._is_valid_js_url(url):
                        self.logger.debug(f"Invalid URL: {url}")
                        return None
                    
                    if not self._is_target_domain(url):
                        self.logger.debug(f"Out of scope: {url}")
                        return None
                    
                    # Fetch content
                    content = await self.fetcher.fetch_content(url)
                    if not content:
                        return None
                    
                    # Calculate hash
                    from ..utils.hashing import calculate_hash
                    file_hash = await calculate_hash(content)
                    
                    # Check if already scanned
                    if not self.state.mark_as_scanned_if_new(file_hash, url):
                        self.logger.debug(f"Duplicate: {url}")
                        self.stats['failures']['duplicates'] += 1
                        return None
                    
                    # Generate filename
                    readable_name = self._get_readable_filename(url, file_hash)
                    
                    # Save minified version
                    minified_path = Path(self.paths['files_minified']) / readable_name
                    with open(minified_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Save manifest
                    self._save_file_manifest(url, file_hash, readable_name)
                    
                    self.stats['total_files'] += 1
                    
                    return {
                        'url': url,
                        'hash': file_hash,
                        'filename': readable_name,
                        'minified_path': str(minified_path),
                        'content': content
                    }
                
                except Exception as e:
                    self.logger.error(f"Download failed {url}: {e}")
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
        
        return downloaded_files
    
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
        
        self.logger.info(f"✅ Processed {len(files)} files")
    
    async def _unminify_all_files(self, files: List[dict]):
        """
        PHASE 5: Beautify all files in parallel
        
        Args:
            files: List of file info dictionaries from _download_all_files()
        """
        semaphore = asyncio.Semaphore(self.config.get('threads', 50))
        
        async def unminify_one(file_info: dict):
            async with semaphore:
                try:
                    content = file_info['content']
                    minified_path = file_info['minified_path']
                    filename = file_info['filename']
                    
                    # Process (beautify)
                    processed = await self.processor.process(content, minified_path)
                    
                    # Save unminified version
                    unminified_path = Path(self.paths['files_unminified']) / filename
                    with open(unminified_path, 'w', encoding='utf-8') as f:
                        f.write(processed)
                    
                except Exception as e:
                    self.logger.error(f"Unminify failed {file_info['url']}: {e}")
        
        tasks = [unminify_one(f) for f in files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info(f"✅ Beautified {len(files)} files")
    
    async def _cleanup_minified_files(self):
        """
        PHASE 6: Delete all minified files to save disk space
        """
        import shutil
        
        minified_dir = Path(self.paths['files_minified'])
        
        if minified_dir.exists():
            file_count = len(list(minified_dir.glob('*')))
            shutil.rmtree(minified_dir)
            minified_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"✅ Deleted {file_count} minified files")
    
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
                    continue
                
                # Check if it looks like a valid domain
                parsed = urlparse(url)
                if not parsed.netloc:
                    invalid_urls.append(url)
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
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Remove www
            clean_domain = domain.replace('www.', '')
            
            # Check if domain or parent domain is in allowed list
            for allowed in self.allowed_domains:
                if clean_domain == allowed or clean_domain.endswith('.' + allowed):
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
            if parsed.path.endswith(('/.js', '/.ts', '/.jsx', '/.tsx', '/.mjs', '/.cts', '/.mts')):  # Empty filename
                return False
            if parsed.path in ('/.js', '/.ts', '/.jsx', '/.tsx', '/.mjs', '/.cts', '/.mts'):
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
            
            # Build final name: domain-filename-hash.js
            final_name = f"{domain}-{filename}-{short_hash}.js"
            
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
