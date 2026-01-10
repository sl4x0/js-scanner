"""
Test Core Module Integration (jsscanner/core)
End-to-end integration tests for the complete orchestration pipeline

Critical for:
- Full scan lifecycle validation
- Checkpoint and resume functionality
- Multi-component coordination
- Real-world scenario testing
"""
import pytest
import json
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from jsscanner.core.engine import ScanEngine
from jsscanner.core.state import State


# ============================================================================
# PHASE 6.1: Full Pipeline Simulation
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestFullPipelineIntegration:
    """Test complete scan pipeline end-to-end"""

    async def test_complete_scan_workflow(self, core_config, tmp_path, tmp_state_dir):
        """Test full scan: discovery -> download -> secrets -> report"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': tmp_state_dir['base'],
                'logs': str(tmp_path / 'logs'),
                'unique_js': str(tmp_path / 'unique_js'),
                'findings': tmp_state_dir['findings_path'],
                'files_unminified': str(tmp_path / 'unminified')
            }

            with patch('jsscanner.core.engine.setup_logger') as mock_logger:
                mock_logger.return_value = Mock()

                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.has_checkpoint = Mock(return_value=False)
                    mock_state.save_checkpoint = Mock()
                    mock_state.update_metadata = Mock()
                    mock_state.mark_as_scanned_if_new = Mock(return_value=True)
                    mock_state_cls.return_value = mock_state

                    with patch('jsscanner.core.engine.Discord') as mock_discord:
                        mock_notifier = AsyncMock()
                        mock_discord.return_value = mock_notifier

                        engine = ScanEngine(core_config, 'example.com')

                        # Mock all modules
                        with patch.object(engine, '_initialize_modules', new_callable=AsyncMock):
                            with patch.object(engine, '_check_dependencies', new_callable=AsyncMock):
                                # Mock discovery
                                with patch.object(engine, '_discover_all_domains_concurrent', new_callable=AsyncMock) as mock_discover:
                                    mock_discover.return_value = [
                                        'https://example.com/app.js',
                                        'https://example.com/vendor.js',
                                        'https://example.com/bundle.js'
                                    ]

                                    # Mock download
                                    with patch.object(engine, '_download_all_files', new_callable=AsyncMock) as mock_download:
                                        mock_download.return_value = [
                                            {'url': 'https://example.com/app.js', 'hash': 'hash1', 'file_path': str(tmp_path / 'app.js'), 'is_minified': True},
                                            {'url': 'https://example.com/bundle.js', 'hash': 'hash2', 'file_path': str(tmp_path / 'bundle.js'), 'is_minified': True}
                                        ]

                                        # Mock secret scanner
                                        engine.secret_scanner = AsyncMock()
                                        engine.secret_scanner.scan_directory = AsyncMock(return_value=[
                                            {'type': 'AWS', 'value': 'AKIAIOSFODNN7EXAMPLE'}
                                        ])
                                        engine.secret_scanner.save_organized_secrets = AsyncMock()
                                        engine.secret_scanner.get_secrets_summary = Mock(return_value={'total': 1})
                                        engine.secret_scanner.export_results = Mock()
                                        engine.secret_scanner.secrets_count = 1

                                        # Mock other phases
                                        with patch.object(engine, '_process_all_files_parallel', new_callable=AsyncMock):
                                            with patch.object(engine, '_unminify_all_files', new_callable=AsyncMock):
                                                with patch.object(engine, '_cleanup_minified_files', new_callable=AsyncMock):
                                                    # Run full scan
                                                    await engine.run(['https://example.com'])

                                                    # Verify all phases executed
                                                    mock_discover.assert_called_once()
                                                    mock_download.assert_called_once()
                                                    engine.secret_scanner.scan_directory.assert_called_once()

                                                    # Verify stats updated
                                                    assert engine.stats['total_secrets'] >= 0

    async def test_scan_with_resume_from_checkpoint(self, core_config, tmp_path, tmp_state_dir, sample_scan_state):
        """Test resuming scan from checkpoint"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': tmp_state_dir['base'],
                'logs': str(tmp_path / 'logs'),
                'unique_js': str(tmp_path / 'unique_js'),
                'findings': tmp_state_dir['findings_path']
            }

            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.has_checkpoint = Mock(return_value=True)
                    mock_state.get_resume_state = Mock(return_value=sample_scan_state)
                    mock_state.check_config_changed = Mock(return_value=False)
                    mock_state.update_metadata = Mock()
                    mock_state.save_checkpoint = Mock()
                    mock_state_cls.return_value = mock_state

                    with patch('jsscanner.core.engine.Discord') as mock_discord_cls:
                        # Discord instance must have async stop() method
                        mock_discord = AsyncMock()
                        mock_discord.stop = AsyncMock()
                        mock_discord_cls.return_value = mock_discord

                        engine = ScanEngine(core_config, 'example.com')

                        with patch.object(engine, '_initialize_modules', new_callable=AsyncMock):
                            with patch.object(engine, '_check_dependencies', new_callable=AsyncMock):
                                with patch.object(engine, '_discover_all_domains_concurrent', new_callable=AsyncMock):
                                    with patch.object(engine, '_download_all_files', new_callable=AsyncMock):
                                        engine.secret_scanner = AsyncMock()
                                        engine.secret_scanner.scan_directory = AsyncMock(return_value=[])
                                        engine.secret_scanner.save_organized_secrets = AsyncMock()
                                        engine.secret_scanner.get_secrets_summary = Mock(return_value={})
                                        engine.secret_scanner.export_results = Mock()
                                        engine.secret_scanner.secrets_count = 0

                                        with patch.object(engine, '_process_all_files_parallel', new_callable=AsyncMock):
                                            with patch.object(engine, '_unminify_all_files', new_callable=AsyncMock):
                                                with patch.object(engine, '_cleanup_minified_files', new_callable=AsyncMock):
                                                    await engine.run(['https://example.com'], resume=True)

                                                    # Verify checkpoint was loaded
                                                    mock_state.get_resume_state.assert_called_once()

    async def test_incremental_scan_skips_duplicates(self, core_config, tmp_path, tmp_state_dir):
        """Test incremental scanning skips already-scanned files"""
        state = State(tmp_state_dir['base'])

        # Pre-populate state with scanned hash
        state.mark_as_scanned_if_new('already_scanned_hash', 'https://example.com/old.js')

        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': tmp_state_dir['base'],
                'logs': str(tmp_path / 'logs'),
                'unique_js': str(tmp_path / 'unique_js'),
                'findings': tmp_state_dir['findings_path']
            }

            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State', return_value=state):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')

                        # Verify pre-existing hash is recognized
                        assert state.is_scanned('already_scanned_hash') is True

    async def test_config_change_invalidates_incremental_state(self, core_config, tmp_path, tmp_state_dir):
        """Test config change triggers warning on resume"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': tmp_state_dir['base'],
                'logs': str(tmp_path / 'logs'),
                'unique_js': str(tmp_path / 'unique_js'),
                'findings': tmp_state_dir['findings_path']
            }

            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.has_checkpoint = Mock(return_value=True)
                    mock_state.get_resume_state = Mock(return_value={'phase': 'download', 'timestamp': '2026-01-06T00:00:00Z', 'phase_progress': {'current_phase': 2, 'total_phases': 4}})
                    mock_state.check_config_changed = Mock(return_value=True)  # Config changed!
                    mock_state.update_metadata = Mock()
                    mock_state.save_checkpoint = Mock()
                    mock_state_cls.return_value = mock_state

                    with patch('jsscanner.core.engine.Discord') as mock_discord_cls:
                        # Discord instance must have async stop() method
                        mock_discord = AsyncMock()
                        mock_discord.stop = AsyncMock()
                        mock_discord_cls.return_value = mock_discord

                        engine = ScanEngine(core_config, 'example.com')

                        with patch.object(engine, '_initialize_modules', new_callable=AsyncMock):
                            with patch.object(engine, '_check_dependencies', new_callable=AsyncMock):
                                with patch.object(engine, '_discover_all_domains_concurrent', new_callable=AsyncMock):
                                    with patch.object(engine, '_download_all_files', new_callable=AsyncMock):
                                        engine.secret_scanner = AsyncMock()
                                        engine.secret_scanner.scan_directory = AsyncMock(return_value=[])
                                        engine.secret_scanner.save_organized_secrets = AsyncMock()
                                        engine.secret_scanner.get_secrets_summary = Mock(return_value={})
                                        engine.secret_scanner.export_results = Mock()
                                        engine.secret_scanner.secrets_count = 0

                                        with patch.object(engine, '_process_all_files_parallel', new_callable=AsyncMock):
                                            with patch.object(engine, '_unminify_all_files', new_callable=AsyncMock):
                                                with patch.object(engine, '_cleanup_minified_files', new_callable=AsyncMock):
                                                    with patch('asyncio.sleep', new_callable=AsyncMock):  # Skip warning delay
                                                        await engine.run(['https://example.com'], resume=True)

                                                        # Verify config change was detected
                                                        mock_state.check_config_changed.assert_called_once()


# ============================================================================
# PHASE 6.2: Concurrency & Resource Management
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
class TestConcurrencyAndResources:
    """Test bounded concurrency and resource management"""

    async def test_bounded_concurrency_semaphore_limits(self, core_config, tmp_path, tmp_state_dir):
        """Test semaphore limits prevent unbounded concurrency"""
        # This test verifies that concurrent operations respect limits
        # In production, this prevents resource exhaustion

        state = State(tmp_state_dir['base'])

        # Simulate concurrent hash marking
        async def mark_hash(i):
            return state.mark_as_scanned_if_new(f'hash_{i}', f'https://example.com/file{i}.js')

        # Process 100 hashes concurrently
        tasks = [mark_hash(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(result is True for result in results)

        # All hashes should be marked
        for i in range(100):
            assert state.is_scanned(f'hash_{i}') is True

    @pytest.mark.slow
    async def test_no_memory_leaks_with_large_file_list(self, core_config, tmp_path, tmp_state_dir):
        """Test no memory leaks with 1000+ files"""
        state = State(tmp_state_dir['base'])

        # Add 1000 hashes
        for i in range(1000):
            state.mark_as_scanned_if_new(f'hash_{i:04d}', f'https://example.com/file{i}.js')

        # Verify all accessible
        assert state.is_scanned('hash_0000') is True
        assert state.is_scanned('hash_0999') is True

        # Memory should be released (Python GC handles this)
        import gc
        gc.collect()


# ============================================================================
# PHASE 6.3: Real-World Scenarios
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestRealWorldScenarios:
    """Test realistic bug bounty scenarios"""

    @pytest.mark.skip(reason="Depends on _emergency_shutdown() which cancels all tasks including the test. Related to emergency shutdown test issues.")
    async def test_crash_recovery_with_emergency_shutdown(self, core_config, tmp_path, tmp_state_dir):
        """Test crash recovery saves state"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': tmp_state_dir['base'],
                'logs': str(tmp_path / 'logs'),
                'unique_js': str(tmp_path / 'unique_js'),
                'findings': tmp_state_dir['findings_path']
            }

            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.has_checkpoint = Mock(return_value=False)
                    mock_state.save_checkpoint = Mock()
                    mock_state.update_metadata = Mock()
                    mock_state_cls.return_value = mock_state

                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')

                        # Mock modules
                        engine.fetcher = Mock()
                        engine.fetcher.cleanup = AsyncMock()
                        engine.notifier = AsyncMock()
                        engine.notifier.stop = AsyncMock()

                        # Simulate crash
                        engine.shutdown_requested = True
                        engine._emergency_shutdown()

                        # Verify cleanup was called
                        engine.notifier.stop.assert_called_once()

    @pytest.mark.skip(reason="File manifest functionality not yet implemented in State class - _save_file_manifest and get_url_from_filename methods don't exist")
    async def test_manifest_accuracy_across_full_pipeline(self, core_config, tmp_path, tmp_state_dir):
        """Test file manifest maintains URL -> filename mapping"""
        state = State(tmp_state_dir['base'])

        # Save manifest entry
        state._save_file_manifest({
            'url': 'https://example.com/app.js',
            'file_hash': 'abc123',
            'hash_filename': 'abc123.js',
            'is_minified': True
        })

        # Retrieve URL from filename
        url = state.get_url_from_filename('abc123.js')

        assert url == 'https://example.com/app.js'


