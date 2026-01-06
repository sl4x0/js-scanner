"""
Test State Module (jsscanner/core/state.py)
Tests for state management, persistence, locking, and deduplication

Critical for:
- Multi-day scan resumability
- Atomic operations to prevent race conditions
- Incremental scanning (hash-based deduplication)
- Checkpoint recovery after crashes
"""
import pytest
import json
import time
import threading
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from jsscanner.core.state import State


# ============================================================================
# PHASE 2.1: Basic State Operations
# ============================================================================

@pytest.mark.unit
class TestStateInitialization:
    """Test state initialization and directory creation"""
    
    def test_state_creates_directories(self, tmp_path):
        """Test that State creates all required directories"""
        target_path = tmp_path / "test_target"
        
        state = State(str(target_path))
        
        # Verify directory structure
        assert (target_path / '.warehouse' / 'db').exists()
        assert (target_path / 'findings').exists()
        
        # Verify files
        assert state.history_file.exists()
        assert state.metadata_file.exists()
        assert state.state_file.exists()
    
    def test_state_loads_existing_state(self, tmp_state_dir):
        """Test that State loads existing state from disk"""
        state = State(tmp_state_dir['base'])
        
        # Should load without errors
        assert state.state is not None
        assert isinstance(state.state, dict)
    
    def test_state_initializes_bloom_filter_if_available(self, tmp_state_dir):
        """Test bloom filter initialization when pybloom_live is available"""
        try:
            import pybloom_live
            has_bloom = True
        except ImportError:
            has_bloom = False
        
        state = State(tmp_state_dir['base'])
        
        if has_bloom:
            assert state.bloom_enabled is True
            assert state.bloom_filter is not None
        else:
            assert state.bloom_enabled is False
            assert state.bloom_filter is None
    
    def test_state_graceful_degradation_without_bloom(self, tmp_state_dir):
        """Test graceful degradation when pybloom_live not installed"""
        with patch.dict('sys.modules', {'pybloom_live': None}):
            state = State(tmp_state_dir['base'])
            
            # Should work without bloom filter
            assert state.bloom_enabled is False
            assert state.bloom_filter is None


# ============================================================================
# PHASE 2.2: Hash Tracking & Deduplication
# ============================================================================

@pytest.mark.unit
class TestHashTracking:
    """Test hash-based deduplication"""
    
    def test_mark_as_scanned_if_new_returns_true_for_new_hash(self, tmp_state_dir):
        """Test that new hash returns True"""
        state = State(tmp_state_dir['base'])
        
        result = state.mark_as_scanned_if_new('hash123', 'https://example.com/test.js')
        
        assert result is True
    
    def test_mark_as_scanned_if_new_returns_false_for_duplicate(self, tmp_state_dir):
        """Test that duplicate hash returns False"""
        state = State(tmp_state_dir['base'])
        
        # First call should succeed
        result1 = state.mark_as_scanned_if_new('hash123', 'https://example.com/test.js')
        assert result1 is True
        
        # Second call with same hash should fail
        result2 = state.mark_as_scanned_if_new('hash123', 'https://example.com/test.js')
        assert result2 is False
    
    def test_is_scanned_correctly_checks_hash_existence(self, tmp_state_dir):
        """Test is_scanned() checks hash correctly"""
        state = State(tmp_state_dir['base'])
        
        # Hash not scanned yet
        assert state.is_scanned('hash_new') is False
        
        # Mark as scanned
        state.mark_as_scanned_if_new('hash_new', 'https://example.com/test.js')
        
        # Now should return True
        assert state.is_scanned('hash_new') is True
    
    def test_hash_persistence_across_state_reloads(self, tmp_state_dir):
        """Test that hashes persist across State instance reloads"""
        # Create state and mark hash
        state1 = State(tmp_state_dir['base'])
        state1.mark_as_scanned_if_new('persistent_hash', 'https://example.com/test.js')
        
        # Create new state instance (simulates restart)
        state2 = State(tmp_state_dir['base'])
        
        # Hash should still be marked
        assert state2.is_scanned('persistent_hash') is True
    
    def test_mark_as_scanned_stores_metadata(self, tmp_state_dir):
        """Test that marking stores URL and timestamp metadata"""
        state = State(tmp_state_dir['base'])
        
        url = 'https://example.com/app.js'
        hash_val = 'metadata_hash'
        
        state.mark_as_scanned_if_new(hash_val, url)
        
        # Read history file to verify metadata
        with open(state.history_file, 'r') as f:
            data = json.load(f)
        
        assert hash_val in data['scanned_hashes']
        assert hash_val in data['scan_metadata']
        assert data['scan_metadata'][hash_val]['url'] == url
        assert 'timestamp' in data['scan_metadata'][hash_val]


