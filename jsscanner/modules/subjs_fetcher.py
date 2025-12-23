"""
SubJS Fetcher Module
Handles JavaScript URL discovery using SubJS tool
"""
import subprocess
import logging
import asyncio
from typing import List, Set, Optional
from urllib.parse import urlparse
from ..utils.retry import retry_sync, RETRY_CONFIG_SUBPROCESS


class SubJSFetcher:
    """Fetch JavaScript URLs using SubJS tool"""
    
    def __init__(self, config: dict, logger=None):
        """
        Initialize SubJS fetcher
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger('jsscanner')
        self.config = config
        self.timeout = config.get('subjs', {}).get('timeout', 60)
        self.enabled = config.get('subjs', {}).get('enabled', True)
        
    def fetch_urls(self, target: str, scope_domains: Optional[Set[str]] = None) -> List[str]:
        """Fetch JS URLs for a target using SubJS with retry on subprocess failures"""
        if not self.enabled:
            self.logger.debug("SubJS is disabled in configuration")
            return []
        
        # Get retry config
        retry_config = self.config.get('retry', {})
        max_attempts = retry_config.get('subprocess_calls', 2)
        backoff_base = retry_config.get('backoff_base', 2.0)
        
        # Ensure full URL with protocol
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        self.logger.info(f"🔍 Fetching JS URLs with SubJS for {target}")
        
        # Wrap SubJS call with retry logic
        @retry_sync(
            max_attempts=max_attempts,
            backoff_base=backoff_base,
            retry_on=(subprocess.SubprocessError, subprocess.TimeoutExpired),
            operation_name=f"SubJS({target})"
        )
        def _run_subjs():
            # Run SubJS with full URL
            result = subprocess.run(
                ['subjs'],
                input=target + '\n',
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                # Raise exception to trigger retry
                raise subprocess.SubprocessError(f"SubJS failed: {error_msg}")
            
            return result.stdout
            
        try:
            stdout = _run_subjs()
            
            # Parse output
            urls = []
            for line in stdout.strip().split('\n'):
                url = line.strip()
                if url and self._is_valid_url(url):
                    urls.append(url)
            
            self.logger.info(f"✓ SubJS found {len(urls)} URLs for {target}")
            
            # Apply scope filtering if requested
            if scope_domains is not None:
                filtered_urls = self._filter_by_scope(urls, scope_domains)
                if len(filtered_urls) < len(urls):
                    self.logger.info(
                        f"✓ Filtered to {len(filtered_urls)} in-scope URLs "
                        f"(removed {len(urls) - len(filtered_urls)} out-of-scope)"
                    )
                return filtered_urls
            
            return urls
            
        except FileNotFoundError:
            self.logger.error(
                "❌ SubJS not installed. Install with:\n"
                "   go install -v github.com/lc/subjs@latest"
            )
            return []
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            # All retries exhausted
            self.logger.warning(f"⚠️ SubJS failed after {max_attempts} attempts for {target}")
            return []
        except Exception as e:
            self.logger.error(f"❌ SubJS error for {target}: {str(e)}")
            return []
    
    async def fetch_batch(self, domains: List[str], scope_domains: Optional[Set[str]] = None) -> List[str]:
        """
        Fetch JS URLs for multiple domains concurrently using SubJS
        
        Args:
            domains: List of domains to fetch JS URLs from
            scope_domains: Optional set of in-scope domains for filtering
            
        Returns:
            List of all discovered JavaScript URLs from all domains
        """
        if not self.enabled:
            self.logger.debug("SubJS is disabled in configuration")
            return []
        
        if not domains:
            return []
        
        self.logger.info(f"🔍 Starting SubJS batch discovery for {len(domains)} domains")
        
        # Store all discovered URLs
        all_urls = []
        
        # Create async wrapper for synchronous fetch_urls
        async def fetch_domain(domain: str) -> List[str]:
            """Async wrapper to run fetch_urls in executor"""
            try:
                # Run synchronous fetch_urls in thread pool
                loop = asyncio.get_event_loop()
                urls = await loop.run_in_executor(
                    None, 
                    self.fetch_urls, 
                    domain, 
                    scope_domains
                )
                
                if urls:
                    self.logger.info(f"  ✓ {domain}: Found {len(urls)} JS files")
                else:
                    self.logger.debug(f"  - {domain}: No JS files found")
                    
                return urls
                
            except Exception as e:
                # Handle errors gracefully - one domain failure shouldn't crash the batch
                self.logger.warning(f"  ✗ {domain}: Failed - {str(e)}")
                return []
        
        # Use TaskGroup for structured concurrency (Python 3.11+)
        try:
            async with asyncio.TaskGroup() as tg:
                # Create tasks for all domains
                tasks = [tg.create_task(fetch_domain(domain)) for domain in domains]
            
            # Collect results from all tasks
            for task in tasks:
                try:
                    urls = task.result()
                    all_urls.extend(urls)
                except Exception as e:
                    # TaskGroup should handle exceptions, but just in case
                    self.logger.debug(f"Task result error: {e}")
                    
        except* Exception as eg:
            # Handle ExceptionGroup from TaskGroup
            self.logger.error(f"Critical error in SubJS batch processing: {eg}")
        
        self.logger.info(f"✓ SubJS batch complete: {len(all_urls)} total JS files discovered")
        return all_urls
    
    def fetch_from_file(self, filepath: str, scope_domains: Optional[Set[str]] = None) -> List[str]:
        """
        Fetch JS URLs from a domain list file using SubJS
        
        Args:
            filepath: Path to file with one domain per line
            scope_domains: Set of in-scope domains for filtering
            
        Returns:
            List of all JS URLs found
        """
        if not self.enabled:
            self.logger.debug("SubJS is disabled in configuration")
            return []
            
        try:
            self.logger.info(f"🔍 Fetching JS URLs with SubJS from file: {filepath}")
            
            # Read domains from file and clean them
            domains = []
            with open(filepath, 'r') as f:
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):
                        # Clean domain
                        clean_domain = domain.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
                        domains.append(clean_domain)
            
            if not domains:
                self.logger.warning(f"No valid domains found in {filepath}")
                return []
            
            # Run SubJS with stdin
            domain_input = '\n'.join(domains)
            result = subprocess.run(
                ['subjs'],
                input=domain_input,
                capture_output=True,
                text=True,
                timeout=self.timeout * len(domains)  # Scale timeout by number of domains
            )
            
            if result.returncode != 0:
                self.logger.warning(f"SubJS failed: {result.stderr}")
                return []
            
            # Parse output - one URL per line
            urls = []
            for line in result.stdout.strip().split('\n'):
                url = line.strip()
                if url and (url.startswith('http://') or url.startswith('https://')):
                    urls.append(url)
            
            self.logger.info(f"✓ SubJS found {len(urls)} URLs total from {len(domains)} domains")
            
            # Filter by scope if provided
            if scope_domains:
                urls = self._filter_by_scope(urls, scope_domains)
                self.logger.info(f"✓ Filtered to {len(urls)} in-scope URLs")
            
            return urls
            
        except Exception as e:
            self.logger.error(f"❌ SubJS error: {str(e)}")
            return []
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and starts with http(s)"""
        return url and (url.startswith('http://') or url.startswith('https://'))
    
    def _filter_by_scope(self, urls: List[str], scope_domains: Set[str]) -> List[str]:
        """
        Filter URLs to only include those from in-scope domains
        
        Args:
            urls: List of URLs to filter
            scope_domains: Set of allowed domains (e.g., {'example.com', 'api.example.com'})
            
        Returns:
            Filtered list of URLs
        """
        filtered_urls = []
        
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Remove port if present
                if ':' in domain:
                    domain = domain.split(':')[0]
                
                # Check if domain or any parent domain is in scope
                if self._is_in_scope(domain, scope_domains):
                    filtered_urls.append(url)
                else:
                    self.logger.debug(f"Filtered out-of-scope URL: {url}")
                    
            except Exception as e:
                self.logger.debug(f"Failed to parse URL {url}: {e}")
                continue
        
        return filtered_urls
    
    def _is_in_scope(self, domain: str, scope_domains: Set[str]) -> bool:
        """
        Check if a domain is in scope
        
        Handles subdomains: api.example.com matches if example.com is in scope
        
        Args:
            domain: Domain to check
            scope_domains: Set of allowed domains
            
        Returns:
            True if domain is in scope, False otherwise
        """
        domain = domain.lower()
        
        # Exact match
        if domain in scope_domains:
            return True
        
        # Check parent domains (e.g., api.example.com → example.com)
        parts = domain.split('.')
        for i in range(len(parts)):
            parent = '.'.join(parts[i:])
            if parent in scope_domains:
                return True
        
        return False
    
    @staticmethod
    def is_installed() -> bool:
        """
        Check if SubJS is installed and available
        
        Returns:
            True if SubJS is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ['subjs', '-h'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
