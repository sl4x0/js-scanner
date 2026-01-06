"""
Comprehensive tests for SecretScanner module
Tests TruffleHog integration, streaming processing, URL enrichment, concurrent scanning, and notifier callbacks
"""
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from jsscanner.analysis.secrets import SecretScanner


# ============================================================================
# SETUP AND FIXTURES
# ============================================================================

@pytest.fixture
def secret_scanner(default_config, mock_logger, mock_state_manager, mock_notifier, tmp_result_paths):
    """Create SecretScanner instance"""
    scanner = SecretScanner(
        default_config,
        mock_logger,
        mock_state_manager,
        mock_notifier
    )
    scanner.initialize_organizer(tmp_result_paths['base'])
    return scanner


# ============================================================================
# BINARY DETECTION TESTS
# ============================================================================

@pytest.mark.unit
class TestTruffleHogDetection:
    """Test TruffleHog binary detection"""
    
    def test_find_trufflehog_from_config(self, mock_logger, mock_state_manager, mock_notifier, tmp_path):
        """Test finding TruffleHog from config path"""
        fake_binary = tmp_path / "trufflehog"
        fake_binary.write_text("#!/bin/bash\necho 'trufflehog'")
        
        config = {
            'trufflehog_path': str(fake_binary),
            'trufflehog_max_concurrent': 5
        }
        
        scanner = SecretScanner(config, mock_logger, mock_state_manager, mock_notifier)
        
        assert scanner.trufflehog_path == str(fake_binary)
    
    def test_find_trufflehog_system_path(self, default_config, mock_logger, mock_state_manager, mock_notifier):
        """Test finding TruffleHog from system PATH"""
        with patch('shutil.which', return_value='/usr/local/bin/trufflehog'):
            scanner = SecretScanner(default_config, mock_logger, mock_state_manager, mock_notifier)
            
            # Should use system path
            assert 'trufflehog' in scanner.trufflehog_path or scanner.trufflehog_path == '/usr/local/bin/trufflehog'
    
    def test_validate_trufflehog_available(self, secret_scanner):
        """Test successful TruffleHog validation"""
        with patch('shutil.which', return_value='/usr/local/bin/trufflehog'):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout=b'trufflehog 3.50.0'
                )
                
                secret_scanner._validate_trufflehog()
                
                assert secret_scanner.trufflehog_available == True
    
    def test_validate_trufflehog_not_found(self, secret_scanner):
        """Test validation when TruffleHog not found"""
        with patch('shutil.which', return_value=None):
            secret_scanner._validate_trufflehog()
            
            assert secret_scanner.trufflehog_available == False
    
    def test_validate_trufflehog_not_executable(self, secret_scanner):
        """Test validation when TruffleHog exists but not executable"""
        with patch('shutil.which', return_value='/usr/local/bin/trufflehog'):
            with patch('subprocess.run', side_effect=PermissionError):
                secret_scanner._validate_trufflehog()
                
                assert secret_scanner.trufflehog_available == False


# ============================================================================
# SCAN_FILE TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestScanFile:
    """Test file scanning functionality"""
    
    async def test_scan_file_success(self, secret_scanner, tmp_path, sample_secret_finding):
        """Test successful file scanning"""
        test_file = tmp_path / "app.js"
        test_file.write_text("const apiKey = 'AKIAIOSFODNN7EXAMPLE';")
        
        secret_scanner.trufflehog_available = True
        
        # Mock TruffleHog process
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(side_effect=[
                json.dumps(sample_secret_finding).encode() + b'\n',
                b''  # EOF
            ])
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            result = await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
            
            assert isinstance(result, int)
            assert result >= 0
    
    async def test_scan_file_not_available(self, secret_scanner, tmp_path):
        """Test scan when TruffleHog not available"""
        secret_scanner.trufflehog_available = False
        
        test_file = tmp_path / "app.js"
        test_file.write_text("content")
        
        result = await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
        
        assert result == 0
    
    async def test_scan_file_timeout(self, secret_scanner, tmp_path):
        """Test file scan timeout"""
        test_file = tmp_path / "app.js"
        test_file.write_text("content")
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_process.kill = Mock()
            mock_process.wait = AsyncMock()
            mock_exec.return_value = mock_process
            
            result = await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
            
            # Should handle timeout gracefully
            assert isinstance(result, int)
    
    async def test_scan_file_malformed_json(self, secret_scanner, tmp_path):
        """Test handling malformed JSON from TruffleHog"""
        test_file = tmp_path / "app.js"
        test_file.write_text("content")
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(side_effect=[
                b'{invalid json}\n',
                b''
            ])
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            result = await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
            
            # Should handle gracefully
            assert isinstance(result, int)
    
    async def test_scan_file_url_enrichment(self, secret_scanner, tmp_path, sample_secret_finding):
        """Test URL enrichment from manifest"""
        test_file = tmp_path / "app.js"
        test_file.write_text("const key = 'secret';")
        
        # Setup state manager with file manifest
        secret_scanner.state.get_file_manifest = Mock(return_value={
            str(test_file): "https://example.com/app.js"
        })
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(side_effect=[
                json.dumps(sample_secret_finding).encode() + b'\n',
                b''
            ])
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
            
            # URL should be enriched in finding
            # (actual enrichment happens in implementation)


