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
from .domain_organizer import DomainExtractOrganizer


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
        
        # Track sources for each extract
        self.extracts_db = {
            'endpoints': {},  # {endpoint: {sources: [], total_count: 0, domains: set()}}
            'params': {},
            'domains': {},
            'links': {},
            'words': {}  # Add words tracking for domain-specific wordlists
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
            self.logger.warning(f"Failed to initialize Tree-sitter: {e}")
            self.logger.warning(f"⚠️  AST parsing disabled - falling back to regex (lower accuracy)")
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
            
            for param in params:
                if param not in self.extracts_db['params']:
                    self.extracts_db['params'][param] = {
                        'sources': [],
                        'total_count': 0,
                        'domains': set()
                    }
                self.extracts_db['params'][param]['sources'].append({
                    'file': source_url,
                    'domain': source_domain,
                    'occurrences': 1
                })
                self.extracts_db['params'][param]['total_count'] += 1
                self.extracts_db['params'][param]['domains'].add(source_domain)
            
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
            
            # Save extracts to files (for backwards compatibility)
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
            
            # Track wordlist with source tracking for domain organization
            for word in wordlist:
                if word not in self.extracts_db['words']:
                    self.extracts_db['words'][word] = {
                        'sources': [],
                        'total_count': 0,
                        'domains': set()
                    }
                
                self.extracts_db['words'][word]['sources'].append({
                    'file': source_url,
                    'domain': source_domain,
                    'occurrences': 1
                })
                self.extracts_db['words'][word]['total_count'] += 1
                self.extracts_db['words'][word]['domains'].add(source_domain)
            
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
    
    def _extract_params_sync(self, node, content: str) -> List[str]:
        """Extracts parameter names from AST (synchronous for executor)"""
        params = set()
        
        # Look for object properties and query parameters
        def traverse(n):
            # Existing: Object properties
            if n.type == 'property_identifier' or n.type == 'shorthand_property_identifier':
                text = content[n.start_byte:n.end_byte]
                if text and len(text) > 1 and self._is_valid_param(text):
                    params.add(text)
            
            # NEW Phase 2a: JSON object keys
            if n.type == 'pair':
                key_node = n.child_by_field_name('key')
                if key_node:
                    if key_node.type == 'property_identifier':
                        key = content[key_node.start_byte:key_node.end_byte]
                    elif key_node.type == 'string':
                        key = content[key_node.start_byte:key_node.end_byte].strip('"\'')
                    else:
                        key = content[key_node.start_byte:key_node.end_byte]
                    
                    if key and self._is_valid_param(key):
                        params.add(key)
            
            # NEW Phase 2b: Variable declarations (var, let, const)
            if n.type in ('variable_declarator', 'lexical_declaration'):
                for child in n.children:
                    if child.type == 'variable_declarator':
                        name_node = child.child_by_field_name('name')
                        if name_node and name_node.type == 'identifier':
                            var_name = content[name_node.start_byte:name_node.end_byte]
                            if self._is_valid_param(var_name):
                                params.add(var_name)
                    elif child.type == 'identifier':
                        var_name = content[child.start_byte:child.end_byte]
                        if self._is_valid_param(var_name):
                            params.add(var_name)
            
            # Function parameters
            if n.type == 'formal_parameters':
                for child in n.children:
                    if child.type == 'identifier':
                        param_name = content[child.start_byte:child.end_byte]
                        if self._is_valid_param(param_name):
                            params.add(param_name)
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        
        # NEW Phase 2c: HTML input field extraction
        html_params = self._extract_html_input_names(content)
        params.update(html_params)
        
        return list(params)
    
    def _is_valid_param(self, param: str) -> bool:
        """
        Validate if a string is a valid parameter name
        
        Args:
            param: Parameter name to validate
            
        Returns:
            True if valid parameter
        """
        # Length check
        if not param or len(param) < 2 or len(param) > 50:
            return False
        
        # Must start with letter or underscore
        if not (param[0].isalpha() or param[0] == '_'):
            return False
        
        # Only alphanumeric and underscores
        if not all(c.isalnum() or c in ('_', '-') for c in param):
            return False
        
        # Skip common JavaScript keywords
        js_keywords = {
            'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for',
            'while', 'do', 'switch', 'case', 'break', 'continue', 'try', 'catch',
            'throw', 'new', 'this', 'super', 'class', 'extends', 'import', 'export',
            'default', 'async', 'await', 'true', 'false', 'null', 'undefined',
            'typeof', 'instanceof', 'void', 'delete', 'in', 'of', 'with'
        }
        
        if param.lower() in js_keywords:
            return False
        
        # Skip very common variable names
        common_vars = {'i', 'j', 'k', 'x', 'y', 'z', 'a', 'b', 'c', 'e', 't', 'n', 'r', 's'}
        if param.lower() in common_vars:
            return False
        
        return True
    
    def _extract_html_input_names(self, content: str) -> Set[str]:
        """
        Extract name/id attributes from HTML input fields
        
        Args:
            content: Content to search (may contain HTML in strings)
            
        Returns:
            Set of parameter names from HTML inputs
        """
        params = set()
        
        # Patterns for HTML input fields
        patterns = [
            r'<input[^>]+name=["\']([^"\']+)["\']',
            r'<input[^>]+id=["\']([^"\']+)["\']',
            r'<textarea[^>]+name=["\']([^"\']+)["\']',
            r'<select[^>]+name=["\']([^"\']+)["\']',
            r'<form[^>]+name=["\']([^"\']+)["\']',
            # Also check for data attributes
            r'data-name=["\']([^"\']+)["\']',
            r'data-field=["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self._is_valid_param(match):
                    params.add(match)
        
        return params
    
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
    
    def _generate_wordlist_sync(self, node, content: str) -> List[str]:
        """Generates custom wordlist from identifiers (synchronous for executor)"""
        words = set()
        
        def traverse(n):
            if n.type in ['identifier', 'property_identifier']:
                text = content[n.start_byte:n.end_byte]
                if len(text) >= self.min_word_length and text.isalpha():
                    words.add(text.lower())
            
            # Extract from string literals and comments
            if n.type == 'string':
                text = content[n.start_byte:n.end_byte].strip('"\'')
                words.update(self._tokenize_text(text))
            
            if n.type == 'comment':
                text = content[n.start_byte:n.end_byte]
                words.update(self._tokenize_text(text))
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        
        # NEW Phase 3a: Extract from HTML content
        html_words = self._extract_words_from_html(content)
        words.update(html_words)
        
        return list(self._filter_wordlist(words))
    
    def _tokenize_text(self, text: str) -> Set[str]:
        """
        Split text into words (Phase 3 enhancement)
        
        Args:
            text: Text to tokenize
            
        Returns:
            Set of words
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove special characters, keep only letters
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Split on whitespace and extract words
        tokens = set()
        for word in text.split():
            if len(word) >= self.min_word_length and word.isalpha():
                tokens.add(word.lower())
        
        return tokens
    
    def _extract_words_from_html(self, content: str) -> Set[str]:
        """
        Extract words from HTML content (Phase 3a)
        
        Args:
            content: Content possibly containing HTML
            
        Returns:
            Set of words from HTML
        """
        words = set()
        
        # HTML Comments
        comments = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
        for comment in comments:
            words.update(self._tokenize_text(comment))
        
        # Image alt text
        alts = re.findall(r'<img[^>]+alt=["\']([^"\']+)["\']', content, re.IGNORECASE)
        for alt in alts:
            words.update(self._tokenize_text(alt))
        
        # Meta tags
        metas = re.findall(r'<meta[^>]+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        for meta in metas:
            words.update(self._tokenize_text(meta))
        
        # Title tags
        titles = re.findall(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        for title in titles:
            words.update(self._tokenize_text(title))
        
        # Aria labels
        aria_labels = re.findall(r'aria-label=["\']([^"\']+)["\']', content, re.IGNORECASE)
        for label in aria_labels:
            words.update(self._tokenize_text(label))
        
        # Placeholder text
        placeholders = re.findall(r'placeholder=["\']([^"\']+)["\']', content, re.IGNORECASE)
        for placeholder in placeholders:
            words.update(self._tokenize_text(placeholder))
        
        return words
    
    # NEW Phase 3b: Stop words list
    STOP_WORDS = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her',
        'was', 'one', 'our', 'out', 'this', 'that', 'from', 'with', 'have',
        'has', 'had', 'been', 'were', 'said', 'there', 'what', 'when', 'where',
        'which', 'who', 'will', 'more', 'than', 'other', 'some', 'time', 'into',
        'could', 'them', 'see', 'him', 'your', 'come', 'its', 'now', 'than',
        'like', 'just', 'know', 'take', 'people', 'year', 'good', 'some', 'would',
        'make', 'their', 'about', 'many', 'then', 'such', 'also', 'only', 'over',
        'think', 'back', 'after', 'use', 'two', 'how', 'work', 'first', 'well',
        'way', 'even', 'want', 'because', 'any', 'these', 'give', 'most', 'should',
        'very', 'being', 'through', 'here', 'each', 'much', 'before', 'however',
        # Common web/programming terms
        'var', 'let', 'const', 'function', 'return', 'void', 'null', 'true', 'false',
        'undefined', 'typeof', 'instanceof', 'new', 'delete', 'class', 'extends',
        'async', 'await', 'export', 'import', 'default', 'require', 'module',
        # Generic words
        'item', 'value', 'object', 'array', 'string', 'number', 'boolean', 'date',
        'error', 'message', 'type', 'name', 'text', 'link', 'image', 'file'
    }
    
    def _filter_wordlist(self, words: set) -> set:
        """Filter out low-quality words from extracted wordlist"""
        filtered = set()
        
        for word in words:
            # Skip very short words (<4 chars)
            if len(word) < 4:
                continue
            
            # NEW Phase 3b: Skip stop words
            if word.lower() in self.STOP_WORDS:
                continue
            
            # Skip words that are all the same character
            if len(set(word)) == 1:
                continue
            
            # Skip words with no vowels
            if not any(c in 'aeiou' for c in word.lower()):
                continue
            
            # Skip words with excessive character repetition (>50% same char)
            if any(word.count(c) > len(word) / 2 for c in set(word)):
                continue
            
            # Skip fragment words ending in vowels (likely cut-off: "abili")
            if len(word) < 6 and word[-1] in 'aeiouy':
                continue
            
            # Skip words with too few vowels (<2 vowels)
            vowel_count = sum(1 for c in word.lower() if c in 'aeiou')
            if vowel_count < 2:
                continue
            
            # Skip words that are mostly numbers
            digit_count = sum(1 for c in word if c.isdigit())
            if digit_count > len(word) / 2:
                continue
            
            # NEW: Skip ALL uppercase words (likely acronyms/constants)
            if word.isupper() and len(word) > 3:
                continue
            
            # NEW: Skip camelCase/PascalCase by splitting and checking each part
            # But only if it would result in valid words
            if word[0].isupper() or any(c.isupper() for c in word[1:]):
                # Skip for now - these are likely variable names
                # Could be enhanced to split and add both parts
                pass
            
            filtered.add(word)
        
        return filtered
    
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
    
    def _extract_with_regex(self, code: str, source_url: str, source_domain: str) -> Dict[str, Any]:
        """Extract data using improved regex patterns with source tracking"""
        
        # ENDPOINTS - Expanded patterns for better detection
        endpoint_patterns = [
            # Specific API paths (high confidence)
            r'["\']/(api|graphql|v\d+|rest|endpoint|ajax|auth|user|admin|cart|checkout|account|payment|order|product|search)/[a-zA-Z0-9/_\-\.]*["\']',
            # fetch() and axios calls
            r'(?:fetch|axios\.[a-z]+|\.get|\.post|\.put|\.delete|\.patch)\s*\(\s*["\']([/][a-zA-Z0-9/_\-\.]+)["\']',
            # Full URLs with API indicators
            r'["\']https?://[a-zA-Z0-9\.\-]+/(api|v\d+|graphql|rest)/[a-zA-Z0-9/_\-\.]*["\']',
            # Any path starting with / (relative paths)
            r'["\']/([\w\-/]+\.(?:js|json|xml|html|php|asp))["\']',
            # href properties and assignments
            r'href\s*:\s*["\']([^"\']+)["\']',
            r'href\s*=\s*["\']([^"\']+)["\']',
            # URL assignments and window.location
            r'(?:url|path|endpoint)\s*:\s*["\']([/][^"\']+)["\']',
            r'window\.location(?:\.href)?\s*=\s*["\']([/][^"\']+)["\']',
        ]
        
        endpoints = []
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    endpoint = match[-1] if match[-1] else (match[0] if len(match) > 0 else '')
                else:
                    endpoint = match
                
                endpoint = endpoint.strip('"\'')
                
                if (endpoint.startswith(('/')) or endpoint.startswith('http')) and \
                   len(endpoint) > 4 and len(endpoint) < 150 and \
                   not any(x in endpoint.lower() for x in ['retry-after', 'content-type', 'x-request', 'cf-ray']) and \
                   not any(x in endpoint.lower() for x in ['swiper-', 'gravity-', '.css', '.scss', '-button']) and \
                   '/' in endpoint[1:] and \
                   self._is_valid_endpoint(endpoint):
                    endpoints.append(endpoint)
        
        # PARAMETERS
        param_patterns = [
            r'[?&]([a-zA-Z_][a-zA-Z0-9_]{1,30})=',
            r'\.(?:set|append|get|has)\s*\(\s*["\']([a-zA-Z_][a-zA-Z0-9_]{1,30})["\']',
            r'params\s*:\s*\{[^}]*["\']([a-zA-Z_][a-zA-Z0-9_]{1,30})["\']',
            r'FormData\s*\.\s*append\s*\(\s*["\']([a-zA-Z_][a-zA-Z0-9_]{1,30})["\']',
        ]
        
        params = []
        for pattern in param_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                param = match if isinstance(match, str) else match[0]
                
                if (len(param) >= 2 and len(param) <= 30 and param[0].isalpha() and
                    param not in ['null', 'this', 'true', 'false', 'undefined', 'render', 'return', 'import', 'export'] and
                    not (len(param) == 2 and param[1].isdigit())):
                    params.append(param)
        
        # DOMAINS
        domain_patterns = [
            r'https?://([a-zA-Z0-9][-a-zA-Z0-9]{0,62}(?:\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+)',
            r'["\']//([a-zA-Z0-9][-a-zA-Z0-9]{0,62}(?:\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+)',
        ]
        
        domains = []
        for pattern in domain_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                domain = match.strip().split('/')[0].split(':')[0]
                
                if ('.' in domain and len(domain) > 4 and len(domain) < 100 and
                    not domain.endswith(('.js', '.css', '.svg', '.png', '.jpg')) and
                    domain not in ['localhost', 'example.com', 'test.com'] and
                    len(domain.split('.')[-1]) >= 2):
                    domains.append(domain)
        
        # Track sources (count occurrences per file)
        from collections import Counter
        
        result = {
            'endpoints': Counter(endpoints),
            'params': Counter(params),
            'domains': Counter(domains),
            'links': Counter([]),
            'source_url': source_url,
            'source_domain': source_domain
        }
        
        return result
    
    async def _analyze_with_regex(self, content: str, source_url: str):
        """Fallback analysis using regex when Tree-sitter is unavailable"""
        
        # Extract domain from source URL
        from urllib.parse import urlparse
        try:
            source_domain = urlparse(source_url).netloc.replace('www.', '')
        except:
            source_domain = 'unknown'
        
        # Extract with source tracking
        extracted = self._extract_with_regex(content, source_url, source_domain)
        
        # Update global database with source tracking
        for extract_type in ['endpoints', 'params', 'domains', 'links']:
            for value, count in extracted[extract_type].items():
                if value not in self.extracts_db[extract_type]:
                    self.extracts_db[extract_type][value] = {
                        'sources': [],
                        'total_count': 0,
                        'domains': set()
                    }
                
                self.extracts_db[extract_type][value]['sources'].append({
                    'file': source_url,
                    'domain': source_domain,
                    'occurrences': count
                })
                self.extracts_db[extract_type][value]['total_count'] += count
                self.extracts_db[extract_type][value]['domains'].add(source_domain)
        
        # Still save to individual files for backwards compatibility
        extracts_path = Path(self.paths['extracts'])
        
        if extracted['endpoints']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'endpoints.txt'),
                list(extracted['endpoints'].keys())
            )
        
        if extracted['params']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'params.txt'),
                list(extracted['params'].keys())
            )
        
        if extracted['domains']:
            await FileOps.append_unique_lines(
                str(extracts_path / 'domains.txt'),
                list(extracted['domains'].keys())
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
    
    def get_extracts_with_sources(self) -> dict:
        """Export extracts database with source information"""
        result = {
            'endpoints': [],
            'params': [],
            'domains': [],
            'links': [],
            'domains_summary': {}
        }
        
        # Convert to list format with source info
        for extract_type in ['endpoints', 'params', 'domains', 'links']:
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
        for extract_type in ['endpoints', 'params']:
            for item in result[extract_type]:
                for source in item['sources']:
                    domain = source['domain']
                    if domain not in domains_summary:
                        domains_summary[domain] = {
                            'endpoints': set(),
                            'params': set(),
                            'file_count': set()
                        }
                    
                    if extract_type == 'endpoints':
                        domains_summary[domain]['endpoints'].add(item['value'])
                    elif extract_type == 'params':
                        domains_summary[domain]['params'].add(item['value'])
                    
                    domains_summary[domain]['file_count'].add(source['file'])
        
        # Convert sets to sorted lists
        for domain, data in domains_summary.items():
            result['domains_summary'][domain] = {
                'endpoints': sorted(list(data['endpoints'])),
                'params': sorted(list(data['params'])),
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
