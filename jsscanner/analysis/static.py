"""
AST Analyzer Module
Uses Tree-sitter to parse JavaScript and extract endpoints, domains, and links
"""
import asyncio
import re
from tree_sitter import Parser
from typing import List, Set, Dict, Any
from pathlib import Path
from ..utils.fs import FileSystem
from .organizer import DomainExtractOrganizer


class StaticAnalyzer:
    """Analyzes JavaScript using AST parsing"""
    
    def __init__(self, config: dict, logger, paths: dict) -> None:
        """
        Initialize AST analyzer
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            paths: Dictionary of result paths
        """
        self.config = config
        self.logger = logger
        self.paths = paths
        self._tree_sitter_warning_logged = False  # Only warn once
        
        # Configurable max file size for AST parsing (default 15MB)
        self.max_file_size = config.get('ast', {}).get('max_file_size_mb', 15) * 1024 * 1024
        
        # Track sources for each extract
        self.extracts_db = {
            'endpoints': {},  # {endpoint: {sources: [], total_count: 0, domains: set()}}
            'domains': {},
            'links': {}
        }
        
        # Initialize domain organizer for new directory structure
        self.domain_organizer = DomainExtractOrganizer(paths['extracts'], logger)
        
        # Initialize Tree-sitter parser
        try:
            import tree_sitter_javascript as tsjavascript
            import tree_sitter
            from tree_sitter import Parser, Language
            
            # Get the language capsule
            JS_LANGUAGE = tsjavascript.language()
            
            # Try to get version for logging
            try:
                from importlib.metadata import version
                version_str = version('tree-sitter')
            except:
                try:
                    version_str = tree_sitter.__version__
                except AttributeError:
                    version_str = "unknown"
            
            # Try different API patterns (version-agnostic approach)
            parser_initialized = False
            last_error = None
            
            # Method 1: Try Language wrapper + Parser (v0.22 recommended)
            if not parser_initialized:
                try:
                    wrapped_language = Language(JS_LANGUAGE)
                    self.parser = Parser()
                    self.parser.set_language(wrapped_language)
                    self.logger.info(f"✓ Tree-sitter initialized (v{version_str}, Language wrapper API)")
                    parser_initialized = True
                except Exception as e:
                    last_error = f"Method 1 failed: {e}"
            
            # Method 2: Try old set_language API directly (v0.20-0.21)
            if not parser_initialized:
                try:
                    self.parser = Parser()
                    self.parser.set_language(JS_LANGUAGE)
                    self.logger.info(f"✓ Tree-sitter initialized (v{version_str}, direct set_language API)")
                    parser_initialized = True
                except Exception as e:
                    last_error = f"Method 2 failed: {e}"
            
            # Method 3: Try Parser() with language capsule directly (v0.23+)
            if not parser_initialized:
                try:
                    self.parser = Parser(JS_LANGUAGE)
                    self.logger.info(f"✓ Tree-sitter initialized (v{version_str}, direct capsule API)")
                    parser_initialized = True
                except Exception as e:
                    last_error = f"Method 3 failed: {e}"
            
            if not parser_initialized:
                error_details = f"All initialization methods failed. Last error: {last_error}"
                self.logger.error(f"Tree-sitter initialization failed: {error_details}")
                self.logger.error(f"  tree-sitter version: {version_str}")
                self.logger.error(f"  tree-sitter-javascript installed: {hasattr(tsjavascript, 'language')}")
                self.logger.error(f"  Language capsule type: {type(JS_LANGUAGE)}")
                raise RuntimeError(error_details)
                
        except Exception as e:
            # More explicit warning and guidance for users
            self.logger.warning(
                f"⚠️  Tree-sitter initialization skipped: {e}\n"
                "   Falling back to regex-based parsing.\n"
                "   To enable full AST parsing, install: pip install tree-sitter tree-sitter-javascript\n"
                "   Impact: ~20-30% slower parsing and reduced accuracy for complex patterns."
            )
            self.parser = None
    
    async def analyze(self, content: str, source_url: str):
        """
        Analyzes JavaScript content using AST (tree-sitter required)
        
        Args:
            content: JavaScript content
            source_url: Source URL
        """
        if not self.parser:
            # Use regex-based fallback extraction with a single warning
            if not self._tree_sitter_warning_logged:
                self.logger.warning(
                    "⚠️  Tree-sitter not available. Using regex fallback for analysis.\n"
                    "   Install tree-sitter & tree-sitter-javascript for best results: pip install tree-sitter tree-sitter-javascript\n"
                    "   Impact: ~20-30% slower and less precise AST extraction."
                )
                self._tree_sitter_warning_logged = True

            try:
                # Simple regex-based extraction alternatives
                links = await self._extract_links(content)
                domains = await self._extract_domains(content)
                cloud_assets = await self._extract_cloud_assets(content)

                # Basic endpoint detection using heuristics (regex search for /api/ or /v1/ etc.)
                endpoint_candidates = set()
                for m in re.findall(r'(["\'](?:/[^"\']*(?:/api/|/v\d/)[^"\']*)["\'])', content, re.IGNORECASE):
                    cleaned = m.strip('"\'')
                    if self._is_endpoint(cleaned):
                        endpoint_candidates.add(cleaned)

                endpoints = list(endpoint_candidates)

                # Save extracts similarly to AST path (legacy files)
                extracts_path = Path(self.paths['extracts'])
                if endpoints:
                    await FileSystem.append_unique_lines(str(extracts_path / 'endpoints.txt'), endpoints)
                if links:
                    await FileSystem.append_unique_lines(str(extracts_path / 'links.txt'), links)
                if domains:
                    await FileSystem.append_unique_lines(str(extracts_path / 'domains.txt'), domains)
                if cloud_assets:
                    await FileSystem.append_unique_lines(str(extracts_path / 'cloud_assets.txt'), cloud_assets)

                # Update internal DB summaries
                for endpoint in endpoints:
                    if endpoint not in self.extracts_db['endpoints']:
                        self.extracts_db['endpoints'][endpoint] = {'sources': [], 'total_count': 0, 'domains': set()}
                    self.extracts_db['endpoints'][endpoint]['sources'].append({'file': source_url, 'domain': 'unknown', 'occurrences': 1})
                    self.extracts_db['endpoints'][endpoint]['total_count'] += 1

                for domain in domains:
                    if domain not in self.extracts_db['domains']:
                        self.extracts_db['domains'][domain] = {'sources': [], 'total_count': 0, 'domains': set()}
                    self.extracts_db['domains'][domain]['sources'].append({'file': source_url, 'domain': 'unknown', 'occurrences': 1})
                    self.extracts_db['domains'][domain]['total_count'] += 1

                self.logger.debug(f"Regex fallback extracted: {len(endpoints)} endpoints, {len(domains)} domains, {len(links)} links, {len(cloud_assets)} cloud assets")
                return
            except Exception as e:
                self.logger.error(f"Regex fallback analysis failed: {e}")
                return
        
        try:
            # Parse content in executor to avoid blocking event loop (CPU-bound)
            loop = asyncio.get_event_loop()
            tree = await loop.run_in_executor(None, self._parse_content, content)
            root_node = tree.root_node
            
            # Extract various elements (run in executor since they traverse large ASTs)
            endpoints = await loop.run_in_executor(None, self._extract_endpoints_sync, root_node, content)
            links = await self._extract_links(content)
            domains = await self._extract_domains(content)
            
            # NEW: Extract cloud assets (S3, Azure, GCS, Firebase) in same pass
            cloud_assets = await self._extract_cloud_assets(content)
            
            # NEW: Extract dynamic imports if enabled
            code_splitting_config = self.config.get('code_splitting', {})
            if code_splitting_config.get('detect_dynamic_imports', True):
                await self.extract_and_save_dynamic_imports(content, source_url)
            
            # Extract domain from source URL for tracking
            from urllib.parse import urlparse
            try:
                source_domain = urlparse(source_url).netloc.replace('www.', '')
            except:
                source_domain = 'unknown'
            
            # Track sources in extracts_db
            from collections import Counter
            for endpoint in endpoints:
                if endpoint not in self.extracts_db['endpoints']:
                    self.extracts_db['endpoints'][endpoint] = {
                        'sources': [],
                        'total_count': 0,
                        'domains': set()
                    }
                self.extracts_db['endpoints'][endpoint]['sources'].append({
                    'file': source_url,
                    'domain': source_domain,
                    'occurrences': 1
                })
                self.extracts_db['endpoints'][endpoint]['total_count'] += 1
                self.extracts_db['endpoints'][endpoint]['domains'].add(source_domain)
            
            for domain in domains:
                if domain not in self.extracts_db['domains']:
                    self.extracts_db['domains'][domain] = {
                        'sources': [],
                        'total_count': 0,
                        'domains': set()
                    }
                self.extracts_db['domains'][domain]['sources'].append({
                    'file': source_url,
                    'domain': source_domain,
                    'occurrences': 1
                })
                self.extracts_db['domains'][domain]['total_count'] += 1
                self.extracts_db['domains'][domain]['domains'].add(source_domain)
            
            for link in links:
                if link not in self.extracts_db['links']:
                    self.extracts_db['links'][link] = {
                        'sources': [],
                        'total_count': 0,
                        'domains': set()
                    }
                self.extracts_db['links'][link]['sources'].append({
                    'file': source_url,
                    'domain': source_domain,
                    'occurrences': 1
                })
                self.extracts_db['links'][link]['total_count'] += 1
                self.extracts_db['links'][link]['domains'].add(source_domain)
            
            # NEW: Track cloud assets
            for asset in cloud_assets:
                if asset not in self.extracts_db.get('cloud_assets', {}):
                    if 'cloud_assets' not in self.extracts_db:
                        self.extracts_db['cloud_assets'] = {}
                    self.extracts_db['cloud_assets'][asset] = {
                        'sources': [],
                        'total_count': 0,
                        'domains': set()
                    }
                self.extracts_db['cloud_assets'][asset]['sources'].append({
                    'file': source_url,
                    'domain': source_domain,
                    'occurrences': 1
                })
                self.extracts_db['cloud_assets'][asset]['total_count'] += 1
                self.extracts_db['cloud_assets'][asset]['domains'].add(source_domain)
            
            # Save extracts to files (for backwards compatibility)
            extracts_path = Path(self.paths['extracts'])
            
            if endpoints:
                await FileSystem.append_unique_lines(
                    str(extracts_path / 'endpoints.txt'),
                    endpoints
                )
            
            if links:
                await FileSystem.append_unique_lines(
                    str(extracts_path / 'links.txt'),
                    links
                )
            
            if domains:
                await FileSystem.append_unique_lines(
                    str(extracts_path / 'domains.txt'),
                    domains
                )
            
            # NEW: Save cloud assets
            if cloud_assets:
                await FileSystem.append_unique_lines(
                    str(extracts_path / 'cloud_assets.txt'),
                    cloud_assets
                )
            
            self.logger.debug(
                f"Extracted: {len(endpoints)} endpoints, {len(domains)} domains, {len(links)} links, {len(cloud_assets)} cloud assets"
            )
            
        except Exception as e:
            self.logger.error(f"AST analysis failed: {e}")
            # No fallback - tree-sitter is required
        finally:
            # Issue #6: Explicit cleanup to prevent memory leaks
            if 'tree' in locals():
                del tree
            if 'root_node' in locals():
                del root_node
    
    def _parse_content(self, content: str):
        """Synchronous tree-sitter parsing (CPU-bound)"""
        # Prevent memory issues with very large files
        max_size_mb = self.max_file_size / (1024 * 1024)
        if len(content) > self.max_file_size:
            self.logger.warning(f"Skipping AST parsing for file >{max_size_mb:.0f}MB (too large)")
            raise ValueError("File too large for AST parsing")
        
        # Skip empty or nearly empty files
        if len(content) < 10:  # Less than 10 bytes
            self.logger.debug(f"Skipping AST parsing for file <10 bytes (too small)")
            raise ValueError("File too small for meaningful AST parsing")
        
        tree = self.parser.parse(bytes(content, 'utf8'))
        
        # Issue #6: Validate parsed tree
        if not tree or not tree.root_node:
            raise ValueError("Failed to parse JavaScript")
        
        return tree
    
    def _get_string_value(self, node, content: str) -> str:
        """
        Get the string value from a node, or return 'EXPR' if it's a dynamic expression
        
        Args:
            node: AST node
            content: Source code content
            
        Returns:
            String value or 'EXPR' for dynamic expressions
        """
        if node is None:
            return 'EXPR'
        
        # String literals
        if node.type == 'string':
            return content[node.start_byte:node.end_byte].strip('"\'')
        
        # Template strings - replace ${...} with EXPR
        if node.type == 'template_string':
            text = content[node.start_byte:node.end_byte].strip('`')
            # Replace template expressions
            return re.sub(r'\$\{[^}]+\}', 'EXPR', text)
        
        # Identifiers, function calls, etc. = dynamic
        return 'EXPR'
    
    def _reconstruct_concatenated_strings(self, node, content: str) -> str:
        """
        Reconstruct string concatenations like:
        "/api/" + version + "/users" → "/api/EXPR/users"
        
        Args:
            node: Binary expression node
            content: Source code content
            
        Returns:
            Reconstructed string or None if not a concatenation
        """
        if node.type != 'binary_expression':
            return None
        
        operator_node = node.child_by_field_name('operator')
        if operator_node is None:
            return None
        
        operator = content[operator_node.start_byte:operator_node.end_byte]
        
        # Only handle + operator (string concatenation)
        if operator != '+':
            return None
        
        left_node = node.child_by_field_name('left')
        right_node = node.child_by_field_name('right')
        
        # Recursively handle nested concatenations
        if left_node and left_node.type == 'binary_expression':
            left = self._reconstruct_concatenated_strings(left_node, content)
        else:
            left = self._get_string_value(left_node, content)
        
        if right_node and right_node.type == 'binary_expression':
            right = self._reconstruct_concatenated_strings(right_node, content)
        else:
            right = self._get_string_value(right_node, content)
        
        if left is None or right is None:
            return None
        
        # Combine the parts
        result = left + right
        
        # Only return if it looks like an endpoint or URL
        if result.startswith('/') or result.startswith('http') or 'api' in result.lower():
            return result
        
        return None
    
    def _extract_endpoints_sync(self, node, content: str) -> List[str]:
        """Extracts API endpoints from AST (synchronous for executor)"""
        endpoints = set()
        
        # Look for string literals that look like endpoints
        def traverse(n):
            # NEW: Check for string concatenations (Priority 1 feature)
            if n.type == 'binary_expression':
                concatenated = self._reconstruct_concatenated_strings(n, content)
                if concatenated and self._is_endpoint(concatenated):
                    # Validate with relaxed rules for EXPR placeholders
                    if self._is_valid_concatenated_endpoint(concatenated):
                        endpoints.add(concatenated)
            
            if n.type == 'string':
                text = content[n.start_byte:n.end_byte].strip('"\'')
                if self._is_endpoint(text) and self._is_valid_endpoint(text):
                    endpoints.add(text)
                # Also check for template literals with endpoints
                elif '${' in text or text.startswith('/'):
                    # Extract potential endpoint parts
                    parts = re.split(r'\$\{[^}]+\}', text)
                    for part in parts:
                        if self._is_endpoint(part) and self._is_valid_endpoint(part):
                            endpoints.add(part)
            
            # Check template strings
            if n.type == 'template_string':
                text = content[n.start_byte:n.end_byte].strip('`')
                # Extract URL patterns from template strings
                if 'http' in text or text.startswith('/'):
                    # Remove template expressions for pattern matching
                    cleaned = re.sub(r'\$\{[^}]+\}', '', text)
                    if (self._is_endpoint(cleaned) or 'api' in cleaned.lower()) and self._is_valid_endpoint(cleaned):
                        # Keep template expression markers
                        templated = re.sub(r'\$\{[^}]+\}', 'EXPR', text)
                        endpoints.add(templated)
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return list(endpoints)
    
    async def _extract_links(self, content: str) -> List[str]:
        """Extracts internal document links"""
        links = set()
        
        # Regex patterns for various file types
        patterns = [
            r'["\']([^"\']*\.(?:pdf|json|xml|csv|xlsx|doc|docx))["\']',
            r'["\']([^"\']*\.md)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            links.update(matches)
        
        return list(links)
    
    async def _extract_cloud_assets(self, content: str) -> List[str]:
        """
        Extracts cloud storage URLs (S3, Azure, GCS, Firebase) for asset intelligence
        
        Cloud providers detected:
        - AWS S3: s3.amazonaws.com, s3-*.amazonaws.com, *.s3.amazonaws.com, *.s3.*.amazonaws.com
        - Azure Storage: *.blob.core.windows.net, *.file.core.windows.net, *.queue.core.windows.net
        - Google Cloud Storage: storage.googleapis.com, *.storage.googleapis.com, storage.cloud.google.com
        - Firebase: *.firebaseio.com, *.firebasestorage.app, *.cloudfunctions.net (firebase-related)
        
        Args:
            content: JavaScript content
            
        Returns:
            List of unique cloud storage URLs
        """
        cloud_assets = set()
        
        # AWS S3 patterns
        s3_patterns = [
            # Standard S3 URLs
            r'https?://([a-z0-9\-]+\.)?s3[.-]([a-z0-9\-]+\.)?amazonaws\.com/[^\s"\'>]+',
            # S3 bucket subdomains
            r'https?://[a-z0-9\-]+\.s3\.amazonaws\.com[^\s"\'>]*',
            r'https?://s3-[a-z0-9\-]+\.amazonaws\.com/[^\s"\'>]+',
            # S3 virtual-hosted style
            r'https?://[a-z0-9\-]+\.s3-[a-z0-9\-]+\.amazonaws\.com[^\s"\'>]*'
        ]
        
        # Azure Storage patterns
        azure_patterns = [
            r'https?://[a-z0-9\-]+\.blob\.core\.windows\.net[^\s"\'>]*',
            r'https?://[a-z0-9\-]+\.file\.core\.windows\.net[^\s"\'>]*',
            r'https?://[a-z0-9\-]+\.queue\.core\.windows\.net[^\s"\'>]*',
            r'https?://[a-z0-9\-]+\.table\.core\.windows\.net[^\s"\'>]*'
        ]
        
        # Google Cloud Storage patterns
        gcs_patterns = [
            r'https?://storage\.googleapis\.com/[^\s"\'>]+',
            r'https?://[a-z0-9\-]+\.storage\.googleapis\.com[^\s"\'>]*',
            r'https?://storage\.cloud\.google\.com/[^\s"\'>]+'
        ]
        
        # Firebase patterns
        firebase_patterns = [
            r'https?://[a-z0-9\-]+\.firebaseio\.com[^\s"\'>]*',
            r'https?://[a-z0-9\-]+\.firebasestorage\.app[^\s"\'>]*',
            r'https?://[a-z0-9\-]+\.cloudfunctions\.net[^\s"\'>]*'
        ]
        
        # Combine all patterns
        all_patterns = s3_patterns + azure_patterns + gcs_patterns + firebase_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Clean up the URL (remove trailing quotes, brackets, etc.)
                if isinstance(match, tuple):
                    # Extract full match from tuple
                    continue
                url = match.strip().rstrip('",\'>;)')
                
                # Validate it's a complete URL
                if url.startswith('http') and len(url) > 20 and len(url) < 500:
                    cloud_assets.add(url)
        
        # Also search for full matches (non-capturing)
        for pattern in all_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                url = match.group(0).strip().rstrip('",\'>;)')
                if url.startswith('http') and len(url) > 20 and len(url) < 500:
                    cloud_assets.add(url)
        
        return list(cloud_assets)
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain to filter out JavaScript namespaces and invalid entries"""
        # Must have at least one dot
        if domain.count('.') < 1:
            return False
        
        # Must have valid TLD (common extensions)
        valid_tlds = (
            'com', 'net', 'org', 'io', 'dev', 'ch', 'uk', 'fr', 'de', 'jp', 'cn',
            'app', 'xyz', 'tech', 'co', 'me', 'ai', 'in', 'it', 'ca', 'au', 'br',
            'ru', 'nl', 'se', 'no', 'es', 'kr', 'tw', 'sg', 'hk', 'nz', 'us'
        )
        if not any(domain.lower().endswith('.' + tld) for tld in valid_tlds):
            return False
        
        # Reject JavaScript namespaces and event handlers
        js_prefixes = (
            'ui.', 'bs.', 'click.', 'show.', 'hide.', 'event.', 'data.',
            'components.', 'sk.', 'jquery.', 'js.', 'window.', 'document.'
        )
        if any(domain.lower().startswith(prefix) for prefix in js_prefixes):
            return False
        
        # Reject file extensions disguised as domains
        if domain.startswith('.') or domain.endswith('.js') or domain.endswith('.css'):
            return False
        
        # Require at least 2 characters before first dot
        first_part = domain.split('.')[0]
        if len(first_part) < 2:
            return False
        
        return True
    
    async def _extract_domains(self, content: str) -> List[str]:
        """Extracts external domains with strict validation"""
        domains = set()
        
        # Pattern for URLs and domains (stricter)
        url_pattern = r'https?://([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,6}'
        matches = re.findall(url_pattern, content, re.IGNORECASE)
        for match in matches:
            if self._is_valid_domain(match):
                domains.add(match)
        
        # Pattern for domain-like strings (stricter)
        domain_pattern = r'["\']([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,6}["\']'
        matches = re.findall(domain_pattern, content, re.IGNORECASE)
        for match in matches:
            if self._is_valid_domain(match):
                domains.add(match)
        
        return list(domains)
    
    async def extract_js_urls(self, content: str, base_url: str) -> List[str]:
        """
        Extract .js URLs from JavaScript content for recursive discovery
        
        This enables finding 2nd/3rd level JS files referenced within other JS files.
        Extracts:
        - Direct .js file references in strings
        - Dynamic imports: import('./module.js')
        - require() calls: require('./file.js')
        - Script tag src attributes
        - Webpack/Vite chunk references
        
        Args:
            content: JavaScript content to analyze
            base_url: Base URL for resolving relative paths
            
        Returns:
            List of absolute .js URLs found in the content
        """
        from urllib.parse import urljoin, urlparse
        js_urls = set()
        
        # Pattern 1: String literals ending in .js or .mjs
        # Matches: "path/to/file.js", './module.js', '../utils.js'
        string_patterns = [
            r'["\']([^"\']+\.(?:js|mjs))(?:["\']|\?)',  # .js or .mjs with optional query
            r'["\']([^"\']+\.js)["\']',  # Simple .js references
        ]
        
        for pattern in string_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Skip data URIs, blob URLs, and obviously invalid paths
                if match.startswith(('data:', 'blob:', 'javascript:')):
                    continue
                
                # Convert to absolute URL
                try:
                    absolute_url = urljoin(base_url, match)
                    # Validate it's a proper HTTP URL
                    parsed = urlparse(absolute_url)
                    if parsed.scheme in ('http', 'https') and parsed.path.endswith(('.js', '.mjs')):
                        js_urls.add(absolute_url)
                except Exception:
                    continue
        
        # Pattern 2: import() dynamic imports
        # Matches: import('./file.js'), import("module.js")
        import_pattern = r'import\s*\(\s*["\']([^"\']+\.(?:js|mjs))["\']'
        matches = re.findall(import_pattern, content, re.IGNORECASE)
        for match in matches:
            try:
                absolute_url = urljoin(base_url, match)
                if urlparse(absolute_url).scheme in ('http', 'https'):
                    js_urls.add(absolute_url)
            except Exception:
                continue
        
        # Pattern 3: require() calls
        # Matches: require('./file.js'), require("module.js")
        require_pattern = r'require\s*\(\s*["\']([^"\']+\.(?:js|mjs))["\']'
        matches = re.findall(require_pattern, content, re.IGNORECASE)
        for match in matches:
            try:
                absolute_url = urljoin(base_url, match)
                if urlparse(absolute_url).scheme in ('http', 'https'):
                    js_urls.add(absolute_url)
            except Exception:
                continue
        
        # Pattern 4: Webpack/Vite chunk files
        # Matches: "assets/chunk-abc123.js", "dist/vendor.js"
        chunk_pattern = r'["\']([a-zA-Z0-9/_\-\.]+/[a-zA-Z0-9\-_]+\.js)["\']'
        matches = re.findall(chunk_pattern, content)
        for match in matches:
            # Only include if it looks like a real path (has directory separator)
            if '/' in match and not match.startswith(('http://', 'https://')):
                try:
                    absolute_url = urljoin(base_url, match)
                    if urlparse(absolute_url).scheme in ('http', 'https'):
                        js_urls.add(absolute_url)
                except Exception:
                    continue
        
        self.logger.debug(f"Extracted {len(js_urls)} JS URLs from {base_url}")
        return list(js_urls)
    
    def _is_valid_endpoint(self, endpoint: str) -> bool:
        """Validate endpoint before adding to results"""
        # Remove endpoints with code artifacts
        if any(char in endpoint for char in ['{', '}', '(', ')', ';', '`', '$', '=', '>', '<']):
            return False
        
        # Must start with /
        if not endpoint.startswith('/'):
            return False
        
        # No template strings
        if '${' in endpoint:
            return False
        
        # No incomplete syntax
        if endpoint.rstrip().endswith((',', ':', ';', '\\', '|', '&')):
            return False
        
        # No double slashes
        if '//' in endpoint[1:]:
            return False
        
        # Reasonable length
        if len(endpoint) > 100:
            return False
        
        # Valid URL characters only (strict regex check)
        import re
        if not re.match(r'^/[a-zA-Z0-9/_\-\.]+$', endpoint):
            return False
        
        return True
    
    def _is_valid_concatenated_endpoint(self, endpoint: str) -> bool:
        """
        Validate concatenated endpoint (allows EXPR placeholder)
        
        Args:
            endpoint: Endpoint string possibly containing EXPR
            
        Returns:
            True if valid
        """
        # Must start with /
        if not endpoint.startswith('/') and not endpoint.startswith('http'):
            return False
        
        # No template strings (already converted to EXPR)
        if '${' in endpoint:
            return False
        
        # No incomplete syntax
        if endpoint.rstrip().endswith((',', ':', ';', '\\', '|', '&')):
            return False
        
        # Reasonable length
        if len(endpoint) > 200:  # Longer than normal due to EXPR
            return False
        
        # Valid URL characters + EXPR placeholder
        import re
        # Allow EXPR as a placeholder
        if not re.match(r'^[/]?[a-zA-Z0-9/_\-\.EXPR?&=]+$', endpoint):
            return False
        
        # Must have at least one slash after the first character
        if '/' not in endpoint[1:]:
            return False
        
        return True
    
    @staticmethod
    def _is_endpoint(text: str) -> bool:
        """Checks if a string looks like an API endpoint"""
        if not text or len(text) < 3:
            return False
        
        # Must start with / for relative paths or be absolute URL
        if not (text.startswith('/') or text.startswith('http')):
            return False
        
        # Expanded API patterns for better detection
        api_indicators = [
            '/api/', '/v1/', '/v2/', '/v3/', '/graphql', '/rest/', '/ajax/',
            '/ws/', '/wss/', '/socket', '/endpoint', '/service',
            # REST and RPC patterns
            '/data/', '/query/', '/mutation/', '/rpc/', '/jsonrpc',
            # Admin/access patterns
            '/admin/', '/internal/', '/private/', '/public/',
            # Subdomain patterns
            'api.', 'gateway.', 'service.'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in api_indicators)
    
    def get_extracts_with_sources(self) -> dict:
        """Export extracts database with source information"""
        result = {
            'endpoints': [],
            'domains': [],
            'links': [],
            'domains_summary': {}
        }
        
        # Convert to list format with source info
        for extract_type in ['endpoints', 'domains', 'links']:
            items = []
            for value, data in self.extracts_db[extract_type].items():
                items.append({
                    'value': value,
                    'sources': data['sources'],
                    'total_occurrences': data['total_count'],
                    'unique_domains': sorted(list(data['domains'])),
                    'domain_count': len(data['domains'])
                })
            
            # Sort by domain count (most widespread first), then by occurrences
            items.sort(key=lambda x: (x['domain_count'], x['total_occurrences']), reverse=True)
            result[extract_type] = items[:100]  # Limit to top 100
        
        # Build domains summary
        domains_summary = {}
        for extract_type in ['endpoints']:
            for item in result[extract_type]:
                for source in item['sources']:
                    domain = source['domain']
                    if domain not in domains_summary:
                        domains_summary[domain] = {
                            'endpoints': set(),
                            'file_count': set()
                        }
                    
                    if extract_type == 'endpoints':
                        domains_summary[domain]['endpoints'].add(item['value'])
                    
                    domains_summary[domain]['file_count'].add(source['file'])
        
        # Convert sets to sorted lists
        for domain, data in domains_summary.items():
            result['domains_summary'][domain] = {
                'endpoints': sorted(list(data['endpoints'])),
                'file_count': len(data['file_count'])
            }
        
        return result
    
    async def save_organized_extracts(self):
        """
        Save extracts in both domain-specific and legacy formats
        """
        # Save domain-specific organization
        await self.domain_organizer.save_by_domain(self.extracts_db)
        
        # Save legacy format for backward compatibility
        await self.domain_organizer.save_legacy_format(self.extracts_db)
        
        self.logger.info("✅ Saved extracts in both domain-specific and legacy formats")
    
    def get_domain_summary(self) -> Dict[str, Any]:
        """Get summary of domain-specific extracts"""
        return self.domain_organizer.get_domain_summary()
    
    # ========== DYNAMIC IMPORT DETECTION (NEW) ==========
    
    def _extract_dynamic_imports(self, node, content: str) -> List[Dict]:
        """
        Extract dynamic import patterns from AST for code splitting detection.
        
        Detects 9 import patterns:
        1. import() - ES6 dynamic imports
        2. require() - CommonJS
        3. __webpack_require__.e() - Webpack chunk loading
        4. React.lazy() - React lazy loading
        5. loadable() - loadable-components
        6. System.import() - SystemJS
        7. require() - AMD/RequireJS
        8. dynamic() - Next.js dynamic imports
        9. import.meta.glob() - Vite glob imports
        
        Args:
            node: AST root node
            content: JavaScript source code
            
        Returns:
            List of import dictionaries with type, target, line, etc.
        """
        imports = []
        
        def traverse(n):
            if not n:
                return
            
            # 1. Dynamic import() calls
            if n.type == 'call_expression':
                callee = n.child_by_field_name('function')
                if callee:
                    callee_text = content[callee.start_byte:callee.end_byte]
                    
                    # ES6 dynamic import
                    if callee_text == 'import':
                        args = n.child_by_field_name('arguments')
                        if args and args.named_children:
                            arg = args.named_children[0]
                            module_path = self._get_string_value(arg, content)
                            imports.append({
                                'type': 'dynamic_import',
                                'target': module_path,
                                'line': n.start_point[0] + 1,
                                'is_template': '${' in module_path or 'EXPR' in module_path,
                                'pattern': 'import()'
                            })
                    
                    # 2. CommonJS require()
                    elif callee_text == 'require':
                        args = n.child_by_field_name('arguments')
                        if args and args.named_children:
                            module_path = self._get_string_value(args.named_children[0], content)
                            imports.append({
                                'type': 'commonjs_require',
                                'target': module_path,
                                'line': n.start_point[0] + 1,
                                'is_template': '${' in module_path,
                                'pattern': 'require()'
                            })
                    
                    # 3. Webpack chunk loading: __webpack_require__.e(chunkId)
                    elif '__webpack_require__.e' in callee_text:
                        imports.append({
                            'type': 'webpack_chunk',
                            'target': f'CHUNK_{n.start_point[0]}',
                            'line': n.start_point[0] + 1,
                            'is_template': False,
                            'pattern': '__webpack_require__.e()'
                        })
                    
                    # 4. React.lazy()
                    elif 'lazy' in callee_text and ('React.lazy' in callee_text or callee_text == 'lazy'):
                        imports.append({
                            'type': 'react_lazy',
                            'target': 'LAZY_COMPONENT',
                            'line': n.start_point[0] + 1,
                            'is_template': False,
                            'pattern': 'React.lazy()'
                        })
                    
                    # 5. loadable() from loadable-components
                    elif 'loadable' in callee_text:
                        imports.append({
                            'type': 'loadable_component',
                            'target': 'LOADABLE_COMPONENT',
                            'line': n.start_point[0] + 1,
                            'is_template': False,
                            'pattern': 'loadable()'
                        })
                    
                    # 6. SystemJS: System.import()
                    elif 'System.import' in callee_text:
                        args = n.child_by_field_name('arguments')
                        if args and args.named_children:
                            module_path = self._get_string_value(args.named_children[0], content)
                            imports.append({
                                'type': 'systemjs_import',
                                'target': module_path,
                                'line': n.start_point[0] + 1,
                                'is_template': False,
                                'pattern': 'System.import()'
                            })
                    
                    # 8. Next.js dynamic()
                    elif callee_text == 'dynamic':
                        imports.append({
                            'type': 'nextjs_dynamic',
                            'target': 'DYNAMIC_COMPONENT',
                            'line': n.start_point[0] + 1,
                            'is_template': False,
                            'pattern': 'dynamic()'
                        })
            
            # 9. Vite glob imports: import.meta.glob()
            if n.type == 'call_expression':
                callee = n.child_by_field_name('function')
                if callee:
                    callee_text = content[callee.start_byte:callee.end_byte]
                    if 'import.meta.glob' in callee_text:
                        args = n.child_by_field_name('arguments')
                        if args and args.named_children:
                            glob_pattern = self._get_string_value(args.named_children[0], content)
                            imports.append({
                                'type': 'vite_glob',
                                'target': glob_pattern,
                                'line': n.start_point[0] + 1,
                                'is_template': False,
                                'pattern': 'import.meta.glob()'
                            })
            
            # Recursively traverse children
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return imports
    
    def _extract_chunk_relationships(self, content: str) -> Dict:
        """
        Extract webpack/vite chunk loading patterns and relationships.
        
        Parses:
        - Webpack manifests (webpackJsonp, webpackChunk)
        - Chunk loading calls (__webpack_require__.e)
        - Chunk filenames and IDs
        
        Args:
            content: JavaScript source code
            
        Returns:
            Dictionary with entry_chunks, lazy_chunks, chunk_files
        """
        relationships = {
            'entry_chunks': [],
            'lazy_chunks': [],
            'chunk_files': [],
            'chunk_dependencies': {}
        }
        
        # Pattern 1: Webpack manifest - webpackJsonp([chunkIds], modules)
        manifest_pattern = r'webpackJsonp\s*\(\s*\[([^\]]+)\]'
        matches = re.findall(manifest_pattern, content)
        for match in matches:
            chunk_ids = [int(x.strip()) for x in match.split(',') if x.strip().isdigit()]
            relationships['entry_chunks'].extend(chunk_ids)
        
        # Pattern 2: Chunk loading calls - __webpack_require__.e(chunkId)
        chunk_load_pattern = r'__webpack_require__\.e\s*\(\s*(\d+)\s*\)'
        chunk_loads = re.findall(chunk_load_pattern, content)
        relationships['lazy_chunks'] = list(set(int(x) for x in chunk_loads))
        
        # Pattern 3: Chunk filenames - [hash].chunk.js or [name].chunk.js
        chunk_file_pattern = r'["\']([a-zA-Z0-9\-_]+\.chunk\.js)["\']'
        chunk_files = re.findall(chunk_file_pattern, content)
        relationships['chunk_files'] = list(set(chunk_files))
        
        # Pattern 4: Vite chunks - [hash].js in import.meta.url contexts
        vite_chunk_pattern = r'import\.meta\.url.*?["\']([a-zA-Z0-9\-_]+\.js)["\']'
        vite_chunks = re.findall(vite_chunk_pattern, content)
        relationships['chunk_files'].extend(list(set(vite_chunks)))
        
        # Pattern 5: Chunk ID to filename mapping (Webpack)
        # Looks for: {0:"chunk-0.js", 1:"chunk-1.js"}
        chunk_map_pattern = r'(\d+)\s*:\s*["\']([^"\']+\.js)["\']'
        chunk_mappings = re.findall(chunk_map_pattern, content)
        for chunk_id, filename in chunk_mappings:
            relationships['chunk_dependencies'][int(chunk_id)] = filename
        
        return relationships
    
    def predict_chunks(self, content: str, base_url: str) -> List[str]:
        """
        Predict chunk URLs for SPAs by analyzing webpack/vite patterns.
        
        This enables discovery of lazy-loaded chunks that aren't linked in HTML.
        Example: If main.js references chunks 0-5, generate:
            - https://example.com/0.js
            - https://example.com/1.js
            - ... etc
        
        Args:
            content: JavaScript source code
            base_url: Base URL to construct absolute chunk URLs
            
        Returns:
            List of predicted chunk URLs
        """
        from urllib.parse import urljoin, urlparse
        
        predicted_urls = []
        chunk_map = self._extract_chunk_relationships(content)
        
        # Get base path from current URL
        parsed = urlparse(base_url)
        base_path = '/'.join(parsed.path.split('/')[:-1]) + '/'  # Remove filename, keep path
        base_origin = f"{parsed.scheme}://{parsed.netloc}"
        
        # Strategy 1: Use explicit chunk mappings
        for chunk_id, filename in chunk_map.get('chunk_dependencies', {}).items():
            chunk_url = urljoin(base_origin + base_path, filename)
            predicted_urls.append(chunk_url)
        
        # Strategy 2: Enumerate known chunk IDs
        all_chunk_ids = set(chunk_map.get('entry_chunks', []) + chunk_map.get('lazy_chunks', []))
        for chunk_id in all_chunk_ids:
            # Try common patterns
            patterns = [
                f"{chunk_id}.js",
                f"chunk-{chunk_id}.js",
                f"{chunk_id}.chunk.js",
                f"{chunk_id}.{parsed.path.split('/')[-1].split('.')[0]}.js"  # e.g., 0.main.js
            ]
            for pattern in patterns:
                chunk_url = urljoin(base_origin + base_path, pattern)
                predicted_urls.append(chunk_url)
        
        # Strategy 3: Use explicit chunk filenames found in code
        for chunk_file in chunk_map.get('chunk_files', []):
            chunk_url = urljoin(base_origin + base_path, chunk_file)
            predicted_urls.append(chunk_url)
        
        # Deduplicate and log
        predicted_urls = list(set(predicted_urls))
        if predicted_urls:
            self.logger.info(f"🧩 Predicted {len(predicted_urls)} webpack/vite chunks from {base_url}")
        
        return predicted_urls
    
    async def extract_and_save_dynamic_imports(self, content: str, source_url: str) -> None:
        """
        Extract dynamic imports and chunk relationships, save to dynamic_imports.json.
        
        Args:
            content: JavaScript source code
            source_url: Source URL for attribution
        """
        # Only run if enabled in config
        code_splitting_config = self.config.get('code_splitting', {})
        if not code_splitting_config.get('detect_dynamic_imports', True):
            return
        
        dynamic_imports = []
        chunk_map = {}
        
        try:
            # Parse content and extract dynamic imports
            if self.parser:
                tree = self.parser.parse(bytes(content, 'utf8'))
                if tree and tree.root_node:
                    dynamic_imports = self._extract_dynamic_imports(tree.root_node, content)
            
            # Extract chunk relationships if enabled
            if code_splitting_config.get('extract_chunk_map', True):
                chunk_map = self._extract_chunk_relationships(content)
            
            # Save results if anything found
            if dynamic_imports or any(chunk_map.values()):
                import json
                from urllib.parse import urlparse
                source_domain = urlparse(source_url).netloc or 'unknown'
                
                # Load existing data
                output_file = Path(self.paths['extracts']) / 'dynamic_imports.json'
                existing_data = {'imports': [], 'chunk_maps': {}}
                
                if output_file.exists():
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except:
                        pass
                
                # Append new imports
                for imp in dynamic_imports:
                    imp['source_file'] = source_url
                    imp['source_domain'] = source_domain
                    existing_data['imports'].append(imp)
                
                # Add chunk map for this file
                if chunk_map and any(chunk_map.values()):
                    existing_data['chunk_maps'][source_url] = chunk_map
                
                # Save atomically
                temp_file = output_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2)
                temp_file.replace(output_file)
                
                self.logger.debug(f"Found {len(dynamic_imports)} dynamic imports in {source_url}")
        
        except Exception as e:
            self.logger.debug(f"Dynamic import extraction failed for {source_url}: {e}")