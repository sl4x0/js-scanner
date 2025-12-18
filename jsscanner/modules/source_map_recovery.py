"""
Source Map Recovery Module
Downloads and extracts original source code from source maps
"""
import json
import aiohttp
import asyncio
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
import re
from ..utils.retry import retry_async, RETRY_CONFIG_LIGHT


class SourceMapRecoverer:
    """Recovers original source code from source maps"""

    def __init__(self, config: dict, logger, paths: dict):
        """
        Initialize source map recoverer

        Args:
            config: Configuration dictionary
            logger: Logger instance
            paths: Result paths dictionary
        """
        self.config = config
        self.logger = logger
        self.paths = paths
        self.stats = {
            'maps_found': 0,
            'maps_downloaded': 0,
            'sources_recovered': 0,
            'errors': 0
        }

    async def recover_from_file(self, js_url: str, js_content: str) -> Optional[Dict[str, str]]:
        """
        Attempt to recover source map for a JS file

        Args:
            js_url: URL of the JavaScript file
            js_content: Content of the JavaScript file

        Returns:
            Dictionary mapping source paths to source content, or None
        """
        try:
            # Find source map URL
            map_url = self._find_map_url(js_content, js_url)
            if not map_url:
                return None

            self.stats['maps_found'] += 1
            self.logger.info(f"🗺️  Found source map: {map_url}")

            # Download source map
            map_content = await self._fetch_map(map_url)
            if not map_content:
                self.stats['errors'] += 1
                return None

            self.stats['maps_downloaded'] += 1

            # Parse and extract sources
            sources = await self._extract_sources(map_content, map_url)
            if sources:
                self.stats['sources_recovered'] += len(sources)
                self.logger.info(f"✅ Recovered {len(sources)} source files from map")
                return sources

            return None

        except Exception as e:
            self.logger.debug(f"Source map recovery failed for {js_url}: {e}")
            self.stats['errors'] += 1
            return None

    def _find_map_url(self, content: str, base_url: str) -> Optional[str]:
        """
        Find source map URL from JS file content

        Args:
            content: JavaScript file content
            base_url: Base URL for resolving relative paths

        Returns:
            Absolute URL to source map, or None
        """
        # Look for sourceMappingURL comment (usually at end of file)
        # Format: //# sourceMappingURL=app.js.map
        patterns = [
            r'//[@#]\s*sourceMappingURL=(.+)',
            r'/\*[@#]\s*sourceMappingURL=(.+)\s*\*/'
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                map_path = match.group(1).strip()
                
                # Handle inline source maps (data:)
                if map_path.startswith('data:'):
                    return map_path
                
                # Resolve relative URL
                return urljoin(base_url, map_path)

        return None

    async def _fetch_map(self, map_url: str) -> Optional[str]:
        """
        Download source map file with retry on failures.
        Uses lighter retry config (2 attempts) since maps are optional.

        Args:
            map_url: URL of source map

        Returns:
            Source map content, or None
        """
        # Get retry config
        retry_config = self.config.get('retry', {})
        max_attempts = retry_config.get('http_requests', 3)
        # Use lighter retry for source maps (optional resources)
        max_attempts = min(max_attempts, 2)
        backoff_base = retry_config.get('backoff_base', 0.5)
        
        # Define retry wrapper
        @retry_async(
            max_attempts=max_attempts,
            backoff_base=backoff_base,
            retry_on=(asyncio.TimeoutError, aiohttp.ClientError),
            operation_name=f"fetch_map({map_url[:50]}...)"
        )
        async def _do_fetch_map():
            # Handle inline maps (data: URLs)
            if map_url.startswith('data:'):
                # Extract base64 data
                import base64
                if 'base64,' in map_url:
                    data = map_url.split('base64,')[1]
                    return base64.b64decode(data).decode('utf-8')
                else:
                    # URL-encoded JSON
                    from urllib.parse import unquote
                    return unquote(map_url.split('data:application/json,')[1])

            # Download external map
            async with aiohttp.ClientSession() as session:
                async with session.get(map_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        # Non-200 status - don't retry
                        self.logger.debug(f"Failed to fetch map (HTTP {response.status}): {map_url}")
                        return None
        
        try:
            return await _do_fetch_map()
        except (asyncio.TimeoutError, aiohttp.ClientError):
            self.logger.debug(f"Source map fetch failed after retries: {map_url}")
            return None
        except Exception as e:
            self.logger.debug(f"Error fetching map {map_url}: {e}")
            return None

    async def _extract_sources(self, map_content: str, map_url: str) -> Dict[str, str]:
        """
        Extract source files from source map

        Args:
            map_content: Source map JSON content
            map_url: URL of the source map (for resolving relative paths)

        Returns:
            Dictionary mapping source paths to source content
        """
        try:
            source_map = json.loads(map_content)
            sources = {}

            # Get source paths
            source_paths = source_map.get('sources', [])
            sources_content = source_map.get('sourcesContent', [])

            # Check if sources are embedded
            if sources_content:
                # Embedded sources (common in modern builds)
                for i, source_path in enumerate(source_paths):
                    if i < len(sources_content) and sources_content[i]:
                        # Clean path for filesystem
                        clean_path = self._clean_source_path(source_path)
                        sources[clean_path] = sources_content[i]
            else:
                # Sources need to be fetched separately
                self.logger.debug(f"Source map requires fetching {len(source_paths)} source files")
                
                # Fetch first 10 sources (limit to avoid overwhelming servers)
                for source_path in source_paths[:10]:
                    source_url = urljoin(map_url, source_path)
                    source_content = await self._fetch_source(source_url)
                    if source_content:
                        clean_path = self._clean_source_path(source_path)
                        sources[clean_path] = source_content

            return sources

        except json.JSONDecodeError as e:
            self.logger.debug(f"Invalid source map JSON: {e}")
            return {}
        except Exception as e:
            self.logger.debug(f"Error extracting sources: {e}")
            return {}

    async def _fetch_source(self, source_url: str) -> Optional[str]:
        """
        Fetch a single source file with retry on failures.
        Uses lighter retry config (2 attempts) since individual sources are optional.
        """
        # Get retry config
        retry_config = self.config.get('retry', {})
        max_attempts = min(retry_config.get('http_requests', 3), 2)  # Max 2 attempts
        backoff_base = retry_config.get('backoff_base', 0.5)
        
        @retry_async(
            max_attempts=max_attempts,
            backoff_base=backoff_base,
            retry_on=(asyncio.TimeoutError, aiohttp.ClientError),
            operation_name=f"fetch_source({source_url[:40]}...)"
        )
        async def _do_fetch_source():
            async with aiohttp.ClientSession() as session:
                async with session.get(source_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        
        try:
            return await _do_fetch_source()
        except Exception:
            return None

    @staticmethod
    def _clean_source_path(path: str) -> str:
        """
        Clean source path for filesystem storage

        Args:
            path: Original source path from source map

        Returns:
            Cleaned path safe for filesystem
        """
        # Remove webpack:/// and other prefixes
        path = re.sub(r'^webpack:///', '', path)
        path = re.sub(r'^\.\/', '', path)
        path = re.sub(r'^/', '', path)
        
        # Replace path separators with underscores
        path = path.replace('/', '_').replace('\\', '_')
        
        # Remove invalid filename characters
        path = re.sub(r'[<>:"|?*]', '_', path)
        
        # Limit length
        if len(path) > 200:
            path = path[:200]
        
        return path

    async def save_sources(self, url: str, sources: Dict[str, str]) -> None:
        """
        Save recovered sources to disk

        Args:
            url: Original JS file URL (for organizing output)
            sources: Dictionary of source path -> content
        """
        # Create source_code directory
        source_dir = Path(self.paths['base']) / 'source_code'
        source_dir.mkdir(exist_ok=True)

        # Get domain from URL
        domain = urlparse(url).netloc
        domain_dir = source_dir / domain
        domain_dir.mkdir(exist_ok=True)

        # Save each source file
        for source_path, content in sources.items():
            try:
                output_file = domain_dir / source_path
                
                # Create parent directories if needed
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.debug(f"Saved source: {output_file}")
            except Exception as e:
                self.logger.debug(f"Failed to save {source_path}: {e}")

    def get_stats(self) -> Dict:
        """Get recovery statistics"""
        return {
            **self.stats,
            'recovery_rate': f"{(self.stats['maps_downloaded']/self.stats['maps_found']*100):.1f}%"
            if self.stats['maps_found'] > 0 else "0.0%"
        }
