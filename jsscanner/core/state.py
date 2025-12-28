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


class State:
    """Manages scanner state using JSON files with file locking"""
    
    def __init__(self, target_path: str):
        """
        Initialize state manager
        
        Args:
            target_path: Path to the target's results directory
        """
        self.target_path = Path(target_path)
        
        # Updated paths for reorganized structure (.warehouse/db/)
        db_path = self.target_path / '.warehouse' / 'db'
        findings_path = self.target_path / 'findings'
        
        # CRITICAL: Ensure directories exist BEFORE accessing files
        # Fixes: FileNotFoundError: [Errno 2] No such file or directory
        db_path.mkdir(parents=True, exist_ok=True)
        findings_path.mkdir(parents=True, exist_ok=True)
        
        self.history_file = db_path / 'history.json'
        self.metadata_file = db_path / 'metadata.json'
        self.secrets_file = findings_path / 'secrets.json'
        self.state_file = db_path / 'state.json'
        self.checkpoint_file = db_path / 'checkpoint.json'
        self.bloom_path = db_path / 'state.bloom'
        self.problematic_domains_path = db_path / 'problematic_domains.bloom'
        
        # In-memory state cache for incremental scanning
        self.state = self._load_state()
        
        # Checkpoint tracking
        self.last_checkpoint_time = time.time()
        
        # Bloom filter for O(1) hash lookups (optional, requires pybloom_live)
        self.bloom_filter = self._load_bloom_filter()
        self.bloom_enabled = self.bloom_filter is not None
        
        # Bloom filter for problematic domains (domains that timeout repeatedly)
        self.problematic_domains_filter = self._load_problematic_domains_filter()
        self.problematic_domains_enabled = self.problematic_domains_filter is not None
        
        # Counter for batching problematic domains saves (save every 10 adds)
        self.problematic_domains_save_counter = 0
        
        # Thread lock for Bloom filter operations (thread safety)
        import threading
        self._bloom_lock = threading.Lock()
    
    def _load_bloom_filter(self):
        """
        Load Bloom filter from disk or create new one (optional optimization)
        
        Returns:
            Bloom filter instance or None if pybloom_live not available
        """
        try:
            from pybloom_live import ScalableBloomFilter
            
            if self.bloom_path.exists():
                with open(self.bloom_path, 'rb') as f:
                    return ScalableBloomFilter.fromfile(f)
            else:
                # Create new bloom filter with reasonable defaults
                return ScalableBloomFilter(initial_capacity=100000, error_rate=0.001)
        except ImportError:
            # pybloom_live not installed - graceful degradation to JSON-only
            return None
        except Exception as e:
            # Failed to load bloom filter - continue without it
            return None
    
    def _load_problematic_domains_filter(self):
        """
        Load problematic domains Bloom filter from disk or create new one
        
        Returns:
            Bloom filter instance or None if pybloom_live not available
        """
        try:
            from pybloom_live import ScalableBloomFilter
            
            if self.problematic_domains_path.exists():
                with open(self.problematic_domains_path, 'rb') as f:
                    return ScalableBloomFilter.fromfile(f)
            else:
                # Create new bloom filter with reasonable defaults for domains
                return ScalableBloomFilter(initial_capacity=1000, error_rate=0.01)
        except ImportError:
            return None
        except Exception as e:
            return None
    
    def _save_bloom_filter(self):
        """Save Bloom filter to disk"""
        if self.bloom_filter:
            try:
                self.bloom_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.bloom_path, 'wb') as f:
                    self.bloom_filter.tofile(f)
            except Exception:
                pass  # Silent failure - not critical
    
    def _save_problematic_domains_filter(self):
        """Save problematic domains Bloom filter to disk"""
        if self.problematic_domains_filter:
            try:
                self.problematic_domains_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.problematic_domains_path, 'wb') as f:
                    self.problematic_domains_filter.tofile(f)
            except Exception:
                pass  # Silent failure - not critical
    
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
        Checks if a file hash has already been scanned (O(1) with Bloom filter)
        
        Args:
            file_hash: SHA256 hash of the file
            
        Returns:
            True if already scanned, False otherwise
        """
        # Fast path: Check Bloom filter first (O(1)) with thread safety
        if self.bloom_enabled:
            with self._bloom_lock:
                if file_hash in self.bloom_filter:
                    return True
        
        # Fallback to disk check for accuracy
        with open(self.history_file, 'r+', encoding='utf-8') as f:
            # Acquire shared lock for reading
            self._lock_file(f, exclusive=False)
            try:
                data = json.load(f)
                scanned_hashes = data.get('scanned_hashes', [])
                return file_hash in scanned_hashes
            finally:
                self._unlock_file(f)
    
    def is_problematic_domain(self, domain: str) -> bool:
        """
        Check if domain is marked as problematic (repeated timeouts)
        
        Args:
            domain: Domain name
            
        Returns:
            True if domain is problematic, False otherwise
        """
        if self.problematic_domains_enabled:
            with self._bloom_lock:
                return domain in self.problematic_domains_filter
        return False
    
    def mark_domain_problematic(self, domain: str):
        """
        Mark domain as problematic (add to bloom filter)
        
        Args:
            domain: Domain name to mark
        """
        if self.problematic_domains_enabled:
            with self._bloom_lock:
                self.problematic_domains_filter.add(domain)
            # Batch saves to reduce IO lag (save every 10 additions)
            self.problematic_domains_save_counter += 1
            if self.problematic_domains_save_counter % 10 == 0:
                self._save_problematic_domains_filter()
    
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
                    
                    # Add to Bloom filter for fast lookups (with thread safety)
                    if self.bloom_enabled:
                        with self._bloom_lock:
                            self.bloom_filter.add(file_hash)
                            # Periodically save bloom filter
                            if len(self.bloom_filter) % 1000 == 0:
                                self._save_bloom_filter()
                    
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
    
    # ========== CHECKPOINT SYSTEM (NEW) ==========
    
    def _load_checkpoint(self) -> dict:
        """
        Load checkpoint from disk if it exists.
        
        Returns:
            Checkpoint dictionary or empty template
        """
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                    return checkpoint
            except Exception as e:
                # Corrupted checkpoint - return empty
                return self._create_empty_checkpoint()
        return self._create_empty_checkpoint()
    
    def _create_empty_checkpoint(self) -> dict:
        """Create empty checkpoint structure"""
        return {
            'version': '1.0',
            'timestamp': self._get_timestamp(),
            'phase': 'PHASE_0_START',
            'phase_progress': {
                'current_phase': 0,
                'total_phases': 6,
                'phase_completion': 0.0
            },
            'discovery': {
                'completed': False,
                'urls_discovered': [],
                'total_urls': 0
            },
            'download': {
                'completed': False,
                'downloaded_urls': [],
                'pending_urls': [],
                'failed_urls': {},
                'total_downloaded': 0,
                'total_pending': 0
            },
            'scanning': {
                'completed': False,
                'scanned_files': [],
                'pending_files': [],
                'secrets_found': 0
            },
            'extraction': {
                'completed': False,
                'processed_files': 0,
                'pending_files': 0,
                'extracts': {}
            },
            'beautification': {
                'completed': False,
                'beautified_files': 0,
                'pending_files': 0
            },
            'stats': {
                'elapsed_time': 0.0,
                'files_per_second': 0.0,
                'estimated_remaining': 0.0
            }
        }
    
    def save_checkpoint(self, phase: str, progress: dict) -> None:
        """
        Save checkpoint with current phase and progress.
        Uses atomic write (temp file + rename) to prevent corruption.
        
        Args:
            phase: Current phase identifier (e.g., 'PHASE_2_DOWNLOADING')
            progress: Dictionary with phase-specific progress data
        """
        checkpoint = self._load_checkpoint()
        
        # Update checkpoint
        checkpoint['phase'] = phase
        checkpoint['timestamp'] = self._get_timestamp()
        
        # Merge progress data
        for key, value in progress.items():
            if key in checkpoint:
                if isinstance(checkpoint[key], dict) and isinstance(value, dict):
                    checkpoint[key].update(value)
                else:
                    checkpoint[key] = value
            else:
                checkpoint[key] = value
        
        # Calculate phase completion
        phase_number = self._get_phase_number(phase)
        checkpoint['phase_progress']['current_phase'] = phase_number
        
        # Atomic write: write to temp file, then rename
        temp_file = self.checkpoint_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
            
            # Atomic rename (overwrites existing checkpoint)
            temp_file.replace(self.checkpoint_file)
            
            self.last_checkpoint_time = time.time()
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            # Log error but don't fail scan
            pass
    
    def has_checkpoint(self) -> bool:
        """
        Check if a resumable checkpoint exists.
        
        Returns:
            True if checkpoint exists and scan is not complete
        """
        if not self.checkpoint_file.exists():
            return False
        
        try:
            checkpoint = self._load_checkpoint()
            # Check if scan was completed
            phase = checkpoint.get('phase', '')
            if phase == 'PHASE_6_COMPLETE':
                return False
            
            # Check if checkpoint is recent (within 7 days)
            timestamp_str = checkpoint.get('timestamp', '')
            if timestamp_str:
                checkpoint_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                days_old = (datetime.now(checkpoint_time.tzinfo) - checkpoint_time).days
                if days_old > 7:
                    return False
            
            return True
        except Exception:
            return False
    
    def get_resume_state(self) -> dict:
        """
        Get checkpoint state for resuming scan.
        
        Returns:
            Checkpoint dictionary with all saved progress
        """
        return self._load_checkpoint()
    
    def delete_checkpoint(self) -> None:
        """Delete checkpoint file (call on successful scan completion)"""
        if self.checkpoint_file.exists():
            try:
                self.checkpoint_file.unlink()
            except Exception:
                pass
    
    def should_save_checkpoint(self, frequency: int = 10) -> bool:
        """
        Determine if checkpoint should be saved based on time/frequency.
        
        Args:
            frequency: Minimum seconds between checkpoints (default: 30s)
            
        Returns:
            True if enough time has passed since last checkpoint
        """
        # Also save based on time (every 30 seconds)
        time_threshold = frequency
        return (time.time() - self.last_checkpoint_time) >= time_threshold
    
    @staticmethod
    def _get_phase_number(phase: str) -> int:
        """Extract phase number from phase string"""
        phase_map = {
            'PHASE_0_START': 0,
            'PHASE_1_DISCOVERY': 1,
            'PHASE_1_COMPLETE': 1,
            'PHASE_2_DOWNLOADING': 2,
            'PHASE_2_COMPLETE': 2,
            'PHASE_3_SCANNING': 3,
            'PHASE_3_COMPLETE': 3,
            'PHASE_4_EXTRACTION': 4,
            'PHASE_4_COMPLETE': 4,
            'PHASE_5_BEAUTIFICATION': 5,
            'PHASE_5_COMPLETE': 5,
            'PHASE_6_COMPLETE': 6
        }
        return phase_map.get(phase, 0)
    
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """
        Calculate hash of relevant config fields that affect scanning
        
        Args:
            config: Configuration dictionary
            
        Returns:
            SHA256 hash of config
        """
        # Only hash fields that affect scan results
        relevant_fields = {
            'threads': config.get('threads'),
            'timeout': config.get('timeout'),
            'min_file_size': config.get('min_file_size'),
            'max_file_size': config.get('max_file_size'),
            'recover_source_maps': config.get('recover_source_maps'),
            'trufflehog_path': config.get('trufflehog_path'),
            'trufflehog_extra_args': config.get('trufflehog_extra_args'),
            'wordlist_extraction': config.get('wordlist_extraction'),
            'beautify': config.get('beautify'),
            'unpack_bundles': config.get('unpack_bundles')
        }
        
        # Serialize to JSON and hash
        config_str = json.dumps(relevant_fields, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def check_config_changed(self, current_config: Dict[str, Any]) -> bool:
        """
        Check if config has changed since last scan
        
        Args:
            current_config: Current configuration dictionary
            
        Returns:
            True if config changed, False otherwise
        """
        current_hash = self._calculate_config_hash(current_config)
        
        try:
            metadata = self.get_metadata()
            last_config_hash = metadata.get('config_hash')
            
            if not last_config_hash:
                # First scan, store hash
                self.update_metadata({'config_hash': current_hash})
                return False
            
            return current_hash != last_config_hash
            
        except (FileNotFoundError, json.JSONDecodeError):
            # No previous scan
            return False
    
    def update_config_hash(self, config: Dict[str, Any]):
        """
        Update stored config hash
        
        Args:
            config: Current configuration dictionary
        """
        config_hash = self._calculate_config_hash(config)
        self.update_metadata({'config_hash': config_hash})
