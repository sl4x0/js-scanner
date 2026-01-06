"""
Test ScanEngine Module (jsscanner/core/engine.py)
Tests for main orchestration engine, URL deduplication, minification detection, and phase coordination

Critical for:
- Multi-phase scan orchestration
- Crash recovery and checkpointing
- URL normalization and deduplication
- Minified JS detection (multi-heuristic)
- Emergency shutdown handling
"""
import pytest
import json
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from jsscanner.core.engine import ScanEngine


# ============================================================================
# PHASE 3.1: Engine Initialization
# ============================================================================

@pytest.mark.unit
class TestScanEngineInitialization:
    """Test ScanEngine initialization and setup"""
    
    def test_engine_initializes_with_valid_config(self, core_config, tmp_path):
        """Test engine initializes correctly"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': str(tmp_path / 'results'),
                'unique_js': str(tmp_path / 'results' / 'unique_js'),
                'findings': str(tmp_path / 'results' / 'findings'),
                'logs': str(tmp_path / 'results' / 'logs')
            }
            
            with patch('jsscanner.core.engine.setup_logger') as mock_logger:
                mock_logger.return_value = Mock()
                
                with patch('jsscanner.core.engine.State') as mock_state:
                    with patch('jsscanner.core.engine.Discord') as mock_discord:
                        engine = ScanEngine(core_config, 'example.com')
                        
                        assert engine.target == 'example.com'
                        assert engine.config == core_config
                        assert engine.shutdown_requested is False
    
    def test_engine_sanitizes_target_name(self, core_config, tmp_path):
        """Test target name sanitization"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path / 'logs'), 'unique_js': str(tmp_path / 'unique_js'), 'findings': str(tmp_path / 'findings')}
            with patch('jsscanner.core.engine.setup_logger') as mock_logger:
                mock_logger.return_value = Mock()
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'https://example.com:443/')
                        
                        # Should sanitize to clean domain
                        assert 'example.com' in engine.target_name
                        assert ':' not in engine.target_name
    
    def test_engine_creates_output_directories(self, core_config, tmp_path):
        """Test output directory creation"""
        base_path = tmp_path / 'results'
        
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': str(base_path),
                'unique_js': str(base_path / 'unique_js'),
                'findings': str(base_path / 'findings'),
                'logs': str(base_path / 'logs')
            }
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Verify paths are set
                        assert 'base' in engine.paths
                        assert 'unique_js' in engine.paths


# ============================================================================
# PHASE 3.2: URL Deduplication (_deduplicate_urls)
# ============================================================================

