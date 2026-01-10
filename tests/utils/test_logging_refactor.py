"""
Unit tests for refactored logging system
Focus on edge cases, rotation, and engine integration
"""
import pytest
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time

from jsscanner.utils.log import get_target_logger, _sanitize_filename
from jsscanner.utils.log_analyzer import (
    analyze_log_file,
    generate_summary_report,
    cleanup_old_logs
)


class TestFilenameSanitization:
    """Test edge cases in filename sanitization"""

    def test_sanitize_removes_http_protocol(self):
        """HTTP protocol should be stripped"""
        assert _sanitize_filename("http://example.com") == "example.com"

    def test_sanitize_removes_https_protocol(self):
        """HTTPS protocol should be stripped"""
        assert _sanitize_filename("https://api.example.com") == "api.example.com"

    def test_sanitize_removes_websocket_protocol(self):
        """WebSocket protocols should be stripped"""
        assert _sanitize_filename("ws://socket.io") == "socket.io"
        assert _sanitize_filename("wss://secure.socket.io") == "secure.socket.io"

    def test_sanitize_replaces_slashes(self):
        """Forward and back slashes should be replaced with underscores"""
        assert _sanitize_filename("path/to/resource") == "path_to_resource"
        assert _sanitize_filename("path\\to\\resource") == "path_to_resource"

    def test_sanitize_replaces_colons(self):
        """Colons (port numbers) should be replaced"""
        assert _sanitize_filename("api.com:8080") == "api.com_8080"

    def test_sanitize_replaces_special_characters(self):
        """Special filesystem characters should be replaced"""
        special_chars = '<>:"|?*'
        for char in special_chars:
            result = _sanitize_filename(f"test{char}file")
            assert char not in result
            assert result == "test_file"

    def test_sanitize_limits_length(self):
        """Long filenames should be truncated to 200 chars"""
        long_name = "a" * 300
        result = _sanitize_filename(long_name)
        assert len(result) == 200

    def test_sanitize_handles_empty_string(self):
        """Empty strings should return default"""
        assert _sanitize_filename("") == "unknown_target"

    def test_sanitize_handles_only_special_chars(self):
        """Strings with only special chars should return default"""
        assert _sanitize_filename("///:::") == "unknown_target"

    def test_sanitize_complex_url(self):
        """Complex URL should be fully sanitized"""
        url = "https://api.example.com:8080/v1/users?id=123"
        result = _sanitize_filename(url)
        assert "https" not in result
        assert "/" not in result
        assert ":" not in result or result.count(":") == 0
        assert "?" not in result