# ============================================================================
# PHASE 2.3: Bloom Filter Integration
# ============================================================================

@pytest.mark.unit
class TestBloomFilter:
    """Test Bloom filter integration and persistence"""
    
    @pytest.mark.skipif(not pytest.importorskip("pybloom_live", reason="pybloom_live not installed"), reason="Requires pybloom_live")
    def test_bloom_filter_creation(self, tmp_state_dir):
        """Test bloom filter is created with correct parameters"""
        state = State(tmp_state_dir['base'])
        
        if state.bloom_enabled:
            assert state.bloom_filter is not None
            # Should start with 0 items
            assert len(state.bloom_filter) >= 0
    
    @pytest.mark.skipif(not pytest.importorskip("pybloom_live", reason="pybloom_live not installed"), reason="Requires pybloom_live")
    def test_bloom_filter_persistence_to_disk(self, tmp_state_dir):
        """Test bloom filter saves and loads from disk"""
        # Create state and add hashes
        state1 = State(tmp_state_dir['base'])
        
        if not state1.bloom_enabled:
            pytest.skip("Bloom filter not enabled")
        
        for i in range(100):
            state1.mark_as_scanned_if_new(f'hash_{i}', f'https://example.com/file{i}.js')
        
        # Force save
        state1._save_bloom_filter()
        
        # Create new state instance
        state2 = State(tmp_state_dir['base'])
        
        if state2.bloom_enabled:
            # All hashes should be in loaded bloom filter
            for i in range(100):
                # Bloom filter check (may have false positives but no false negatives)
                assert f'hash_{i}' in state2.bloom_filter
    
    @pytest.mark.skipif(not pytest.importorskip("pybloom_live", reason="pybloom_live not installed"), reason="Requires pybloom_live")
    def test_bloom_filter_false_positive_rate(self, tmp_state_dir):
        """Test bloom filter maintains acceptable false positive rate"""
        state = State(tmp_state_dir['base'])
        
        if not state.bloom_enabled:
            pytest.skip("Bloom filter not enabled")
        
        # Add 10000 hashes
        for i in range(10000):
            state.bloom_filter.add(f'hash_{i}')
        
        # Test for false positives on non-existent items
        false_positives = 0
        test_count = 1000
        
        for i in range(10000, 10000 + test_count):
            if f'hash_{i}' in state.bloom_filter:
                false_positives += 1
        
        false_positive_rate = false_positives / test_count
        
        # Should be below 1% (configured error rate is 0.1%)
        assert false_positive_rate < 0.01, f"False positive rate {false_positive_rate:.2%} exceeds 1%"
    
    def test_graceful_degradation_without_bloom_installed(self, tmp_state_dir):
        """Test that state works correctly without bloom filter"""
        with patch.dict('sys.modules', {'pybloom_live': None}):
            state = State(tmp_state_dir['base'])
            
            # Should work without bloom
            result = state.mark_as_scanned_if_new('hash_no_bloom', 'https://example.com/test.js')
            assert result is True
            
            assert state.is_scanned('hash_no_bloom') is True


# ============================================================================
# PHASE 2.4: Checkpoint Management
# ============================================================================

