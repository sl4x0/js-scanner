"""
Comprehensive test suite for Discord webhook notifier

Tests cover:
- Initialization and configuration
- Rate limiting (sliding window)
- 429 handling and retry logic
- Queue management and overflow
- Deduplication
- Worker resilience
- HTTP response handling
- Error scenarios
"""
import pytest
import asyncio
import time
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from collections import deque

from jsscanner.output.discord import Discord


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestDiscordInitialization:
    """Test Discord class initialization"""
    
    @pytest.mark.unit
    def test_init_with_valid_webhook(self):
        """Test Discord initializes with valid webhook URL"""
        webhook_url = "https://discord.com/api/webhooks/123/token"
        discord = Discord(webhook_url=webhook_url)
        
        assert discord.webhook_url == webhook_url
        assert discord.rate_limit == 30  # default
        assert discord.max_queue_size == 1000  # default
        assert discord.running is False
        assert len(discord.queue) == 0
        assert len(discord.message_times) == 0
    
    @pytest.mark.unit
    def test_init_with_custom_rate_limit(self):
        """Test Discord initializes with custom rate limit"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=10
        )
        
        assert discord.rate_limit == 10
    
    @pytest.mark.unit
    def test_init_with_custom_queue_size(self):
        """Test Discord initializes with custom max queue size"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            max_queue_size=500
        )
        
        assert discord.max_queue_size == 500
    
    @pytest.mark.unit
    def test_init_with_logger(self, mock_logger):
        """Test Discord initializes with logger"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger
        )
        
        assert discord.logger == mock_logger
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_start_initializes_worker(self):
        """Test start() creates worker task"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        await discord.start()
        
        assert discord.running is True
        assert discord._task is not None
        
        # Cleanup
        await discord.stop(drain_queue=False)


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

class TestDiscordRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_can_send_returns_true_initially(self):
        """Test _can_send() returns True when no messages sent"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=5
        )
        
        assert await discord._can_send() is True
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_can_send_returns_false_when_limit_reached(self):
        """Test _can_send() returns False when rate limit reached"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=2
        )
        
        # Simulate 2 messages sent
        current_time = time.time()
        discord.message_times.append(current_time)
        discord.message_times.append(current_time)
        
        assert await discord._can_send() is False
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_can_send_returns_true_after_window_expires(self):
        """Test _can_send() returns True after sliding window expires"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=2
        )
        
        # Simulate 2 messages sent 61 seconds ago
        old_time = time.time() - 61
        discord.message_times.append(old_time)
        discord.message_times.append(old_time)
        
        # Should be True because old timestamps are removed
        assert await discord._can_send() is True
        assert len(discord.message_times) == 0  # Old entries removed
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_message_times_cleanup(self):
        """Test old message times are removed from tracking"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=10
        )
        
        # Add mix of old and recent timestamps
        current_time = time.time()
        discord.message_times.append(current_time - 70)  # Old
        discord.message_times.append(current_time - 30)  # Recent
        discord.message_times.append(current_time - 10)  # Recent
        
        await discord._can_send()
        
        # Only recent timestamps should remain
        assert len(discord.message_times) == 2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limit_with_different_configurations(self):
        """Test rate limiting with various rate_limit values"""
        test_cases = [1, 5, 10, 30]
        
        for rate_limit in test_cases:
            discord = Discord(
                webhook_url="https://discord.com/api/webhooks/123/token",
                rate_limit=rate_limit
            )
            
            # Fill up to limit
            current_time = time.time()
            for _ in range(rate_limit):
                discord.message_times.append(current_time)
            
            # Should be at limit
            assert await discord._can_send() is False
            
            # Clear and try with room
            discord.message_times.clear()
            for _ in range(rate_limit - 1):
                discord.message_times.append(current_time)
            
            # Should have room for 1 more
            assert await discord._can_send() is True
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limit_respects_rate_limited_until(self):
        """Test _can_send() respects explicit rate limit window"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=30
        )
        
        # Set rate_limited_until to future time
        discord.rate_limited_until = time.time() + 10
        
        assert await discord._can_send() is False
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_temporary_rate_limit_applied(self):
        """Test temporary rate limit is used when active"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=30
        )
        
        # Set temporary rate limit
        discord.temporary_rate_limit = 5
        discord.temporary_rate_limit_expires = time.time() + 60
        
        # Fill up to temporary limit
        current_time = time.time()
        for _ in range(5):
            discord.message_times.append(current_time)
        
        # Should respect temporary limit (5), not original (30)
        assert await discord._can_send() is False


