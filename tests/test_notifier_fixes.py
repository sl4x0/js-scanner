"""
Unit tests for Discord notifier fixes
Tests for Issue #1: Individual secret notifications instead of batching
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from jsscanner.core.notifier import DiscordNotifier


class TestQueueBatchAlert:
    """Test that queue_batch_alert sends individual alerts instead of batching"""
    
    @pytest.mark.asyncio
    async def test_queue_batch_alert_sends_individual_messages(self):
        """Verify that queue_batch_alert sends one message per secret"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        
        # Create 3 mock secrets
        secrets = [
            {
                'DetectorName': 'APIKey',
                'Verified': False,
                'SourceMetadata': {
                    'url': 'https://example.com/app.js',
                    'line': 42
                },
                'Raw': 'sk_live_abc123',
                'Entropy': 4.5
            },
            {
                'DetectorName': 'SlackWebhook',
                'Verified': False,
                'SourceMetadata': {
                    'url': 'https://example.com/config.js',
                    'line': 100
                },
                'Raw': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX',
                'Entropy': 5.2
            },
            {
                'DetectorName': 'DatadogToken',
                'Verified': True,
                'SourceMetadata': {
                    'url': 'https://example.com/api.js',
                    'line': 15
                },
                'Raw': 'dd_verification_token_xyz',
                'Entropy': 4.8
            }
        ]
        
        # Mock the queue_alert method to track calls
        notifier.queue_alert = AsyncMock()
        
        # Call queue_batch_alert
        await notifier.queue_batch_alert(secrets)
        
        # Verify queue_alert was called once for each secret
        assert notifier.queue_alert.call_count == 3
        
        # Verify each call was with the correct secret
        for i, call in enumerate(notifier.queue_alert.call_args_list):
            assert call[0][0] == secrets[i]
    
    @pytest.mark.asyncio
    async def test_queue_batch_alert_empty_list(self):
        """Verify that queue_batch_alert handles empty list gracefully"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        notifier.queue_alert = AsyncMock()
        
        # Should not raise and should not call queue_alert
        await notifier.queue_batch_alert([])
        notifier.queue_alert.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_queue_batch_alert_single_secret(self):
        """Verify that queue_batch_alert handles single secret correctly"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        notifier.queue_alert = AsyncMock()
        
        secret = {
            'DetectorName': 'APIKey',
            'Verified': False,
            'SourceMetadata': {'url': 'https://example.com/app.js', 'line': 42},
            'Raw': 'sk_live_abc123'
        }
        
        await notifier.queue_batch_alert([secret])
        
        # Should still send as individual alert
        notifier.queue_alert.assert_called_once_with(secret)


class TestCreateEmbedEnhancements:
    """Test that _create_embed includes all necessary details for manual review"""
    
    def test_create_embed_includes_domain(self):
        """Verify that embed includes domain information"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        
        secret = {
            'DetectorName': 'APIKey',
            'Verified': False,
            'SourceMetadata': {
                'url': 'https://example.com/app.js',
                'line': 42
            },
            'Raw': 'sk_live_abc123',
            'Entropy': 4.5
        }
        
        embed = notifier._create_embed(secret)
        
        # Verify embed structure
        assert 'embeds' in embed
        assert len(embed['embeds']) > 0
        
        embed_data = embed['embeds'][0]
        
        # Verify title includes domain
        assert 'example.com' in embed_data['title']
        assert 'APIKey' in embed_data['title']
        
        # Verify fields include domain
        field_names = [f['name'] for f in embed_data['fields']]
        assert '🎯 Domain' in field_names
    
    def test_create_embed_includes_source_file_with_line(self):
        """Verify that embed includes source file with line number"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        
        secret = {
            'DetectorName': 'SlackWebhook',
            'Verified': False,
            'SourceMetadata': {
                'url': 'https://example.com/config.js',
                'line': 100
            },
            'Raw': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX'
        }
        
        embed = notifier._create_embed(secret)
        embed_data = embed['embeds'][0]
        
        # Find source file field
        source_field = next((f for f in embed_data['fields'] if f['name'] == '📄 Source File'), None)
        assert source_field is not None
        assert 'config.js:100' in source_field['value']
    
    def test_create_embed_includes_entropy(self):
        """Verify that embed includes entropy level"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        
        secret = {
            'DetectorName': 'DatadogToken',
            'Verified': True,
            'SourceMetadata': {
                'url': 'https://example.com/api.js',
                'line': 15
            },
            'Raw': 'dd_verification_token_xyz',
            'Entropy': 4.8
        }
        
        embed = notifier._create_embed(secret)
        embed_data = embed['embeds'][0]
        
        # Find entropy field
        entropy_field = next((f for f in embed_data['fields'] if f['name'] == '📊 Entropy'), None)
        assert entropy_field is not None
        assert '4.8' in entropy_field['value']
    
    def test_create_embed_includes_key_preview(self):
        """Verify that embed includes key preview"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        
        secret = {
            'DetectorName': 'APIKey',
            'Verified': False,
            'SourceMetadata': {
                'url': 'https://example.com/app.js',
                'line': 42
            },
            'Raw': 'sk_live_this_is_a_very_long_api_key_that_should_be_truncated'
        }
        
        embed = notifier._create_embed(secret)
        embed_data = embed['embeds'][0]
        
        # Find key preview field
        key_field = next((f for f in embed_data['fields'] if f['name'] == '🔑 Key Preview'), None)
        assert key_field is not None
        # Key preview is wrapped in backticks, verify it contains the key start
        assert 'sk_live_this_is_a_very_long_ap' in key_field['value']
    
    def test_create_embed_verification_status(self):
        """Verify that embed clearly shows verification status"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        
        # Test verified
        verified_secret = {
            'DetectorName': 'APIKey',
            'Verified': True,
            'SourceMetadata': {
                'url': 'https://example.com/app.js',
                'line': 42
            },
            'Raw': 'sk_live_abc123'
        }
        
        embed = notifier._create_embed(verified_secret)
        embed_data = embed['embeds'][0]
        
        # Should have red color for verified
        assert embed_data['color'] == 0xFF0000
        
        # Find status field
        status_field = next((f for f in embed_data['fields'] if f['name'] == '✓ Status'), None)
        assert status_field is not None
        assert '✅' in status_field['value']
        assert 'Verified' in status_field['value']


class TestFlushBatchedSecrets:
    """Test that flush_batched_secrets sends individual alerts"""
    
    @pytest.mark.asyncio
    async def test_flush_batched_secrets_sends_individual_alerts(self):
        """Verify that flush_batched_secrets sends one message per secret"""
        notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/test/test", logger=None)
        notifier.queue_alert = AsyncMock()
        
        secrets = [
            {
                'DetectorName': 'APIKey',
                'Verified': False,
                'SourceMetadata': {'url': 'https://example.com/app.js'},
                'Raw': 'sk_live_abc123'
            },
            {
                'DetectorName': 'SlackWebhook',
                'Verified': False,
                'SourceMetadata': {'url': 'https://example.com/config.js'},
                'Raw': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX'
            }
        ]
        
        await notifier.flush_batched_secrets(secrets)
        
        # Should call queue_alert for each secret
        assert notifier.queue_alert.call_count == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