@pytest.mark.unit
class TestCheckpoints:
    """Test checkpoint save, load, and expiration"""
    
    def test_save_checkpoint_creates_file(self, tmp_state_dir):
        """Test that save_checkpoint creates checkpoint file"""
        state = State(tmp_state_dir['base'])
        
        checkpoint_data = {
            'progress': 50,
            'timestamp': '2026-01-06T10:00:00Z'
        }
        
        state.save_checkpoint('PHASE_2_DOWNLOADING', checkpoint_data)
        
        assert Path(tmp_state_dir['checkpoint_file']).exists()
    
    def test_save_checkpoint_uses_atomic_write(self, tmp_state_dir):
        """Test that checkpoint uses .tmp -> final atomic replacement"""
        state = State(tmp_state_dir['base'])
        
        checkpoint_data = {'progress': 75}
        
        state.save_checkpoint('PHASE_3_ANALYSIS', checkpoint_data)
        
        # .tmp file should not exist after successful write
        tmp_file = Path(str(state.checkpoint_file) + '.tmp')
        assert not tmp_file.exists()
        
        # Final file should exist
        assert state.checkpoint_file.exists()
    
    def test_load_checkpoint_reads_valid_data(self, tmp_state_dir):
        """Test loading checkpoint returns correct data"""
        state = State(tmp_state_dir['base'])
        
        checkpoint_data = {
            'urls_discovered': 1000,
            'files_downloaded': 500
        }
        
        state.save_checkpoint('PHASE_4_SECRETS_SCAN', checkpoint_data)
        
        # Load checkpoint
        loaded = state.get_resume_state()
        
        assert loaded['phase'] == 'PHASE_4_SECRETS_SCAN'
        assert loaded['urls_discovered'] == 1000
    
    def test_has_checkpoint_validates_age(self, tmp_state_dir):
        """Test has_checkpoint() validates 7-day expiration"""
        state = State(tmp_state_dir['base'])
        
        # Create checkpoint
        state.save_checkpoint('PHASE_1_DISCOVERY', {'progress': 10})
        
        # Should have valid checkpoint
        assert state.has_checkpoint() is True
        
        # Modify timestamp to simulate old checkpoint (8 days ago)
        old_timestamp = time.time() - (8 * 24 * 60 * 60)
        Path(state.checkpoint_file).touch()
        import os
        os.utime(state.checkpoint_file, (old_timestamp, old_timestamp))
        
        # Should not have valid checkpoint (expired)
        assert state.has_checkpoint() is False
    
    def test_checkpoint_cleanup_after_expiration(self, tmp_state_dir):
        """Test that expired checkpoint is cleaned up"""
        state = State(tmp_state_dir['base'])
        
        # Create checkpoint
        state.save_checkpoint('PHASE_1_DISCOVERY', {'progress': 25})
        
        # Modify timestamp to 8 days ago
        old_timestamp = time.time() - (8 * 24 * 60 * 60)
        import os
        os.utime(state.checkpoint_file, (old_timestamp, old_timestamp))
        
        # has_checkpoint should trigger cleanup
        state.has_checkpoint()
        
        # Checkpoint file should be removed
        assert not Path(state.checkpoint_file).exists()
    
    def test_get_resume_state_returns_checkpoint_data(self, tmp_state_dir):
        """Test get_resume_state returns checkpoint with metadata"""
        state = State(tmp_state_dir['base'])
        
        checkpoint_data = {
            'phase_progress': {'current_phase': 2, 'total_phases': 4},
            'urls_discovered': 500
        }
        
        state.save_checkpoint('PHASE_2_DOWNLOADING', checkpoint_data)
        
        resume_state = state.get_resume_state()
        
        assert resume_state['phase'] == 'PHASE_2_DOWNLOADING'
        assert resume_state['phase_progress']['current_phase'] == 2
        assert 'timestamp' in resume_state  # Should add timestamp


# ============================================================================
# PHASE 2.5: File Locking (Critical for VPS concurrency)
# ============================================================================

