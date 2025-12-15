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
            
            # Save minified version
            minified_path = Path(self.paths['files_minified']) / f"{file_hash}.js"
            with open(minified_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Process content (beautify, extract source maps)
            processed_content = await self.processor.process(content, str(minified_path))
            
            # Save unminified version
            unminified_path = Path(self.paths['files_unminified']) / f"{file_hash}.js"
            with open(unminified_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
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
        Reads URLs from input file
        
        Args:
            filepath: Path to input file
            
        Returns:
            List of URLs
        """
        urls = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        return urls
    
    async def _cleanup(self):
        """Cleanup resources"""
        if self.fetcher:
            await self.fetcher.cleanup()
    
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
