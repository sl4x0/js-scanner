"""
Katana Fetcher Module
Handles JavaScript URL discovery using Katana (ProjectDiscovery)
Fast Go-based crawler for breadth-first discovery
"""
import subprocess
import logging
import os
import tempfile
import sys
from typing import List, Set, Optional
from urllib.parse import urlparse
from pathlib import Path


class KatanaFetcher:
    """Fetch JavaScript URLs using Katana crawler (hybrid fast-pass layer)"""

    def __init__(self, config: dict, logger=None):
        """
        Initialize Katana fetcher
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger('jsscanner')
        self.config = config
        
        # Katana configuration with sensible defaults
        katana_config = config.get('katana', {})
        self.enabled = katana_config.get('enabled', False)
        self.depth = katana_config.get('depth', 2)
        self.concurrency = katana_config.get('concurrency', 20)
        self.rate_limit = katana_config.get('rate_limit', 150)
        self.timeout = katana_config.get('timeout', 300)
        self.custom_args = katana_config.get('args', '')
        
        # Detect Katana binary path
        self.katana_path = self._find_katana_binary()

    def _find_katana_binary(self) -> Optional[str]:
        """
        Find Katana binary with cross-platform support
        
        Priority:
        1. Config file path (if specified)
        2. System PATH
        3. Go bin directory
        
        Returns:
            Path to Katana binary or None
        """
        import shutil
        
        # 1. Check config
        config_path = self.config.get('katana', {}).get('binary_path')
        if config_path and Path(config_path).exists():
            return config_path
        
        # 2. Check system PATH
        katana_name = 'katana.exe' if sys.platform == 'win32' else 'katana'
        system_path = shutil.which(katana_name)
        if system_path:
            return system_path
        
        # 3. Check Go bin directory
        go_bin = Path.home() / 'go' / 'bin' / katana_name
        if go_bin.exists():
            return str(go_bin)
        
        return None

    def fetch_urls(self, targets: List[str], scope_domains: Optional[Set[str]] = None) -> List[str]:
        """
        Run Katana on a list of targets (batch mode for maximum speed)
        
        Args:
            targets: List of domains/URLs to crawl
            scope_domains: Set of in-scope domains for filtering
            
        Returns:
            List of discovered JavaScript URLs
        """
        if not self.enabled:
            self.logger.debug("Katana is disabled in configuration")
            return []
        
        if not self.katana_path:
            self.logger.warning("⚠️  Katana binary not found. Install with: go install github.com/projectdiscovery/katana/cmd/katana@latest")
            return []
        
        if not targets:
            return []
        
        self.logger.info(f"⚔️  Katana fast-crawl: Processing {len(targets)} targets (depth: {self.depth}, concurrency: {self.concurrency})")
        
        # Create temp file for batch input
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp:
            # Filter out direct JS URLs (Katana crawls domains, not files)
            crawl_targets = [t for t in targets if not self._is_direct_js_url(t)]
            if not crawl_targets:
                self.logger.debug("No domains to crawl (only direct JS URLs)")
                return []
            
            tmp.write('\n'.join(crawl_targets))
            target_path = tmp.name

        urls = []
        try:
            # Build Katana command
            cmd = [
                self.katana_path,
                '-list', target_path,
                '-d', str(self.depth),
                '-c', str(self.concurrency),
                '-rl', str(self.rate_limit),
                '-silent',  # Clean output
                '-jc',      # JavaScript crawling
                '-kf', 'all',  # Known files (robots.txt, sitemap.xml)
            ]
            
            # Add custom arguments if specified
            if self.custom_args:
                cmd.extend(self.custom_args.split())
            
            self.logger.debug(f"Running: {' '.join(cmd)}")
            
            # Execute Katana with timeout
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=self.timeout
            )

            if process.returncode == 0:
                # Parse output line by line
                for line in process.stdout.splitlines():
                    url = line.strip()
                    # Filter for JS files only
                    if url and self._is_js_url(url):
                        urls.append(url)
                
                self.logger.info(f"  ✓ Katana discovered {len(urls)} JS files")
            else:
                stderr = process.stderr.strip()
                if stderr:
                    # Log only first 200 chars to avoid spam
                    self.logger.warning(f"Katana warning: {stderr[:200]}")

        except subprocess.TimeoutExpired:
            self.logger.warning(f"⚠️  Katana timeout after {self.timeout}s (increase timeout in config if needed)")
        except FileNotFoundError:
            self.logger.error(f"❌ Katana binary not found at {self.katana_path}")
        except Exception as e:
            self.logger.error(f"❌ Katana execution error: {type(e).__name__}: {str(e)}")
        finally:
            # Cleanup temp file
            try:
                if os.path.exists(target_path):
                    os.unlink(target_path)
            except:
                pass

        # Apply scope filtering if requested
        if scope_domains and urls:
            original_count = len(urls)
            urls = self._filter_by_scope(urls, scope_domains)
            filtered_count = original_count - len(urls)
            if filtered_count > 0:
                self.logger.info(f"  ✓ Scope filter: Kept {len(urls)} in-scope, removed {filtered_count} out-of-scope")

        return urls

    def _is_direct_js_url(self, url: str) -> bool:
        """Check if URL is already a direct JS file (not a domain to crawl)"""
        if not url:
            return False
        url_lower = url.lower()
        # Check if it's a full URL ending in .js/.mjs/.ts
        if '.js' in url_lower or '.mjs' in url_lower or '.ts' in url_lower:
            # Make sure it's not just a domain with 'js' in it
            parsed = urlparse(url)
            path = parsed.path.lower()
            return path.endswith(('.js', '.mjs', '.ts', '.jsx', '.tsx'))
        return False

    def _is_js_url(self, url: str) -> bool:
        """
        Check if URL is a JavaScript file
        
        Args:
            url: URL to check
            
        Returns:
            True if URL points to a JS file
        """
        if not url:
            return False
        
        url_lower = url.lower()
        
        # Check file extension
        js_extensions = ['.js', '.mjs', '.jsx', '.ts', '.tsx']
        for ext in js_extensions:
            if ext in url_lower:
                # Verify it's actually a file extension, not just part of domain
                parsed = urlparse(url)
                path = parsed.path.lower()
                if path.endswith(ext) or f'{ext}?' in path or f'{ext}#' in path:
                    return True
        
        return False

    def _filter_by_scope(self, urls: List[str], scope_domains: Set[str]) -> List[str]:
        """
        Keep only in-scope URLs
        
        Args:
            urls: List of URLs to filter
            scope_domains: Set of allowed domains
            
        Returns:
            Filtered list of URLs
        """
        filtered = []
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Remove port if present
                if ':' in domain:
                    domain = domain.split(':')[0]
                
                # Check if domain or any parent domain is in scope
                domain_parts = domain.split('.')
                in_scope = False
                
                # Check all possible domain combinations
                # e.g., for "api.example.com" check: "api.example.com", "example.com"
                for i in range(len(domain_parts)):
                    check_domain = '.'.join(domain_parts[i:])
                    if check_domain in scope_domains:
                        in_scope = True
                        break
                
                if in_scope:
                    filtered.append(url)
                    
            except Exception as e:
                # If parsing fails, skip the URL
                self.logger.debug(f"Failed to parse URL for scope check: {url} ({e})")
                continue
        
        return filtered

    @staticmethod
    def is_installed() -> bool:
        """
        Check if Katana binary is available on the system
        
        Returns:
            True if Katana is installed and accessible
        """
        import shutil
        
        # Check system PATH
        katana_name = 'katana.exe' if sys.platform == 'win32' else 'katana'
        if shutil.which(katana_name):
            return True
        
        # Check Go bin directory
        go_bin = Path.home() / 'go' / 'bin' / katana_name
        if go_bin.exists():
            return True
        
        return False

    def get_version(self) -> Optional[str]:
        """
        Get Katana version
        
        Returns:
            Version string or None if not available
        """
        if not self.katana_path:
            return None
        
        try:
            result = subprocess.run(
                [self.katana_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse version from output
                return result.stdout.strip()
        except:
            pass
        
        return None