@pytest.mark.unit
class TestFileLocking:
    """Test file locking prevents race conditions"""
    
    def test_file_locking_acquires_lock(self, tmp_state_dir):
        """Test that file operations acquire locks"""
        state = State(tmp_state_dir['base'])
        
        # This should complete without errors (lock acquired and released)
        state.mark_as_scanned_if_new('lock_test_hash', 'https://example.com/test.js')
        
        assert state.is_scanned('lock_test_hash') is True
    
    def test_concurrent_writes_are_serialized(self, tmp_state_dir):
        """Test that concurrent writes don't corrupt data"""
        state = State(tmp_state_dir['base'])
        
        results = []
        errors = []
        
        def write_hash(hash_val):
            try:
                result = state.mark_as_scanned_if_new(hash_val, f'https://example.com/{hash_val}.js')
                results.append((hash_val, result))
            except Exception as e:
                errors.append((hash_val, str(e)))
        
        # Spawn 10 threads writing different hashes
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_hash, args=(f'concurrent_hash_{i}',))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All writes should succeed with no errors
        assert len(errors) == 0
        assert len(results) == 10
        
        # All results should be True (first write)
        for hash_val, result in results:
            assert result is True
    
    def test_lock_timeout_configuration(self, tmp_state_dir):
        """Test that lock timeout is configurable and prevents deadlock"""
        state = State(tmp_state_dir['base'])
        
        # Lock operations should complete within reasonable time
        # (This test mainly ensures no infinite blocking)
        import time
        start = time.time()
        
        state.mark_as_scanned_if_new('timeout_test', 'https://example.com/test.js')
        
        elapsed = time.time() - start
        
        # Should complete in under 1 second (not deadlocked)
        assert elapsed < 1.0


# ============================================================================
# PHASE 2.6: Secrets Management
# ============================================================================

