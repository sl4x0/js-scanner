#!/usr/bin/env python3
"""
Discord Webhook Validator
Tests Discord webhook functionality without spamming production channels
"""
import asyncio
import aiohttp
import json
from datetime import datetime


class WebhookValidator:
    """Validates Discord webhook functionality"""
    
    def __init__(self, webhook_url: str):
        """
        Initialize validator
        
        Args:
            webhook_url: Discord webhook URL to test
        """
        self.webhook_url = webhook_url
        self.test_results = []
    
    async def send_test_message(self, content: str, embed: dict = None) -> bool:
        """
        Send a test message to Discord
        
        Args:
            content: Message content
            embed: Optional embed object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {'content': content}
                if embed:
                    payload['embeds'] = [embed]
                
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 204:
                        return True
                    else:
                        print(f"❌ Failed: Status {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_basic_message(self) -> bool:
        """Test basic text message"""
        print("\n📝 Test 1: Basic Message")
        content = "🧪 **Test Message** - Discord webhook validation"
        result = await self.send_test_message(content)
        self.test_results.append(('Basic Message', result))
        print("✅ Passed" if result else "❌ Failed")
        return result
    
    async def test_embed_message(self) -> bool:
        """Test embed message"""
        print("\n📝 Test 2: Embed Message")
        embed = {
            'title': '🔐 Test Secret Detection',
            'description': 'This is a test secret notification',
            'color': 0xff0000,
            'fields': [
                {'name': 'Detector', 'value': 'Test-Detector', 'inline': True},
                {'name': 'File', 'value': 'test.js', 'inline': True},
                {'name': 'Line', 'value': '42', 'inline': True}
            ],
            'footer': {'text': 'Test notification'},
            'timestamp': datetime.utcnow().isoformat()
        }
        result = await self.send_test_message('', embed)
        self.test_results.append(('Embed Message', result))
        print("✅ Passed" if result else "❌ Failed")
        return result
    
    async def test_multiple_secrets(self) -> bool:
        """Test batch notification (multiple secrets)"""
        print("\n📝 Test 3: Batch Notification (3 secrets)")
        
        embeds = []
        for i in range(3):
            embed = {
                'title': f'🔐 Secret {i+1}/3',
                'description': f'Test secret #{i+1}',
                'color': 0xff0000,
                'fields': [
                    {'name': 'Detector', 'value': f'Test-Detector-{i+1}', 'inline': True},
                    {'name': 'File', 'value': 'test_multiple.js', 'inline': True},
                    {'name': 'Line', 'value': str((i+1) * 10), 'inline': True}
                ]
            }
            embeds.append(embed)
        
        # Discord supports up to 10 embeds per message
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json={'embeds': embeds},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = response.status == 204
                    self.test_results.append(('Batch Notification', result))
                    print("✅ Passed" if result else "❌ Failed")
                    return result
        except Exception as e:
            print(f"❌ Failed: {e}")
            self.test_results.append(('Batch Notification', False))
            return False
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting behavior"""
        print("\n📝 Test 4: Rate Limiting (5 messages)")
        
        success_count = 0
        for i in range(5):
            content = f"🧪 Rate limit test {i+1}/5"
            if await self.send_test_message(content):
                success_count += 1
            await asyncio.sleep(0.5)  # Small delay between messages
        
        result = success_count == 5
        self.test_results.append(('Rate Limiting', result))
        print(f"✅ Passed ({success_count}/5)" if result else f"⚠️  Partial ({success_count}/5)")
        return result
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "="*60)
        print("🧪 Discord Webhook Validation Tests")
        print("="*60)
        
        await self.test_basic_message()
        await asyncio.sleep(1)
        
        await self.test_embed_message()
        await asyncio.sleep(1)
        
        await self.test_multiple_secrets()
        await asyncio.sleep(1)
        
        await self.test_rate_limiting()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nResult: {passed}/{total} tests passed")
        print("="*60 + "\n")
        
        return passed == total


async def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python webhook_validator.py <discord_webhook_url>")
        print("\nExample:")
        print("  python webhook_validator.py https://discord.com/api/webhooks/...")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    
    validator = WebhookValidator(webhook_url)
    success = await validator.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
