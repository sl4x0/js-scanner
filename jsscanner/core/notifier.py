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
        
        # Wait for queue to drain with dynamic timeout (2 seconds per message + 60 second buffer)
        if drain_queue and self.queue:
            if self.logger:
                self.logger.info(f"📤 Sending {len(self.queue)} queued Discord messages...")
            # Dynamic timeout: 2 seconds per message + 60 second buffer
            timeout_duration = (len(self.queue) * 2) + 60
            deadline = time.time() + timeout_duration
            
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
                self.logger.error(f"❌ Discord notification error: {type(e).__name__}: {str(e)}")
            else:
                print(f"Failed to send Discord notification: {e}")
    
    def _create_embed(self, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a clean, minimal Discord embed for secret findings
        
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
        
        # Get the actual secret
        raw_secret = secret_data.get('Raw', secret_data.get('RawV2', secret_data.get('secret', '')))
        redacted = secret_data.get('Redacted', '')
        
        # Use redacted version if available, otherwise show raw (truncated if needed)
        display_secret = redacted if redacted else raw_secret
        if len(display_secret) > 150:
            display_secret = display_secret[:150] + "..."
        
        # Build minimal description with secret
        description = f"```\n{display_secret}\n```"
        
        # Build minimal fields
        fields = []
        
        # Source metadata
        source_metadata = secret_data.get('SourceMetadata', {})
        
        if source_metadata:
            # Combined File + URL in one field
            file_path = source_metadata.get('file', '')
            url = source_metadata.get('url', '')
            
            if file_path and url:
                from pathlib import Path
                filename = Path(file_path).name
                # Truncate URL for display
                display_url = url if len(url) <= 80 else url[:77] + "..."
                fields.append({
                    'name': '📄 Source',
                    'value': f"`{filename}`\n{url}",
                    'inline': False
                })
            
            # Line number and detector on same row
            line_num = source_metadata.get('line', 0)
            if line_num:
                fields.append({
                    'name': 'Line',
                    'value': f"`{line_num}`",
                    'inline': True
                })
        
        fields.append({
            'name': 'Type',
            'value': f"`{detector_name}`",
            'inline': True
        })
        
        # Verification status
        status_text = "✅ Verified" if verified else "⚠️ Unverified"
        fields.append({
            'name': 'Status',
            'value': status_text,
            'inline': True
        })
        
        # Create embed
        title = f"{'🔴' if verified else '🟠'} {detector_name} Secret"
        embed = {
            'embeds': [{
                'title': title,
                'description': description,
                'color': color,
                'fields': fields,
                'footer': {
                    'text': 'JS-Scanner v3.1'
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
