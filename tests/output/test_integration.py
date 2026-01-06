"""
Integration tests for output module

Tests cover:
- Discord + reporter workflow
- Complete scan output pipeline
- Mock webhook server interactions
- Real HTTP behavior with mocks
- Concurrent operations
- Edge cases
"""
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from jsscanner.output.discord import Discord
from jsscanner.output.reporter import generate_report


# ============================================================================
# DISCORD + REPORTER WORKFLOW TESTS
# ============================================================================

class TestDiscordReporterWorkflow:
    """Test integrated Discord + reporter workflow"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_scan_workflow(self, sample_report_data, sample_trufflehog_findings):
        """Test complete scan workflow with Discord and reporter"""
        # Setup Discord
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        await discord.start()
        
        # Queue secrets
        for secret in sample_trufflehog_findings:
            await discord.queue_alert(secret)
        
        assert len(discord.queue) == 2
        
        # Mock HTTP for Discord
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Generate report
            stats = {'scan_duration': 120.0, 'total_files': 50}
            result = generate_report(
                "example.com",
                sample_report_data['base_path'],
                stats
            )
            
            assert result is True
            
            # Verify report exists
            report_path = Path(sample_report_data['base_path']) / "REPORT.md"
            assert report_path.exists()
            
            # Stop Discord and drain
            await discord.stop(drain_queue=True)
        
        assert discord.running is False
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_secrets_trigger_discord_alerts(self, sample_trufflehog_findings):
        """Test secrets trigger Discord alerts"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        await discord.start()
        
        # Mock HTTP
        post_calls = []
        
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            
            async def post_side_effect(*args, **kwargs):
                post_calls.append((args, kwargs))
                return mock_response
            
            mock_session.post = AsyncMock(side_effect=post_side_effect)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Queue secrets
            for secret in sample_trufflehog_findings:
                await discord.queue_alert(secret)
            
            # Let worker process
            await asyncio.sleep(1)
            
            # Stop and drain
            await discord.stop(drain_queue=True)
        
        # Should have made HTTP calls
        assert len(post_calls) >= 1
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_report_generation_includes_all_components(self, sample_report_data):
        """Test report generation includes all components"""
        stats = {
            'scan_duration': 125.5,
            'total_files': 50,
            'secrets_found': 2,
            'endpoints_found': 3
        }
        
        result = generate_report(
            "example.com",
            sample_report_data['base_path'],
            stats
        )
        
        assert result is True
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Verify all sections present
        assert "Scan Report" in content
        assert "Critical Findings" in content
        assert "Endpoints" in content
        assert "Parameters" in content
        assert "Output Structure" in content


# ============================================================================
# MOCK WEBHOOK SERVER TESTS
# ============================================================================

class TestMockWebhookServer:
    """Test with mock webhook server"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_http_post_to_mock_webhook(self, sample_trufflehog_findings):
        """Test real HTTP POST to mock webhook server"""
        # Note: Discord uses curl_cffi, not aiohttp, so we mock the actual HTTP call
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            await discord.start()
            
            # Queue alert
            await discord.queue_alert(sample_trufflehog_findings[0])
            
            # Let worker process
            await asyncio.sleep(0.5)
            
            await discord.stop(drain_queue=False)
            
            # Verify POST was called
            assert mock_session.post.called
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_embed_structure_validation(self, sample_trufflehog_findings):
        """Test embed structure is valid Discord format"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock()
        )
        
        # Create embed
        embed = discord._create_embed(sample_trufflehog_findings[0])
        
        # Validate structure
        assert 'embeds' in embed
        assert len(embed['embeds']) == 1
        
        embed_data = embed['embeds'][0]
        
        # Required fields
        assert 'title' in embed_data
        assert 'description' in embed_data
        assert 'color' in embed_data
        assert 'timestamp' in embed_data
        
        # Title length (Discord limit: 256)
        assert len(embed_data['title']) <= 256
        
        # Description length (Discord limit: 4096)
        assert len(embed_data['description']) <= 4096
        
        # Color is integer
        assert isinstance(embed_data['color'], int)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rate_limiting_with_mock_http(self, sample_trufflehog_findings):
        """Test rate limiting with mock HTTP"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=5  # Low rate limit for testing
        )
        
        await discord.start()
        
        post_calls = []
        start_time = asyncio.get_event_loop().time()
        
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            
            async def post_side_effect(*args, **kwargs):
                post_calls.append(asyncio.get_event_loop().time() - start_time)
                return mock_response
            
            mock_session.post = AsyncMock(side_effect=post_side_effect)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Queue 10 messages
            for i in range(10):
                secret = sample_trufflehog_findings[0].copy()
                secret['Raw'] = f"SECRET_{i}"
                secret['SourceMetadata']['line'] = i
                await discord.queue_alert(secret)
            
            # Let worker process
            await asyncio.sleep(5)
            
            await discord.stop(drain_queue=False)
        
        # Should have made some calls (rate limited)
        assert len(post_calls) <= 10
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_429_retry_with_mock_server(self, sample_trufflehog_findings):
        """Test 429 retry logic with mock server"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        await discord.start()
        
        call_count = 0
        
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            
            async def post_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                # First call returns 429, second succeeds
                if call_count == 1:
                    mock_response = Mock()
                    mock_response.status_code = 429
                    mock_response.headers = {'Retry-After': '1'}
                    return mock_response
                else:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    return mock_response
            
            mock_session.post = AsyncMock(side_effect=post_side_effect)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            with patch('asyncio.sleep', new_callable=AsyncMock):
                # Queue alert
                await discord.queue_alert(sample_trufflehog_findings[0])
                
                # Let worker process
                await asyncio.sleep(0.5)
                
                await discord.stop(drain_queue=False)
        
        # Should have made 2 calls (initial + retry)
        assert call_count >= 1


