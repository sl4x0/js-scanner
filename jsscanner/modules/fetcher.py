"""
Fetcher Module
Handles fetching JavaScript files from live sites using Playwright
"""
import asyncio
import aiohttp
import time
import socket
import random
from playwright.async_api import async_playwright, Browser, BrowserContext
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re
from .noise_filter import NoiseFilter
from ..utils.retry import retry_async, RETRY_CONFIG_HTTP


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
        self.last_failure_reason = None
        self.verbose = config.get('verbose', False)
        self._browser_lock = asyncio.Lock()  # Prevent concurrent cleanup

        # Error tracking for summary
        self.error_stats = {
            'dns_errors': 0,
            'connection_refused': 0,
            'ssl_errors': 0,
            'timeouts': 0,
            'rate_limits': 0,
            'http_errors': 0
        }

        # Initialize noise filter
        self.noise_filter = NoiseFilter(logger=logger)

        # Playwright settings
        self.max_concurrent = config.get('playwright', {}).get('max_concurrent', 3)
        self.restart_after = config.get('playwright', {}).get('restart_after', 100)
        self.page_timeout = config.get('playwright', {}).get('page_timeout', 30000)
        self.headless = config.get('playwright', {}).get('headless', True)
        
        # User-Agent rotation (randomize to avoid WAF fingerprinting)
        self.user_agents = config.get('user_agents', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ])
        
        # Session and connector will be initialized in initialize() method
        self.session = None
        self.connector = None
        self.ssl_context = None
        
        # Enforce minimum retry count (minimum 3 retries for reliability)
        if 'retry' not in self.config:
            self.config['retry'] = {}
        if self.config['retry'].get('http_requests', 0) < 3:
            self.logger.warning("⚠️  Enforcing minimum retry count: http_requests = 3")
            self.config['retry']['http_requests'] = 3
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent to avoid WAF fingerprinting"""
        return random.choice(self.user_agents)
    
    def _is_in_scope(self, url: str, target: str) -> bool:
        """Check if URL is in scope (same root domain as target)"""
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
    
    async def validate_domain(self, target: str) -> Tuple[bool, str]:
        """Fast DNS validation to filter dead domains before scanning
        
        Args:
            target: Domain or URL to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            # Extract domain from URL
            if target.startswith('http'):
                parsed = urlparse(target)
                domain = parsed.netloc
            else:
                domain = target.split('/')[0]
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Quick DNS lookup (non-blocking)
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, socket.gethostbyname, domain),
                timeout=1.0
            )
            return True, "valid"
            
        except socket.gaierror:
            self.error_stats['dns_errors'] += 1
            return False, "DNS resolution failed"
        except asyncio.TimeoutError:
            self.error_stats['timeouts'] += 1
            return False, "DNS timeout"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    async def initialize(self) -> None:
        """Initialize HTTP session and Playwright browser"""
        # 1. Initialize shared HTTP session (CRITICAL for connection pooling)
        timeout_val = self.config.get('timeouts', {}).get('http_request', 15)
        timeout = aiohttp.ClientTimeout(total=timeout_val, connect=5.0)
        
        import ssl
        verify_ssl = self.config.get('verify_ssl', False)
        self.ssl_context = ssl.create_default_context()
        if not verify_ssl:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Connection pool settings
        pool_settings = self.config.get('connection_pool', {})
        self.connector = aiohttp.TCPConnector(
            ssl=self.ssl_context,
            limit=pool_settings.get('max_connections', 100),
            limit_per_host=pool_settings.get('max_per_host', 10),
            ttl_dns_cache=pool_settings.get('ttl_dns_cache', 300)
        )
        
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout
        )
        self.logger.info("✅ HTTP Session initialized with Connection Pooling (prevents connection exhaustion)")
        
        # 2. Initialize Playwright browser only if needed
        skip_live = self.config.get('skip_live', False)
        if not skip_live:
            self.playwright = await async_playwright().start()
            self.browser_manager = BrowserManager(
                self.playwright,
                max_concurrent=self.max_concurrent,
                restart_after=self.restart_after,
                headless=self.headless,
                logger=self.logger
            )
            self.logger.info("Playwright browser manager initialized")
        else:
            self.logger.info("Playwright initialization skipped (--no-live flag)")
    
    async def _smart_interactions(self, page) -> None:
        """Trigger lazy loaders through smart interactions"""
        try:
            # Check if page is closed before starting
            if page.is_closed():
                self.logger.debug("⚠️  Page already closed, skipping interactions")
                return

            # 1. Progressive scroll
            self.logger.debug("🖱️  Progressive scrolling to trigger lazy content...")
            try:
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
            except Exception as e:
                # Gracefully handle page closure during scroll
                if any(msg in str(e) for msg in ["Target closed", "browser has been closed", "Page.evaluate"]):
                    self.logger.debug("⚠️  Page closed during scroll interaction, continuing...")
                    return
                raise

            # 2. Hover on interactive elements
            self.logger.debug("🖱️  Hovering on interactive elements...")
            try:
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
                                // Ignore errors
                            }
                        });
                    }
                """)
            except Exception as e:
                # Gracefully handle page closure during hover
                if any(msg in str(e) for msg in ["Target closed", "browser has been closed", "Page.evaluate"]):
                    self.logger.debug("⚠️  Page closed during hover interaction, continuing...")
                    return
                raise

            # 3. Trigger tab switches
            self.logger.debug("🖱️  Activating tabs...")
            try:
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
            except Exception as e:
                # Gracefully handle page closure during tab activation
                if any(msg in str(e) for msg in ["Target closed", "browser has been closed", "Page.evaluate"]):
                    self.logger.debug("⚠️  Page closed during tab activation, continuing...")
                    return
                raise

            # Wait for network idle after interactions (configurable)
            interaction_delay = self.config.get('interaction_delay', 0.5)
            if interaction_delay > 0:
                self.logger.debug(f"⏱️  Waiting {interaction_delay}s for network idle...")
                try:
                    await page.wait_for_load_state('networkidle', timeout=int(interaction_delay * 1000))
                    self.logger.debug("✓ Network idle detected")
                except Exception:
                    # Timeout is OK - network might not go idle, but we gave it a chance
                    await asyncio.sleep(interaction_delay)

        except Exception as e:
            # Gracefully handle page closure errors instead of treating as failures
            error_msg = str(e)
            if any(msg in error_msg for msg in ["Target closed", "context has been closed", "Execution context was destroyed", "browser has been closed", "Page.evaluate"]):
                self.logger.debug(f"Interaction stopped (page closed): {error_msg}")
            else:
                self.logger.warning(f"⚠️  Interaction triggers failed: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup HTTP session and Playwright resources - thread-safe with lock"""
        async with self._browser_lock:
            # Close HTTP session first
            if self.session:
                try:
                    await self.session.close()
                    self.logger.info("HTTP Session closed successfully")
                except Exception as e:
                    self.logger.warning(f"HTTP session cleanup error: {e}")
            
            if self.connector:
                try:
                    await self.connector.close()
                    self.logger.debug("TCP Connector closed successfully")
                except Exception as e:
                    self.logger.debug(f"Connector cleanup error: {e}")
            
            # Then close Playwright
            if self.browser_manager:
                try:
                    await self.browser_manager.close()
                    self.logger.info("Browser manager closed successfully")
                except Exception as e:
                    self.logger.warning(f"Browser manager cleanup error: {e}")
            
            if self.playwright:
                try:
                    await self.playwright.stop()
                    self.logger.info("Playwright stopped successfully")
                except Exception as e:
                    self.logger.warning(f"Playwright cleanup error: {e}")
    
    async def fetch_live(self, target: str) -> List[str]:
        """Fetch JavaScript URLs from live site using Playwright with smart retries"""
        max_retries = 4  # Increased for timeout scenarios
        retry_delay = 2
        is_dns_error = False
        is_connection_error = False

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    self.logger.info(f"🔄 Retry attempt {attempt + 1}/{max_retries} for {target}")
                    await asyncio.sleep(retry_delay * attempt)

                result = await self._fetch_live_attempt(target)
                return result

            except Exception as e:
                error_msg = str(e)
                
                # Categorize error type for smart retry
                is_timeout = "Timeout" in error_msg or "timeout" in error_msg.lower()
                is_dns_error = "net::ERR_NAME_NOT_RESOLVED" in error_msg
                is_connection_error = "net::ERR_CONNECTION_REFUSED" in error_msg
                is_ssl_error = "net::ERR_CERT" in error_msg or "SSL" in error_msg
                is_browser_crash = any(x in error_msg for x in [
                    "Target closed", "Protocol error", "browser has been closed",
                    "context has been closed", "page has been closed"
                ])

                # Track errors
                if is_dns_error:
                    self.error_stats['dns_errors'] += 1
                elif is_connection_error:
                    self.error_stats['connection_refused'] += 1
                elif is_ssl_error:
                    self.error_stats['ssl_errors'] += 1
                elif is_timeout:
                    self.error_stats['timeouts'] += 1

                # Smart retry logic: DNS errors get 1 retry, timeouts get full retries
                should_retry = False
                if is_browser_crash and attempt < max_retries - 1:
                    should_retry = True
                elif is_timeout and attempt < max_retries - 1:
                    should_retry = True  # Retry timeouts multiple times
                elif (is_dns_error or is_connection_error or is_ssl_error) and attempt == 0:
                    should_retry = True  # Only 1 retry for permanent errors

                if should_retry:
                    if is_browser_crash:
                        self.logger.warning(f"⚠️  Browser crashed (attempt {attempt + 1}/{max_retries}): {error_msg[:100]}")
                        self.logger.info(f"🔄 Restarting browser and retrying...")
                        try:
                            if self.browser_manager and self.browser_manager.browser:
                                await self.browser_manager.browser.close()
                                self.browser_manager.browser = None
                        except:
                            pass
                    continue
                else:
                    # Final failure - log categorized error
                    if "Download is starting" in error_msg or "download" in error_msg.lower():
                        self.logger.info(f"⚠️  URL triggers a download (not a page): {target}")
                        if target.endswith('.js') or target.endswith('.mjs') or '.js?' in target:
                            return [target]
                    elif is_dns_error:
                        self.logger.warning(f"[DNS ERROR] Could not resolve domain: {target}")
                    elif is_connection_error:
                        self.logger.warning(f"[CONNECTION REFUSED] Server rejected connection: {target}")
                    elif is_ssl_error:
                        self.logger.warning(f"[SSL ERROR] Certificate validation failed: {target}")
                    elif "net::ERR_ABORTED" in error_msg:
                        self.logger.info(f"⚠️  Navigation aborted (redirect or client-side routing): {target}")
                    elif is_timeout:
                        self.logger.warning(f"[TIMEOUT] Page load timeout for {target}")
                    else:
                        self.logger.warning(f"[ERROR] Live scan failed for {target}: {error_msg[:150]}")

                    return []

        return []
    
    async def _fetch_live_attempt(self, target: str) -> List[str]:
        """Single attempt to fetch JavaScript URLs from live site"""
        self.logger.info(f"🌐 Launching browser to scan live site: {target}")

        if not target.startswith('http'):
            target = f'https://{target}'

        js_urls = set()
        lazy_loaded_urls = set()
        context = None
        page = None

        try:
            self.logger.info(f"Opening page in headless browser...")
            await self.browser_manager._ensure_browser()

            context = await self.browser_manager.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=self._get_random_user_agent(),  # Rotate user agents
                ignore_https_errors=True,
                java_script_enabled=True,
                bypass_csp=True
            )

            page = await context.new_page()
            page.set_default_timeout(60000)

            request_start_time = time.time()

            async def handle_request(request):
                url = request.url
                resource_type = request.resource_type

                if not self._is_in_scope(url, target):
                    return

                if not url.startswith(('http://', 'https://')):
                    return

                if ' ' in url or any(ord(c) < 32 or ord(c) > 126 for c in url[:100]):
                    self.logger.debug(f"Skipping malformed URL: {url[:100]}")
                    return

                request_time = time.time() - request_start_time

                if resource_type == 'script':
                    js_urls.add(url)
                    if request_time > 2.0:
                        lazy_loaded_urls.add(url)
                        self.logger.info(f"🎯 Lazy-loaded: {url}")
                    else:
                        self.logger.info(f"✓ Found JS: {url}")
                elif '.js' in url.lower():
                    parsed = urlparse(url)
                    if parsed.path.endswith('.js') or parsed.path.endswith('.mjs') or '.js?' in url.lower():
                        js_urls.add(url)
                        if request_time > 2.0:
                            lazy_loaded_urls.add(url)
                            self.logger.info(f"🎯 Lazy-loaded: {url}")
                        else:
                            self.logger.info(f"✓ Found JS: {url}")

            page.on('request', handle_request)

            self.logger.info(f"Navigating to {target}...")
            try:
                await page.goto(target, wait_until='domcontentloaded', timeout=30000)
                self.logger.info(f"Page loaded, waiting for dynamic content...")
            except Exception as e:
                if 'Timeout' in str(e) or 'timeout' in str(e).lower():
                    self.logger.warning(f"⚠️  Navigation timeout, but may have discovered JS files: {len(js_urls)} found")
                    if js_urls:
                        self.logger.info(f"🎯 Returning {len(js_urls)} JS files discovered before timeout")
                        return list(js_urls)
                    return []
                else:
                    raise

            self.logger.info(f"🖱️  Triggering interactions for lazy-loaded content...")
            await self._smart_interactions(page)

            # Add timeout protection for DOM operations to prevent infinite hangs
            try:
                scripts = await asyncio.wait_for(
                    page.query_selector_all('script[src]'),
                    timeout=10
                )
                for script in scripts:
                    src = await asyncio.wait_for(script.get_attribute('src'), timeout=5)
                    if src:
                        absolute_url = urljoin(target, src)
                        if '.js' in absolute_url.lower():
                            js_urls.add(absolute_url)
                            self.logger.debug(f"Found JS (DOM): {absolute_url}")
            except asyncio.TimeoutError:
                self.logger.warning(f"⚠️  Timeout querying script[src] tags, continuing with discovered files")
            except Exception as e:
                self.logger.debug(f"Error querying script tags: {e}")

            # FIX: Stricter regex for inline scripts with timeout protection
            try:
                inline_scripts = await asyncio.wait_for(
                    page.query_selector_all('script:not([src])'),
                    timeout=10
                )
                for script in inline_scripts:
                    try:
                        content = await asyncio.wait_for(script.inner_text(), timeout=5)
                        
                        # SAFETY FIX: Skip if content is too massive (e.g. data blobs)
                        if len(content) > 100000:  # 100KB limit for inline scripts
                            continue
                        
                        import re
                        # FIX: Enforce valid URL characters for JS files (added . to character class)
                        urls_in_script = re.findall(r'["\']([a-zA-Z0-9_\-:/.]+\.js(?:[\?#][^"\']*)?)["\']', content)
                        
                        for url in urls_in_script:
                            absolute_url = urljoin(target, url)
                            js_urls.add(absolute_url)
                    except:
                        pass
            except asyncio.TimeoutError:
                self.logger.warning(f"⚠️  Timeout querying inline script tags, continuing with discovered files")
            except Exception as e:
                self.logger.debug(f"Error querying inline scripts: {e}")

        except asyncio.TimeoutError:
            self.logger.warning(f"[TIMEOUT] Live scan timed out after {self.page_timeout/1000}s for {target}")
            raise
        except Exception as e:
            raise
        finally:
            try:
                if page:
                    await page.close()
            except Exception:
                pass

            try:
                if context:
                    await context.close()
            except Exception:
                pass

        js_urls = list(js_urls)

        self.logger.info(f"🎯 Live scan complete: Found {len(js_urls)} JavaScript files")

        if lazy_loaded_urls:
            self.logger.info(f"   ├─ Initial load: {len(js_urls) - len(lazy_loaded_urls)} files")
            self.logger.info(f"   └─ Lazy-loaded: {len(lazy_loaded_urls)} files")
        return js_urls
    
    async def fetch_content(self, url: str, retry_count: int = 0) -> Optional[str]:
        """
        Fetches the content of a JavaScript file with automatic retry on transient failures.
        
        Retries on:
        - Network timeouts (asyncio.TimeoutError)
        - Connection errors (aiohttp.ClientError)
        - DNS resolution failures
        
        Does NOT retry on:
        - Rate limiting (429, 503) - to avoid API bans
        - Client errors (4xx) - won't be fixed by retry
        """
        # Pre-flight noise filter check (no network call)
        should_skip, reason = self.noise_filter.should_skip_url(url)
        if should_skip:
            self.logger.debug(f"⏭️  Filtered (noise): {url} - {reason}")
            self.last_failure_reason = 'filtered_noise'
            return None

        self.last_failure_reason = None
        
        # Get retry config from global config
        retry_config = self.config.get('retry', {})
        max_attempts = retry_config.get('http_requests', 3)
        backoff_base = retry_config.get('backoff_base', 1.0)
        
        # Define retry exceptions (network-related only)
        retry_exceptions = (
            asyncio.TimeoutError,
            aiohttp.ClientError,
            aiohttp.ServerTimeoutError,
            aiohttp.ClientConnectorError,
            ConnectionError,
        )
        
        # Wrap the actual fetch logic with retry decorator
        @retry_async(
            max_attempts=max_attempts,
            backoff_base=backoff_base,
            retry_on=retry_exceptions,
            operation_name=f"fetch({url[:50]}...)"
        )
        async def _do_fetch():
            return await self._fetch_content_impl(url)
        
        try:
            return await _do_fetch()
        except retry_exceptions:
            # All retries exhausted
            self.logger.debug(f"❌ [RETRY EXHAUSTED] {url}")
            self.last_failure_reason = 'retry_exhausted'
            return None
        except Exception as e:
            # Non-retryable error
            self.logger.error(f"❌ [NON-RETRYABLE ERROR] {url}: {e}")
            self.last_failure_reason = 'non_retryable_error'
            return None
    
    async def _fetch_content_impl(self, url: str) -> Optional[str]:
        """
        Internal implementation of fetch_content (separated for retry logic).
        This method may raise exceptions that trigger retries.
        Uses the SHARED session to prevent connection exhaustion.
        """
        if not self.session:
            raise RuntimeError("Fetcher not initialized! Call initialize() first.")
        
        max_size = self.config.get('max_file_size', 10485760)
        # Rotate User-Agent for stealth
        headers = {
            'User-Agent': self._get_random_user_agent()
        }
        
        # Use the shared session - this is the key fix for connection pooling
        async with self.session.get(url, ssl=self.ssl_context, headers=headers, allow_redirects=False) as response:
                # No retries - fail immediately on rate limiting (return None, not exception)
                if response.status in [429, 503]:
                    self.logger.debug(f"[RATE LIMITED] {url} (status {response.status})")
                    self.last_failure_reason = 'rate_limit'
                    self.error_stats['rate_limits'] += 1
                    return None


                if response.status == 200:
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > max_size:
                        self.logger.warning(
                            f"❌ File too large: {url} ({int(content_length) / 1024 / 1024:.2f} MB)"
                        )
                        self.last_failure_reason = 'too_large'
                        return None

                    chunks = []
                    total_size = 0

                    async for chunk in response.content.iter_chunked(8192):
                        total_size += len(chunk)
                        if total_size > max_size:
                            self.logger.warning(
                                f"❌ File exceeded size during download: {url}"
                            )
                            self.last_failure_reason = 'too_large'
                            return None
                        chunks.append(chunk)

                    content = b''.join(chunks).decode('utf-8', errors='ignore')

                    should_skip, reason = self.noise_filter.should_skip_content(content, url)
                    if should_skip:
                        self.logger.debug(f"⏭️  Filtered (known lib): {url} - {reason}")
                        self.last_failure_reason = 'filtered_known_library'
                        return None

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

                    if not content or len(content.strip()) < 50:
                        if self.verbose:
                            self.logger.warning(f"❌ Content too short: {url}")
                        else:
                            self.logger.debug(f"Filtered short content: {url}")
                        self.last_failure_reason = 'too_short'
                        return None

                    return content
                else:
                    if self.verbose:
                        self.logger.warning(f"❌ HTTP {response.status}: {url}")
                    else:
                        self.logger.debug(f"HTTP {response.status}: {url}")
                    self.last_failure_reason = 'http_error'
                    self.error_stats['http_errors'] += 1
                    return None
    
    async def fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetches content using Playwright"""
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

        except Exception as e:
            self.logger.error(f"Playwright error {url}: {e}")
            return None
        finally:
            if page:
                await page.close()
            if context:
                await context.close()
