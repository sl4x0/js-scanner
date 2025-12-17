"""
State Manager
Handles JSON file operations with file locking for thread-safe access
Implements incremental scanning with hash-based change detection
"""
import json
import os
import sys
import time
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import io

# Platform-specific file locking
if sys.platform == 'win32':
    import msvcrt
else:
    import fcntl


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
        self.state_file = self.target_path / 'state.json'
        
        # In-memory state cache for incremental scanning
        self.state = self._load_state()
    
    def _lock_file(self, file_obj, exclusive=True):
        """
        Cross-platform file locking with retry logic
        
        Windows: Uses msvcrt with retry on permission denied
        Linux: Uses fcntl with blocking lock
        """
        if sys.platform == 'win32':
            # Windows file locking with retry
            max_retries = 10
            retry_delay = 0.01  # 10ms
            
            for attempt in range(max_retries):
                try:
                    # Try to lock the file
                    lock_mode = msvcrt.LK_LOCK if exclusive else msvcrt.LK_NBLCK
                    msvcrt.locking(file_obj.fileno(), lock_mode, 1)
                    return  # Success
                except (OSError, IOError) as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        # Last attempt failed - proceed without lock
                        pass
        else:
            # Unix file locking (blocking)
            fcntl.flock(file_obj.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
    
    def _unlock_file(self, file_obj):
        """Cross-platform file unlocking"""
        if sys.platform == 'win32':
            try:
                msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
            except:
                pass  # Ignore unlocking errors on Windows
        else:
            fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
    
    def is_scanned(self, file_hash: str) -> bool:
        """
        Checks if a file hash has already been scanned
        
        Args:
            file_hash: SHA256 hash of the file
            
        Returns:
            True if already scanned, False otherwise
        """
        with open(self.history_file, 'r+', encoding='utf-8') as f:
            # Acquire shared lock for reading
            self._lock_file(f, exclusive=False)
            try:
                data = json.load(f)
                scanned_hashes = data.get('scanned_hashes', [])
                return file_hash in scanned_hashes
            finally:
                self._unlock_file(f)
    
    def mark_as_scanned(self, file_hash: str, url: str = None):
        """
        Marks a file hash as scanned
        
        Args:
            file_hash: SHA256 hash of the file
            url: Optional URL where the file was found
        """
        with open(self.history_file, 'r+', encoding='utf-8') as f:
            # Acquire exclusive lock for writing
            self._lock_file(f, exclusive=True)
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
                self._unlock_file(f)
    
    def mark_as_scanned_if_new(self, file_hash: str, url: str = None) -> bool:
        """
        Atomically checks if hash is new and marks it as scanned
        Prevents race condition between is_scanned() and mark_as_scanned()
        
        Args:
            file_hash: SHA256 hash of the file
            url: Optional URL where the file was found
            
        Returns:
            True if newly marked (should process), False if already exists (skip)
        """
        with open(self.history_file, 'r+', encoding='utf-8') as f:
            self._lock_file(f, exclusive=True)
            try:
                f.seek(0)
                data = json.load(f)
                
                # Check if already scanned (atomic)
                if file_hash in data['scanned_hashes']:
                    return False  # Already exists
                
                # Mark as scanned
                data['scanned_hashes'].append(file_hash)
                
                if 'scan_metadata' not in data:
                    data['scan_metadata'] = {}
                
                data['scan_metadata'][file_hash] = {
                    'url': url,
                    'timestamp': self._get_timestamp()
                }
                
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
                return True  # Newly added
            finally:
                self._unlock_file(f)
    
    def add_secret(self, secret_data: Dict[str, Any]):
        """
        Adds a verified secret to secrets.json
        
        Args:
            secret_data: Dictionary containing secret information
        """
        with open(self.secrets_file, 'r+', encoding='utf-8') as f:
            # Acquire exclusive lock
            self._lock_file(f, exclusive=True)
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
                self._unlock_file(f)
    
    def update_metadata(self, updates: Dict[str, Any]):
        """
        Updates metadata.json with scan statistics
        
        Args:
            updates: Dictionary of fields to update
        """
        with open(self.metadata_file, 'r+', encoding='utf-8') as f:
            # Acquire exclusive lock
            self._lock_file(f, exclusive=True)
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
                self._unlock_file(f)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Retrieves current metadata
        
        Returns:
            Dictionary containing metadata
        """
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            self._lock_file(f, exclusive=False)
            try:
                return json.load(f)
            finally:
                self._unlock_file(f)
    
    def get_total_secrets(self) -> int:
        """
        Gets the total number of secrets found
        
        Returns:
            Count of secrets
        """
        with open(self.secrets_file, 'r', encoding='utf-8') as f:
            self._lock_file(f, exclusive=False)
            try:
                secrets = json.load(f)
                return len(secrets)
            finally:
                self._unlock_file(f)
    
    @staticmethod
    def _get_timestamp() -> str:
        """
        Gets current timestamp in ISO format
        
        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def _load_state(self) -> Dict:
        """Load state file for incremental scanning"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Return default state structure
        return {
            'version': '1.0',
            'files': {},
            'stats': {
                'total_scans': 0,
                'total_files_ever': 0,
                'endpoints_found': 0,
                'secrets_found': 0
            },
            'last_scan': None
        }
    
    def _save_state(self) -> None:
        """Save state to disk"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            # Non-critical - don't fail scan if state save fails
            pass
    
    def should_rescan_file(self, url: str, new_hash: str, force: bool = False) -> bool:
        """
        Determine if file needs rescanning based on hash comparison
        
        Args:
            url: File URL
            new_hash: Current hash of file
            force: If True, always rescan
            
        Returns:
            True if file should be scanned, False to skip
        """
        if force:
            return True
        
        file_state = self.state.get('files', {}).get(url)
        
        if not file_state:
            # Never scanned before
            return True
        
        old_hash = file_state.get('hash')
        if old_hash != new_hash:
            # Content changed
            return True
        
        # Optional: Force rescan after 30 days
        try:
            last_scan_str = file_state.get('last_scanned')
            if last_scan_str:
                last_scan = datetime.fromisoformat(last_scan_str.replace('Z', '+00:00'))
                days_old = (datetime.now(last_scan.tzinfo) - last_scan).days
                
                if days_old > 30:
                    return True
        except Exception:
            pass
        
        return False
    
    def mark_file_scanned(self, url: str, file_hash: str, metadata: Optional[Dict] = None) -> None:
        """
        Record that file was scanned with its hash and metadata
        
        Args:
            url: File URL
            file_hash: Content hash
            metadata: Optional metadata (status, size, findings, etc.)
        """
        if 'files' not in self.state:
            self.state['files'] = {}
        
        if metadata is None:
            metadata = {}
        
        self.state['files'][url] = {
            'hash': file_hash,
            'last_scanned': self._get_timestamp(),
            'status': metadata.get('status', 200),
            'size': metadata.get('size', 0),
            'endpoints_found': metadata.get('endpoints', 0),
            'secrets_found': metadata.get('secrets', 0),
            'extracted': metadata.get('extracted', False)
        }
        
        # Update global stats
        self.state['stats']['total_files_ever'] = len(self.state['files'])
        self.state['last_scan'] = self._get_timestamp()
        
        # Save state periodically (every 10 files)
        if len(self.state['files']) % 10 == 0:
            self._save_state()
    
    def finalize_scan(self) -> None:
        """Save final state after scan completes"""
        self.state['stats']['total_scans'] += 1
        self._save_state()
    
    def get_scan_stats(self) -> Dict:
        """Get incremental scanning statistics"""
        total_files = len(self.state.get('files', {}))
        return {
            'total_files_tracked': total_files,
            'total_scans': self.state.get('stats', {}).get('total_scans', 0),
            'last_scan': self.state.get('last_scan'),
            'endpoints_found': self.state.get('stats', {}).get('endpoints_found', 0),
            'secrets_found': self.state.get('stats', {}).get('secrets_found', 0)
        }