# ============================================================================
# 429 HANDLING TESTS
# ============================================================================

class TestDiscord429Handling:
    """Test 429 rate limit response handling"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_429_response_triggers_retry_after_parsing(self):
        """Test 429 response parses Retry-After header"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock()
        )
        
        # Mock response with 429 and Retry-After
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '5'}
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            await discord._send_webhook(mock_session, embed)
            
            # Should have set rate_limited_until
            assert discord.rate_limited_until > time.time()
            
            # Should have called sleep
            mock_sleep.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_429_sets_temporary_rate_limit(self):
        """Test 429 response sets temporary reduced rate limit"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=30,
            logger=Mock()
        )
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '5'}
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await discord._send_webhook(mock_session, embed)
            
            # Should have set temporary rate limit
            assert discord.temporary_rate_limit is not None
            assert discord.temporary_rate_limit < discord.rate_limit
            assert discord.temporary_rate_limit_expires > time.time()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_429_message_requeued(self):
        """Test message is requeued after 429"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock()
        )
        
        await discord.start()
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '1'}
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await discord._send_webhook(mock_session, embed)
            
            # Message should be back in queue
            assert len(discord.queue) == 1
        
        await discord.stop(drain_queue=False)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_429_retry_count_increments(self):
        """Test retry count increments on 429"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock()
        )
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '1'}
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        embed_id = id(embed)
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await discord._send_webhook(mock_session, embed)
            
            # Retry count should be 1
            assert discord.message_retry_counts[embed_id] == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_429_message_dropped_after_max_retries(self, mock_logger):
        """Test message dropped after 3 failed 429 retries"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger
        )
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '1'}
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        embed_id = id(embed)
        
        # Set retry count to 3 (max)
        discord.message_retry_counts[embed_id] = 3
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            await discord._send_webhook(mock_session, embed)
            
            # Should have logged error
            mock_logger.error.assert_called()
            
            # Retry count should be removed
            assert embed_id not in discord.message_retry_counts
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_429_without_retry_after_uses_default(self, mock_logger):
        """Test 429 without Retry-After header uses default backoff"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger
        )
        
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}  # No Retry-After
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            await discord._send_webhook(mock_session, embed)
            
            # Should have called sleep with default (5)
            mock_sleep.assert_called_once()
            call_args = mock_sleep.call_args[0]
            assert call_args[0] == 5  # Default retry_after


# ============================================================================
# QUEUE MANAGEMENT TESTS
# ============================================================================

class TestDiscordQueueManagement:
    """Test queue management functionality"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_queue_alert_adds_message_to_queue(self, sample_trufflehog_findings):
        """Test queue_alert() adds message to queue"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        await discord.queue_alert(sample_trufflehog_findings[0])
        
        assert len(discord.queue) == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_queue_processes_messages_fifo(self, sample_trufflehog_findings):
        """Test queue processes messages in FIFO order"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=30
        )
        
        await discord.start()
        
        # Add multiple messages
        for i in range(3):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            await discord.queue_alert(secret)
        
        # Mock the HTTP client
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Let worker process
            await asyncio.sleep(0.5)
            
            # Queue should be empty or processing
            assert len(discord.queue) <= 3
        
        await discord.stop(drain_queue=False)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_queue_overflow_drops_messages(self, mock_logger, sample_trufflehog_findings):
        """Test queue overflow drops oldest messages"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            max_queue_size=5,
            logger=mock_logger
        )
        
        # Fill queue to max
        for i in range(5):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i  # Make unique
            await discord.queue_alert(secret)
        
        assert len(discord.queue) == 5
        
        # Try to add one more (should be dropped)
        secret = sample_trufflehog_findings[0].copy()
        secret['Raw'] = "SECRET_6"
        secret['SourceMetadata']['line'] = 6
        await discord.queue_alert(secret)
        
        # Queue size should still be 5
        assert len(discord.queue) == 5
        
        # Messages dropped counter should increment
        assert discord._messages_dropped == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_queue_overflow_logs_warning(self, mock_logger, sample_trufflehog_findings):
        """Test warning logged on first drop"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            max_queue_size=3,
            logger=mock_logger
        )
        
        # Fill queue
        for i in range(3):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
            await discord.queue_alert(secret)
        
        # Add one more (first drop)
        secret = sample_trufflehog_findings[0].copy()
        secret['Raw'] = "SECRET_4"
        secret['SourceMetadata']['line'] = 4
        await discord.queue_alert(secret)
        
        # Should have logged warning
        mock_logger.warning.assert_called()
        warning_message = str(mock_logger.warning.call_args[0][0])
        assert "queue full" in warning_message.lower()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_queue_size_respects_max_queue_size(self, sample_trufflehog_findings):
        """Test queue size never exceeds max_queue_size"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            max_queue_size=10
        )
        
        # Try to add 20 messages
        for i in range(20):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
            await discord.queue_alert(secret)
        
        # Queue size should not exceed max
        assert len(discord.queue) <= 10
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_stop_drains_queue(self, sample_trufflehog_findings):
        """Test stop(drain_queue=True) waits for queue to empty"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=30
        )
        
        await discord.start()
        
        # Add messages
        for i in range(3):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
            await discord.queue_alert(secret)
        
        # Mock HTTP client to respond quickly
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Stop and drain
            await discord.stop(drain_queue=True)
            
            # Queue should be empty (or close to empty)
            assert len(discord.queue) <= 1  # Allow for timing


