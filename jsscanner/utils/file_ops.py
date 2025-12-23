"""
File Operations Utility
Creates result folders dynamically and manages file I/O
"""
import os
import json
import aiofiles
from pathlib import Path
from typing import Any, Dict


class FileOps:
    """Handles all file operations for the scanner"""
    
    @staticmethod
    def create_result_structure(target_name: str, base_path: str = "results") -> Dict[str, str]:
        """
        Creates the Tiered Directory Structure (Hunter-Architect Standard)
        
        Implements the "Warehouse vs. Showroom" model:
        - TIER 1: REPORT.md (Executive Summary)
        - TIER 2: findings/ (High-value intelligence)
        - TIER 3: artifacts/ (Human-readable evidence)
        - TIER 4: logs/ (Audit trail)
        - TIER 5: .warehouse/ (Hidden machine data)
        
        Args:
            target_name: Name of the target (e.g., example.com)
            base_path: Base results directory
            
        Returns:
            Dictionary mapping folder types to their paths (backward compatible)
        """
        root = Path(base_path) / target_name
        
        # Define The Tiers
        dirs = {
            # Root
            'base': root,
            
            # TIER 2: Findings (The intelligence - clean outputs for pipelines)
            'findings': root / 'findings',
            
            # TIER 3: Artifacts (Readable code/evidence)
            'source_code': root / 'artifacts' / 'source_code',
            'artifacts': root / 'artifacts',
            
            # TIER 4: Logs (Audit trail)
            'logs': root / 'logs',
            
            # TIER 5: The Warehouse (Hidden/Raw data - machine processing zone)
            'warehouse': root / '.warehouse',
            'raw_js': root / '.warehouse' / 'raw_js',
            'db': root / '.warehouse' / 'db',
            'temp': root / '.warehouse' / 'temp',
            'minified': root / '.warehouse' / 'minified',
            'unminified': root / '.warehouse' / 'unminified',
            'cache': root / '.warehouse' / 'cache',
            'final_source': root / '.warehouse' / 'final_source'
        }

        # Create all directories
        for p in dirs.values():
            p.mkdir(parents=True, exist_ok=True)

        # Map to backward-compatible keys (Engine expects these exact names)
        paths = {
            'base': str(dirs['base']),
            'logs': str(dirs['logs']),
            
            # Findings mapped to TIER 2 (findings/)
            'extracts': str(dirs['findings']),   # endpoints.txt, params.txt go here
            'secrets': str(dirs['findings']),    # secrets.json goes here
            
            # Artifacts mapped to TIER 3 (artifacts/)
            'source_code': str(dirs['source_code']),
            
            # Warehouse mapped to TIER 5 (.warehouse/)
            'unique_js': str(dirs['raw_js']),
            'final_source_code': str(dirs['final_source']),
            'cache': str(dirs['cache']),
            'temp': str(dirs['temp']),
            'files_minified': str(dirs['minified']),
            'files_unminified': str(dirs['unminified']),
            
            # Database files (in .warehouse/db/)
            'history_file': str(dirs['db'] / 'history.json'),
            'metadata_file': str(dirs['db'] / 'metadata.json')
        }
        
        # Initialize JSON database files if they don't exist
        json_files = {
            'secrets': dirs['findings'] / 'secrets.json',
            'trufflehog': dirs['findings'] / 'trufflehog.json',
            'history': dirs['db'] / 'history.json',
            'metadata': dirs['db'] / 'metadata.json'
        }
        
        for name, filepath in json_files.items():
            if not filepath.exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    if name == 'history':
                        json.dump({'scanned_hashes': [], 'scan_metadata': {}}, f, indent=2)
                    elif name == 'metadata':
                        json.dump({
                            'total_files': 0,
                            'total_secrets': 0,
                            'scan_duration': 0,
                            'errors': [],
                            'start_time': None,
                            'end_time': None,
                            'source_urls': []
                        }, f, indent=2)
                    else:
                        json.dump([], f, indent=2)
        
        return paths
    
    @staticmethod
    async def append_to_json(filepath: str, data: Any):
        """
        Appends data to a JSON array file (for secrets.json)
        
        Args:
            filepath: Path to the JSON file
            data: Data to append (dict or list)
        """
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            existing = json.loads(content) if content else []
        
        if isinstance(existing, list):
            existing.append(data)
        else:
            raise ValueError(f"Expected list in {filepath}")
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(existing, indent=2))
    
    @staticmethod
    async def write_text_file(filepath: str, content: str, mode: str = 'w'):
        """
        Writes content to a text file
        
        Args:
            filepath: Path to the file
            content: Content to write
            mode: File mode ('w' or 'a')
        """
        async with aiofiles.open(filepath, mode, encoding='utf-8') as f:
            await f.write(content)
    
    @staticmethod
    async def append_unique_lines(filepath: str, lines: list):
        """
        Appends unique lines to a file (for endpoints, params, etc.)
        
        Args:
            filepath: Path to the file
            lines: List of lines to append
        """
        # Read existing lines with UTF-8 encoding (Windows fix)
        existing = set()
        if os.path.exists(filepath):
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                existing = set(content.splitlines())
        
        # Filter new unique lines
        new_lines = [line for line in lines if line not in existing]
        
        if new_lines:
            async with aiofiles.open(filepath, 'a', encoding='utf-8') as f:
                await f.write('\n'.join(new_lines) + '\n')
    
    @staticmethod
    def get_target_path(target_name: str, base_path: str = "results") -> str:
        """
        Gets the path for a target's results directory
        
        Args:
            target_name: Name of the target
            base_path: Base results directory
            
        Returns:
            Path to target directory
        """
        return str(Path(base_path) / target_name)
