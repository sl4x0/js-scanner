"""
Discord Notifier
Rate-limited Discord webhook alerting system

Optimizations:
- Batch notifications: Groups multiple secrets from same file into single message
- Rate limiting: Prevents hitting Discord's API limits (30 msgs/min default)
- Queuing system: Ensures no alerts are lost during high-volume scans
"""
import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional
from collections import deque
from datetime import datetime


class DiscordNotifier:
    """Handles Discord webhook notifications with rate limiting"""
    
    def __init__(self, webhook_url: str, rate_limit: int = 30, logger=None):
        """
        Initialize Discord notifier
        
        Args:
            webhook_url: Discord webhook URL
            rate_limit: Maximum messages per minute (default: 30)
            logger: Logger instance for error reporting
        """
        self.webhook_url = webhook_url
        self.rate_limit = rate_limit
        self.queue = deque()
        self.message_times = deque()
        self.running = False
        self._task = None
        self.logger = logger
    
    async def start(self):
        """Starts the notification worker"""
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._worker())
    
    async def stop(self, drain_queue: bool = True):
        """
        Stops the notification worker
        
        Args:
            drain_queue: If True, wait for queued messages to send
        """
        self.running = False
        
        # Wait for queue to drain (max 60 seconds)
        if drain_queue and self.queue:
            if self.logger:
                self.logger.info(f"📤 Sending {len(self.queue)} queued Discord messages...")
            deadline = time.time() + 60
            
            while self.queue and time.time() < deadline:
                await asyncio.sleep(0.5)
            
            if self.queue and self.logger:
                self.logger.warning(f"⚠️  {len(self.queue)} messages not sent (timeout)")
        
        if self._task:
            await self._task
    
    async def queue_alert(self, secret_data: Dict[str, Any]):
        """
        Queues a secret alert for sending
        
        Args:
            secret_data: Dictionary containing secret information
        """
        embed = self._create_embed(secret_data)
        self.queue.append(embed)
    
    async def queue_batch_alert(self, secrets: list, file_path: str):
        """
        Queue multiple secrets from same file as single notification
        This reduces Discord spam and improves notification efficiency
        
        Args:
            secrets: List of secret data dictionaries
            file_path: Path to the file containing the secrets
        """
        from pathlib import Path
        
        # If only one secret, use regular alert
        if len(secrets) == 1:
            await self.queue_alert(secrets[0])
            return
        
        # Determine if any are verified
        has_verified = any(s.get('Verified', s.get('verified', False)) for s in secrets)
        color = 0xFF0000 if has_verified else 0xFFA500  # Red if any verified, orange otherwise
        
        # Create batch embed
        filename = Path(file_path).name
        
        # Build fields (max 25 fields per Discord embed, limit to 10 for readability)
        fields = []
        for i, secret in enumerate(secrets[:10], 1):
            detector_name = secret.get('DetectorName', secret.get('type', 'Unknown'))
            verified = secret.get('Verified', secret.get('verified', False))
            
            fields.append({
                'name': f'Secret #{i}: {detector_name}',
                'value': f'Verified: {"✅ YES" if verified else "❌ NO"}',
                'inline': True
            })
        
        # Add overflow message if more than 10
        if len(secrets) > 10:
            fields.append({
                'name': '⚠️ More Secrets',
                'value': f'+ {len(secrets) - 10} additional secrets (check logs)',
                'inline': False
            })
        
        embed = {
            'embeds': [{
                'title': f'🚨 {len(secrets)} Secrets Found in {filename}',
                'description': f'Multiple secrets detected in the same file',
                'color': color,
                'fields': fields,
                'footer': {
                    'text': f'File: {file_path}'
                },
                'timestamp': datetime.utcnow().isoformat()
            }]
        }
        
        self.queue.append(embed)
    
    async def _worker(self):
        """Background worker that sends queued messages"""
        async with aiohttp.ClientSession() as session:
            while self.running or self.queue:
                if not self.queue:
                    await asyncio.sleep(1)
                    continue
                
                # Check rate limit
                if await self._can_send():
                    embed = self.queue.popleft()
                    await self._send_webhook(session, embed)
                    self.message_times.append(time.time())
                else:
                    # Wait a bit before checking again
                    await asyncio.sleep(2)
    
    async def _can_send(self) -> bool:
        """
        Checks if we can send a message without exceeding rate limit
        
        Returns:
            True if we can send, False otherwise
        """
        current_time = time.time()
        
        # Remove timestamps older than 60 seconds
        while self.message_times and current_time - self.message_times[0] > 60:
            self.message_times.popleft()
        
        # Check if we're under the rate limit
        return len(self.message_times) < self.rate_limit
    
    async def _send_webhook(self, session: aiohttp.ClientSession, embed: Dict[str, Any]):
        """
        Sends a webhook message
        
        Args:
            session: aiohttp session
            embed: Embed data to send
        """
        try:
            # Issue #4: Add timeout to prevent hanging if Discord is down
            timeout = aiohttp.ClientTimeout(total=10)
            async with session.post(self.webhook_url, json=embed, timeout=timeout) as response:
                if response.status == 429:
                    # Rate limited by Discord
                    retry_after = int(response.headers.get('Retry-After', 5))
                    await asyncio.sleep(retry_after)
                    # Re-queue the message
                    self.queue.appendleft(embed)
                elif response.status not in [200, 204]:
                    error_text = await response.text()
                    if self.logger:
                        self.logger.error(
                            f"❌ Discord webhook failed!\n"
                            f"   Status: {response.status}\n"
                            f"   Error: {error_text[:200]}\n"
                            f"   Check your webhook URL in config.yaml"
                        )
                    else:
                        print(f"Discord webhook error: {response.status}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Discord notification error: {e}")
            else:
                print(f"Failed to send Discord notification: {e}")
    
    def _create_embed(self, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an enhanced Discord embed with all data needed for manual verification
        
        Args:
            secret_data: Dictionary containing secret information
            
        Returns:
            Discord webhook payload
        """
        # Determine verification status and color
        verified = secret_data.get('Verified', secret_data.get('verified', False))
        color = 0xFF0000 if verified else 0xFFA500  # Red = verified, Orange = unverified
        
        # Get detector info
        detector_name = secret_data.get('DetectorName', secret_data.get('type', 'Unknown'))
        detector_desc = secret_data.get('DetectorDescription', '')
        
        # Build rich description
        description_parts = []
        
        # Status badge
        status_badge = "🔴 VERIFIED CREDENTIAL" if verified else "🟠 POTENTIAL FINDING"
        description_parts.append(f"**{status_badge}**\n")
        
        # Detector info
        if detector_desc:
            description_parts.append(f"_{detector_desc}_\n")
        
        # Get the actual secret
        raw_secret = secret_data.get('Raw', secret_data.get('RawV2', secret_data.get('secret', '')))
        redacted = secret_data.get('Redacted', '')
        
        if raw_secret:
            # Show redacted version if available, otherwise truncate
            display_secret = redacted if redacted else raw_secret
            if len(display_secret) > 200:
                display_secret = display_secret[:200] + "..."
            description_parts.append(f"**Secret:**\n```\n{display_secret}\n```")
        
        # Verification error if present
        verification_error = secret_data.get('VerificationError', '')
        if verification_error and not verified:
            description_parts.append(f"⚠️ **Verification Failed:** {verification_error}")
        
        description = '\n'.join(description_parts)
        
        # Build comprehensive fields
        fields = []
        
        # Source metadata
        source_metadata = secret_data.get('SourceMetadata', {})
        
        if source_metadata:
            # File information
            file_path = source_metadata.get('file', '')
            if file_path:
                from pathlib import Path
                filename = Path(file_path).name
                fields.append({
                    'name': '📁 File',
                    'value': f"`{filename}`",
                    'inline': False
                })
            
            # Original URL
            url = source_metadata.get('url', '')
            if url:
                # Make URL clickable and truncate if needed
                display_url = url if len(url) <= 100 else url[:97] + "..."
                fields.append({
                    'name': '🔗 Source URL',
                    'value': f"[{display_url}]({url})",
                    'inline': False
                })
            
            # Line number
            line_num = source_metadata.get('line', 0)
            if line_num:
                fields.append({
                    'name': '📍 Line Number',
                    'value': f"`{line_num}`",
                    'inline': True
                })
        
        # Detection metadata
        fields.append({
            'name': '🔍 Detector',
            'value': f"`{detector_name}`",
            'inline': True
        })
        
        decoder_name = secret_data.get('DecoderName', '')
        if decoder_name:
            fields.append({
                'name': '🔓 Decoder',
                'value': f"`{decoder_name}`",
                'inline': True
            })
        
        # Verification status with icon
        verification_icon = "✅" if verified else "❌"
        verification_text = "**VERIFIED**" if verified else "Not Verified"
        fields.append({
            'name': f'{verification_icon} Status',
            'value': verification_text,
            'inline': True
        })
        
        # Add verification from cache indicator
        if secret_data.get('VerificationFromCache', False):
            fields.append({
                'name': '💾 Cache',
                'value': 'Verified from cache',
                'inline': True
            })
        
        # Action items for manual verification
        action_items = []
        if not verified:
            action_items.append("1️⃣ Check if secret is still active")
            action_items.append("2️⃣ Test credential validity")
            action_items.append("3️⃣ Verify scope and permissions")
            
            fields.append({
                'name': '📋 Manual Verification Steps',
                'value': '\n'.join(action_items),
                'inline': False
            })
        
        # Create embed
        title_icon = "🔴" if verified else "🟠"
        embed = {
            'embeds': [{
                'title': f'{title_icon} Secret Detected: {detector_name}',
                'description': description,
                'color': color,
                'fields': fields,
                'footer': {
                    'text': f'JS-Scanner v3.0 | {"IMMEDIATE ACTION REQUIRED" if verified else "Review Recommended"}'
                },
                'timestamp': datetime.utcnow().isoformat()
            }]
        }
        
        return embed
    
    async def send_status(self, message: str, status_type: str = 'info'):
        """
        Sends a status message
        
        Args:
            message: Status message
            status_type: Type of status ('info', 'success', 'error')
        """
        colors = {
            'info': 0x3498DB,
            'success': 0x2ECC71,
            'error': 0xE74C3C
        }
        
        embed = {
            'embeds': [{
                'description': message,
                'color': colors.get(status_type, 0x3498DB),
                'timestamp': datetime.utcnow().isoformat()
            }]
        }
        
        self.queue.append(embed)
