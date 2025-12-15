"""
Engine
Main orchestrator that routes input to appropriate modules
"""
import asyncio
import aiohttp
import json
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
        self.notifier = DiscordNotifier(webhook_url, rate_limit, self.logger)
        
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
    
    async def run(self, inputs: List[str], discovery_mode: bool = False):
        """
        Main execution method
        
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
            
            # === NEW: Process inputs based on discovery mode ===
            urls_to_scan = []
            
            for item in inputs:
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
            
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"📊 Total unique JavaScript files to scan: {len(urls_to_scan)}")
            self.logger.info(f"{'='*80}\n")
            
            # Log sample URLs for debugging
            if urls_to_scan and len(urls_to_scan) > 0:
                self.logger.debug(f"Sample URLs: {urls_to_scan[:3]}")
            
            # Store source URLs in metadata
            self.state.update_metadata({
                'source_urls': urls_to_scan[:100]  # Store first 100 to avoid bloat
            })
            
            # Process each URL with progress indicator and ETA
            total_urls = len(urls_to_scan)
            file_start_time = time.time()
            
            for idx, url in enumerate(urls_to_scan, 1):
                # Calculate progress percentage
                progress = (idx / total_urls) * 100
                
                # Calculate ETA (after processing at least 3 files)
                eta_str = ""
                if idx > 3:
                    elapsed = time.time() - file_start_time
                    avg_time_per_file = elapsed / (idx - 1)
                    remaining_files = total_urls - idx
                    eta_seconds = avg_time_per_file * remaining_files
                    
                    if eta_seconds < 60:
                        eta_str = f" | ETA: {int(eta_seconds)}s"
                    elif eta_seconds < 3600:
                        eta_str = f" | ETA: {int(eta_seconds / 60)}m {int(eta_seconds % 60)}s"
                    else:
                        hours = int(eta_seconds / 3600)
                        minutes = int((eta_seconds % 3600) / 60)
                        eta_str = f" | ETA: {hours}h {minutes}m"
                
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"📍 [{idx}/{total_urls}] ({progress:.1f}%){eta_str} Processing: {url}")
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
            
            # Extract root domain using helper method (handles multi-part TLDs)
            root_domain = self._extract_root_domain(domain)
            
            # Get target root domain
            target_lower = self.target.lower()
            target_lower = target_lower.replace('https://', '').replace('http://', '')
            target_lower = target_lower.replace('www.', '')
            
            # Extract target root domain using helper method
            target_root = self._extract_root_domain(target_lower)
            
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
