"""
Engine
Main orchestrator that routes input to appropriate modules
"""
import asyncio
import time
from pathlib import Path
from typing import Optional, List
from ..utils.file_ops import FileOps
from ..utils.logger import setup_logger, log_stats
from .state_manager import StateManager
from .notifier import DiscordNotifier


class ScanEngine:
    """Main scanning engine that orchestrates all modules"""
    
    def __init__(self, config: dict, target: str):
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
        self.notifier = DiscordNotifier(webhook_url, rate_limit)
        
        # Modules will be initialized when needed
        self.fetcher = None
        self.processor = None
        self.secret_scanner = None
        self.ast_analyzer = None
        self.crawler = None
        
        # Statistics
        self.start_time = None
        self.stats = {
            'total_files': 0,
            'total_secrets': 0,
            'errors': []
        }
    
    async def run(self, input_file: Optional[str] = None, urls: Optional[List[str]] = None):
        """
        Main execution method
        
        Args:
            input_file: Optional file containing URLs (one per line)
            urls: Optional list of URLs to scan
        """
        self.start_time = time.time()
        
        # Update metadata with start time
        from datetime import datetime
        self.state.update_metadata({
            'start_time': datetime.utcnow().isoformat() + 'Z'
        })
        
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
            
            # Collect URLs to scan
            urls_to_scan = []
            
            if input_file:
                urls_to_scan.extend(await self._read_input_file(input_file))
            
            if urls:
                urls_to_scan.extend(urls)
            
            if not urls_to_scan:
                # No URLs provided, fetch from Wayback and live site
                self.logger.info("No URLs provided, fetching from Wayback and live site")
                urls_to_scan = await self._discover_urls()
            
            # Deduplicate URLs by normalizing (remove query params for comparison)
            urls_to_scan = self._deduplicate_urls(urls_to_scan)
            
            self.logger.info(f"Found {len(urls_to_scan)} URLs to scan")
            
            # Store source URLs in metadata
            self.state.update_metadata({
                'source_urls': urls_to_scan[:100]  # Store first 100 to avoid bloat
            })
            
            # Process each URL
            for url in urls_to_scan:
                await self._process_url(url)
            
            # Final statistics
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
    
    async def _discover_urls(self) -> List[str]:
        """
        Discovers URLs from Wayback and live site
        
        Returns:
            List of discovered URLs
        """
        urls = []
        
        # Fetch from Wayback (unless --no-wayback)
        if not self.config.get('skip_wayback', False):
            wayback_urls = await self.fetcher.fetch_wayback(self.target)
            urls.extend(wayback_urls)
        
        # Fetch from live site (unless --no-live)
        if not self.config.get('skip_live', False):
            live_urls = await self.fetcher.fetch_live(self.target)
            urls.extend(live_urls)
        
        return list(set(urls))  # Remove duplicates
    
    async def _process_url(self, url: str, depth: int = 0):
        """
        Processes a single JavaScript URL
        
        Args:
            url: URL to process
            depth: Current recursion depth
        """
        max_depth = self.config.get('recursion', {}).get('max_depth', 3)
        
        # Check depth limit
        if depth >= max_depth:
            self.logger.debug(f"Max depth {max_depth} reached for {url}")
            return
        
        # Skip third-party domains
        if not self._is_target_domain(url):
            self.logger.debug(f"Skipping third-party domain: {url}")
            return
        
        # Validate URL
        if not self._is_valid_js_url(url):
            self.logger.debug(f"Invalid JS URL: {url}")
            return
        
        try:
            self.logger.info(f"Processing: {url}")
            
            # Fetch content with retry logic
            max_retries = 3
            content = None
            
            for attempt in range(max_retries):
                try:
                    content = await self.fetcher.fetch_content(url)
                    if content:
                        break
                except Exception as e:
                    self.logger.warning(f"Fetch attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    else:
                        self.logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                        self.stats['errors'].append(f"Fetch failed: {url}")
                        return
            
            if not content:
                self.logger.warning(f"Empty content from {url}")
                return
            
            # Calculate hash
            from ..utils.hashing import calculate_hash
            file_hash = await calculate_hash(content)
            
            # Check if already scanned
            if self.state.is_scanned(file_hash):
                self.logger.debug(f"Skipping duplicate: {url}")
                return
            
            # Mark as scanned
            self.state.mark_as_scanned(file_hash, url)
            self.stats['total_files'] += 1
            
            # Generate readable filename
            readable_name = self._get_readable_filename(url, file_hash)
            
            # Save minified version
            minified_path = Path(self.paths['files_minified']) / readable_name
            with open(minified_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Process content (beautify, extract source maps)
            processed_content = await self.processor.process(content, str(minified_path))
            
            # Save unminified version
            unminified_path = Path(self.paths['files_unminified']) / readable_name
            with open(unminified_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            # Save to manifest
            self._save_file_manifest(url, file_hash, readable_name)
            
            # Scan for secrets (streaming)
            secrets_found = await self.secret_scanner.scan_file(str(unminified_path), url)
            self.stats['total_secrets'] += secrets_found
            
            # AST analysis
            await self.ast_analyzer.analyze(processed_content, url)
            
            # Recursive crawling (if enabled)
            if self.config.get('recursion', {}).get('enabled', False):
                linked_urls = await self.crawler.extract_js_links(processed_content, url, depth)
                for linked_url in linked_urls:
                    await self._process_url(linked_url, depth + 1)
            
        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
            self.stats['errors'].append(str(e))
    
    async def _read_input_file(self, filepath: str) -> List[str]:
        """
        Reads URLs/domains from input file
        
        Args:
            filepath: Path to input file
            
        Returns:
            List of URLs to scan
        """
        urls = []
        domains = []
        skipped = 0
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Check if it's a JS URL
                    if '.js' in line.lower() or line.endswith('.mjs'):
                        urls.append(line)
                    # Check if it's a domain (for discovery)
                    elif self._is_valid_domain(line):
                        domains.append(line)
                    else:
                        skipped += 1
        
        # If we found domains, discover JS from them
        if domains:
            self.logger.info(f"Found {len(domains)} domains in input file, discovering JS URLs...")
            for domain in domains:
                discovered_urls = await self._discover_urls_for_domain(domain)
                urls.extend(discovered_urls)
        
        if skipped > 0:
            self.logger.info(f"Skipped {skipped} invalid lines from input file")
        
        return urls
    
    def _is_valid_domain(self, line: str) -> bool:
        """
        Check if line is a valid domain
        
        Args:
            line: Line to check
            
        Returns:
            True if valid domain
        """
        # Simple domain validation
        if line.startswith(('http://', 'https://')):
            return False  # This is a URL, not a domain
        
        # Check for domain pattern
        import re
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        return bool(re.match(domain_pattern, line))
    
    async def _discover_urls_for_domain(self, domain: str) -> List[str]:
        """
        Discover JS URLs for a specific domain
        
        Args:
            domain: Domain to discover
            
        Returns:
            List of discovered JS URLs
        """
        urls = []
        
        # Fetch from Wayback (unless --no-wayback)
        if not self.config.get('skip_wayback', False):
            wayback_urls = await self.fetcher.fetch_wayback(domain)
            urls.extend(wayback_urls)
        
        # Fetch from live site (unless --no-live)
        if not self.config.get('skip_live', False):
            live_urls = await self.fetcher.fetch_live(domain)
            urls.extend(live_urls)
        
        return list(set(urls))  # Remove duplicates
    
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
        
        for url in urls:
            try:
                parsed = urlparse(url)
                # Create base URL without query params
                base_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                
                # Keep the URL, prefer one without query params
                if base_url not in unique_urls:
                    unique_urls[base_url] = url
                else:
                    # If current URL has no query params, prefer it
                    if not parsed.query and '?' in unique_urls[base_url]:
                        unique_urls[base_url] = url
                        
            except Exception:
                # If parsing fails, keep the URL as-is
                unique_urls[url] = url
        
        original_count = len(urls)
        deduplicated = list(unique_urls.values())
        
        if original_count > len(deduplicated):
            self.logger.info(f"Deduplicated {original_count} URLs to {len(deduplicated)} unique files (removed {original_count - len(deduplicated)} duplicates)")
        
        return deduplicated
    
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
        """
        Checks if URL belongs to target domain or subdomain
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from target domain/subdomain
        """
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Remove www. prefix for comparison
            domain = domain.replace('www.', '')
            
            # Check if exact match or subdomain
            target_lower = self.target.lower()
            
            # Remove protocol from target if present
            target_lower = target_lower.replace('https://', '').replace('http://', '')
            # Remove www. prefix from target
            target_lower = target_lower.replace('www.', '')
            
            # Check if it's the target domain or a subdomain
            if domain == target_lower:
                return True
            if domain.endswith('.' + target_lower):
                return True
                
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def _is_valid_js_url(url: str) -> bool:
        """
        Validates if URL is a valid JS file
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid JS URL
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
            if parsed.path.endswith('/.js'):  # Empty filename
                return False
            if parsed.path == '/.js':
                return False
                
            # Must be JS file
            path_lower = parsed.path.lower()
            if not ('.js' in path_lower or parsed.path.endswith('.mjs')):
                return False
                
            return True
            
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
            
            # Remove file extension
            filename = filename.replace('.js', '').replace('.mjs', '')
            
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