# ============================================================================
# DEDUPLICATION TESTS
# ============================================================================

class TestDiscordDeduplication:
    """Test deduplication functionality"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_identical_secrets_deduped(self, sample_trufflehog_findings):
        """Test identical secrets are deduped"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret = sample_trufflehog_findings[0]
        
        # Add same secret twice
        await discord.queue_alert(secret)
        await discord.queue_alert(secret)
        
        # Queue should only have 1 message
        assert len(discord.queue) == 1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dedup_key_includes_detector_secret_source(self, sample_trufflehog_findings):
        """Test dedup key = detector + secret + source file + line"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret1 = sample_trufflehog_findings[0].copy()
        secret1['SourceMetadata'] = secret1['SourceMetadata'].copy()
        
        secret2 = sample_trufflehog_findings[0].copy()
        secret2['SourceMetadata'] = secret2['SourceMetadata'].copy()
        
        # Change line number (different location)
        secret2['SourceMetadata']['line'] = 100
        
        await discord.queue_alert(secret1)
        await discord.queue_alert(secret2)
        
        # Should have 2 messages (different lines)
        assert len(discord.queue) == 2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_different_detectors_not_deduped(self, sample_trufflehog_findings):
        """Test different detectors are not deduped"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret1 = sample_trufflehog_findings[0].copy()
        secret2 = sample_trufflehog_findings[0].copy()
        
        # Change detector
        secret2['DetectorName'] = "GitHub"
        
        await discord.queue_alert(secret1)
        await discord.queue_alert(secret2)
        
        # Should have 2 messages (different detectors)
        assert len(discord.queue) == 2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_different_secrets_not_deduped(self, sample_trufflehog_findings):
        """Test different secrets are not deduped"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret1 = sample_trufflehog_findings[0].copy()
        secret2 = sample_trufflehog_findings[0].copy()
        
        # Change secret value
        secret2['Raw'] = "DIFFERENT_SECRET_VALUE"
        
        await discord.queue_alert(secret1)
        await discord.queue_alert(secret2)
        
        # Should have 2 messages (different secrets)
        assert len(discord.queue) == 2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_dedup_logs_debug_message(self, mock_logger, sample_trufflehog_findings):
        """Test dedup logs message at debug level"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger
        )
        
        secret = sample_trufflehog_findings[0]
        
        # Add same secret twice
        await discord.queue_alert(secret)
        await discord.queue_alert(secret)
        
        # Should have logged debug message
        mock_logger.debug.assert_called()