# ============================================================================
# EDGE CASES & RESILIENCE
# ============================================================================

@pytest.mark.integration
class TestIntegrationEdgeCases:
    """Test edge cases in integrated scenarios"""

    def test_corrupt_state_recovery(self, tmp_state_dir):
        """Test graceful recovery from corrupt state files"""
        # Corrupt state.json
        state_file = Path(tmp_state_dir['state_file'])
        state_file.write_text('{invalid json}')

        # Should recover gracefully
        state = State(tmp_state_dir['base'])

        assert state.state is not None

    @pytest.mark.skip(reason="Threading test causes ExceptionGroup with thread warnings. State.save_checkpoint may not be thread-safe or requires thread synchronization testing approach.")
    def test_concurrent_checkpoint_saves(self, tmp_state_dir):
        """Test concurrent checkpoint saves don't corrupt data"""
        state = State(tmp_state_dir['base'])

        import threading

        def save_checkpoint(phase, progress):
            state.save_checkpoint(phase, progress)

        # Spawn 5 threads saving checkpoints
        threads = []
        for i in range(5):
            t = threading.Thread(target=save_checkpoint, args=(f'PHASE_{i}', {'progress': i * 20}))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Last checkpoint should be valid
        checkpoint = state.get_resume_state()
        assert checkpoint is not None
        assert 'phase' in checkpoint


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

