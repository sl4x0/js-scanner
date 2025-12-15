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
        Creates the complete directory structure for a target
        
        Args:
            target_name: Name of the target (e.g., example.com)
            base_path: Base results directory
            
        Returns:
            Dictionary mapping folder types to their paths
        """
        target_path = Path(base_path) / target_name
        
        # Define structure
        structure = {
            'base': target_path,
            'files_minified': target_path / 'files' / 'minified',
            'files_unminified': target_path / 'files' / 'unminified',
            'extracts': target_path / 'extracts',
            'logs': target_path / 'logs',
            'cache': target_path / 'cache',
            'temp': target_path / 'temp'
        }
        
        # Create all directories
        for path in structure.values():
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize JSON files if they don't exist
        json_files = {
            'secrets': target_path / 'secrets.json',
            'history': target_path / 'history.json',
            'metadata': target_path / 'metadata.json',
            'trufflehog': target_path / 'trufflehog.json'
        }
        
        for name, filepath in json_files.items():
            if not filepath.exists():
                with open(filepath, 'w') as f:
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
        
        # Convert paths to strings for return
        return {k: str(v) for k, v in structure.items()}
    
    @staticmethod
    async def append_to_json(filepath: str, data: Any):
        """
        Appends data to a JSON array file (for secrets.json)
        
        Args:
            filepath: Path to the JSON file
            data: Data to append (dict or list)
        """
        async with aiofiles.open(filepath, 'r') as f:
            content = await f.read()
            existing = json.loads(content) if content else []
        
        if isinstance(existing, list):
            existing.append(data)
        else:
            raise ValueError(f"Expected list in {filepath}")
        
        async with aiofiles.open(filepath, 'w') as f:
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
        async with aiofiles.open(filepath, mode) as f:
            await f.write(content)
    
    @staticmethod
    async def append_unique_lines(filepath: str, lines: list):
        """
        Appends unique lines to a file (for endpoints, params, etc.)
        
        Args:
            filepath: Path to the file
            lines: List of lines to append
        """
        # Read existing lines
        existing = set()
        if os.path.exists(filepath):
            async with aiofiles.open(filepath, 'r') as f:
                content = await f.read()
                existing = set(content.splitlines())
        
        # Filter new unique lines
        new_lines = [line for line in lines if line not in existing]
        
        if new_lines:
            async with aiofiles.open(filepath, 'a') as f:
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
