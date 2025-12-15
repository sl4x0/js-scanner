"""
State Manager
Handles JSON file operations with file locking for thread-safe access
"""
import json
import fcntl
import os
from typing import List, Dict, Any
from pathlib import Path


class StateManager:
    """Manages scanner state using JSON files with file locking"""
    
    def __init__(self, target_path: str):
        """
        Initialize state manager
        
        Args:
            target_path: Path to the target's results directory
        """
        self.target_path = Path(target_path)
        self.history_file = self.target_path / 'history.json'
        self.secrets_file = self.target_path / 'secrets.json'
        self.metadata_file = self.target_path / 'metadata.json'
    
    def is_scanned(self, file_hash: str) -> bool:
        """
        Checks if a file hash has already been scanned
        
        Args:
            file_hash: SHA256 hash of the file
            
        Returns:
            True if already scanned, False otherwise
        """
        with open(self.history_file, 'r+') as f:
            # Acquire shared lock for reading
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
                scanned_hashes = data.get('scanned_hashes', [])
                return file_hash in scanned_hashes
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def mark_as_scanned(self, file_hash: str, url: str = None):
        """
        Marks a file hash as scanned
        
        Args:
            file_hash: SHA256 hash of the file
            url: Optional URL where the file was found
        """
        with open(self.history_file, 'r+') as f:
            # Acquire exclusive lock for writing
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                data = json.load(f)
                
                if file_hash not in data['scanned_hashes']:
                    data['scanned_hashes'].append(file_hash)
                    
                    # Optionally store metadata about the hash
                    if 'scan_metadata' not in data:
                        data['scan_metadata'] = {}
                    
                    data['scan_metadata'][file_hash] = {
                        'url': url,
                        'timestamp': self._get_timestamp()
                    }
                    
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def add_secret(self, secret_data: Dict[str, Any]):
        """
        Adds a verified secret to secrets.json
        
        Args:
            secret_data: Dictionary containing secret information
        """
        with open(self.secrets_file, 'r+') as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                secrets = json.load(f)
                
                # Add timestamp if not present
                if 'timestamp' not in secret_data:
                    secret_data['timestamp'] = self._get_timestamp()
                
                secrets.append(secret_data)
                
                f.seek(0)
                f.truncate()
                json.dump(secrets, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def update_metadata(self, updates: Dict[str, Any]):
        """
        Updates metadata.json with scan statistics
        
        Args:
            updates: Dictionary of fields to update
        """
        with open(self.metadata_file, 'r+') as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                metadata = json.load(f)
                
                # Update fields
                for key, value in updates.items():
                    if key == 'errors' and isinstance(value, list):
                        # Append errors instead of replacing
                        metadata.setdefault('errors', []).extend(value)
                    elif key in ['total_files', 'total_secrets']:
                        # Increment counters
                        metadata[key] = metadata.get(key, 0) + value
                    else:
                        metadata[key] = value
                
                # Add last updated timestamp
                metadata['last_updated'] = self._get_timestamp()
                
                f.seek(0)
                f.truncate()
                json.dump(metadata, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Retrieves current metadata
        
        Returns:
            Dictionary containing metadata
        """
        with open(self.metadata_file, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def get_total_secrets(self) -> int:
        """
        Gets the total number of secrets found
        
        Returns:
            Count of secrets
        """
        with open(self.secrets_file, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                secrets = json.load(f)
                return len(secrets)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    @staticmethod
    def _get_timestamp() -> str:
        """
        Gets current timestamp in ISO format
        
        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
