"""
Engine
Main orchestrator that routes input to appropriate modules
"""
import asyncio
import aiohttp
import time
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
            
            # Log sample URLs for debugging
            if urls_to_scan and len(urls_to_scan) > 0:
                self.logger.debug(f"Sample URLs: {urls_to_scan[:3]}")
            
            # Store source URLs in metadata
            self.state.update_metadata({
                'source_urls': urls_to_scan[:100]  # Store first 100 to avoid bloat
            })
            
            # Process each URL with progress indicator
            total_urls = len(urls_to_scan)
            for idx, url in enumerate(urls_to_scan, 1):
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"📍 [{idx}/{total_urls}] Processing: {url}")
                self.logger.info(f"{'='*80}")
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
            self.logger.warning(f"Invalid JS URL rejected: {url}")
            return
        
        try:
            # Fetch content with retry logic
            max_retries = 3
            content = None
            
            for attempt in range(max_retries):
                try:
                    content = await self.fetcher.fetch_content(url)
                    if content:
                        if attempt > 0:
                            self.logger.info(f"✓ Fetch successful on attempt {attempt + 1}/{max_retries}")
                        else:
                            self.logger.info(f"✓ Fetch successful")
                        break
                except asyncio.TimeoutError as e:
                    self.logger.warning(
                        f"⚠️  Attempt {attempt + 1}/{max_retries} timed out\n"
                        f"   URL: {url}\n"
                        f"   Error: {str(e)[:100]}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                except (aiohttp.ClientError, aiohttp.ClientConnectorError) as e:
                    self.logger.warning(
                        f"⚠️  Attempt {attempt + 1}/{max_retries} failed\n"
                        f"   Error: {str(e)[:100]}\n"
                        f"   Type: {type(e).__name__}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    self.logger.error(
                        f"⚠️  Unexpected error on attempt {attempt + 1}/{max_retries}\n"
                        f"   Error: {str(e)[:100]}\n"
                        f"   Type: {type(e).__name__}",
                        exc_info=True
                    )
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
            
            # Check if already scanned (atomic operation to prevent race condition)
            if not self.state.mark_as_scanned_if_new(file_hash, url):
                self.logger.debug(f"Skipping duplicate: {url}")
                return
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
            
        except ValueError as e:
            self.logger.error(f"Invalid data while processing {url}: {e}", exc_info=True)
            self.stats['errors'].append(f"ValueError: {str(e)}")
        except IOError as e:
            self.logger.error(f"File I/O error processing {url}: {e}", exc_info=True)
            self.stats['errors'].append(f"IOError: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing {url}: {e}", exc_info=True)
            self.stats['errors'].append(f"Unexpected: {str(e)}")
            raise  # Re-raise for debugging
    
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
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
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
        except (UnicodeDecodeError, IOError) as e:
            self.logger.error(f"Failed to read input file {filepath}: {e}")
            return []
        
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
        invalid_urls = []
        
        for url in urls:
            try:
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
                if not parsed.netloc or not parsed.path:
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
                self.logger.debug(f\"Failed to parse URL {url[:100]}: {e}\")
                invalid_urls.append(url)
        
        if invalid_urls:
            self.logger.warning(f\"Filtered out {len(invalid_urls)} invalid URLs\")
        
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
        Strictly checks if URL belongs to target domain or subdomain
        Rejects all third-party domains, blob URLs, data URLs, etc.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from target domain/subdomain ONLY
        """
        from urllib.parse import urlparse
        
        try:
            # Reject non-HTTP schemes immediately
            if not url.startswith(('http://', 'https://')):
                self.logger.debug(f"[SCOPE] Rejected non-HTTP URL: {url}")
                return False
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Must have a domain
            if not domain:
                return False
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Extract root domain (last 2 parts)
            # e.g., subdomain.powerschool.com -> powerschool.com
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                root_domain = '.'.join(domain_parts[-2:])
            else:
                root_domain = domain
            
            # Get target root domain
            target_lower = self.target.lower()
            target_lower = target_lower.replace('https://', '').replace('http://', '')
            target_lower = target_lower.replace('www.', '')
            
            target_parts = target_lower.split('.')
            if len(target_parts) >= 2:
                target_root = '.'.join(target_parts[-2:])
            else:
                target_root = target_lower
            
            # Strict match: root domains must be identical
            if root_domain == target_root:
                return True
            
            # Log rejection for visibility
            if root_domain != target_root:
                self.logger.debug(f"[SCOPE] Rejected third-party: {domain} (target: {target_root})")
            
            return False
            
        except Exception as e:
            self.logger.debug(f"[SCOPE] Parse error for {url}: {e}")
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
                
            # Must be JS file (.js, .mjs, or .js with query params)
            path_lower = parsed.path.lower()
            full_url_lower = url.lower()
            
            if (path_lower.endswith('.js') or 
                path_lower.endswith('.mjs') or 
                '.js?' in full_url_lower or
                '.js#' in full_url_lower):
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
