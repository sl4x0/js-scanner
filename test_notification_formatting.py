"""
Quick test for notification formatting fixes
Tests:
1. No duplicate secrets sent
2. Proper embed format with JS file info
3. Clean secret preview without duplication
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jsscanner.core.notifier import DiscordNotifier
from jsscanner.utils.logger import setup_logger


async def test_notification_formatting():
    """Test the notification formatting fixes"""
    
    # Setup logger
    logger = setup_logger("test", "DEBUG")
    
    # Create notifier (with fake webhook URL for testing)
    notifier = DiscordNotifier(
        webhook_url="https://discord.com/api/webhooks/test/test",
        rate_limit=30,
        logger=logger
    )
    
    print("=" * 80)
    print("🧪 Testing Notification Formatting Fixes")
    print("=" * 80)
    
    # Test Case 1: Check embed format
    print("\n📝 Test 1: Embed Format (JS file info, no duplication)")
    print("-" * 80)
    
    secret_data = {
        'DetectorName': 'AlgoliaAdminKey',
        'Raw': 'b02ee67bc8481fb1a916b88d47ed6e1a',
        'RawV2': 'EXMN7D0HQ1:b02ee67bc8481fb1a916b88d47ed6e1a',
        'Redacted': '',
        'Verified': False,
        'Entropy': 4.23,
        'SourceMetadata': {
            'url': 'https://example.com/static/bundle.js',
            'file': 'bundle.js',
            'line': 1234
        }
    }
    
    embed = notifier._create_embed(secret_data)
    
    # Check embed structure
    assert 'embeds' in embed, "❌ Missing 'embeds' key"
    assert len(embed['embeds']) == 1, "❌ Should have exactly 1 embed"
    
    embed_data = embed['embeds'][0]
    
    # Check title format
    print(f"✓ Title: {embed_data['title']}")
    assert 'AlgoliaAdminKey' in embed_data['title'], "❌ Missing detector name in title"
    assert 'example.com' in embed_data['title'], "❌ Missing domain in title"
    
    # Check description (should have preview, not full secret twice)
    print(f"✓ Description: {embed_data['description']}")
    assert 'Secret Preview:' in embed_data['description'], "❌ Missing 'Secret Preview' label"
    assert embed_data['description'].count('b02ee67bc8481fb1a916b88d47ed6e1a') <= 1, "❌ Secret shown multiple times!"
    
    # Check fields
    field_names = [f['name'] for f in embed_data['fields']]
    print(f"✓ Fields: {field_names}")
    
    # Should have Domain field
    assert '🎯 Domain' in field_names, "❌ Missing Domain field"
    
    # Should have JS File field (NOT "Source File")
    assert '📄 JS File' in field_names, "❌ Missing 'JS File' field"
    
    # Should NOT have duplicate "Key Preview" field
    assert '🔑 Key Preview' not in field_names, "❌ Duplicate 'Key Preview' field found!"
    
    # Check JS File field content
    js_file_field = next(f for f in embed_data['fields'] if f['name'] == '📄 JS File')
    print(f"✓ JS File field: {js_file_field['value']}")
    assert 'View Source' in js_file_field['value'], "❌ Missing 'View Source' link"
    assert 'Line: 1234' in js_file_field['value'], "❌ Missing line number"
    assert 'https://example.com/static/bundle.js' in js_file_field['value'], "❌ Missing source URL"
    
    print("\n✅ Test 1 PASSED: Embed format is correct!")
    
    # Test Case 2: Deduplication
    print("\n📝 Test 2: Deduplication (no duplicate secrets)")
    print("-" * 80)
    
    await notifier.start()
    
    # Queue same secret twice
    await notifier.queue_alert(secret_data)
    await notifier.queue_alert(secret_data)  # Duplicate
    
    # Check queue size (should only have 1 message)
    queue_size = len(notifier.queue)
    print(f"✓ Queue size after 2 identical secrets: {queue_size}")
    assert queue_size == 1, f"❌ Expected 1 message, got {queue_size} (duplicates not filtered!)"
    
    print("✅ Test 2 PASSED: Duplicates are filtered!")
    
    # Test Case 3: Different secrets are NOT filtered
    print("\n📝 Test 3: Different Secrets (should NOT be deduplicated)")
    print("-" * 80)
    
    secret_data_2 = {
        'DetectorName': 'URI',
        'Raw': 'http://user:password@example.com:8080',
        'Verified': False,
        'SourceMetadata': {
            'url': 'https://example.com/static/app.js',
            'file': 'app.js',
            'line': 567
        }
    }
    
    await notifier.queue_alert(secret_data_2)
    
    queue_size = len(notifier.queue)
    print(f"✓ Queue size after adding different secret: {queue_size}")
    assert queue_size == 2, f"❌ Expected 2 messages, got {queue_size}"
    
    print("✅ Test 3 PASSED: Different secrets are queued separately!")
    
    # Cleanup
    await notifier.stop(drain_queue=False)
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED! Notification formatting is fixed:")
    print("   ✓ No duplicate secret display in embed")
    print("   ✓ JS file source with line number included")
    print("   ✓ Duplicate secrets are filtered")
    print("   ✓ Clean, readable format for Discord")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(test_notification_formatting())