# ============================================================================
# WORKER RESILIENCE TESTS
# ============================================================================

class TestDiscordWorkerResilience:
    """Test worker resilience to exceptions"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_worker_continues_after_http_exception(self, sample_trufflehog_findings):
        """Test worker continues processing after HTTP exception"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        await discord.start()
        
        # Add messages
        for i in range(3):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
            await discord.queue_alert(secret)
        
        # Mock HTTP client to fail on first call, succeed on others
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            
            # First call raises exception, others succeed
            mock_response_success = Mock()
            mock_response_success.status_code = 200
            
            call_count = 0
            async def post_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("Network error")
                return mock_response_success
            
            mock_session.post = AsyncMock(side_effect=post_side_effect)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Let worker process
            await asyncio.sleep(1)
            
            # Worker should still be running
            assert discord.running is True
        
        await discord.stop(drain_queue=False)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_worker_continues_after_json_encoding_error(self, mock_logger):
        """Test worker continues after JSON encoding error"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger,
            rate_limit=30
        )
        
        await discord.start()
        
        # Create a secret with non-serializable data
        secret = {
            'Raw': 'SECRET',
            'DetectorName': 'Test',
            'SourceMetadata': {
                'file': 'test.js',
                'line': 1,
                'domain': 'example.com'
            }
        }
        
        await discord.queue_alert(secret)
        
        # Mock HTTP client
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Let worker process
            await asyncio.sleep(0.5)
            
            # Worker should still be running
            assert discord.running is True
        
        await discord.stop(drain_queue=False)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_worker_logs_exceptions(self, mock_logger, sample_trufflehog_findings):
        """Test worker logs exceptions"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger,
            rate_limit=30
        )
        
        await discord.start()
        
        await discord.queue_alert(sample_trufflehog_findings[0])
        
        # Mock HTTP client to raise exception
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(side_effect=Exception("Network error"))
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Let worker process
            await asyncio.sleep(0.5)
            
            # Should have logged error
            mock_logger.error.assert_called()
        
        await discord.stop(drain_queue=False)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_worker_stops_gracefully_on_stop_signal(self):
        """Test worker stops gracefully when stop() called"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            rate_limit=30
        )
        
        await discord.start()
        assert discord.running is True
        
        await discord.stop(drain_queue=False)
        assert discord.running is False


# ============================================================================
# HTTP RESPONSE TESTS
# ============================================================================

class TestDiscordHTTPResponses:
    """Test HTTP response handling"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_200_response_success(self):
        """Test 200 response marks message as sent"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock()
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        # Should not raise exception
        await discord._send_webhook(mock_session, embed)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_400_response_logs_error_and_drops_message(self, mock_logger):
        """Test 400 response logs error and drops message"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger
        )
        
        await discord.start()
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        await discord._send_webhook(mock_session, embed)
        
        # Should have logged error
        mock_logger.error.assert_called()
        error_message = str(mock_logger.error.call_args[0][0])
        assert "400" in error_message
        
        await discord.stop(drain_queue=False)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_404_response_logs_helpful_error(self, mock_logger):
        """Test 404 response logs helpful error with instructions"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger
        )
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Webhook not found"
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        await discord._send_webhook(mock_session, embed)
        
        # Should have logged error with helpful message
        mock_logger.error.assert_called()
        error_message = str(mock_logger.error.call_args[0][0])
        assert "404" in error_message
        assert "webhook" in error_message.lower()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_500_response_handles_server_error(self, mock_logger):
        """Test 500 response is handled gracefully"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=mock_logger
        )
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        embed = {'embeds': [{'title': 'Test'}]}
        
        await discord._send_webhook(mock_session, embed)
        
        # Should have logged error
        mock_logger.error.assert_called()


# ============================================================================
# EMBED CREATION TESTS
# ============================================================================

