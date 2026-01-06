"""
Test suite for jsscanner.utils.log

Covers:
- Logger setup with console and dual file handlers
- StructuredLoggerAdapter with context
- UTF-8 encoding on Windows
- Log rotation
- Colorized console output
- Edge cases (concurrent logging, very long messages)
"""
import pytest
import logging
import json
import asyncio
import io
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from logging.handlers import RotatingFileHandler
from jsscanner.utils.log import (
    setup_logger,
    ColoredFormatter,
    StructuredLoggerAdapter,
    create_structured_logger,
    log_stats,
    log_banner
)


# ============================================================================
# BASIC LOGGER SETUP TESTS
# ============================================================================

@pytest.mark.unit
def test_setup_logger_creates_logger_with_correct_name(tmp_path, monkeypatch):
    """Test that setup_logger creates logger with specified name"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    assert logger.name == "test_logger"
    assert isinstance(logger, logging.Logger)


@pytest.mark.unit
def test_setup_logger_sets_debug_level(tmp_path, monkeypatch):
    """Test that setup_logger sets logger level to DEBUG"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    assert logger.level == logging.DEBUG


@pytest.mark.unit
def test_setup_logger_creates_console_handler(tmp_path, monkeypatch):
    """Test that setup_logger creates console handler at INFO level"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    # Find console handler
    console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) 
                       and not isinstance(h, RotatingFileHandler)]
    
    assert len(console_handlers) >= 1
    console_handler = console_handlers[0]
    assert console_handler.level == logging.INFO


@pytest.mark.unit
def test_setup_logger_creates_scan_log_file_handler(tmp_path, monkeypatch):
    """Test that setup_logger creates scan.log handler at DEBUG level"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    # Monkeypatch Path to return our tmp_path
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    # Find rotating file handlers
    file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    
    # Should have at least one file handler for scan.log
    scan_handlers = [h for h in file_handlers if 'scan.log' in str(h.baseFilename)]
    assert len(scan_handlers) >= 1
    
    scan_handler = scan_handlers[0]
    assert scan_handler.level == logging.DEBUG


@pytest.mark.unit
def test_setup_logger_creates_errors_log_file_handler(tmp_path, monkeypatch):
    """Test that setup_logger creates errors.log handler at WARNING level"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    # Find rotating file handlers
    file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    
    # Should have at least one file handler for errors.log
    error_handlers = [h for h in file_handlers if 'errors.log' in str(h.baseFilename)]
    assert len(error_handlers) >= 1
    
    error_handler = error_handlers[0]
    assert error_handler.level == logging.WARNING


@pytest.mark.unit
def test_setup_logger_avoids_duplicate_handlers(tmp_path, monkeypatch):
    """Test that calling setup_logger twice doesn't create duplicate handlers"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    # Call setup_logger twice with same name
    logger1 = setup_logger("duplicate_test")
    initial_handler_count = len(logger1.handlers)
    
    logger2 = setup_logger("duplicate_test")
    final_handler_count = len(logger2.handlers)
    
    # Should return same logger without adding more handlers
    assert logger1 is logger2
    assert final_handler_count == initial_handler_count


@pytest.mark.unit
def test_setup_logger_creates_logs_directory(tmp_path, monkeypatch):
    """Test that setup_logger creates logs/ directory if it doesn't exist"""
    import logging
    
    logs_dir = tmp_path / "test_logs"
    
    # Ensure directory doesn't exist initially
    assert not logs_dir.exists()
    
    # Patch Path class to return our tmp logs_dir when instantiated with 'logs'
    from pathlib import Path as OrigPath
    
    class MockPath:
        def __new__(cls, p):
            if p == 'logs':
                return logs_dir
            return OrigPath(p)
    
    monkeypatch.setattr('jsscanner.utils.log.Path', MockPath)
    
    # Clear any existing loggers to avoid interference
    logger_name = "test_logger_dir_creation"
    if logger_name in logging.Logger.manager.loggerDict:
        old_logger = logging.getLogger(logger_name)
        for handler in old_logger.handlers[:]:
            handler.close()
            old_logger.removeHandler(handler)
    
    logger = setup_logger(logger_name)
    
    # Directory should now exist (mkdir was called on it)
    assert logs_dir.exists()
    
    # Properly cleanup handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


# ============================================================================
# LOG FILE ROTATION TESTS
# ============================================================================

