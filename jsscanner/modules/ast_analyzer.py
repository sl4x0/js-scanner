"""
AST Analyzer Module
Uses Tree-sitter to parse JavaScript and extract endpoints, parameters, and wordlists
"""
import asyncio
import re
from tree_sitter import Parser
from typing import List, Set, Dict, Any
from pathlib import Path
from ..utils.file_ops import FileOps


class ASTAnalyzer:
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
        self.min_word_length = config.get('ast', {}).get('min_word_length', 4)
        self._tree_sitter_warning_logged = False  # Only warn once
        
        # Initialize Tree-sitter parser
        try:
            import tree_sitter_javascript as tsjavascript
            import tree_sitter
            
            # Get the language
            language = tsjavascript.language()
            
            # Issue #12: Check tree-sitter version explicitly with fallback
            try:
                ts_version = tuple(map(int, tree_sitter.__version__.split('.')[:2]))
                version_str = tree_sitter.__version__
            except AttributeError:
                # Fallback: Try to detect API by checking if set_language exists
                ts_version = (0, 22)  # Assume new API if no version
                version_str = "unknown"
            
            if ts_version >= (0, 22):
                # New API (v0.22+)
                self.parser = Parser()
                self.parser.set_language(language)
            else:
                # Old API (v0.20-0.21) - requires Language wrapper
                from tree_sitter import Language
                js_lang = Language(language)
                self.parser = Parser(js_lang)
            
            self.logger.info(f"Tree-sitter parser initialized (v{version_str})")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Tree-sitter: {e}")
            self.parser = None
    
    async def analyze(self, content: str, source_url: str):
        """
        Analyzes JavaScript content using AST
        
        Args:
            content: JavaScript content
            source_url: Source URL
        """
        if not self.parser:
            if not self._tree_sitter_warning_logged:
                self.logger.warning("Tree-sitter not available, using regex fallback for all files")
                self._tree_sitter_warning_logged = True
            await self._analyze_with_regex(content, source_url)
            return
        
        try:
            # Parse content in executor to avoid blocking event loop (CPU-bound)
            loop = asyncio.get_event_loop()
            tree = await loop.run_in_executor(None, self._parse_content, content)
            root_node = tree.root_node
            
            # Extract various elements (run in executor since they traverse large ASTs)
            endpoints = await loop.run_in_executor(None, self._extract_endpoints_sync, root_node, content)
            params = await loop.run_in_executor(None, self._extract_params_sync, root_node, content)
            links = await self._extract_links(content)
            domains = await self._extract_domains(content)
            wordlist = await loop.run_in_executor(None, self._generate_wordlist_sync, root_node, content)
            
            # Save extracts
            extracts_path = Path(self.paths['extracts'])
            
            if endpoints:
                await FileOps.append_unique_lines(
                    str(extracts_path / 'endpoints.txt'),
                    endpoints
                )
            
            if params:
                await FileOps.append_unique_lines(
                    str(extracts_path / 'params.txt'),
                    params
                )
            
            if links:
                await FileOps.append_unique_lines(
                    str(extracts_path / 'links.txt'),
                    links
                )
            
            if domains:
                await FileOps.append_unique_lines(
                    str(extracts_path / 'domains.txt'),
                    domains
                )
            
            if wordlist:
                await FileOps.append_unique_lines(
                    str(extracts_path / 'wordlist.txt'),
                    wordlist
                )
            
            self.logger.info(
                f"Extracted: {len(endpoints)} endpoints, {len(params)} params, "
                f"{len(wordlist)} words"
            )
            
        except Exception as e:
            self.logger.error(f"AST analysis failed: {e}")
            await self._analyze_with_regex(content, source_url)
        finally:
            # Issue #6: Explicit cleanup to prevent memory leaks
            if 'tree' in locals():
                del tree
            if 'root_node' in locals():
                del root_node
    
    def _parse_content(self, content: str):
        """Synchronous tree-sitter parsing (CPU-bound)"""
        # Prevent memory issues with very large files
        if len(content) > 5 * 1024 * 1024:  # 5MB
            self.logger.warning(f"Skipping AST parsing for file >5MB (too large)")
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
    
    def _extract_endpoints_sync(self, node, content: str) -> List[str]:
        """Extracts API endpoints from AST (synchronous for executor)"""
        endpoints = set()
        
        # Look for string literals that look like endpoints
        def traverse(n):
            if n.type == 'string':
                text = content[n.start_byte:n.end_byte].strip('"\'')
                if self._is_endpoint(text):
                    endpoints.add(text)
                # Also check for template literals with endpoints
                elif '${' in text or text.startswith('/'):
                    # Extract potential endpoint parts
                    parts = re.split(r'\$\{[^}]+\}', text)
                    for part in parts:
                        if self._is_endpoint(part):
                            endpoints.add(part)
            
            # Check template strings
            if n.type == 'template_string':
                text = content[n.start_byte:n.end_byte].strip('`')
                # Extract URL patterns from template strings
                if 'http' in text or text.startswith('/'):
                    # Remove template expressions for pattern matching
                    cleaned = re.sub(r'\$\{[^}]+\}', '', text)
                    if self._is_endpoint(cleaned) or 'api' in cleaned.lower():
                        endpoints.add(text)
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return list(endpoints)
    
    def _extract_params_sync(self, node, content: str) -> List[str]:
        """Extracts parameter names from AST (synchronous for executor)"""
        params = set()
        
        # Look for object properties and query parameters
        def traverse(n):
            if n.type == 'property_identifier' or n.type == 'shorthand_property_identifier':
                text = content[n.start_byte:n.end_byte]
                if text and len(text) > 1:
                    params.add(text)
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return list(params)
    
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
    
    async def _extract_domains(self, content: str) -> List[str]:
        """Extracts external domains"""
        domains = set()
        
        # Pattern for URLs and domains
        url_pattern = r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        matches = re.findall(url_pattern, content)
        domains.update(matches)
        
        # Pattern for domain-like strings
        domain_pattern = r'["\']([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']'
        matches = re.findall(domain_pattern, content)
        # Filter out obvious false positives
        for match in matches:
            if '.' in match and not match.endswith('.js'):
                domains.add(match)
        
        return list(domains)
    
    def _generate_wordlist_sync(self, node, content: str) -> List[str]:
        """Generates custom wordlist from identifiers (synchronous for executor)"""
        words = set()
        
        def traverse(n):
            if n.type in ['identifier', 'property_identifier']:
                text = content[n.start_byte:n.end_byte]
                if len(text) >= self.min_word_length and text.isalpha():
                    words.add(text.lower())
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return list(words)
    
    def _extract_with_regex(self, code: str) -> Dict[str, Any]:
        """Extract data using improved regex patterns"""
        
        # ENDPOINTS - Only real API endpoints
        endpoint_patterns = [
            r'["\']/(api|v\d+|graphql|rest|endpoint)/[a-zA-Z0-9/_-]+["\']',  # API paths
            r'["\']https?://[^"\']+?/(api|v\d+|graphql)[^"\']*["\']',  # Full API URLs
            r'fetch\(["\']([^"\']+)["\']',  # fetch() calls
            r'axios\.[a-z]+\(["\']([^"\']+)["\']',  # axios calls
            r'\.get\(["\']([^"\']+)["\']',  # .get() calls
            r'\.post\(["\']([^"\']+)["\']',  # .post() calls
        ]
        
        endpoints = set()
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                endpoint = match[0] if isinstance(match, tuple) else match
                # Filter out garbage
                if (len(endpoint) > 5 and 
                    len(endpoint) < 200 and
                    not any(x in endpoint.lower() for x in ['graphql{', 'query ', 'mutation ', 'fragment ', '__typename'])):
                    endpoints.add(endpoint.strip('"\''))
        
        # PARAMETERS - Only URL parameters
        param_patterns = [
            r'[?&]([a-zA-Z_][a-zA-Z0-9_]{0,30})=',  # URL params
            r'params\s*:\s*\{[^}]*["\']([a-zA-Z_][a-zA-Z0-9_]{0,30})["\']',  # params object
            r'searchParams\.append\(["\']([a-zA-Z_][a-zA-Z0-9_]{0,30})["\']',  # URLSearchParams
        ]
        
        params = set()
        for pattern in param_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                param = match[0] if isinstance(match, tuple) else match
                # Filter: only valid parameter names
                if (len(param) >= 1 and 
                    len(param) <= 30 and
                    (param.isalnum() or '_' in param)):
                    params.add(param)
        
        # DOMAINS - Only real domains
        domain_patterns = [
            r'https?://([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+[a-zA-Z]{2,}',  # Full URLs
            r'//([a-zA-Z0-9][-a-zA-Z0-9]{0,62}\.)+[a-zA-Z]{2,}',  # Protocol-relative
        ]
        
        domains = set()
        for pattern in domain_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                domain = match[0] if isinstance(match, tuple) else match
                domain = domain.rstrip('.')
                # Filter: must be valid domain
                if ('.' in domain and 
                    len(domain) > 4 and 
                    len(domain) < 100 and
                    not any(x in domain.lower() for x in ['.js', '.css', '.svg', '.png', '.jpg', 'localhost', 'example.com'])):
                    domains.add(domain)
        
        # LINKS - Only external resources
        link_patterns = [
            r'<script[^>]+src=["\']([^"\']+)["\']',
            r'<link[^>]+href=["\']([^"\']+)["\']',
            r'import\s+.*?from\s+["\']([^"\']+)["\']',
        ]
        
        links = set()
        for pattern in link_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                link = match[0] if isinstance(match, tuple) else match
                if link.startswith(('http://', 'https://', '//')):
                    links.add(link)
        
        # COMMENTS - Extract for context (but limit)
        comments = []
        comment_patterns = [
            r'//\s*TODO:?\s*(.+)',
            r'//\s*FIXME:?\s*(.+)',
            r'//\s*API:?\s*(.+)',
            r'/\*\s*TODO:?\s*(.+?)\*/',
        ]
        
        for pattern in comment_patterns:
            matches = re.findall(pattern, code, re.DOTALL)
            comments.extend([m.strip()[:200] for m in matches[:10]])  # Max 10 comments, 200 chars each
        
        return {
            'endpoints': sorted(list(endpoints))[:100],  # Max 100
            'params': sorted(list(params))[:100],  # Max 100
            'domains': sorted(list(domains))[:50],  # Max 50
            'links': sorted(list(links))[:50],  # Max 50
            'comments': comments[:10],  # Max 10
            'wordlist': []  # Disabled - usually useless
        }
    
    async def _analyze_with_regex(self, content: str, source_url: str):
        """Fallback analysis using regex when Tree-sitter is unavailable"""
        extracts_path = Path(self.paths['extracts'])
        
        # Use improved extraction
        extracted = self._extract_with_regex(content)
        
        # Save endpoints
        if extracted['endpoints']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'endpoints.txt'),
                extracted['endpoints']
            )
        
        # Save parameters
        if extracted['params']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'params.txt'),
                extracted['params']
            )
        
        # Save links
        if extracted['links']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'links.txt'),
                extracted['links']
            )
        
        # Save domains
        if extracted['domains']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'domains.txt'),
                extracted['domains']
            )
        
        # Save comments if any
        if extracted['comments']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'comments.txt'),
                extracted['comments']
            )
    
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
