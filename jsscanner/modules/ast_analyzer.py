"""
AST Analyzer Module
Uses Tree-sitter to parse JavaScript and extract endpoints, parameters, and wordlists
"""
import re
from tree_sitter import Language, Parser
from typing import List, Set
from pathlib import Path
from ..utils.file_ops import FileOps


class ASTAnalyzer:
    """Analyzes JavaScript using AST parsing"""
    
    def __init__(self, config: dict, logger, paths: dict):
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
        
        # Initialize Tree-sitter parser
        try:
            import tree_sitter_javascript as tsjavascript
            self.JS_LANGUAGE = Language(tsjavascript.language())
            self.parser = Parser(self.JS_LANGUAGE)
            self.logger.info("Tree-sitter parser initialized")
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
            self.logger.warning("Tree-sitter not available, using regex fallback")
            await self._analyze_with_regex(content, source_url)
            return
        
        try:
            # Parse content
            tree = self.parser.parse(bytes(content, 'utf8'))
            root_node = tree.root_node
            
            # Extract various elements
            endpoints = await self._extract_endpoints(root_node, content)
            params = await self._extract_params(root_node, content)
            links = await self._extract_links(content)
            domains = await self._extract_domains(content)
            wordlist = await self._generate_wordlist(root_node, content)
            
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
    
    async def _extract_endpoints(self, node, content: str) -> List[str]:
        """Extracts API endpoints from AST"""
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
                    import re
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
    
    async def _extract_params(self, node, content: str) -> List[str]:
        """Extracts parameter names from AST"""
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
    
    async def _generate_wordlist(self, node, content: str) -> List[str]:
        """Generates custom wordlist from identifiers"""
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
    
    async def _analyze_with_regex(self, content: str, source_url: str):
        """Fallback analysis using regex when Tree-sitter is unavailable"""
        extracts_path = Path(self.paths['extracts'])
        
        # Extract endpoints with enhanced patterns
        endpoint_patterns = [
            # API routes
            r'["\']([/api/][^"\']*)["\']',
            r'["\']([/v\d+/][^"\']*)["\']',
            r'["\']([/graphql][^"\']*)["\']',
            r'["\']([/rest/][^"\']*)["\']',
            r'["\']([/ajax/][^"\']*)["\']',
            # HTTP methods
            r'(?:fetch|axios\.(?:get|post|put|delete|patch))\(["\']([^"\']*)["\']',
            r'\$.(?:get|post|ajax)\(["\']([^"\']*)["\']',
            # XMLHttpRequest
            r'open\(["\'](?:GET|POST|PUT|DELETE|PATCH)["\'],\s*["\']([^"\']*)["\']',
            # WebSocket
            r'new\s+WebSocket\(["\']([^"\']*)["\']',
            # GraphQL
            r'gql`[^`]*query[^`]*`',
            r'graphql\(["\']([^"\']*)["\']'
        ]
        
        endpoints = set()
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ''
                if match and (self._is_endpoint(match) or 'graphql' in match.lower() or 'ws' in match.lower()):
                    endpoints.add(match)
        
        if endpoints:
            await FileOps.append_unique_lines(
                str(extracts_path / 'endpoints.txt'),
                list(endpoints)
            )
        
        # Extract parameters from common patterns
        param_patterns = [
            r'new\s+URLSearchParams\(\{([^}]+)\}\)',
            r'FormData\.append\(["\']([^"\']*)["\']',
            r'\?([a-zA-Z_][a-zA-Z0-9_]*)='
        ]
        
        params = set()
        for pattern in param_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Extract parameter names
                if ':' in match or ',' in match:
                    # Object syntax
                    for param in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:', match):
                        params.add(param)
                else:
                    params.add(match)
        
        if params:
            await FileOps.append_unique_lines(
                str(extracts_path / 'params.txt'),
                list(params)
            )
        
        # Extract links
        links = await self._extract_links(content)
        if links:
            await FileOps.append_unique_lines(
                str(extracts_path / 'links.txt'),
                links
            )
        
        # Extract domains
        domains = await self._extract_domains(content)
        if domains:
            await FileOps.append_unique_lines(
                str(extracts_path / 'domains.txt'),
                domains
            )
    
    @staticmethod
    def _is_endpoint(text: str) -> bool:
        """Checks if a string looks like an API endpoint"""
        if not text or len(text) < 3:
            return False
        
        # Must start with / for relative paths or be absolute URL
        if not (text.startswith('/') or text.startswith('http')):
            return False
        
        # Common API patterns
        api_indicators = [
            '/api/', '/v1/', '/v2/', '/v3/', '/graphql', '/rest/', '/ajax/',
            '/ws/', '/wss/', '/socket', '/endpoint', '/service'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in api_indicators)