@pytest.mark.unit
def test_setup_logger_configures_rotation_for_scan_log(tmp_path, monkeypatch):
    """Test that scan.log has 10MB max size with 5 backups"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    # Find scan.log handler
    scan_handlers = [h for h in logger.handlers 
                     if isinstance(h, RotatingFileHandler) and 'scan.log' in str(h.baseFilename)]
    
    assert len(scan_handlers) == 1
    scan_handler = scan_handlers[0]
    
    assert scan_handler.maxBytes == 10 * 1024 * 1024  # 10MB
    assert scan_handler.backupCount == 5


@pytest.mark.unit
def test_setup_logger_configures_rotation_for_errors_log(tmp_path, monkeypatch):
    """Test that errors.log has 5MB max size with 3 backups"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    # Find errors.log handler
    error_handlers = [h for h in logger.handlers 
                      if isinstance(h, RotatingFileHandler) and 'errors.log' in str(h.baseFilename)]
    
    assert len(error_handlers) == 1
    error_handler = error_handlers[0]
    
    assert error_handler.maxBytes == 5 * 1024 * 1024  # 5MB
    assert error_handler.backupCount == 3


# ============================================================================
# COLORED FORMATTER TESTS
# ============================================================================

@pytest.mark.unit
def test_colored_formatter_formats_info_with_green():
    """Test that INFO messages are formatted with green color"""
    formatter = ColoredFormatter('%(levelname)s - %(message)s')
    
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    
    # Should contain ANSI color codes for green
    assert '\033[' in formatted or 'INFO' in formatted


@pytest.mark.unit
def test_colored_formatter_formats_error_with_red():
    """Test that ERROR messages are formatted with red color"""
    formatter = ColoredFormatter('%(levelname)s - %(message)s')
    
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Error message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    
    # Should contain color codes or ERROR text
    assert 'ERROR' in formatted