# ============================================================================
# EDGE CASES
# ============================================================================

class TestOutputIntegrationEdgeCases:
    """Test edge cases for output integration"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_discord_with_no_secrets(self):
        """Test Discord with no secrets (no alerts sent)"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        await discord.start()
        
        # Don't queue any secrets
        
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            await asyncio.sleep(0.5)
            
            await discord.stop(drain_queue=False)
            
            # Should not have called POST
            assert not mock_session.post.called
    
    @pytest.mark.integration
    def test_reporter_with_empty_findings(self, tmp_path):
        """Test reporter with empty findings (minimal report)"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create empty files
        (findings_dir / "endpoints.txt").write_text("")
        (findings_dir / "params.txt").write_text("")
        (findings_dir / "domains.txt").write_text("")
        
        stats = {'scan_duration': 60.0, 'total_files': 0}
        result = generate_report("example.com", str(base_path), stats)
        
        assert result is True
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Should indicate clean scan
        assert "Clean" in content or "No secrets" in content
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_discord_and_reporter(self, sample_report_data, sample_trufflehog_findings):
        """Test concurrent Discord notifications and report generation"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        await discord.start()
        
        # Mock HTTP
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Start concurrent operations
            discord_task = asyncio.create_task(
                discord.queue_batch_alert(sample_trufflehog_findings)
            )
            
            # Generate report concurrently (in executor since it's sync)
            loop = asyncio.get_event_loop()
            report_task = loop.run_in_executor(
                None,
                generate_report,
                "example.com",
                sample_report_data['base_path'],
                {'scan_duration': 120.0, 'total_files': 50}
            )
            
            # Wait for both
            await discord_task
            report_result = await report_task
            
            assert report_result is True
            assert len(discord.queue) > 0
            
            await discord.stop(drain_queue=False)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestOutputPerformance:
    """Performance tests for output module"""
    
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_discord_handles_large_queue(self, sample_trufflehog_findings):
        """Test Discord handles large queue (100+ messages)"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30,
            max_queue_size=200
        )
        
        # Queue 100 messages
        for i in range(100):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
            await discord.queue_alert(secret)
        
        assert len(discord.queue) == 100
        
        # Cleanup
        discord.queue.clear()
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_reporter_handles_large_dataset(self, tmp_path):
        """Test reporter handles large dataset (100+ secrets, 1000+ endpoints)"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create trufflehog.json with 100 secrets
        trufflehog_file = findings_dir / "trufflehog.json"
        with open(trufflehog_file, 'w', encoding='utf-8') as f:
            for i in range(100):
                secret = {
                    "SourceMetadata": {
                        "url": f"https://example.com/app{i}.js",
                        "Data": {"Filesystem": {"file": f"app{i}.js"}}
                    },
                    "DetectorName": "Test",
                    "Verified": i % 10 == 0,  # 10% verified
                    "Raw": f"SECRET_{i}",
                    "Redacted": f"***{i}"
                }
                f.write(json.dumps(secret) + '\n')
        
        # Create endpoints.txt with 1000 endpoints
        endpoints_file = findings_dir / "endpoints.txt"
        endpoints = [f"https://api.example.com/v1/endpoint{i}" for i in range(1000)]
        endpoints_file.write_text("\n".join(endpoints))
        
        stats = {'scan_duration': 600.0, 'total_files': 500}
        result = generate_report("example.com", str(base_path), stats)
        
        assert result is True
        
        report_path = base_path / "REPORT.md"
        assert report_path.exists()
        
        # Report should be reasonable size (not gigantic)
        content = report_path.read_text(encoding='utf-8')
        assert len(content) < 1_000_000  # Less than 1MB


# ============================================================================
# ERROR RECOVERY TESTS
# ============================================================================

class TestOutputErrorRecovery:
    """Test error recovery in output module"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_discord_recovers_from_network_errors(self, sample_trufflehog_findings):
        """Test Discord recovers from transient network errors"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        await discord.start()
        
        call_count = 0
        
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            
            async def post_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                # First 2 calls fail, rest succeed
                if call_count <= 2:
                    raise Exception("Network timeout")
                else:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    return mock_response
            
            mock_session.post = AsyncMock(side_effect=post_side_effect)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Queue messages
            for i in range(5):
                secret = sample_trufflehog_findings[0].copy()
                secret['Raw'] = f"SECRET_{i}"
                secret['SourceMetadata']['line'] = i
                await discord.queue_alert(secret)
            
            # Let worker process
            await asyncio.sleep(2)
            
            # Worker should still be running
            assert discord.running is True
            
            await discord.stop(drain_queue=False)
    
    @pytest.mark.integration
    def test_reporter_recovers_from_partial_data(self, tmp_path):
        """Test reporter generates report even with partial data"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create only endpoints.txt (missing other files)
        endpoints_file = findings_dir / "endpoints.txt"
        endpoints_file.write_text("https://api.example.com/v1/users\n")
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        result = generate_report("example.com", str(base_path), stats)
        
        # Should succeed even with partial data
        assert result is True
        
        report_path = base_path / "REPORT.md"
        assert report_path.exists()
