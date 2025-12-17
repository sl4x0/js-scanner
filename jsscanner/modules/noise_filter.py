"""
Noise Filter Module
Filters out vendor libraries, CDNs, and analytics scripts
"""
import json
import fnmatch
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional


class NoiseFilter:
    """Filter vendor libraries, CDNs, and analytics scripts"""
    
    def __init__(self, config_path: str = "data/ignored_patterns.json", logger=None):
        """
        Initialize noise filter
        
        Args:
            config_path: Path to ignored patterns configuration
            logger: Logger instance
        """
        self.config_path = Path(config_path)
        self.logger = logger
        self.config = self._load_config()
        self.stats = {
            'filtered_cdn': 0,
            'filtered_pattern': 0,
            'filtered_hash': 0,
            'total_checked': 0
        }
    
    def _load_config(self) -> Dict:
        """Load blacklist configuration"""
        try:
            if not self.config_path.exists():
                if self.logger:
                    self.logger.warning(f"Noise filter config not found: {self.config_path}, using minimal defaults")
                return {
                    'cdn_domains': [],
                    'url_patterns': [],
                    'known_library_hashes': {}
                }
            
            with open(self.config_path, encoding='utf-8') as f:
                config = json.load(f)
                if self.logger:
                    self.logger.info(f"✓ Loaded noise filter: {len(config.get('cdn_domains', []))} CDNs, "
                                   f"{len(config.get('url_patterns', []))} patterns")
                return config
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load noise filter config: {e}")
            return {
                'cdn_domains': [],
                'url_patterns': [],
                'known_library_hashes': {}
            }
    
    def should_skip_url(self, url: str) -> Tuple[bool, str]:
        """
        Check if URL should be skipped based on domain or pattern
        
        Args:
            url: URL to check
            
        Returns:
            (should_skip, reason)
        """
        self.stats['total_checked'] += 1
        
        try:
            # Check CDN domains
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            if domain in self.config.get('cdn_domains', []):
                self.stats['filtered_cdn'] += 1
                return True, f"CDN: {domain}"
            
            # Check URL patterns (case-insensitive)
            url_lower = url.lower()
            for pattern in self.config.get('url_patterns', []):
                if fnmatch.fnmatch(url_lower, pattern.lower()):
                    self.stats['filtered_pattern'] += 1
                    return True, f"Pattern: {pattern}"
            
            return False, ""
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error checking URL {url}: {e}")
            return False, ""
    
    def should_skip_content(self, content: str, filename: str = "") -> Tuple[bool, str]:
        """
        Check if content hash matches known vendor libraries or matches vendor patterns
        
        Args:
            content: File content
            filename: Optional filename for logging
            
        Returns:
            (should_skip, reason)
        """
        try:
            # Calculate content hash (MD5 is fine for deduplication)
            content_hash = hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()
            
            # Check against known library hashes
            known_hashes = self.config.get('known_library_hashes', {})
            for lib_name, lib_hash in known_hashes.items():
                if content_hash == lib_hash:
                    self.stats['filtered_hash'] += 1
                    return True, f"Known library: {lib_name}"
            
            # Heuristic vendor detection
            is_vendor, reason = self._is_likely_vendor_library(content)
            if is_vendor:
                self.stats['filtered_vendor'] += 1  # Count as vendor heuristic
                return True, reason
            
            return False, ""
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error checking content hash: {e}")
            return False, ""
    
    def _is_likely_vendor_library(self, content: str) -> Tuple[bool, str]:
        """
        Detect vendor libraries using heuristic patterns
        
        Args:
            content: File content
            
        Returns:
            (is_vendor, reason)
        """
        try:
            size = len(content)
            newline_count = content.count('\n')
            
            # Large minified files (>50KB) with very few newlines = likely vendor lib
            if size > 50000 and newline_count < 20:
                return True, "Vendor (large minified file)"
            
            # Check for common vendor signatures in first 1000 chars
            header = content[:1000]
            vendor_signatures = [
                ('!function(e,t){"object"==typeof exports', 'UMD pattern'),
                ('/*! jQuery v', 'jQuery'),
                ('/*! Lazy Load', 'Lazy Load'),
                ('* Swiper ', 'Swiper'),
                ('define.amd', 'AMD module'),
                ('React.createElement', 'React'),
                ('Vue.component', 'Vue'),
                ('angular.module', 'Angular'),
                ('/*! Bootstrap v', 'Bootstrap'),
                ('Shopify.theme', 'Shopify theme'),
            ]
            
            for signature, lib_name in vendor_signatures:
                if signature in header:
                    return True, f"Vendor ({lib_name})"
            
            return False, ""
            
        except Exception as e:
            return False, ""
    
    def get_stats(self) -> Dict:
        """Get filtering statistics"""
        total = self.stats['total_checked']
        filtered = sum([
            self.stats['filtered_cdn'],
            self.stats['filtered_pattern'],
            self.stats['filtered_hash']
        ])
        
        return {
            **self.stats,
            'total_filtered': filtered,
            'filter_rate': f"{(filtered/total*100):.1f}%" if total > 0 else "0.0%",
            'passed': total - filtered
        }
    
    def reset_stats(self):
        """Reset filtering statistics"""
        self.stats = {
            'filtered_cdn': 0,
            'filtered_pattern': 0,
            'filtered_hash': 0,
            'total_checked': 0
        }