class TestLogRotation:
    """Test log rotation mechanisms"""

    def test_size_rotation_creates_backup(self):
        """Writing beyond max_bytes should create backup file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            rotation_config = {
                'type': 'size',
                'max_bytes': 500,  # Small size to trigger rotation
                'backup_count': 2
            }

            logger = get_target_logger(
                "rotation_test",
                log_dir=tmpdir,
                level=logging.DEBUG,
                rotation_config=rotation_config,
                console_enabled=False
            )

            # Write enough data to trigger rotation (>500 bytes)
            # Use WARNING because INFO is filtered out (console-only)
            for i in range(50):
                logger.warning(f"Test message {i} " + "x" * 50)

            # Close handlers
            for handler in logger.handlers[:]:
                handler.flush()
                handler.close()
                logger.removeHandler(handler)

            # Check for rotated files
            log_files = list(Path(tmpdir).glob("rotation_test*.log*"))
            # Should have at least main log + 1 backup
            assert len(log_files) >= 2, f"Expected rotation, found {len(log_files)} files"

    def test_time_rotation_configuration(self):
        """Time-based rotation should be configurable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            rotation_config = {
                'type': 'time',
                'when': 'midnight',
                'interval': 1,
                'backup_count': 7
            }

            logger = get_target_logger(
                "time_rotation_test",
                log_dir=tmpdir,
                level=logging.INFO,
                rotation_config=rotation_config,
                console_enabled=False
            )

            logger.info("Test message")

            # Verify handler is TimedRotatingFileHandler
            from logging.handlers import TimedRotatingFileHandler
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]

            # At least one should be a timed rotating handler
            has_timed = any(isinstance(h, TimedRotatingFileHandler) for h in file_handlers)
            assert has_timed, "Expected TimedRotatingFileHandler for time-based rotation"

            # Cleanup
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

    def test_no_rotation_with_none_config(self):
        """No rotation config should use simple FileHandler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = get_target_logger(
                "no_rotation_test",
                log_dir=tmpdir,
                level=logging.INFO,
                rotation_config=None,
                console_enabled=False
            )

            logger.info("Test message")

            # Verify handler type
            from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]

            # Should have regular FileHandler (not rotating)
            has_rotating = any(
                isinstance(h, (RotatingFileHandler, TimedRotatingFileHandler))
                for h in file_handlers
            )

            # Cleanup
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)


class TestEngineIntegration:
    """Test integration with ScanEngine"""

    @patch('jsscanner.core.engine.get_target_logger')
    @patch('jsscanner.core.engine.FileSystem')
    @patch('jsscanner.core.engine.State')
    @patch('jsscanner.core.engine.Discord')
    def test_engine_uses_per_target_logger(self, mock_discord, mock_state, mock_fs, mock_logger):
        """ScanEngine should create per-target logger on init"""
        from jsscanner.core.engine import ScanEngine

        # Setup mocks
        mock_fs.create_result_structure.return_value = {
            'base': '/tmp/test',
            'logs': '/tmp/test/logs'
        }
        mock_logger.return_value = MagicMock()
        # Single file approach - only log_path in metadata
        mock_logger.return_value._log_metadata = {
            'log_path': '/tmp/test.log'
        }

        # Create engine
        config = {
            'logging': {
                'dir': 'logs',
                'level': 'INFO',
                'rotation': {
                    'type': 'size',
                    'max_bytes': 10485760,
                    'backup_count': 5
                },
                'console_enabled': True
            }
        }

        engine = ScanEngine(config, "example.com")

        # Verify get_target_logger was called
        mock_logger.assert_called_once()

        # Verify arguments passed
        call_args = mock_logger.call_args
        assert call_args.kwargs['target_name'] == "example.com"
        assert call_args.kwargs['log_dir'] == 'logs'
        assert call_args.kwargs['level'] == logging.INFO
        assert call_args.kwargs['rotation_config'] == config['logging']['rotation']
        assert call_args.kwargs['console_enabled'] is True

    @patch('jsscanner.core.engine.get_target_logger')
    @patch('jsscanner.core.engine.FileSystem')
    @patch('jsscanner.core.engine.State')
    @patch('jsscanner.core.engine.Discord')
    def test_engine_handles_missing_logging_config(self, mock_discord, mock_state, mock_fs, mock_logger):
        """Engine should use defaults if logging config missing"""
        from jsscanner.core.engine import ScanEngine

        mock_fs.create_result_structure.return_value = {
            'base': '/tmp/test',
            'logs': '/tmp/test/logs'
        }
        mock_logger.return_value = MagicMock()
        mock_logger.return_value._log_metadata = {}

        # Config without logging section
        config = {}

        engine = ScanEngine(config, "example.com")

        # Should still call logger with defaults
        mock_logger.assert_called_once()
        call_args = mock_logger.call_args

        assert call_args.kwargs['log_dir'] == 'logs'  # default
        assert call_args.kwargs['level'] == logging.INFO  # default


class TestLogAnalyzerEdgeCases:
    """Test edge cases in log analysis"""

    def test_analyze_nonexistent_file(self):
        """Analyzer should handle missing files gracefully"""
        stats = analyze_log_file('/nonexistent/path/test.log')

        assert stats['total_lines'] == 0
        assert len(stats['level_counts']) == 0
        assert stats['first_timestamp'] is None

    def test_analyze_empty_file(self):
        """Analyzer should handle empty files"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = f.name

        try:
            stats = analyze_log_file(temp_path)
            assert stats['total_lines'] == 0
            assert stats['duration_seconds'] == 0.0
        finally:
            os.unlink(temp_path)

    def test_analyze_malformed_log_lines(self):
        """Analyzer should skip malformed lines"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("This is not a proper log line\n")
            f.write("2024-01-15 10:00:00 - [test.py:10] - INFO - Valid line\n")
            f.write("Another malformed line\n")
            f.write("2024-01-15 10:00:01 - [test.py:11] - ERROR - Valid error\n")
            temp_path = f.name

        try:
            stats = analyze_log_file(temp_path)
            # Should only count valid lines
            assert stats['total_lines'] == 2
            assert stats['level_counts']['INFO'] == 1
            assert stats['level_counts']['ERROR'] == 1
        finally:
            os.unlink(temp_path)

    def test_cleanup_with_zero_retention_disabled(self):
        """Zero retention_days should disable cleanup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_log = Path(tmpdir) / "test.log"
            test_log.touch()

            deleted = cleanup_old_logs(tmpdir, retention_days=0)

            assert len(deleted) == 0
            assert test_log.exists()

    def test_cleanup_preserves_recent_logs(self):
        """Recent logs should not be deleted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            recent_log = Path(tmpdir) / "recent.log"
            recent_log.touch()

            deleted = cleanup_old_logs(tmpdir, retention_days=30, dry_run=False)

            assert len(deleted) == 0
            assert recent_log.exists()


class TestConsoleOutput:
    """Test console output configuration"""

    def test_console_disabled_removes_stream_handler(self):
        """Console disabled should not add StreamHandler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = get_target_logger(
                "no_console_test",
                log_dir=tmpdir,
                level=logging.INFO,
                console_enabled=False
            )

            # Count StreamHandlers that aren't file handlers
            stream_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.StreamHandler) and not hasattr(h, 'baseFilename')
            ]

            assert len(stream_handlers) == 0, "Console handler should not exist when disabled"

            # Cleanup
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

    def test_console_enabled_adds_stream_handler(self):
        """Console enabled should add StreamHandler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = get_target_logger(
                "console_test",
                log_dir=tmpdir,
                level=logging.INFO,
                console_enabled=True
            )

            # Count StreamHandlers that aren't file handlers
            stream_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.StreamHandler) and not hasattr(h, 'baseFilename')
            ]

            assert len(stream_handlers) > 0, "Console handler should exist when enabled"

            # Cleanup
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
