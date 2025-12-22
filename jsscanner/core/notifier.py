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
    
    def __init__(self, webhook_url: str, rate_limit: int = 30, max_queue_size: int = 1000, logger=None):
        """
        Initialize Discord notifier
        
        Args:
            webhook_url: Discord webhook URL
            rate_limit: Maximum messages per minute (default: 30)
            max_queue_size: Maximum queue size to prevent memory issues (default: 1000)
            logger: Logger instance for error reporting
        """
        self.webhook_url = webhook_url
        self.rate_limit = rate_limit
        self.max_queue_size = max_queue_size
        self.queue = deque()
        self.message_times = deque()
        self.message_retry_counts = {}  # Track retry attempts per message
        self.running = False
        self._task = None
        self.logger = logger
        self._messages_dropped = 0
    
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
        
        # Wait for queue to drain with dynamic timeout (8 seconds per message + 120 second buffer)
        if drain_queue and self.queue:
            if self.logger:
                self.logger.info(f"📤 Sending {len(self.queue)} queued Discord messages...")
            # Dynamic timeout: 8 seconds per message + 120 second buffer (accounts for rate limits + slow Discord API)
            timeout_duration = (len(self.queue) * 8) + 120
            deadline = time.time() + timeout_duration
            
            while self.queue and time.time() < deadline:
                await asyncio.sleep(0.5)
            
            if self.queue and self.logger:
                self.logger.warning(f"⚠️  {len(self.queue)} messages not sent (timeout)")
        
        if self._task:
            await self._task
    
    async def flush_queue(self, timeout: int = 60):
        """
        Flush all queued messages immediately without stopping the worker.
        Useful for sending notifications at phase boundaries.
        
        Args:
            timeout: Maximum seconds to wait for queue to drain (default: 60)
        """
        if not self.queue:
            return
        
        if self.logger:
            self.logger.info(f"📤 Flushing {len(self.queue)} queued Discord messages...")
        
        deadline = time.time() + timeout
        initial_count = len(self.queue)
        
        while self.queue and time.time() < deadline:
            await asyncio.sleep(0.5)
        
        sent_count = initial_count - len(self.queue)
        if self.logger:
            if self.queue:
                self.logger.warning(f"⚠️  Sent {sent_count}/{initial_count} messages (timeout after {timeout}s)")
            else:
                self.logger.info(f"✅ Sent all {sent_count} queued messages")
    
    async def queue_alert(self, secret_data: Dict[str, Any]):
        """
        Queues a secret alert for sending
        
        Args:
            secret_data: Dictionary containing secret information
        """
        # Check queue size limit
        if len(self.queue) >= self.max_queue_size:
            self._messages_dropped += 1
            if self._messages_dropped % 100 == 1:  # Log every 100 drops
                if self.logger:
                    self.logger.warning(
                        f"⚠️  Discord queue full ({self.max_queue_size}), "
                        f"dropped {self._messages_dropped} messages. "
                        f"Increase 'discord_max_queue' in config or reduce notification volume."
                    )
            return
        
        embed = self._create_embed(secret_data)
        self.queue.append(embed)
    
    async def queue_batch_alert(self, secrets: list, file_path: str = None, domain: str = None):
        """
        Queue multiple secrets - sends individual detailed notifications for each
        Previously batched notifications, but now sends one detailed message per secret
        for better manual review and triage
        
        Args:
            secrets: List of secret data dictionaries
            file_path: Path to the file containing the secrets (optional)
            domain: Domain for grouping (optional)
        """
        from pathlib import Path
        from urllib.parse import urlparse
        
        if not secrets:
            return
        
        # CHANGE: Send individual detailed notifications for each secret
        # instead of batching them together
        for secret in secrets:
            await self.queue_alert(secret)
    
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
                    
                    # Add configurable delay between messages to avoid bursts
                    # This helps with rate limiting and readability
                    if self.queue:  # Only delay if more messages are pending
                        await asyncio.sleep(0.5)  # 500ms default delay
                else:
                    # Wait before checking rate limit again
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
            # Issue #4: Add timeout to prevent hanging if Discord is down (increased to 60s for slow API responses during long phases)
            timeout = aiohttp.ClientTimeout(total=60)
            async with session.post(self.webhook_url, json=embed, timeout=timeout) as response:
                if response.status == 429:
                    # Rate limited by Discord - implement retry limit
                    embed_id = id(embed)
                    retry_count = self.message_retry_counts.get(embed_id, 0)
                    
                    if retry_count < 3:  # Max 3 retries per message
                        retry_after = int(response.headers.get('Retry-After', 5))
                        self.message_retry_counts[embed_id] = retry_count + 1
                        
                        if self.logger:
                            self.logger.warning(
                                f"⚠️  Discord rate limit (429), retry {retry_count + 1}/3 in {retry_after}s"
                            )
                        
                        await asyncio.sleep(retry_after)
                        self.queue.appendleft(embed)
                    else:
                        # Max retries reached - drop message
                        if self.logger:
                            self.logger.error(
                                f"❌ Discord message dropped after 3 rate limit retries. "
                                f"Consider reducing notification volume or increasing rate_limit."
                            )
                        self.message_retry_counts.pop(embed_id, None)
                elif response.status not in [200, 204]:
                    error_text = await response.text()
                    if self.logger:
                        if response.status == 404:
                            self.logger.error(
                                f"❌ Discord webhook not found (404)\n"
                                f"   The webhook URL is invalid or was deleted.\n"
                                f"   Please check:\n"
                                f"   1. Go to Discord Server > Settings > Integrations > Webhooks\n"
                                f"   2. Copy the correct webhook URL\n"
                                f"   3. Update 'discord_webhook' in config.yaml"
                            )
                        elif response.status == 400:
                            self.logger.error(
                                f"❌ Discord webhook bad request (400)\n"
                                f"   Error: {error_text[:200]}\n"
                                f"   The message format may be invalid or too large\n"
                                f"   Discord limits: 2000 chars description, 6000 chars total"
                            )
                        else:
                            self.logger.error(
                                f"❌ Discord webhook failed (HTTP {response.status})\n"
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
        Creates a detailed Discord embed for secret findings with all info needed for manual review
        
        Args:
            secret_data: Dictionary containing secret information
            
        Returns:
            Discord webhook payload
        """
        from urllib.parse import urlparse
        from pathlib import Path
        
        # Determine verification status and color
        verified = secret_data.get('Verified', secret_data.get('verified', False))
        color = 0xFF0000 if verified else 0xFFA500  # Red = verified, Orange = unverified
        
        # Get detector info
        detector_name = secret_data.get('DetectorName', secret_data.get('type', 'Unknown'))
        
        # Get source metadata
        source_metadata = secret_data.get('SourceMetadata', {})
        url = source_metadata.get('url', '')
        file_path = source_metadata.get('file', '')
        
        # Extract domain from URL
        domain = 'Unknown'
        if url:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc or 'Unknown'
            except:
                pass
        
        # If no URL but we have a file path, extract filename for context
        file_context = ''
        if file_path:
            file_context = Path(file_path).name
        
        # Get the actual secret
        raw_secret = secret_data.get('Raw', secret_data.get('RawV2', secret_data.get('secret', '')))
        redacted = secret_data.get('Redacted', '')
        
        # Use redacted version if available, otherwise show raw (truncated if needed)
        display_secret = redacted if redacted else raw_secret
        # Respect Discord's description limit (4096 chars) - keep it short and readable
        if len(display_secret) > 200:
            display_secret = display_secret[:200] + "..."
        
        # Build description with secret in code block
        description = f"```\n{display_secret}\n```"
        
        # Build detailed fields
        fields = []
        
        # Domain/Host field for easy triaging (CRITICAL FOR BUG BOUNTY)
        if domain != 'Unknown':
            fields.append({
                'name': '🎯 Domain',
                'value': f'`{domain}`',
                'inline': False
            })
        
        # Source: Full JS file URL with line number (clean and clickable)
        line_num = source_metadata.get('line', 0)
        if url:
            # Create URL with line number appended
            if line_num:
                source_value = f"{url}:{line_num}"
            else:
                source_value = url
            
            # Show full URL without truncation (Discord handles long URLs well)
            fields.append({
                'name': '📄 Source File',
                'value': source_value,
                'inline': False
            })
        elif file_context:
            # Show filename if no URL
            fields.append({
                'name': '📄 File',
                'value': f'`{file_context}`',
                'inline': False
            })
        
        # Verification status
        status_icon = "✅" if verified else "⚠️"
        status_text = "Verified" if verified else "Unverified"
        fields.append({
            'name': '✓ Status',
            'value': f"{status_icon} {status_text}",
            'inline': True
        })
        
        # Get entropy level for context
        entropy = secret_data.get('Entropy', secret_data.get('entropy', 0))
        if entropy:
            entropy_str = f"{entropy:.2f}" if isinstance(entropy, (int, float)) else str(entropy)
            fields.append({
                'name': '📊 Entropy',
                'value': entropy_str,
                'inline': True
            })
        
        # Get key information (if available)
        key_data = secret_data.get('Raw', secret_data.get('RawV2', ''))
        # Look for common API key indicators
        if key_data and len(key_data) > 10:
            key_preview = key_data[:30]
            if len(key_data) > 30:
                key_preview += "..."
            fields.append({
                'name': '🔑 Key Preview',
                'value': f'`{key_preview}`',
                'inline': False
            })
        
        # Create title with domain/host context (CRITICAL FOR MANUAL TRIAGING)
        title_icon = "🔴" if verified else "🟠"
        if domain != 'Unknown':
            title = f"{title_icon} {detector_name} • {domain}"
        elif file_context:
            title = f"{title_icon} {detector_name} • {file_context}"
        else:
            title = f"{title_icon} {detector_name} Secret"
        # Discord title limit is 256 chars
        if len(title) > 256:
            title = title[:253] + "..."
        
        # Create embed with footer
        embed = {
            'embeds': [{
                'title': title,
                'description': description,
                'color': color,
                'fields': fields,
                'footer': {
                    'text': f'JS-Scanner v3.1 • {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}'
                },
                'timestamp': datetime.utcnow().isoformat()
            }]
        }
        
        return embed
    
    async def flush_batched_secrets(self, unverified_secrets: list, batch_size: int = 10, group_by_domain: bool = True):
        """
        Flush unverified secrets at phase end - sends individual detailed messages
        Previously batched messages, now sends each secret with full details for review
        
        Args:
            unverified_secrets: List of unverified secret data dictionaries
            batch_size: No longer used (kept for backward compatibility)
            group_by_domain: No longer used (kept for backward compatibility)
        """
        if not unverified_secrets:
            return
        
        # Send each secret individually for maximum detail and manual review capability
        for secret in unverified_secrets:
            await self.queue_alert(secret)
    
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
