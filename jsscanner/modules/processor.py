"""
Processor Module
Handles JavaScript beautification and source map extraction
"""
import jsbeautifier
import re
import base64
import json
from typing import Optional


class Processor:
    """Processes JavaScript files (beautify, extract source maps)"""
    
    def __init__(self, logger) -> None:
        """
        Initialize processor
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.beautifier_options = jsbeautifier.default_options()
        self.beautifier_options.indent_size = 2
    
    async def process(self, content: str, file_path: str) -> str:
        """
        Processes JavaScript content
        
        Args:
            content: JavaScript content
            file_path: Path where file is saved
            
        Returns:
            Processed (beautified) content
        """
        # Try to extract source map first
        source_map_content = await self._extract_source_map(content, file_path)
        
        if source_map_content:
            self.logger.info(f"Extracted source map for {file_path}")
            return source_map_content
        
        # Otherwise, beautify the minified code
        return await self._beautify(content)
    
    async def _beautify(self, content: str) -> str:
        """
        Beautifies minified JavaScript
        
        Args:
            content: Minified JavaScript
            
        Returns:
            Beautified JavaScript
            
        Raises:
            ValueError: If content is invalid
        """
        import asyncio
        
        # Skip beautification for very large files (>20MB) - too slow and memory-intensive
        content_size_mb = len(content) / (1024 * 1024)
        if content_size_mb > 20.0:
            self.logger.warning(f"Skipping beautification for large file ({content_size_mb:.1f}MB, limit: 20MB)")
            return content
        
        try:
            # Issue #14 & #3: Practical timeout thresholds to prevent extreme scan times
            # Small files (<1MB): 60s, Medium (<5MB): 180s (3min), Large (<10MB): 600s (10min), Very Large (20MB): 1800s (30min)
            if content_size_mb < 1.0:
                timeout = 60.0
            elif content_size_mb < 5.0:
                timeout = 180.0  # 3 minutes
            elif content_size_mb < 10.0:
                timeout = 600.0  # 10 minutes
            else:
                timeout = 1800.0  # 30 minutes max for 10-20MB files
            
            loop = asyncio.get_event_loop()
            beautified = await asyncio.wait_for(
                loop.run_in_executor(None, jsbeautifier.beautify, content, self.beautifier_options),
                timeout=timeout
            )
            return beautified
        except asyncio.TimeoutError:
            self.logger.warning(f"Beautification timed out after {timeout}s ({content_size_mb:.1f}MB file), using original content")
            return content
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Failed to beautify (invalid content): {e}")
            return content
        except Exception as e:
            self.logger.error(f"Unexpected error during beautification: {e}", exc_info=True)
            return content
    
    async def _extract_source_map(self, content: str, file_path: str) -> Optional[str]:
        """
        Extracts and decodes source map if present
        
        Args:
            content: JavaScript content
            file_path: Path to the file
            
        Returns:
            Extracted source content or None
        """
        # Look for inline source map
        inline_pattern = r'//# sourceMappingURL=data:application/json;base64,([A-Za-z0-9+/=]+)'
        match = re.search(inline_pattern, content)
        
        if match:
            try:
                # Decode base64 source map
                encoded_map = match.group(1)
                decoded_map = base64.b64decode(encoded_map).decode('utf-8')
                source_map = json.loads(decoded_map)
                
                # Extract original sources
                if 'sourcesContent' in source_map and source_map['sourcesContent']:
                    # Combine all sources
                    combined_source = '\n\n// ===== SOURCE FILE =====\n\n'.join(
                        source for source in source_map['sourcesContent'] if source
                    )
                    return combined_source
                
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse source map JSON: {e}")
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Invalid source map structure: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error extracting source map: {e}", exc_info=True)
        
        # Look for external source map reference
        external_pattern = r'//# sourceMappingURL=(.+\.map)'
        match = re.search(external_pattern, content)
        
        if match:
            self.logger.info(f"Found external source map reference: {match.group(1)}")
            # Note: External source map fetching would require additional logic
            # For now, we'll just note it was found
        
        return None
    
    async def extract_strings(self, content: str) -> list:
        """
        Extracts all string literals from JavaScript
        
        Args:
            content: JavaScript content
            
        Returns:
            List of extracted strings
        """
        # Match strings in single and double quotes
        pattern = r'["\']([^"\'\\]*(\\.[^"\'\\]*)*)["\']'
        matches = re.findall(pattern, content)
        
        # Extract just the string content (first group)
        strings = [match[0] for match in matches if match[0]]
        
        return strings
    
    async def remove_comments(self, content: str) -> str:
        """
        Removes JavaScript comments
        
        Args:
            content: JavaScript content
            
        Returns:
            Content without comments
        """
        # Remove single-line comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content
