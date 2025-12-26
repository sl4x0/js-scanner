"""
Discord Notifier
Rate-limited Discord webhook alerting system

Optimizations:
- Batch notifications: Groups multiple secrets from same file into single message
- Rate limiting: Prevents hitting Discord's API limits (30 msgs/min default)
- Queuing system: Ensures no alerts are lost during high-volume scans
"""
import asyncio
from curl_cffi.requests import AsyncSession
import time
from typing import Dict, Any, Optional
from collections import deque
from datetime import datetime


class Discord:
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
        self._sent_secrets = set()  # Track sent secrets to prevent duplicates
        # Dynamic rate limiting state
        self.rate_limited_until = 0.0  # epoch time until which sending is paused
        self.temporary_rate_limit = None  # optional reduced rate_limit after 429
        self.temporary_rate_limit_expires = 0.0
    
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
        Queues a secret alert for sending (with deduplication)
        
        Args:
            secret_data: Dictionary containing secret information
        """
        # Create unique hash for deduplication (based on raw secret + detector + source)
        raw_secret = secret_data.get('Raw', secret_data.get('RawV2', ''))
        detector = secret_data.get('DetectorName', 'Unknown')
        source_metadata = secret_data.get('SourceMetadata', {})
        source_file = source_metadata.get('file', '')
        source_line = source_metadata.get('line', 0)
        
        # Create deduplication key
        dedup_key = f"{detector}:{raw_secret}:{source_file}:{source_line}"
        
        # Skip if already sent
        if dedup_key in self._sent_secrets:
            if self.logger:
                self.logger.debug(f"Skipping duplicate secret: {detector} in {source_file}")
            return
        
        # Mark as sent
        self._sent_secrets.add(dedup_key)
        
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
        async with AsyncSession(impersonate="chrome110") as session:
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
        
        # Respect explicit Discord-imposed rate limit window
        if getattr(self, 'rate_limited_until', 0) and time.time() < self.rate_limited_until:
            return False

        # Use temporary reduced rate limit if active
        effective_limit = self.rate_limit
        if self.temporary_rate_limit and time.time() < self.temporary_rate_limit_expires:
            effective_limit = self.temporary_rate_limit

        return len(self.message_times) < effective_limit
    
    async def _send_webhook(self, session: AsyncSession, embed: Dict[str, Any]):
        """
        Sends a webhook message
        
        Args:
            session: curl_cffi AsyncSession
            embed: Embed data to send
        """
        try:
            # Issue #4: Add timeout to prevent hanging if Discord is down
            response = await session.post(self.webhook_url, json=embed, timeout=60)
            if response.status_code == 429:
                # Rate limited by Discord - implement retry limit
                embed_id = id(embed)
                retry_count = self.message_retry_counts.get(embed_id, 0)
                
                if retry_count < 3:  # Max 3 retries per message
                    retry_after = int(response.headers.get('Retry-After', 5))
                    # Honor server-specified Retry-After window
                    self.rate_limited_until = time.time() + retry_after
                    # Apply a conservative temporary rate limit for the next minute
                    try:
                        self.temporary_rate_limit = max(1, int(self.rate_limit / 2))
                    except Exception:
                        self.temporary_rate_limit = max(1, self.rate_limit // 2)
                    self.temporary_rate_limit_expires = time.time() + max(60, retry_after)

                    if self.logger:
                        self.logger.warning(f"⚠️  Discord responded 429: backing off for {retry_after}s, temporary rate_limit={self.temporary_rate_limit} until {self.temporary_rate_limit_expires}")
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
            elif response.status_code not in [200, 204]:
                error_text = response.text
                if self.logger:
                    if response.status_code == 404:
                        self.logger.error(
                            f"❌ Discord webhook not found (404)\n"
                            f"   The webhook URL is invalid or was deleted.\n"
                            f"   Please check:\n"
                            f"   1. Go to Discord Server > Settings > Integrations > Webhooks\n"
                            f"   2. Copy the correct webhook URL\n"
                            f"   3. Update 'discord_webhook' in config.yaml"
                        )
                    elif response.status_code == 400:
                        self.logger.error(
                            f"❌ Discord webhook bad request (400)\n"
                            f"   Error: {error_text[:200]}\n"
                            f"   The message format may be invalid or too large\n"
                            f"   Discord limits: 2000 chars description, 6000 chars total"
                        )
                    else:
                        self.logger.error(
                            f"❌ Discord webhook failed (HTTP {response.status_code})\n"
                            f"   Error: {error_text[:200]}\n"
                            f"   Check your webhook URL in config.yaml"
                        )
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
        
        # Extract domain from metadata first, then fallback to URL parsing
        domain = source_metadata.get('domain', 'Unknown')
        if domain == 'Unknown' and url:
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
        
        # Use redacted version for preview, otherwise show truncated raw
        display_preview = redacted if redacted else raw_secret
        if len(display_preview) > 30:
            display_preview = display_preview[:30] + "..."
        
        # Build description with ALL critical info upfront for quick triaging
        line_num = source_metadata.get('line', 0)
        
        # Build multi-line description with all key details
        description_parts = []
        
        # 1. Domain/Host (CRITICAL - shows target at a glance)
        if domain != 'Unknown':
            description_parts.append(f"**🎯 Target Domain:** `{domain}`")
        
        # 2. Full JS File URL (CRITICAL - direct link to investigate)
        if url:
            # Truncate very long URLs for better readability, but keep full URL in hyperlink
            display_url = url if len(url) <= 100 else url[:97] + "..."
            description_parts.append(f"**📄 JavaScript File:** {url}")
        elif file_context:
            description_parts.append(f"**📄 File:** `{file_context}`")
        
        # 3. Line Number (CRITICAL - exact location in file)
        if line_num:
            description_parts.append(f"**📍 Line Number:** `{line_num}`")
        
        # 4. Secret Preview (truncated for security)
        description_parts.append(f"**🔐 Secret Preview:** `{display_preview}`")
        
        description = "\n".join(description_parts)
        
        # Build detailed fields
        fields = []
        
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
