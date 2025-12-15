"""
Crawler Module
Recursive static crawler for deep JS scanning
"""
import re
from typing import List, Set
from urllib.parse import urljoin, urlparse


class Crawler:
    """Recursive crawler for discovering linked JavaScript files"""
    
    def __init__(self, config: dict, logger):
        """
        Initialize crawler
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.max_depth = config.get('recursion', {}).get('max_depth', 3)
        self.visited_urls: Set[str] = set()
    
    async def extract_js_links(self, content: str, base_url: str, current_depth: int = 0) -> List[str]:
        """
        Extracts JavaScript file links from content
        
        Args:
            content: JavaScript content
            base_url: Base URL for resolving relative links
            current_depth: Current recursion depth
            
        Returns:
            List of discovered JavaScript URLs
        """
        if current_depth >= self.max_depth:
            return []
        
        js_urls = set()
        
        # Patterns for finding JS imports/requires
        patterns = [
            # ES6 imports
            r'import\s+.*\s+from\s+["\']([^"\']+)["\']',
            # Dynamic imports
            r'import\(["\']([^"\']+)["\']\)',
            # Require statements
            r'require\(["\']([^"\']+)["\']\)',
            # Script src in strings
            r'src\s*[:=]\s*["\']([^"\']+\.js)["\']',
            # Generic .js references
            r'["\']([^"\']*\.js(?:\?[^"\']*)?)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Skip common non-URL patterns
                if self._should_skip(match):
                    continue
                
                # Convert to absolute URL
                absolute_url = urljoin(base_url, match)
                
                # Only add if it's a valid JS URL and not visited
                if self._is_valid_js_url(absolute_url) and absolute_url not in self.visited_urls:
                    js_urls.add(absolute_url)
                    self.visited_urls.add(absolute_url)
        
        self.logger.info(f"Found {len(js_urls)} linked JS files at depth {current_depth}")
        
        return list(js_urls)
    
    def _should_skip(self, url: str) -> bool:
        """
        Checks if a URL should be skipped
        
        Args:
            url: URL to check
            
        Returns:
            True if should skip, False otherwise
        """
        skip_patterns = [
            # Variables/placeholders
            r'\$\{',
            r'\{\{',
            # Protocol-less or invalid
            r'^//',
            # Too short
            r'^.{1,2}$',
            # Common node modules
            r'^[a-z-]+$',  # Bare module names like 'react', 'lodash'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    def _is_valid_js_url(self, url: str) -> bool:
        """
        Validates if a URL is a proper JavaScript URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            
            # Must have scheme (http/https)
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Must have domain
            if not parsed.netloc:
                return False
            
            # Must end with .js or have .js before query params
            path = parsed.path.lower()
            if not (path.endswith('.js') or '.js?' in url.lower()):
                return False
            
            return True
            
        except Exception:
            return False
    
    def reset(self):
        """Resets the visited URLs set"""
        self.visited_urls.clear()
