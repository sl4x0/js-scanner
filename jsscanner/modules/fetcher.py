"""
Fetcher Module
Handles fetching JavaScript files from live sites using Playwright
"""
import asyncio
import aiohttp
import time
from playwright.async_api import async_playwright, Browser, BrowserContext
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import re
from .noise_filter import NoiseFilter


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
        
        # Initialize noise filter
        self.noise_filter = NoiseFilter(logger=logger)
        
        # Playwright settings
        self.max_concurrent = config.get('playwright', {}).get('max_concurrent', 3)
        self.restart_after = config.get('playwright', {}).get('restart_after', 100)
        self.page_timeout = config.get('playwright', {}).get('page_timeout', 30000)
        self.headless = config.get('playwright', {}).get('headless', True)
    
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
        async def _smart_interactions(self, page) -> None:
        """
        Trigger lazy loaders through smart interactions (conservative approach)
        Implements scroll, hover, and tab switching without risky clicks
        
        Args:
            page: Playwright page object
        """
        try:
            # 1. Progressive scroll to trigger infinite scroll and lazy images
            self.logger.debug("🖱️  Progressive scrolling to trigger lazy content...")
            await page.evaluate("""
                async () => {
                    const distance = 100;
                    const delay = 100;
                    const maxScroll = document.body.scrollHeight;
                    
                    for (let i = 0; i < maxScroll; i += distance) {
                        window.scrollTo(0, i);
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                    window.scrollTo(0, 0); // Back to top
                }
            """)
            
            # 2. Hover on interactive elements (triggers tooltips, dropdowns, popovers)
            self.logger.debug("🖱️  Hovering on interactive elements...")
            await page.evaluate("""
                () => {
                    const selectors = [
                        '[data-tooltip]',
                        '[data-popover]',
                        '[aria-haspopup]',
                        '.dropdown-toggle',
                        '[role=\"button\"]',
                        '[data-toggle]',
                        '.has-dropdown'
                    ];
                    
                    selectors.forEach(selector => {
                        try {
                            document.querySelectorAll(selector).forEach(el => {
                                el.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
                                el.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
                            });
                        } catch(e) {
                            // Ignore errors on individual elements
                        }
                    });
                }
            """)
            
            # 3. Trigger tab switches (for tabbed interfaces)
            self.logger.debug("🖱️  Activating tabs...")
            await page.evaluate("""
                () => {
                    document.querySelectorAll('[role=\"tab\"]').forEach((tab, i) => {
                        try {
                            setTimeout(() => {
                                tab.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                            }, i * 100);
                        } catch(e) {
                            // Ignore errors
                        }
                    });
                }
            """)
            
            # 4. Wait for any lazy-loaded scripts to download
            await asyncio.sleep(3)
            
        except Exception as e:
            self.logger.warning(f"⚠️  Interaction triggers failed: {e}")
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
        lazy_loaded_urls = set()  # Track dynamically loaded JS
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
            request_start_time = time.time()
            
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
                
                # Track timing for lazy-load detection
                request_time = time.time() - request_start_time
                
                # Detect JS files by resource type OR file extension
                if resource_type == 'script':
                    js_urls.add(url)
                    # Mark as lazy-loaded if loaded after 2 seconds
                    if request_time > 2.0:
                        lazy_loaded_urls.add(url)
                        self.logger.info(f"🎯 Lazy-loaded: {url}")
                    else:
                        self.logger.info(f"✓ Found JS: {url}")
                elif '.js' in url.lower():
                    # Fallback: check if URL contains .js
                    parsed = urlparse(url)
                    if parsed.path.endswith('.js') or parsed.path.endswith('.mjs') or '.js?' in url.lower():
                        js_urls.add(url)
                        if request_time > 2.0:
                            lazy_loaded_urls.add(url)
                            self.logger.info(f"🎯 Lazy-loaded: {url}")
                        else:
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
            
            # NEW: Smart interactions to trigger lazy-loaded components
            self.logger.info(f"🖱️  Triggering interactions for lazy-loaded content...")
            await self._smart_interactions(page)
            
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
        
        if lazy_loaded_urls:
            self.logger.info(f"   ├─ Initial load: {len(js_urls) - len(lazy_loaded_urls)} files")
            self.logger.info(f"   └─ Lazy-loaded: {len(lazy_loaded_urls)} files")
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
        # Check noise filter early (before downloading)
        should_skip, reason = self.noise_filter.should_skip_url(url)
        if should_skip:
            self.logger.debug(f"⏭️  Filtered (noise): {url} - {reason}")
            self.last_failure_reason = 'filtered_noise'
            return None
        
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
                        
                        # Check content hash for known vendor libraries
                        should_skip, reason = self.noise_filter.should_skip_content(content, url)
                        if should_skip:
                            self.logger.debug(f"⏭️  Filtered (known lib): {url} - {reason}")
                            self.last_failure_reason = 'filtered_known_library'
                            return None
                        
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
