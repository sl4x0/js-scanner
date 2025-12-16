"""
Fetcher Module
Handles fetching JavaScript files from Wayback Machine and live sites using Playwright
"""
import asyncio
import aiohttp
import time
from playwright.async_api import async_playwright, Browser, BrowserContext
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import re


class WaybackRateLimiter:
    """Rate limiter for Wayback Machine API (15 requests/second)"""
    
    def __init__(self, requests_per_second: int = 15):
        self.rate = requests_per_second
        self.tokens = float(self.rate)
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire a token, waiting if necessary"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Refill tokens
            self.tokens = min(
                self.rate,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                # Log rate limiting activity
                import logging
                logger = logging.getLogger('jsscanner')
                logger.debug(f"⏳ Wayback rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.tokens = 1
            
            self.tokens -= 1


class BrowserManager:
    """Manages Playwright browser instances with memory leak prevention"""
    
    def __init__(self, playwright_instance, max_concurrent: int = 3, restart_after: int = 100, headless: bool = True, logger=None):
        self.playwright = playwright_instance
        self.browser = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.page_count = 0
        self.restart_after = restart_after
        self.headless = headless
        self.lock = asyncio.Lock()
        self.logger = logger
    
    async def _ensure_browser(self):
        """Ensures browser is running, restarts if needed"""
        async with self.lock:
            should_restart = self.browser is None or self.page_count >= self.restart_after
            
            if should_restart:
                if self.browser:
                    if self.logger:
                        self.logger.debug(f"Restarting browser (pages: {self.page_count})")
                    await self.browser.close()
                    self.page_count = 0
                    await asyncio.sleep(1)  # Wait for cleanup (Issue #5)
                
                # Cross-platform Chromium launch arguments
                # Linux VPS requires --no-sandbox and --disable-setuid-sandbox
                launch_args = [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-dev-tools',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
                
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    args=launch_args
                )
    
    async def fetch_with_context(self, url: str, page_timeout: int):
        """Fetch URL with proper context management"""
        await self._ensure_browser()
        
        async with self.semaphore:
            context = None
            page = None
            js_urls = []
            
            try:
                context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    ignore_https_errors=True,
                    java_script_enabled=True
                )
                
                page = await context.new_page()
                page.set_default_timeout(page_timeout)
                
                # Intercept script responses
                async def handle_response(response):
                    if response.request.resource_type == 'script':
                        js_urls.append(response.url)
                
                page.on('response', handle_response)
                
                # Navigate and scroll
                await page.goto(url, wait_until='networkidle')
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
                
                self.page_count += 1
                
            except Exception as e:
                raise e
            finally:
                # CRITICAL: Always close to prevent memory leaks
                if page:
                    await page.close()
                if context:
                    await context.close()
            
            return js_urls
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()


class Fetcher:
    """
    Fetches JavaScript files from various sources
    
    This module provides methods for fetching JS URLs from different sources
    but does NOT make decisions about when to use them. The calling code
    (ScanEngine) controls discovery behavior based on user configuration.
    """
    
    def __init__(self, config: dict, logger) -> None:
        """
        Initialize fetcher
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser_manager = None
        self.last_failure_reason = None  # Track last fetch failure reason
        self.verbose = config.get('verbose', False)  # Verbose mode flag
        
        # Rate limiters
        wayback_rate = config.get('wayback', {}).get('rate_limit', 15)
        self.wayback_limiter = WaybackRateLimiter(wayback_rate)
        
        # Playwright settings
        self.max_concurrent = config.get('playwright', {}).get('max_concurrent', 3)
        self.restart_after = config.get('playwright', {}).get('restart_after', 100)
        self.page_timeout = config.get('playwright', {}).get('page_timeout', 30000)
        self.headless = config.get('playwright', {}).get('headless', True)
        
        # Wayback settings
        self.wayback_max_results = config.get('wayback', {}).get('max_results', 10000)
    
    def _is_in_scope(self, url: str, target: str) -> bool:
        """
        Check if URL is in scope (same root domain as target)
        
        Args:
            url: URL to check
            target: Target domain
            
        Returns:
            True if in scope
        """
        from urllib.parse import urlparse
        
        try:
            # Reject blob, data, javascript URLs
            if url.startswith(('blob:', 'data:', 'javascript:')):
                return False
            
            if not url.startswith(('http://', 'https://')):
                return False
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if not domain:
                return False
            
            # Remove port
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Get root domain
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                root_domain = '.'.join(domain_parts[-2:])
            else:
                root_domain = domain
            
            # Get target root domain
            target_clean = target.lower().replace('https://', '').replace('http://', '').replace('www.', '')
            target_parts = target_clean.split('.')
            if len(target_parts) >= 2:
                target_root = '.'.join(target_parts[-2:])
            else:
                target_root = target_clean
            
            return root_domain == target_root
            
        except Exception:
            return False
    
    async def initialize(self) -> None:
        """
        Initialize Playwright browser only if needed
        
        Raises:
            Exception: If Playwright initialization fails
        """
        # Only initialize if live scanning is enabled
        skip_live = self.config.get('skip_live', False)
        
        if not skip_live:
            self.playwright = await async_playwright().start()
            self.browser_manager = BrowserManager(
                self.playwright,
                max_concurrent=self.max_concurrent,
                restart_after=self.restart_after,
                headless=self.headless,
                logger=self.logger  # Issue #5: Pass logger for debug output
            )
            self.logger.info("Playwright browser manager initialized")
        else:
            self.logger.info("Playwright initialization skipped (--no-live flag)")
    
    async def cleanup(self) -> None:
        """
        Cleanup Playwright resources
        
        Raises:
            Exception: If cleanup fails
        """
        if self.browser_manager:
            await self.browser_manager.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("Playwright browser closed")
    
    async def fetch_wayback(self, target: str) -> List[str]:
        """
        Fetch JavaScript URLs from Wayback Machine
        
        Args:
            target: Target domain
            
        Returns:
            List of JavaScript URLs (as Wayback archive URLs)
        """
        self.logger.info(f"Fetching from Wayback Machine: {target}")
        
        # Strip www. prefix to avoid *.www.domain.com pattern
        clean_target = target.replace('http://', '').replace('https://', '').replace('www.', '')
        
        # Get original URLs directly from Wayback CDX API
        cdx_url = "http://web.archive.org/cdx/search/cdx"
        params = {
            'url': f'*.{clean_target}/*',
            'matchType': 'prefix',  # Use prefix for better matching (was 'domain')
            'fl': 'original',
            'collapse': 'urlkey',  # More comprehensive results (groups by URL pattern)
            # REMOVED: 'filter': 'statuscode:200' - Too restrictive, many valid files excluded
            'limit': self.wayback_max_results
        }
        
        js_urls = set()  # Use set for automatic deduplication
        
        # Retry configuration
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting
                await self.wayback_limiter.acquire()
                
                if attempt > 0:
                    self.logger.info(f"🔄 Wayback retry attempt {attempt + 1}/{max_retries} for {clean_target}")
                    await asyncio.sleep(retry_delay * attempt)
                
                self.logger.info(f"Wayback query: {cdx_url}?url={params['url']}&fl={params['fl']}&collapse={params['collapse']}")
                
                async with aiohttp.ClientSession() as session:
                    timeout = aiohttp.ClientTimeout(total=120, sock_read=60)
                    async with session.get(cdx_url, params=params, timeout=timeout) as response:
                        self.logger.info(f"Wayback API response status: {response.status}")
                        
                        if response.status == 200:
                            # Stream line by line to handle large responses
                            line_count = 0
                            async for line in response.content:
                                line_count += 1
                                original_url = line.decode('utf-8', errors='ignore').strip()
                                
                                if not original_url:
                                    continue
                                
                                # Check if it's a valid .js URL using urlparse
                                try:
                                    from urllib.parse import urlparse
                                    parsed = urlparse(original_url)
                                    
                                    # Must have proper scheme and domain
                                    if not parsed.scheme or not parsed.netloc:
                                        continue
                                    
                                    # Check if path ends with .js or .mjs
                                    if parsed.path.endswith('.js') or parsed.path.endswith('.mjs'):
                                        # Add original URL directly (no web.archive.org wrapper)
                                        js_urls.add(original_url)
                                except:
                                    continue
                                
                                # Log progress every 1000 lines
                                if line_count % 1000 == 0:
                                    self.logger.info(f"Processed {line_count} lines, found {len(js_urls)} JS URLs so far...")
                            
                            self.logger.info(f"Wayback returned {line_count} total URLs, found {len(js_urls)} unique .js files")
                            break  # Success, exit retry loop
                        elif response.status == 429:
                            self.logger.warning(f"Wayback rate limit exceeded (429)")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay * 2)  # Longer wait for rate limit
                                continue
                        elif response.status >= 500:
                            self.logger.warning(f"Wayback server error ({response.status})")
                            if attempt < max_retries - 1:
                                continue
                        else:
                            self.logger.warning(f"Wayback returned status {response.status}")
                            break  # Don't retry for client errors
                            
            except asyncio.TimeoutError:
                self.logger.warning(f"Wayback request timed out after 120s (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
            except aiohttp.ClientError as e:
                self.logger.warning(f"Wayback network error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    continue
            except Exception as e:
                self.logger.error(f"Unexpected error fetching from Wayback: {e}")
                break  # Don't retry for unexpected errors
        
        # Filter to only target domain before returning
        filtered_urls = []
        for url in js_urls:
            if self._is_in_scope(url, target):
                filtered_urls.append(url)
            else:
                self.logger.debug(f"[WAYBACK] Filtered out-of-scope URL: {url}")
        
        if len(js_urls) > len(filtered_urls):
            self.logger.info(f"Filtered {len(js_urls) - len(filtered_urls)} out-of-scope URLs from Wayback")
        
        # Issue #3: Warn when large result sets are detected
        if len(filtered_urls) > 5000:
            self.logger.warning(
                f"⚠️  Wayback returned {len(filtered_urls)} JS files!\n"
                f"   This may take a long time to scan.\n"
                f"   Consider using --no-wayback for faster scanning."
            )
        
        # Issue #11: Validate URLs before returning
        validated_urls = []
        for url in filtered_urls:
            if self._validate_wayback_url(url):
                validated_urls.append(url)
            else:
                self.logger.debug(f"[WAYBACK] Rejected malformed URL: {url[:100]}")
        
        if len(filtered_urls) > len(validated_urls):
            self.logger.info(f"Filtered {len(filtered_urls) - len(validated_urls)} malformed URLs from Wayback")
        
        return validated_urls
    
    def _validate_wayback_url(self, url: str) -> bool:
        """
        Validate Wayback URL for safety (Issue #11)
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is safe, False otherwise
        """
        # Check URL length (max 2048 characters)
        if len(url) > 2048:
            return False
        
        # Check for null bytes
        if '\x00' in url:
            return False
        
        # Check for XSS attempts
        url_lower = url.lower()
        if '<script' in url_lower or 'javascript:' in url_lower:
            return False
        
        # Validate character set (printable ASCII only)
        try:
            url.encode('ascii')
            if not all(32 <= ord(c) <= 126 or c in '\r\n' for c in url):
                return False
        except UnicodeEncodeError:
            return False
        
        return True
    
    async def fetch_live(self, target: str) -> List[str]:
        """
        Fetch JavaScript URLs from live site using Playwright
        Enhanced to detect scripts on modern SPAs with retry mechanism
        
        Args:
            target: Target URL
            
        Returns:
            List of JavaScript URLs
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    self.logger.info(f"🔄 Retry attempt {attempt + 1}/{max_retries} for {target}")
                    await asyncio.sleep(retry_delay * attempt)  # Exponential backoff
                
                result = await self._fetch_live_attempt(target)
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if error is retryable
                is_retryable = any(x in error_msg for x in [
                    "Target closed", "Protocol error", "browser has been closed",
                    "context has been closed", "page has been closed"
                ])
                
                if is_retryable and attempt < max_retries - 1:
                    self.logger.warning(f"⚠️  Browser crashed (attempt {attempt + 1}/{max_retries}): {error_msg[:100]}")
                    self.logger.info(f"🔄 Restarting browser and retrying...")
                    
                    # Force browser restart
                    try:
                        if self.browser_manager and self.browser_manager.browser:
                            await self.browser_manager.browser.close()
                            self.browser_manager.browser = None
                    except:
                        pass
                    
                    continue  # Retry
                else:
                    # Non-retryable error or final attempt - handle and return
                    if "Download is starting" in error_msg or "download" in error_msg.lower():
                        self.logger.info(f"⚠️  URL triggers a download (not a page): {target}")
                        if target.endswith('.js') or target.endswith('.mjs') or '.js?' in target:
                            return [target]
                    elif "net::ERR_NAME_NOT_RESOLVED" in error_msg:
                        self.logger.warning(f"[DNS ERROR] Could not resolve domain: {target}")
                    elif "net::ERR_CONNECTION_REFUSED" in error_msg:
                        self.logger.warning(f"[CONNECTION REFUSED] Server rejected connection: {target}")
                    elif "net::ERR_CERT" in error_msg or "SSL" in error_msg:
                        self.logger.warning(f"[SSL ERROR] Certificate validation failed: {target}")
                    elif "net::ERR_ABORTED" in error_msg:
                        self.logger.info(f"⚠️  Navigation aborted (redirect or client-side routing): {target}")
                    else:
                        self.logger.warning(f"[ERROR] Live scan failed for {target}: {error_msg[:150]}")
                    
                    return []
        
        return []  # All retries exhausted
    
    async def _fetch_live_attempt(self, target: str) -> List[str]:
        """
        Single attempt to fetch JavaScript URLs from live site
        
        Args:
            target: Target URL
            
        Returns:
            List of JavaScript URLs
        """
        self.logger.info(f"🌐 Launching browser to scan live site: {target}")
        
        if not target.startswith('http'):
            target = f'https://{target}'
        
        js_urls = set()
        context = None
        page = None
        
        try:
            self.logger.info(f"Opening page in headless browser...")
            await self.browser_manager._ensure_browser()
            
            # Create stealth context to bypass anti-bot measures
            context = await self.browser_manager.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True  # ✅ Bypass Content Security Policy
            )
            
            page = await context.new_page()
            # Increase timeout to 60 seconds for sites with anti-bot protection
            page.set_default_timeout(60000)  # ✅ 60 seconds instead of 30
            
            # Track all JS requests (with strict domain filtering)
            async def handle_request(request):
                url = request.url
                resource_type = request.resource_type
                
                # Skip third-party scripts immediately
                if not self._is_in_scope(url, target):
                    return
                
                # Validate URL format before adding
                if not url.startswith(('http://', 'https://')):
                    return
                
                # Check for obvious corruption (spaces, invalid characters)
                if ' ' in url or any(ord(c) < 32 or ord(c) > 126 for c in url[:100]):
                    self.logger.debug(f"Skipping malformed URL: {url[:100]}")
                    return
                
                # Detect JS files by resource type OR file extension
                if resource_type == 'script':
                    js_urls.add(url)
                    self.logger.info(f"✓ Found JS: {url}")
                elif '.js' in url.lower():
                    # Fallback: check if URL contains .js
                    parsed = urlparse(url)
                    if parsed.path.endswith('.js') or parsed.path.endswith('.mjs') or '.js?' in url.lower():
                        js_urls.add(url)
                        self.logger.info(f"✓ Found JS: {url}")
            
            page.on('request', handle_request)
            
            # Navigate with domcontentloaded (faster, more reliable than networkidle)
            self.logger.info(f"Navigating to {target}...")
            try:
                await page.goto(target, wait_until='domcontentloaded', timeout=30000)
                self.logger.info(f"Page loaded, waiting for dynamic content...")
            except Exception as e:
                # Even if navigation times out, we may have discovered JS files via request handler
                if 'Timeout' in str(e) or 'timeout' in str(e).lower():
                    self.logger.warning(f"⚠️  Navigation timeout, but may have discovered JS files: {len(js_urls)} found")
                    # Return discovered files even if page didn't fully load
                    if js_urls:
                        self.logger.info(f"🎯 Returning {len(js_urls)} JS files discovered before timeout")
                        return list(js_urls)
                    return []
                else:
                    raise  # Re-raise non-timeout errors
            
            # Wait extra time for dynamic content
            await asyncio.sleep(3)
            
            # Scroll to trigger lazy-loaded scripts
            self.logger.info(f"Scrolling to trigger lazy-loaded scripts...")
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
            
            # Also extract from DOM
            scripts = await page.query_selector_all('script[src]')
            for script in scripts:
                src = await script.get_attribute('src')
                if src:
                    absolute_url = urljoin(target, src)
                    # More permissive: accept anything that looks like JS
                    if '.js' in absolute_url.lower():
                        js_urls.add(absolute_url)
                        self.logger.debug(f"Found JS (DOM): {absolute_url}")
            
            # Look for inline script content with URLs
            inline_scripts = await page.query_selector_all('script:not([src])')
            for script in inline_scripts:
                try:
                    content = await script.inner_text()
                    # Find JS URLs in inline scripts
                    import re
                    urls_in_script = re.findall(r'["\']([^"\']*\.js[^"\']*)["\']', content)
                    for url in urls_in_script:
                        absolute_url = urljoin(target, url)
                        js_urls.add(absolute_url)
                except:
                    pass  # Skip if inner_text fails
            
        except asyncio.TimeoutError:
            self.logger.warning(f"[TIMEOUT] Live scan timed out after {self.page_timeout/1000}s for {target}")
            raise  # Re-raise for retry mechanism
        except Exception as e:
            # Re-raise for retry mechanism to handle
            raise
        finally:
            # Graceful cleanup - handle already-closed browser/context
            try:
                if page:
                    await page.close()
            except Exception:
                pass  # Page already closed, ignore
            
            try:
                if context:
                    await context.close()
            except Exception:
                pass  # Context already closed, ignore
        
        # Convert set to list (deduplication already done)
        js_urls = list(js_urls)
        
        self.logger.info(f"🎯 Live scan complete: Found {len(js_urls)} JavaScript files")
        
        return js_urls
    
    async def fetch_content(self, url: str, retry_count: int = 0) -> Optional[str]:
        """
        Fetches the content of a JavaScript file
        Uses streaming to prevent loading large files into memory at once
        
        Args:
            url: URL of the JavaScript file
            retry_count: Current retry attempt (for exponential backoff)
            
        Returns:
            Content of the file, or None if failed
            
        Note:
            Sets self.last_failure_reason to track why fetch failed
        """
        self.last_failure_reason = None
        max_size = self.config.get('max_file_size', 10485760)  # 10MB default
        max_retries = 3
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    # Issue #15: Handle rate limiting with exponential backoff
                    if response.status in [429, 503]:
                        if retry_count < max_retries:
                            # Check for Retry-After header
                            retry_after = response.headers.get('Retry-After')
                            if retry_after:
                                try:
                                    wait_time = int(retry_after)
                                except ValueError:
                                    wait_time = 2 ** retry_count
                            else:
                                wait_time = 2 ** retry_count  # Exponential backoff: 1, 2, 4 seconds
                            
                            self.logger.warning(
                                f"[RATE LIMITED] {url} (status {response.status})\n"
                                f"  Retrying in {wait_time}s (attempt {retry_count + 1}/{max_retries})"
                            )
                            await asyncio.sleep(wait_time)
                            return await self.fetch_content(url, retry_count + 1)
                        else:
                            self.logger.warning(f"[RATE LIMITED] {url}: Max retries exceeded")
                            return None
                    
                    if response.status == 200:
                        # Check content length header first
                        content_length = response.headers.get('Content-Length')
                        if content_length and int(content_length) > max_size:
                            self.logger.warning(
                                f"❌ File too large: {url} ({int(content_length) / 1024 / 1024:.2f} MB, "
                                f"max: {max_size / 1024 / 1024:.2f} MB)"
                            )
                            self.last_failure_reason = 'too_large'
                            return None
                        
                        # ✅ OPTIMIZATION: Stream and check size incrementally (prevents memory overflow)
                        chunks = []
                        total_size = 0
                        
                        async for chunk in response.content.iter_chunked(8192):
                            total_size += len(chunk)
                            if total_size > max_size:
                                self.logger.warning(
                                    f"❌ File exceeded size during download: {url} ({total_size / 1024 / 1024:.2f} MB)"
                                )
                                self.last_failure_reason = 'too_large'
                                return None
                            chunks.append(chunk)
                        
                        content = b''.join(chunks).decode('utf-8', errors='ignore')
                        
                        # Detect soft 404s - HTML error pages with 200 status
                        content_start = content.strip()[:500].lower()
                        if ('<!doctype html' in content_start or 
                            '<html' in content_start or
                            '<head>' in content_start or
                            content_start.startswith('<!')):
                            if self.verbose:
                                self.logger.warning(f"❌ HTML instead of JS: {url}")
                            else:
                                self.logger.debug(f"Filtered HTML response: {url}")
                            self.last_failure_reason = 'html_not_js'
                            return None
                        
                        # Check if content is actually empty or whitespace only (allow minified JS)
                        if not content or len(content.strip()) < 50:
                            if self.verbose:
                                self.logger.warning(f"❌ Content too short ({len(content)} bytes): {url}")
                            else:
                                self.logger.debug(f"Filtered short content ({len(content)} bytes): {url}")
                            self.last_failure_reason = 'too_short'
                            return None
                        
                        return content
                    else:
                        # Only log in verbose mode - these are common (404, 403, etc.)
                        if self.verbose:
                            self.logger.warning(f"❌ HTTP {response.status}: {url}")
                        else:
                            self.logger.debug(f"HTTP {response.status}: {url}")
                        self.last_failure_reason = 'http_error'
                        return None
        except asyncio.TimeoutError:
            self.logger.warning(
                f"❌ [TIMEOUT] {url}\n"
                f"  Request exceeded 30 second timeout"
            )
            self.last_failure_reason = 'timeout'
            return None
        except aiohttp.ClientConnectorError as e:
            self.logger.warning(
                f"❌ [CONNECTION FAILED] {url}\n"
                f"  Error: {str(e)[:200]}"
            )
            self.last_failure_reason = 'http_error'
            return None
        except aiohttp.ClientError as e:
            self.logger.warning(
                f"❌ [HTTP ERROR] {url}\n"
                f"  Error: {str(e)[:200]}"
            )
            self.last_failure_reason = 'http_error'
            return None
        except Exception as e:
            self.logger.error(
                f"❌ [UNEXPECTED ERROR] {url}\n"
                f"  Error: {str(e)[:200]}\n"
                f"  Type: {type(e).__name__}",
                exc_info=True
            )
            self.last_failure_reason = 'http_error'
            return None
    
    async def fetch_with_playwright(self, url: str) -> Optional[str]:
        """
        Fetches content using Playwright (for dynamic content)
        
        Args:
            url: URL to fetch
            
        Returns:
            Page content or None
        """
        context = None
        page = None
        
        try:
            await self.browser_manager._ensure_browser()
            context = await self.browser_manager.browser.new_context()
            page = await context.new_page()
            page.set_default_timeout(self.page_timeout)
            
            await page.goto(url, wait_until='networkidle')
            content = await page.content()
            
            return content
            
        except asyncio.TimeoutError as e:
            self.logger.error(f"Playwright timeout for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching with Playwright {url}: {e}", exc_info=True)
            return None
        finally:
            # CRITICAL: Always close
            if page:
                await page.close()
            if context:
                await context.close()