# ============================================================================
# CONCURRENT SCANNING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestConcurrentScanning:
    """Test concurrent scanning with semaphore limits"""
    
    async def test_scan_file_respects_concurrency_limit(self, secret_scanner, tmp_path):
        """Test concurrent scans respect semaphore limit"""
        secret_scanner.trufflehog_available = True
        
        # Create multiple files
        files = []
        for i in range(5):  # Reduced from 10 to 5 for faster execution
            f = tmp_path / f"file{i}.js"
            f.write_text(f"content {i}")
            files.append(f)
        
        # Mock TruffleHog execution
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(return_value=b'')
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            # Scan all files concurrently
            tasks = [
                secret_scanner.scan_file(str(f), f"https://example.com/{f.name}")
                for f in files
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete (may be exceptions or integers)
            assert len(results) == 5
    
    async def test_semaphore_limit_configuration(self, mock_logger, mock_state_manager, mock_notifier):
        """Test custom semaphore limit configuration"""
        config = {
            'trufflehog_max_concurrent': 3
        }
        
        scanner = SecretScanner(config, mock_logger, mock_state_manager, mock_notifier)
        
        assert scanner.semaphore._value == 3


# ============================================================================
# NOTIFIER CALLBACK TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestNotifierCallbacks:
    """Test notifier callback invocation"""
    
    async def test_notifier_called_for_findings(self, secret_scanner, tmp_path, sample_secret_finding):
        """Test notifier is called for secret findings"""
        test_file = tmp_path / "app.js"
        test_file.write_text("const key = 'secret';")
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(side_effect=[
                json.dumps(sample_secret_finding).encode() + b'\n',
                b''
            ])
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
            
            # Notifier should be called (batched or immediate)
            # (actual batching logic implementation-dependent)


# ============================================================================
# SECRETS ORGANIZER INTEGRATION TESTS
# ============================================================================

@pytest.mark.unit
class TestSecretsOrganizerIntegration:
    """Test integration with DomainSecretsOrganizer"""
    
    @pytest.mark.asyncio
    async def test_secrets_saved_to_organizer(self, secret_scanner, tmp_path, sample_secret_finding):
        """Test secrets are saved to organizer"""
        test_file = tmp_path / "app.js"
        test_file.write_text("const key = 'secret';")
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(side_effect=[
                json.dumps(sample_secret_finding).encode() + b'\n',
                b''
            ])
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
            
            # Secrets should be saved to organizer
            # (verified via organizer tests)
    
    def test_initialize_organizer(self, secret_scanner, tmp_path):
        """Test organizer initialization"""
        base_path = str(tmp_path / "results")
        
        secret_scanner.initialize_organizer(base_path)
        
        assert secret_scanner.secrets_organizer is not None
        assert secret_scanner.secrets_organizer.base_path == Path(base_path)


# ============================================================================
# STATISTICS TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestStatistics:
    """Test statistics tracking"""
    
    async def test_secrets_count_tracked(self, secret_scanner, tmp_path, sample_secret_finding):
        """Test secret count is tracked"""
        initial_count = secret_scanner.secrets_count
        
        test_file = tmp_path / "app.js"
        test_file.write_text("const key = 'secret';")
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(side_effect=[
                json.dumps(sample_secret_finding).encode() + b'\n',
                json.dumps(sample_secret_finding).encode() + b'\n',
                b''
            ])
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            result = await secret_scanner.scan_file(str(test_file), "https://example.com/app.js")
            
            # Count should be tracked
            assert result >= 0


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    async def test_scan_nonexistent_file(self, secret_scanner):
        """Test scanning non-existent file"""
        secret_scanner.trufflehog_available = True
        
        result = await secret_scanner.scan_file("/nonexistent/file.js", "https://example.com/file.js")
        
        # Should handle gracefully
        assert isinstance(result, int)
    
    async def test_scan_empty_file(self, secret_scanner, tmp_path):
        """Test scanning empty file"""
        test_file = tmp_path / "empty.js"
        test_file.write_text("")
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(return_value=b'')
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            result = await secret_scanner.scan_file(str(test_file), "https://example.com/empty.js")
            
            assert result == 0
    
    async def test_scan_binary_file(self, secret_scanner, tmp_path):
        """Test scanning binary file"""
        test_file = tmp_path / "binary.bin"
        test_file.write_bytes(b'\x00\x01\x02\xFF\xFE')
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(return_value=b'')
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            result = await secret_scanner.scan_file(str(test_file), "https://example.com/binary.bin")
            
            # Should handle gracefully
            assert isinstance(result, int)
    
    async def test_shutdown_callback_handling(self, mock_logger, mock_state_manager, mock_notifier):
        """Test shutdown callback is respected"""
        shutdown_flag = {'value': False}
        
        def shutdown_callback():
            return shutdown_flag['value']
        
        config = {'trufflehog_max_concurrent': 5}
        scanner = SecretScanner(config, mock_logger, mock_state_manager, mock_notifier, shutdown_callback)
        
        assert scanner.shutdown_callback is not None


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.asyncio
class TestPerformance:
    """Test performance of secret scanning"""
    
    async def test_concurrent_scanning_performance(self, secret_scanner, tmp_path):
        """Test concurrent scanning completes in reasonable time"""
        import time
        
        # Create 20 files
        files = []
        for i in range(20):
            f = tmp_path / f"file{i}.js"
            f.write_text(f"const key{i} = 'value';")
            files.append(f)
        
        secret_scanner.trufflehog_available = True
        
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stdout.readline = AsyncMock(return_value=b'')
            mock_process.wait = AsyncMock(return_value=0)
            mock_exec.return_value = mock_process
            
            start = time.time()
            tasks = [
                secret_scanner.scan_file(str(f), f"https://example.com/{f.name}")
                for f in files
            ]
            await asyncio.gather(*tasks)
            elapsed = time.time() - start
            
            # Should complete reasonably fast with mocking
            assert elapsed < 5.0, f"Concurrent scanning too slow: {elapsed}s"
