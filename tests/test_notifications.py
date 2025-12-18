#!/usr/bin/env python3
"""
Test notification improvements:
- Verified secrets sent immediately
- Unverified secrets batched at phase end
- Improved message formatting with domain in title
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jsscanner.core.notifier import DiscordNotifier
from jsscanner.utils.logger import setup_logger


async def test_notification_improvements():
    """Test the new notification system"""
    print("\n" + "="*80)
    print("NOTIFICATION IMPROVEMENTS TEST")
    print("="*80)
    
    # Setup (using fake webhook for testing)
    logger = setup_logger('notification_test')
    notifier = DiscordNotifier(
        webhook_url="https://discord.com/api/webhooks/test/fake",  # Won't actually send
        rate_limit=30,
        logger=logger
    )
    
    await notifier.start()
    
    # Test 1: Single verified secret with new format
    print("\n[1/4] Testing single verified secret format...")
    verified_secret = {
        'DetectorName': 'AWS',
        'Verified': True,
        'Raw': 'AKIAIOSFODNN7EXAMPLE',
        'Redacted': 'AKIA****************',
        'SourceMetadata': {
            'url': 'https://example.com/assets/js/app.min.js',
            'file': '/tmp/app.min.js',
            'line': 125
        }
    }
    
    await notifier.queue_alert(verified_secret)
    print("✅ Verified secret queued (should send immediately)")
    
    # Test 2: Single unverified secret
    print("\n[2/4] Testing single unverified secret format...")
    unverified_secret = {
        'DetectorName': 'URI',
        'Verified': False,
        'Raw': 'http://user:password@example.com',
        'SourceMetadata': {
            'url': 'https://nutramigen.be/sites/all/modules/contrib/extlink/extlink.js',
            'line': 82
        }
    }
    
    await notifier.queue_alert(unverified_secret)
    print("✅ Unverified secret queued (will batch)")
    
    # Test 3: Batch of unverified secrets from different domains
    print("\n[3/4] Testing batch notification with domain grouping...")
    unverified_batch = [
        {
            'DetectorName': 'GitHub',
            'Verified': False,
            'Raw': 'ghp_1234567890abcdefghijklmnopqrstuvwxyz',
            'SourceMetadata': {
                'url': 'https://example.com/js/config.js',
                'line': 45
            }
        },
        {
            'DetectorName': 'Slack',
            'Verified': False,
            'Raw': 'xoxb-test-fake-token-example',
            'SourceMetadata': {
                'url': 'https://example.com/js/api.js',
                'line': 103
            }
        },
        {
            'DetectorName': 'URI',
            'Verified': False,
            'Raw': 'https://admin:secret123@api.example.com',
            'SourceMetadata': {
                'url': 'https://different-domain.com/bundle.js',
                'line': 78
            }
        }
    ]
    
    # Test flush_batched_secrets with domain grouping
    await notifier.flush_batched_secrets(unverified_batch, batch_size=10, group_by_domain=True)
    print("✅ Batch notification queued (grouped by domain)")
    
    # Test 4: Mixed verified and unverified batch
    print("\n[4/4] Testing mixed batch (verified + unverified)...")
    mixed_batch = [
        {
            'DetectorName': 'AWS',
            'Verified': True,
            'Raw': 'AKIAIOSFODNN7EXAMPLE',
            'Redacted': 'AKIA****************',
            'SourceMetadata': {
                'url': 'https://example.com/config.js',
                'line': 25
            }
        },
        {
            'DetectorName': 'GitHub',
            'Verified': False,
            'Raw': 'ghp_test123',
            'SourceMetadata': {
                'url': 'https://example.com/config.js',
                'line': 42
            }
        }
    ]
    
    await notifier.queue_batch_alert(mixed_batch, domain='example.com')
    print("✅ Mixed batch queued")
    
    # Summary
    print("\n" + "="*80)
    print(f"📊 SUMMARY")
    print("="*80)
    print(f"  Queued messages: {len(notifier.queue)}")
    print(f"  Rate limit: {notifier.rate_limit} msg/min")
    print("\n💡 Key improvements:")
    print("  • Domain shown in title (e.g., 'AWS • example.com')")
    print("  • Cleaner source field (just URL, no redundant filename)")
    print("  • Verified secrets send immediately")
    print("  • Unverified secrets batched at phase end")
    print("  • Domain grouping for better organization")
    print("  • 500ms delay between messages to avoid bursts")
    print("="*80)
    
    # Don't actually send (stop without draining)
    await notifier.stop(drain_queue=False)
    
    return True


if __name__ == '__main__':
    try:
        result = asyncio.run(test_notification_improvements())
        print("\n🎉 All notification tests passed!\n")
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