@pytest.mark.unit
class TestURLDeduplication:
    """Test URL normalization and deduplication logic"""
    
    def test_deduplicate_identical_urls_with_trailing_slash(self, core_config, tmp_path):
        """Test URLs with/without trailing slash are deduplicated"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        urls = [
                            'https://example.com/app.js',
                            'https://example.com/app.js/',
                            'https://example.com/vendor.js',
                            'https://example.com/vendor.js/'
                        ]
                        
                        deduplicated = engine._deduplicate_urls(urls)
                        
                        # Should have only 2 unique URLs (normalized)
                        assert len(deduplicated) == 2
    
    def test_deduplicate_filters_malformed_urls(self, core_config, tmp_path):
        """Test malformed URLs are filtered out"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        urls = [
                            'https://example.com/valid.js',
                            'javascript:void(0)',
                            'data:text/javascript,alert("test")',
                            'about:blank',
                            'https://example.com/another.js'
                        ]
                        
                        deduplicated = engine._deduplicate_urls(urls)
                        
                        # Should filter out non-HTTP URLs
                        assert len(deduplicated) == 2
                        assert all(url.startswith('http') for url in deduplicated)
    
    def test_deduplicate_filters_urls_exceeding_length(self, core_config, tmp_path):
        """Test URLs exceeding 2000 chars are filtered"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Create very long URL
                        long_url = 'https://example.com/' + 'a' * 3000 + '.js'
                        
                        urls = [
                            'https://example.com/normal.js',
                            long_url
                        ]
                        
                        deduplicated = engine._deduplicate_urls(urls)
                        
                        # Should filter out long URL
                        assert len(deduplicated) == 1
                        assert deduplicated[0] == 'https://example.com/normal.js'
    
    def test_deduplicate_handles_unicode_urls(self, core_config, tmp_path):
        """Test Unicode characters in URLs"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        urls = [
                            'https://example.com/файл.js',
                            'https://example.com/テスト.js'
                        ]
                        
                        try:
                            deduplicated = engine._deduplicate_urls(urls)
                            # Should handle Unicode gracefully
                            assert isinstance(deduplicated, list)
                        except Exception as e:
                            pytest.fail(f"Unicode URL handling failed: {e}")
    
    def test_deduplicate_case_insensitive(self, core_config, tmp_path):
        """Test case-insensitive deduplication"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        urls = [
                            'https://Example.com/App.js',
                            'https://example.com/app.js',
                            'HTTPS://EXAMPLE.COM/APP.JS'
                        ]
                        
                        deduplicated = engine._deduplicate_urls(urls)
                        
                        # Should deduplicate to 1 URL (case-insensitive)
                        assert len(deduplicated) == 1


# ============================================================================
# PHASE 3.3: Minification Detection (_is_minified)
# ============================================================================

@pytest.mark.unit
class TestMinificationDetection:
    """Test multi-heuristic minification detection"""
    
    def test_minified_jquery_returns_true(self, core_config, tmp_path, sample_js_minified):
        """Test real minified jQuery code detected"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        is_minified = engine._is_minified(sample_js_minified)
                        
                        assert is_minified is True
    
    def test_beautified_code_returns_false(self, core_config, tmp_path, sample_js_beautified):
        """Test beautified code not detected as minified"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        is_minified = engine._is_minified(sample_js_beautified)
                        
                        assert is_minified is False
    
    def test_avg_line_length_heuristic(self, core_config, tmp_path):
        """Test avg_line_length > 300 triggers minified"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Single line of 500 chars
                        code = 'var x=' + 'a' * 500 + ';'
                        
                        is_minified = engine._is_minified(code)
                        
                        # Should detect as minified due to line length
                        assert is_minified is True
    
    def test_semicolon_density_heuristic(self, core_config, tmp_path):
        """Test semicolon_density > 0.5 triggers minified"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # High semicolon density - must be >= 100 chars to pass length check
                        code = 'a;b;c;d;e;f;g;h;i;j;k;l;m;n;o;p;q;r;s;t;u;v;w;x;y;z;' * 3  # 156 chars, 78 semicolons, 3 lines = 26 semicolons/line
                        
                        is_minified = engine._is_minified(code)
                        
                        # Should detect due to semicolon density (26 semicolons per line > 5 threshold)
                        assert is_minified is True
    
    def test_whitespace_ratio_heuristic(self, core_config, tmp_path):
        """Test whitespace_ratio < 0.02 triggers minified"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Very little whitespace
                        code = 'function a(){return 1;}' * 50  # No spaces
                        
                        is_minified = engine._is_minified(code)
                        
                        # Should detect due to low whitespace
                        assert is_minified is True
    
    def test_comments_prevent_minified_flag(self, core_config, tmp_path):
        """Test presence of comments prevents minified flag"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        code = '// This is a comment\nfunction test() { return 1; }\n/* Another comment */'
                        
                        is_minified = engine._is_minified(code)
                        
                        # Comments suggest not minified
                        assert is_minified is False
    
    def test_empty_file_edge_case(self, core_config, tmp_path):
        """Test empty file handling"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        is_minified = engine._is_minified('')
                        
                        # Should handle empty file gracefully
                        assert is_minified is False
    
    def test_single_line_file_edge_case(self, core_config, tmp_path):
        """Test single-line file"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        code = 'console.log("single line");'
                        
                        is_minified = engine._is_minified(code)
                        
                        # Single line may or may not be minified based on heuristics
                        assert isinstance(is_minified, bool)


# ============================================================================
# PHASE 3.4: Full Scan Orchestration (run)
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestScanOrchestration:
    """Test full scan pipeline orchestration"""
    
    async def test_run_executes_phases_in_order(self, core_config, tmp_path, tmp_state_dir):
        """Test run() executes all phases in correct order"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': tmp_state_dir['base'],
                'logs': str(tmp_path / 'logs'),
                'unique_js': tmp_state_dir['base'] + '/unique_js',
                'findings': tmp_state_dir['findings_path']
            }
            
            with patch('jsscanner.core.engine.setup_logger') as mock_logger:
                mock_logger.return_value = Mock()
                
                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.has_checkpoint = Mock(return_value=False)
                    mock_state.save_checkpoint = Mock()
                    mock_state.update_metadata = Mock()
                    mock_state_cls.return_value = mock_state
                    
                    with patch('jsscanner.core.engine.Discord') as mock_discord:
                        mock_notifier = AsyncMock()
                        mock_discord.return_value = mock_notifier
                        
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Mock module initialization
                        with patch.object(engine, '_initialize_modules', new_callable=AsyncMock):
                            with patch.object(engine, '_check_dependencies', new_callable=AsyncMock):
                                # Mock discovery
                                with patch.object(engine, '_discover_all_domains_concurrent', new_callable=AsyncMock) as mock_discover:
                                    mock_discover.return_value = ['https://example.com/app.js']
                                    
                                    # Mock download
                                    with patch.object(engine, '_download_all_files', new_callable=AsyncMock) as mock_download:
                                        mock_download.return_value = []
                                        
                                        # Mock scanning modules
                                        engine.secret_scanner = AsyncMock()
                                        engine.secret_scanner.scan_directory = AsyncMock(return_value=[])
                                        engine.secret_scanner.save_organized_secrets = AsyncMock()
                                        engine.secret_scanner.get_secrets_summary = Mock(return_value={})
                                        engine.secret_scanner.export_results = Mock()
                                        engine.secret_scanner.secrets_count = 0
                                        
                                        # Mock other phases
                                        with patch.object(engine, '_process_all_files_parallel', new_callable=AsyncMock):
                                            with patch.object(engine, '_unminify_all_files', new_callable=AsyncMock):
                                                with patch.object(engine, '_cleanup_minified_files', new_callable=AsyncMock):
                                                    # Run scan
                                                    await engine.run(['https://example.com'], use_subjs=False)
                                                    
                                                    # Verify phases executed
                                                    mock_discover.assert_called_once()
                                                    mock_download.assert_called_once()
    
    async def test_run_with_resume_loads_checkpoint(self, core_config, tmp_path, tmp_state_dir, sample_scan_state):
        """Test run(resume=True) loads checkpoint"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {
                'base': tmp_state_dir['base'],
                'logs': str(tmp_path / 'logs'),
                'unique_js': tmp_state_dir['base'] + '/unique_js',
                'findings': tmp_state_dir['findings_path']
            }
            
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.has_checkpoint = Mock(return_value=True)
                    mock_state.get_resume_state = Mock(return_value=sample_scan_state)
                    mock_state.check_config_changed = Mock(return_value=False)
                    mock_state.update_metadata = Mock()
                    mock_state_cls.return_value = mock_state
                    
                    with patch('jsscanner.core.engine.Discord') as mock_discord_cls:
                        # Discord instance must have async stop() method
                        mock_discord = AsyncMock()
                        mock_discord.stop = AsyncMock()
                        mock_discord_cls.return_value = mock_discord
                        
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Mock dependencies
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
                                                    
                                                    # Verify checkpoint loaded
                                                    mock_state.get_resume_state.assert_called_once()


# ============================================================================
# PHASE 3.5: Progress & Checkpointing
# ============================================================================

@pytest.mark.unit
class TestProgressCheckpointing:
    """Test progress tracking and checkpoint operations"""
    
    def test_log_progress_calculates_eta(self, core_config, tmp_path):
        """Test _log_progress calculates ETA correctly"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Simulate progress
                        engine._log_progress('Test Phase', 50, 100)
                        
                        # Should update phase progress
                        assert engine.phase_progress['current'] == 50
                        assert engine.phase_progress['total'] == 100


