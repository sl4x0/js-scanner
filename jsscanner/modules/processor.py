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
    """Processes JavaScript files (beautify, extract source maps, OR unpack bundles)"""
    
    def __init__(self, logger, skip_beautification: bool = False, config: dict = None) -> None:
        """
        Initialize processor
        
        Args:
            logger: Logger instance
            skip_beautification: If True, skip beautification step for faster scans
            config: Configuration dictionary
        """
        self.logger = logger
        self.skip_beautification = skip_beautification
        self.config = config or {}
        self.beautifier_options = jsbeautifier.default_options()
        self.beautifier_options.indent_size = 2
        
        # v3.0: Initialize bundle unpacker
        from .bundle_unpacker import BundleUnpacker
        self.unpacker = BundleUnpacker(logger, config=self.config)
    
    async def process(self, content: str, file_path: str) -> str:
        """
        Processes JavaScript content (v3.0: with bundle unpacking)
        
        Args:
            content: JavaScript content
            file_path: Path where file is saved
            
        Returns:
            Processed (beautified or unpacked) content
        """
        file_size = len(content)
        
        # v3.0: Check if should unpack bundle (respects config.bundle_unpacker.enabled)
        if await self.unpacker.should_unpack(content, file_size):
            from pathlib import Path
            file_stem = Path(file_path).stem
            output_dir = Path(file_path).parent.parent / 'unpacked' / file_stem
            
            self.logger.info(f"🔧 Attempting bundle unpacking for {file_stem}")
            
            # Attempt bundle unpacking
            result = await self.unpacker.unpack_bundle(file_path, str(output_dir))
            
            if result and result['success']:
                self.logger.info(f"✅ Bundle unpacked: {result['file_count']} files extracted")
                # Return original content (unpacked files stored separately)
                return content
            else:
                self.logger.warning("⚠️  Bundle unpacking failed, falling back to beautification")
        
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
        
        # Skip beautification if disabled globally
        if self.skip_beautification:
            return content
        
        # Skip beautification for very large files (>20MB) - too slow and memory-intensive
        content_size_mb = len(content) / (1024 * 1024)
        if content_size_mb > 20.0:
            self.logger.warning(f"Skipping beautification for large file ({content_size_mb:.1f}MB, limit: 20MB)")
            return content
        
        try:
            # Configurable timeout thresholds from config.yaml
            beautification_config = self.config.get('beautification', {})
            if content_size_mb < 1:
                timeout = beautification_config.get('timeout_small', 120)
            elif content_size_mb < 5:
                timeout = beautification_config.get('timeout_medium', 300)
            elif content_size_mb < 10:
                timeout = beautification_config.get('timeout_large', 900)
            else:
                timeout = beautification_config.get('timeout_xlarge', 1800)
            
            loop = asyncio.get_event_loop()
            beautified = await asyncio.wait_for(
                loop.run_in_executor(None, jsbeautifier.beautify, content, self.beautifier_options),
                timeout=timeout
            )
            return beautified
        except asyncio.TimeoutError:
            self.logger.debug(f"Beautification timed out after {timeout}s ({content_size_mb:.1f}MB file), using original content")
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
            self.logger.debug(f"Found external source map reference: {match.group(1)}")
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
    
    async def assess_beautification_quality(self, original: str, beautified: str) -> dict:
        """
        Assess beautification quality by comparing original and beautified content.
        
        Provides metrics to evaluate how well the beautification process worked,
        which helps identify cases where:
        - Code was already well-formatted (minimal improvement)
        - Beautification was highly effective (large improvement)
        - Potential issues with the beautification process
        
        Args:
            original: Original (potentially minified) JavaScript content
            beautified: Beautified JavaScript content
            
        Returns:
            Dictionary with quality metrics:
            {
                'expansion_ratio': float,  # beautified_size / original_size
                'avg_line_length_before': float,
                'avg_line_length_after': float,
                'line_count_before': int,
                'line_count_after': int,
                'quality_score': str,  # 'excellent', 'good', 'poor', 'failed'
                'recommendations': list  # List of recommended actions
            }
        """
        # Prevent division by zero
        if not original or not beautified:
            return {
                'expansion_ratio': 0.0,
                'avg_line_length_before': 0.0,
                'avg_line_length_after': 0.0,
                'line_count_before': 0,
                'line_count_after': 0,
                'quality_score': 'failed',
                'recommendations': ['Empty content - beautification failed']
            }
        
        orig_lines = original.split('\n')
        beau_lines = beautified.split('\n')
        
        # Calculate metrics
        expansion_ratio = len(beautified) / len(original) if len(original) > 0 else 0
        avg_line_before = sum(len(l) for l in orig_lines) / len(orig_lines) if orig_lines else 0
        avg_line_after = sum(len(l) for l in beau_lines) / len(beau_lines) if beau_lines else 0
        
        metrics = {
            'expansion_ratio': round(expansion_ratio, 2),
            'avg_line_length_before': round(avg_line_before, 1),
            'avg_line_length_after': round(avg_line_after, 1),
            'line_count_before': len(orig_lines),
            'line_count_after': len(beau_lines),
            'recommendations': []
        }
        
        # Quality assessment based on expansion ratio and line length
        if expansion_ratio > 2.0 and avg_line_after < 100:
            # Excellent: Significant expansion with reasonable line lengths
            metrics['quality_score'] = 'excellent'
            metrics['recommendations'].append('Beautification highly effective')
        elif expansion_ratio > 1.5 and avg_line_after < 150:
            # Good: Moderate expansion with good formatting
            metrics['quality_score'] = 'good'
            metrics['recommendations'].append('Beautification successful')
        elif expansion_ratio > 1.1:
            # Poor: Minimal expansion suggests limited improvement
            metrics['quality_score'] = 'poor'
            metrics['recommendations'].append('Limited improvement - file may be already formatted or heavily obfuscated')
            if avg_line_after > 200:
                metrics['recommendations'].append('Consider manual formatting - lines still very long')
        else:
            # Failed: No expansion suggests beautification had no effect
            metrics['quality_score'] = 'failed'
            metrics['recommendations'].append('Beautification had minimal effect')
            if expansion_ratio < 1.0:
                metrics['recommendations'].append('Content reduced in size - possible data loss')
            else:
                metrics['recommendations'].append('File may already be formatted or use custom minification')
        
        return metrics