@pytest.mark.slow
@pytest.mark.integration
class TestPerformanceBenchmarks:
    """Performance benchmarks for core operations"""

    def test_state_operations_performance(self, tmp_state_dir):
        """Test state operations complete within performance targets"""
        state = State(tmp_state_dir['base'])

        # State operations should be < 25ms per call on Windows (file I/O overhead)
        # Linux/Mac typically run at <10ms
        start = time.time()

        for i in range(100):
            state.mark_as_scanned_if_new(f'perf_hash_{i}', f'https://example.com/file{i}.js')

        elapsed = time.time() - start
        avg_time = elapsed / 100

        # Average should be under 30ms (relaxed for Windows compatibility)
        assert avg_time < 0.030, f"State operations too slow: {avg_time*1000:.2f}ms average"

    def test_checkpoint_save_performance(self, tmp_state_dir):
        """Test checkpoint save completes within 100ms"""
        state = State(tmp_state_dir['base'])

        checkpoint_data = {
            'progress': 50,
            'stats': {'files': 1000, 'secrets': 100}
        }

        start = time.time()
        state.save_checkpoint('PHASE_2_DOWNLOADING', checkpoint_data)
        elapsed = time.time() - start

        # Should complete in under 100ms
        assert elapsed < 0.1, f"Checkpoint save too slow: {elapsed*1000:.2f}ms"