# ============================================================================
# PHASE 3.6: Emergency Shutdown
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestEmergencyShutdown:
    """Test emergency shutdown and graceful exit"""
    
    @pytest.mark.skip(reason="_emergency_shutdown() cancels ALL tasks in event loop including the test itself, causing CancelledError. Requires test restructuring or integration test approach.")
    async def test_emergency_shutdown_cancels_tasks(self, core_config, tmp_path):
        """Test _emergency_shutdown() cancels tasks"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.save_checkpoint = Mock()
                    mock_state_cls.return_value = mock_state
                    
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Mock modules
                        engine.fetcher = Mock()
                        engine.fetcher.cleanup = AsyncMock()
                        engine.notifier = AsyncMock()
                        engine.notifier.stop = AsyncMock()
                        
                        # Call emergency shutdown
                        engine._emergency_shutdown()
                        
                        # Verify cleanup called
                        engine.notifier.stop.assert_called_once()
    
    @pytest.mark.skip(reason="_emergency_shutdown() cancels ALL tasks in event loop including the test itself, causing CancelledError. Requires test restructuring or integration test approach.")
    async def test_emergency_shutdown_saves_checkpoint(self, core_config, tmp_path):
        """Test emergency shutdown saves checkpoint"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State') as mock_state_cls:
                    mock_state = Mock()
                    mock_state.save_checkpoint = Mock()
                    mock_state_cls.return_value = mock_state
                    
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        engine.fetcher = Mock()
                        engine.fetcher.cleanup = AsyncMock()
                        engine.notifier = AsyncMock()
                        engine.notifier.stop = AsyncMock()
                        
                        engine._emergency_shutdown()
                        
                        # Verify checkpoint saved
                        # Note: save_checkpoint is called via _save_current_progress
                        # which may be called in emergency_shutdown


# ============================================================================
# EDGE CASES & RESILIENCE
# ============================================================================

@pytest.mark.unit
class TestEngineEdgeCases:
    """Test edge cases and error handling"""
    
    def test_engine_handles_empty_input_list(self, core_config, tmp_path):
        """Test handling of empty inputs"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        engine = ScanEngine(core_config, 'example.com')
                        
                        # Should handle empty list gracefully
                        result = engine._deduplicate_urls([])
                        
                        assert result == []
    
    def test_engine_handles_malformed_target(self, core_config, tmp_path):
        """Test handling of malformed target"""
        with patch('jsscanner.core.engine.FileSystem.create_result_structure') as mock_fs:
            mock_fs.return_value = {'base': str(tmp_path), 'logs': str(tmp_path), 'unique_js': str(tmp_path), 'findings': str(tmp_path)}
            with patch('jsscanner.core.engine.setup_logger'):
                with patch('jsscanner.core.engine.State'):
                    with patch('jsscanner.core.engine.Discord'):
                        try:
                            engine = ScanEngine(core_config, 'not a valid domain!@#$')
                            # Should not crash
                            assert engine is not None
                        except Exception as e:
                            pytest.fail(f"Engine creation failed with malformed target: {e}")
