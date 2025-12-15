"""
Discord Notifier
Rate-limited Discord webhook alerting system
"""
import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional
from collections import deque
from datetime import datetime


class DiscordNotifier:
    """Handles Discord webhook notifications with rate limiting"""
    
    def __init__(self, webhook_url: str, rate_limit: int = 30):
        """
        Initialize Discord notifier
        
        Args:
            webhook_url: Discord webhook URL
            rate_limit: Maximum messages per minute (default: 30)
        """
        self.webhook_url = webhook_url
        self.rate_limit = rate_limit
        self.queue = deque()
        self.message_times = deque()
        self.running = False
        self._task = None
    
    async def start(self):
        """Starts the notification worker"""
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._worker())
    
    async def stop(self):
        """Stops the notification worker"""
        self.running = False
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
            async with session.post(self.webhook_url, json=embed) as response:
                if response.status == 429:
                    # Rate limited by Discord
                    retry_after = int(response.headers.get('Retry-After', 5))
                    await asyncio.sleep(retry_after)
                    # Re-queue the message
                    self.queue.appendleft(embed)
                elif response.status not in [200, 204]:
                    print(f"Discord webhook error: {response.status}")
        except Exception as e:
            print(f"Failed to send Discord notification: {e}")
    
    def _create_embed(self, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a Discord embed from secret data
        
        Args:
            secret_data: Dictionary containing secret information
            
        Returns:
            Discord webhook payload
        """
        # Determine color based on verification status
        verified = secret_data.get('Verified', secret_data.get('verified', False))
        color = 0xFF0000 if verified else 0xFFA500  # Red for verified, Orange for unverified
        
        # Get detector name
        detector_name = secret_data.get('DetectorName', secret_data.get('type', 'Unknown'))
        
        # Build description
        description_parts = []
        
        if detector_name:
            description_parts.append(f"**Detector:** {detector_name}")
        
        if 'DecoderName' in secret_data:
            description_parts.append(f"**Decoder:** {secret_data['DecoderName']}")
        
        # Get secret preview
        raw_secret = secret_data.get('Raw', secret_data.get('secret', ''))
        if raw_secret:
            # Truncate if too long
            if len(raw_secret) > 100:
                raw_secret = raw_secret[:100] + "..."
            description_parts.append(f"**Secret Preview:**\n```{raw_secret}```")
        
        description = '\n'.join(description_parts)
        
        # Build fields
        fields = []
        
        # Source metadata
        source_metadata = secret_data.get('SourceMetadata', {})
        
        if source_metadata:
            file_path = source_metadata.get('file', '')
            if file_path:
                # Show just filename if path is long
                from pathlib import Path
                filename = Path(file_path).name
                fields.append({
                    'name': '📁 File',
                    'value': f"`{filename}`",
                    'inline': False
                })
            
            url = source_metadata.get('url', '')
            if url:
                # Truncate long URLs
                display_url = url if len(url) < 100 else url[:97] + "..."
                fields.append({
                    'name': '🔗 URL',
                    'value': display_url,
                    'inline': False
                })
            
            line_num = source_metadata.get('line', 0)
            if line_num:
                fields.append({
                    'name': '📍 Line',
                    'value': str(line_num),
                    'inline': True
                })
        
        # Verification status
        fields.append({
            'name': '✅ Verified',
            'value': 'YES' if verified else 'NO',
            'inline': True
        })
        
        # Timestamp
        timestamp = secret_data.get('timestamp', datetime.utcnow().isoformat())
        
        embed = {
            'embeds': [{
                'title': f'🚨 Secret Found: {detector_name}',
                'description': description,
                'color': color,
                'fields': fields,
                'footer': {
                    'text': 'JS Scanner | Bug Bounty Edition'
                },
                'timestamp': timestamp if isinstance(timestamp, str) else datetime.utcnow().isoformat()
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