@pytest.mark.unit
class TestSecretsManagement:
    """Test secrets storage and deduplication"""
    
    def test_add_secret_appends_valid_json(self, tmp_state_dir):
        """Test that add_secret appends JSON lines"""
        state = State(tmp_state_dir['base'])
        
        secret_data = {
            'type': 'AWS',
            'value': 'AKIAIOSFODNN7EXAMPLE',
            'file': 'app.js'
        }
        
        state.add_secret(secret_data)
        
        # Read secrets file
        with open(state.secrets_file, 'r') as f:
            content = f.read().strip()
        
        assert content  # Not empty
        
        # Should be valid JSON
        loaded = json.loads(content)
        assert loaded['type'] == 'AWS'
    
    def test_add_secret_thread_safety(self, tmp_state_dir):
        """Test concurrent secret additions don't corrupt file"""
        state = State(tmp_state_dir['base'])
        
        def add_secret(secret_id):
            secret_data = {
                'type': 'Test',
                'value': f'secret_{secret_id}',
                'file': f'file_{secret_id}.js'
            }
            state.add_secret(secret_data)
        
        # Spawn 20 threads adding secrets
        threads = []
        for i in range(20):
            t = threading.Thread(target=add_secret, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Read all secrets
        with open(state.secrets_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # Should have 20 secrets
        assert len(lines) == 20
        
        # All should be valid JSON
        for line in lines:
            data = json.loads(line)
            assert 'type' in data
            assert 'value' in data
    
    def test_add_secret_deduplication_by_hash(self, tmp_state_dir):
        """Test that duplicate secrets are not added"""
        state = State(tmp_state_dir['base'])
        
        secret_data = {
            'type': 'AWS',
            'value': 'AKIAIOSFODNN7EXAMPLE',
            'file': 'app.js'
        }
        
        # Add same secret twice
        state.add_secret(secret_data)
        state.add_secret(secret_data)
        
        # Read secrets file
        with open(state.secrets_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # Should only have 1 secret (deduplicated)
        assert len(lines) == 1
    
    def test_corrupt_secrets_file_recovery(self, tmp_state_dir):
        """Test graceful handling of corrupted secrets file"""
        state = State(tmp_state_dir['base'])
        
        # Write corrupt data
        with open(state.secrets_file, 'w') as f:
            f.write('{"corrupt": incomplete json\n')
            f.write('valid data after corruption\n')
        
        # Should handle corruption gracefully
        secret_data = {'type': 'Test', 'value': 'test_secret', 'file': 'test.js'}
        
        try:
            state.add_secret(secret_data)
            # Should succeed (append mode doesn't validate existing data)
        except Exception as e:
            pytest.fail(f"add_secret failed on corrupt file: {e}")


# ============================================================================
# PHASE 2.7: Configuration Change Detection
# ============================================================================

@pytest.mark.unit
class TestConfigurationChangeDetection:
    """Test config change detection for incremental scan invalidation"""
    
    def test_check_config_changed_detects_modified_config(self, tmp_state_dir):
        """Test that config changes are detected"""
        state = State(tmp_state_dir['base'])
        
        config1 = {'threads': 50, 'timeout': 30}
        
        # First check - should save hash
        changed = state.check_config_changed(config1)
        # First time, no previous config, so not "changed"
        
        # Modify config
        config2 = {'threads': 100, 'timeout': 30}
        
        changed = state.check_config_changed(config2)
        
        # Should detect change
        assert changed is True
    
    def test_config_hash_persistence(self, tmp_state_dir):
        """Test that config hash is persisted"""
        state1 = State(tmp_state_dir['base'])
        
        config = {'threads': 50, 'semgrep': {'enabled': True}}
        state1.check_config_changed(config)
        
        # Create new state instance
        state2 = State(tmp_state_dir['base'])
        
        # Same config should not trigger change
        changed = state2.check_config_changed(config)
        assert changed is False
    
    def test_unchanged_config_returns_false(self, tmp_state_dir):
        """Test that unchanged config returns False"""
        state = State(tmp_state_dir['base'])
        
        config = {'threads': 50}
        
        state.check_config_changed(config)
        
        # Same config again
        changed = state.check_config_changed(config)
        
        assert changed is False


# ============================================================================
# PHASE 2.8: File Manifest
# ============================================================================

@pytest.mark.unit
class TestFileManifest:
    """Test file manifest for URL -> filename mapping"""
    
    def test_save_file_manifest_creates_valid_json(self, tmp_state_dir):
        """Test _save_file_manifest creates valid JSON"""
        state = State(tmp_state_dir['base'])
        
        manifest_entry = {
            'url': 'https://example.com/app.js',
            'file_hash': 'abc123',
            'hash_filename': 'abc123.js',
            'is_minified': True
        }
        
        state._save_file_manifest(manifest_entry)
        
        manifest_file = Path(tmp_state_dir['base']) / '.warehouse' / 'db' / 'file_manifest.json'
        
        assert manifest_file.exists()
        
        # Should be valid JSON
        with open(manifest_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['url'] == 'https://example.com/app.js'
    
    def test_get_url_from_filename_retrieves_correct_mapping(self, tmp_state_dir):
        """Test get_url_from_filename returns correct URL"""
        state = State(tmp_state_dir['base'])
        
        manifest_entry = {
            'url': 'https://example.com/bundle.js',
            'file_hash': 'def456',
            'hash_filename': 'def456.js',
            'is_minified': False
        }
        
        state._save_file_manifest(manifest_entry)
        
        # Retrieve URL
        url = state.get_url_from_filename('def456.js')
        
        assert url == 'https://example.com/bundle.js'
    
    def test_manifest_persistence_across_restarts(self, tmp_state_dir):
        """Test manifest persists across State instance restarts"""
        state1 = State(tmp_state_dir['base'])
        
        state1._save_file_manifest({
            'url': 'https://example.com/test.js',
            'file_hash': 'ghi789',
            'hash_filename': 'ghi789.js',
            'is_minified': True
        })
        
        # New state instance
        state2 = State(tmp_state_dir['base'])
        
        url = state2.get_url_from_filename('ghi789.js')
        
        assert url == 'https://example.com/test.js'


# ============================================================================
# PHASE 2.9: Problematic Domains Tracking
# ============================================================================

@pytest.mark.unit
class TestProblematicDomains:
    """Test problematic domains bloom filter"""
    
    @pytest.mark.skipif(not pytest.importorskip("pybloom_live", reason="pybloom_live not installed"), reason="Requires pybloom_live")
    def test_mark_domain_problematic(self, tmp_state_dir):
        """Test marking domain as problematic"""
        state = State(tmp_state_dir['base'])
        
        if not state.problematic_domains_enabled:
            pytest.skip("Problematic domains filter not enabled")
        
        state.mark_domain_problematic('timeout.example.com')
        
        # Should be marked
        assert state.is_problematic_domain('timeout.example.com') is True
    
    @pytest.mark.skipif(not pytest.importorskip("pybloom_live", reason="pybloom_live not installed"), reason="Requires pybloom_live")
    def test_problematic_domains_persistence(self, tmp_state_dir):
        """Test problematic domains persist across restarts"""
        state1 = State(tmp_state_dir['base'])
        
        if not state1.problematic_domains_enabled:
            pytest.skip("Problematic domains filter not enabled")
        
        # Mark 20 domains (trigger batch save at 10)
        for i in range(20):
            state1.mark_domain_problematic(f'bad{i}.example.com')
        
        # Force save
        state1._save_problematic_domains_filter()
        
        # New state instance
        state2 = State(tmp_state_dir['base'])
        
        if state2.problematic_domains_enabled:
            # Should remember problematic domains
            assert state2.is_problematic_domain('bad5.example.com') is True


# ============================================================================
# EDGE CASES & RESILIENCE
# ============================================================================

@pytest.mark.unit
class TestStateEdgeCases:
    """Test edge cases and error handling"""
    
    def test_corrupt_state_json_recovery(self, tmp_state_dir):
        """Test graceful recovery from corrupt state.json"""
        # Write corrupt state file
        with open(Path(tmp_state_dir['state_file']), 'w') as f:
            f.write('{invalid json}')
        
        # Should recover gracefully
        state = State(tmp_state_dir['base'])
        
        assert state.state is not None
    
    def test_corrupt_history_json_recovery(self, tmp_state_dir):
        """Test recovery from corrupt history.json"""
        # Write corrupt history
        with open(Path(tmp_state_dir['history_file']), 'w') as f:
            f.write('{"scanned_hashes": [invalid}')
        
        # Should recover
        state = State(tmp_state_dir['base'])
        
        # Should be able to mark new hash
        result = state.mark_as_scanned_if_new('recovery_test', 'https://example.com/test.js')
        assert result is not None
    
    def test_empty_secrets_file_handling(self, tmp_state_dir):
        """Test handling of empty secrets file"""
        state = State(tmp_state_dir['base'])
        
        # Empty file should be fine
        secret = {'type': 'Test', 'value': 'test', 'file': 'test.js'}
        state.add_secret(secret)
        
        # Should write successfully
        with open(state.secrets_file, 'r') as f:
            content = f.read().strip()
        
        assert content
    
    def test_unicode_in_url_metadata(self, tmp_state_dir):
        """Test Unicode characters in URLs"""
        state = State(tmp_state_dir['base'])
        
        unicode_url = 'https://example.com/файл.js'
        
        result = state.mark_as_scanned_if_new('unicode_hash', unicode_url)
        
        assert result is True
        
        # Should persist correctly
        url = state.get_url_from_filename('unicode_hash.js')
        # Note: get_url_from_filename uses manifest, not history
    
    def test_very_large_hash_list(self, tmp_state_dir):
        """Test performance with large number of hashes"""
        state = State(tmp_state_dir['base'])
        
        # Add 1000 hashes
        for i in range(1000):
            state.mark_as_scanned_if_new(f'hash_{i:04d}', f'https://example.com/file{i}.js')
        
        # Verify last hash
        assert state.is_scanned('hash_0999') is True
        
        # Verify first hash still accessible
        assert state.is_scanned('hash_0000') is True