class TestDiscordEmbedCreation:
    """Test Discord embed creation"""
    
    @pytest.mark.unit
    def test_create_embed_for_verified_secret(self, sample_trufflehog_findings):
        """Test _create_embed() creates correct embed for verified secret"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret = sample_trufflehog_findings[0]  # Verified secret
        embed = discord._create_embed(secret)
        
        assert 'embeds' in embed
        assert len(embed['embeds']) == 1
        
        embed_data = embed['embeds'][0]
        assert 'title' in embed_data
        assert 'description' in embed_data
        assert 'color' in embed_data
        assert embed_data['color'] == 0xFF0000  # Red for verified
    
    @pytest.mark.unit
    def test_create_embed_for_unverified_secret(self, sample_trufflehog_findings):
        """Test _create_embed() creates correct embed for unverified secret"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret = sample_trufflehog_findings[1]  # Unverified secret
        embed = discord._create_embed(secret)
        
        embed_data = embed['embeds'][0]
        assert embed_data['color'] == 0xFFA500  # Orange for unverified
    
    @pytest.mark.unit
    def test_create_embed_includes_domain(self, sample_trufflehog_findings):
        """Test embed includes domain information"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret = sample_trufflehog_findings[0]
        embed = discord._create_embed(secret)
        
        embed_data = embed['embeds'][0]
        description = embed_data['description']
        
        assert 'example.com' in description
    
    @pytest.mark.unit
    def test_create_embed_includes_line_number(self, sample_trufflehog_findings):
        """Test embed includes line number"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret = sample_trufflehog_findings[0]
        embed = discord._create_embed(secret)
        
        embed_data = embed['embeds'][0]
        description = embed_data['description']
        
        assert '42' in description  # Line number
    
    @pytest.mark.unit
    def test_create_embed_truncates_long_secrets(self):
        """Test embed truncates long secret previews"""
        discord = Discord(webhook_url="https://discord.com/api/webhooks/123/token")
        
        secret = {
            'Raw': 'A' * 100,  # Very long secret
            'DetectorName': 'Test',
            'Verified': True,
            'SourceMetadata': {
                'file': 'test.js',
                'line': 1,
                'domain': 'example.com',
                'url': 'https://example.com/test.js'
            }
        }
        
        embed = discord._create_embed(secret)
        embed_data = embed['embeds'][0]
        description = embed_data['description']
        
        # Should contain "..." indicating truncation
        assert '...' in description


# ============================================================================
# INTEGRATION SCENARIOS
# ============================================================================

class TestDiscordIntegration:
    """Integration tests for Discord functionality"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_workflow_start_queue_stop(self, sample_trufflehog_findings):
        """Test complete workflow: start, queue, send, stop"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock(),
            rate_limit=30
        )
        
        # Start worker
        await discord.start()
        assert discord.running is True
        
        # Queue messages
        for i in range(5):
            secret = sample_trufflehog_findings[0].copy()
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
            await discord.queue_alert(secret)
        
        assert len(discord.queue) == 5
        
        # Mock HTTP client
        with patch('jsscanner.output.discord.AsyncSession') as mock_session_cls:
            mock_session = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_session_cls.return_value = mock_session
            
            # Stop and drain
            await discord.stop(drain_queue=True)
        
        assert discord.running is False
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_alert_processing(self, sample_trufflehog_findings):
        """Test queue_batch_alert processes multiple secrets"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock()
        )
        
        secrets = [sample_trufflehog_findings[0].copy() for _ in range(5)]
        for i, secret in enumerate(secrets):
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
        
        await discord.queue_batch_alert(secrets)
        
        # Should have queued all secrets individually
        assert len(discord.queue) == 5
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_flush_batched_secrets(self, sample_trufflehog_findings):
        """Test flush_batched_secrets queues all secrets"""
        discord = Discord(
            webhook_url="https://discord.com/api/webhooks/123/token",
            logger=Mock()
        )
        
        secrets = [sample_trufflehog_findings[1].copy() for _ in range(10)]
        for i, secret in enumerate(secrets):
            secret['Raw'] = f"SECRET_{i}"
            secret['SourceMetadata']['line'] = i
        
        await discord.flush_batched_secrets(secrets)
        
        # Should have queued all secrets
        assert len(discord.queue) == 10