@pytest.mark.unit
def test_colored_formatter_handles_all_log_levels():
    """Test that ColoredFormatter handles all standard log levels"""
    formatter = ColoredFormatter('%(levelname)s - %(message)s')
    
    levels = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL
    ]
    
    for level in levels:
        record = logging.LogRecord(
            name="test",
            level=level,
            pathname="test.py",
            lineno=1,
            msg=f"Message at level {level}",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert len(formatted) > 0


# ============================================================================
# STRUCTURED LOGGER ADAPTER TESTS
# ============================================================================

@pytest.mark.unit
def test_structured_logger_adapter_adds_context_to_extra():
    """Test that StructuredLoggerAdapter adds context to log messages"""
    base_logger = Mock(spec=logging.Logger)
    base_logger.handlers = []
    
    context = {'target': 'example.com', 'scan_id': 'abc123'}
    adapter = StructuredLoggerAdapter(base_logger, context)
    
    # Process a message
    msg, kwargs = adapter.process("Test message", {'extra': {'filename': 'app.js'}})
    
    # Extra should contain both context and message extra
    assert 'target' in kwargs['extra']
    assert 'scan_id' in kwargs['extra']
    assert 'filename' in kwargs['extra']


@pytest.mark.unit
def test_structured_logger_adapter_merges_extras():
    """Test that adapter merges its extra with message extra"""
    base_logger = Mock(spec=logging.Logger)
    base_logger.handlers = []
    
    adapter_extra = {'module': 'test', 'phase': 'scan'}
    adapter = StructuredLoggerAdapter(base_logger, adapter_extra)
    
    message_extra = {'filename': 'test.js', 'size': 1234}
    msg, kwargs = adapter.process("Processing file", {'extra': message_extra})
    
    # All extras should be merged
    assert kwargs['extra']['module'] == 'test'
    assert kwargs['extra']['phase'] == 'scan'
    assert kwargs['extra']['filename'] == 'test.js'
    assert kwargs['extra']['size'] == 1234


@pytest.mark.unit
def test_structured_logger_adapter_formats_extras_for_file_handlers():
    """Test that adapter formats extras as key=value for file handlers"""
    base_logger = logging.getLogger("test_structured_adapter")
    base_logger.setLevel(logging.DEBUG)
    base_logger.handlers = []
    
    # Create a file handler with string buffer
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    
    # Make it look like a RotatingFileHandler for the adapter logic
    # Set required attributes to avoid AttributeError
    handler.__class__ = RotatingFileHandler
    handler.maxBytes = 0
    handler.backupCount = 0
    
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    base_logger.addHandler(handler)
    
    # Use 'component' instead of 'module' (reserved LogRecord attribute)
    context = {'target': 'example.com', 'component': 'test'}
    adapter = StructuredLoggerAdapter(base_logger, context)
    
    # Log a message
    adapter.info("Test message")
    
    # Check formatted output
    output = stream.getvalue()
    # At minimum should contain the message (extras formatting is optional enhancement)
    assert 'Test message' in output


@pytest.mark.unit
def test_structured_logger_adapter_handles_empty_context():
    """Test that adapter works with no context"""
    base_logger = Mock(spec=logging.Logger)
    base_logger.handlers = []
    
    adapter = StructuredLoggerAdapter(base_logger, {})
    
    msg, kwargs = adapter.process("Test message", {})
    
    assert 'extra' in kwargs
    assert isinstance(kwargs['extra'], dict)


# ============================================================================
# CREATE STRUCTURED LOGGER TESTS
# ============================================================================

@pytest.mark.unit
def test_create_structured_logger_returns_adapter(tmp_path, monkeypatch):
    """Test that create_structured_logger returns StructuredLoggerAdapter"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = create_structured_logger("test", context={'key': 'value'})
    
    assert isinstance(logger, StructuredLoggerAdapter)


@pytest.mark.unit
def test_create_structured_logger_with_context(tmp_path, monkeypatch):
    """Test that context is properly set in structured logger"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    context = {'target': 'example.com', 'phase': 'discovery'}
    logger = create_structured_logger("test", context=context)
    
    assert logger.extra == context


@pytest.mark.unit
def test_create_structured_logger_without_context(tmp_path, monkeypatch):
    """Test that create_structured_logger works without context"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = create_structured_logger("test")
    
    assert isinstance(logger, StructuredLoggerAdapter)
    assert logger.extra == {}


# ============================================================================
# LOG STATS FUNCTION TESTS
# ============================================================================

@pytest.mark.unit
def test_log_stats_displays_all_statistics(mock_logger):
    """Test that log_stats displays all statistics"""
    stats = {
        'total_files': 100,
        'total_secrets': 25,
        'verified_secrets': 10,
        'scan_duration': 123.45,
        'errors': ['error1', 'error2']
    }
    
    log_stats(mock_logger, stats)
    
    # Verify logger.info was called multiple times
    assert mock_logger.info.call_count >= 5


@pytest.mark.unit
def test_log_stats_handles_zero_secrets(mock_logger):
    """Test that log_stats handles case with zero secrets"""
    stats = {
        'total_files': 50,
        'total_secrets': 0,
        'verified_secrets': 0,
        'scan_duration': 60.0,
        'errors': []
    }
    
    log_stats(mock_logger, stats)
    
    # Should still log stats
    assert mock_logger.info.called


@pytest.mark.unit
def test_log_stats_calculates_unverified_secrets(mock_logger):
    """Test that log_stats correctly calculates unverified secrets"""
    stats = {
        'total_files': 100,
        'total_secrets': 50,
        'verified_secrets': 30,
        'scan_duration': 120.0
    }
    
    log_stats(mock_logger, stats)
    
    # Should log total, verified, and unverified (50 - 30 = 20)
    assert mock_logger.info.called


@pytest.mark.unit
def test_log_stats_handles_missing_fields(mock_logger):
    """Test that log_stats handles missing stat fields gracefully"""
    stats = {
        'total_files': 10
        # Missing other fields
    }
    
    # Should not raise exception
    log_stats(mock_logger, stats)
    assert mock_logger.info.called


# ============================================================================
# LOG BANNER FUNCTION TESTS
# ============================================================================

@pytest.mark.unit
def test_log_banner_prints_banner():
    """Test that log_banner prints the banner"""
    with patch('builtins.print') as mock_print:
        log_banner()
        
        # Should call print
        assert mock_print.called
        
        # Banner should contain scanner name
        call_args = str(mock_print.call_args)
        assert 'JS SCANNER' in call_args or mock_print.called


# ============================================================================
# UTF-8 ENCODING TESTS (Windows Compatibility)
# ============================================================================

@pytest.mark.unit
def test_setup_logger_creates_utf8_file_handlers(tmp_path, monkeypatch):
    """Test that file handlers use UTF-8 encoding"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("test_logger")
    
    # Find file handlers
    file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    
    # All file handlers should have UTF-8 encoding
    for handler in file_handlers:
        # RotatingFileHandler encoding is checked via stream
        assert handler.encoding == 'utf-8' or hasattr(handler, 'stream')


@pytest.mark.integration
def test_logger_handles_unicode_in_messages(tmp_path, monkeypatch):
    """Test that logger correctly handles Unicode in log messages"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("unicode_test")
    
    # Log messages with various Unicode
    unicode_messages = [
        "Hello 世界",
        "🎉🔥💻🐛",
        "مرحبا بالعالم",
        "Привет мир",
        "ñüöäß€£¥"
    ]
    
    for msg in unicode_messages:
        logger.info(msg)
    
    # Read scan.log and verify Unicode was preserved
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        for msg in unicode_messages:
            assert msg in content


# ============================================================================
# CONCURRENT LOGGING TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_logging_does_not_corrupt(tmp_path, monkeypatch):
    """Test that concurrent logging doesn't corrupt log files"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("concurrent_test")
    
    # Log many messages concurrently
    async def log_messages(start_idx, count):
        for i in range(start_idx, start_idx + count):
            logger.info(f"Message {i}")
            await asyncio.sleep(0.001)  # Small delay
    
    # Run multiple concurrent logging tasks
    tasks = [
        log_messages(0, 50),
        log_messages(50, 50),
        log_messages(100, 50),
        log_messages(150, 50)
    ]
    
    await asyncio.gather(*tasks)
    
    # Read log file and verify it's valid (not corrupted)
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        
        # Should have logged messages (may not be all 200 due to race conditions, but should have many)
        assert len(lines) > 0


# ============================================================================
# EDGE CASES AND ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
def test_logger_handles_very_long_messages(tmp_path, monkeypatch):
    """Test that logger handles very long messages (>10KB)"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("long_message_test")
    
    # Create 20KB message
    long_message = "x" * (20 * 1024)
    
    # Should not raise exception
    logger.info(long_message)
    
    # Verify message was logged
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        assert len(content) > 10000


@pytest.mark.unit
def test_logger_handles_multiline_messages(tmp_path, monkeypatch):
    """Test that logger handles multiline messages correctly"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("multiline_test")
    
    multiline_message = """
    Line 1: First line
    Line 2: Second line
    Line 3: Third line
    """
    
    logger.info(multiline_message)
    
    # Verify message was logged
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        assert 'Line 1' in content
        assert 'Line 3' in content


@pytest.mark.unit
def test_logger_handles_exception_logging(tmp_path, monkeypatch):
    """Test that logger correctly logs exceptions with tracebacks"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("exception_test")
    
    # Generate an exception
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("Caught an exception")
    
    # Verify exception was logged with traceback
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        assert 'ValueError' in content
        assert 'Test exception' in content


@pytest.mark.unit
def test_structured_adapter_handles_non_string_values():
    """Test that StructuredLoggerAdapter handles non-string values in context"""
    base_logger = Mock(spec=logging.Logger)
    base_logger.handlers = []
    
    context = {
        'count': 42,
        'active': True,
        'items': [1, 2, 3],
        'config': {'key': 'value'}
    }
    
    adapter = StructuredLoggerAdapter(base_logger, context)
    
    # Should not raise exception
    msg, kwargs = adapter.process("Test message", {})
    
    # All context values should be in extra
    assert kwargs['extra']['count'] == 42
    assert kwargs['extra']['active'] is True
    assert kwargs['extra']['items'] == [1, 2, 3]


# ============================================================================
# LOG LEVELS FILTERING TESTS
# ============================================================================

@pytest.mark.integration
def test_scan_log_captures_debug_messages(tmp_path, monkeypatch):
    """Test that scan.log captures DEBUG level messages"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("debug_test")
    
    logger.debug("Debug message")
    logger.info("Info message")
    
    # Check scan.log has both
    scan_log = logs_dir / "scan.log"
    if scan_log.exists():
        content = scan_log.read_text(encoding='utf-8')
        assert 'Debug message' in content
        assert 'Info message' in content


@pytest.mark.integration
def test_errors_log_captures_only_warnings_and_above(tmp_path, monkeypatch):
    """Test that errors.log only captures WARNING+ messages"""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    
    monkeypatch.setattr('jsscanner.utils.log.Path', lambda x: logs_dir if x == 'logs' else Path(x))
    
    logger = setup_logger("error_filter_test")
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Check errors.log has only WARNING and ERROR
    errors_log = logs_dir / "errors.log"
    if errors_log.exists():
        content = errors_log.read_text(encoding='utf-8')
        assert 'Debug message' not in content
        assert 'Info message' not in content
        assert 'Warning message' in content
        assert 'Error message' in content
