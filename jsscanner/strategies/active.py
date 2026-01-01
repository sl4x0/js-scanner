"""
Fetcher Module
Handles fetching JavaScript files from live sites using Playwright
"""
import asyncio
import time
import socket
import random
from curl_cffi.requests import AsyncSession
from playwright.async_api import async_playwright, Browser, BrowserContext
from typing import List, Optional, Tuple
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re
from ..analysis.filtering import NoiseFilter
from ..utils.net import retry_async, RETRY_CONFIG_HTTP


class IncompleteDownloadError(Exception):
    """Raised when a download completes but Content-Length doesn't match received bytes"""
    pass


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
                    try:
                        await asyncio.wait_for(self.browser.close(), timeout=5.0)
                    except asyncio.TimeoutError:
                        if self.logger:
                            self.logger.warning("⚠️  Browser.close() timed out during restart")
                    except Exception as e:
                        if self.logger:
                            self.logger.debug(f"Browser.close() error during restart: {e}")
                    finally:
                        # Ensure reference cleared so a fresh browser is launched
                        self.browser = None
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
                # Suppress TargetClosedError during shutdown (Ctrl+C)
                if page:
                    try:
                        await page.close()
                    except Exception as e:
                        # Suppress "Target closed" errors during forced shutdown
                        if 'Target' not in str(e) and 'closed' not in str(e).lower():
                            raise
                if context:
                    try:
                        await context.close()
                    except Exception as e:
                        # Suppress "Target closed" errors during forced shutdown
                        if 'Target' not in str(e) and 'closed' not in str(e).lower():
                            raise

            return js_urls
    
    async def close(self):
        """Close browser - suppress TargetClosedError during shutdown"""
        if self.browser:
            try:
                try:
                    await asyncio.wait_for(self.browser.close(), timeout=5.0)
                except asyncio.TimeoutError:
                    if self.logger:
                        self.logger.warning("⚠️  Browser.close() timed out during shutdown")
                finally:
                    self.browser = None
            except Exception as e:
                # Suppress "Target closed" errors during forced shutdown (Ctrl+C)
                if 'Target' not in str(e) and 'closed' not in str(e).lower():
                    # Re-raise unexpected errors
                    raise


class ActiveFetcher:
    """
    Fetches JavaScript files from various sources
    """

    def __init__(self, config: dict, logger, state=None) -> None:
        """
        Initialize fetcher

        Args:
            config: Configuration dictionary
            logger: Logger instance
            state: State manager instance (optional)
        """
        self.config = config
        self.logger = logger
        self.state = state
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
        
        # 🔍 DIAGNOSTIC: Track HTTP status codes for debugging
        self.http_status_breakdown = {}

        # Initialize noise filter
        self.noise_filter = NoiseFilter(logger=logger)
        
        # Session Inheritance: Store valid cookies from Playwright for curl_cffi
        self.valid_cookies = {}  # Will be populated during live browser scan
        self.target_domain = None  # Track the domain for Referer header

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
        
        # Session will be initialized in initialize() method
        self.session = None  # Legacy - kept for compatibility
        self.session_pool = []  # Pool of sessions for load distribution
        self.session_counter = 0  # Round-robin counter for session selection
        self.download_counter = 0  # Track downloads for rotation
        self.ssl_verify = config.get('verify_ssl', False)
        
        # Session management configuration
        session_config = config.get('session_management', {})
        self.session_pool_size = session_config.get('pool_size', 3)
        self.rotate_after = session_config.get('rotate_after', 150)
        # Honor configured download timeout; default to 30s for stability with slow domains
        self.download_timeout = config.get('session_management', {}).get('download_timeout', 30)
        
        # Ensure retry config exists; allow user to set low retry counts (fail-fast)
        if 'retry' not in self.config:
            self.config['retry'] = {}
        if self.config['retry'].get('http_requests', 0) < 1:
            self.logger.warning("⚠️  Enforcing minimum retry count: http_requests = 1")
            self.config['retry']['http_requests'] = 1
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent to avoid WAF fingerprinting"""
        return random.choice(self.user_agents)
    
    def _is_in_scope(self, url: str, target: str) -> bool:
        """Check if URL is in scope (same root domain as target)"""
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
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"Domain validation error: {str(e)}")
            self.logger.debug("Full validation error traceback:", exc_info=True)
            return False, f"Validation error: {str(e)}"
    
    async def initialize(self) -> None:
        """Initialize HTTP session pool and Playwright browser"""
        # 1. Initialize curl_cffi session pool with Chrome TLS fingerprint for WAF bypass
        timeout_val = self.config.get('timeouts', {}).get('http_request', 15)
        
        # Create session pool for load distribution and resilience
        self.logger.info(f"Creating session pool with {self.session_pool_size} sessions...")
        for i in range(self.session_pool_size):
            session = AsyncSession(
                impersonate="chrome120",  # Mimics Chrome 120 TLS fingerprint
                timeout=timeout_val,
                verify=self.ssl_verify,
                http_version="1.1"  # Force HTTP/1.1 for maximum speed (HTTP/2 has protocol overhead)
            )
            self.session_pool.append(session)
        
        # Set primary session for backward compatibility
        self.session = self.session_pool[0]
        self.logger.info(f"✅ Stealth HTTP Session Pool initialized ({self.session_pool_size} sessions with Chrome 120 fingerprint)")
        
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

    async def _preflight_check(self, url: str) -> Tuple[bool, str, Optional[int]]:
        """
        Fast pre-flight HEAD request to reject large or invalid files quickly.
        Returns (should_download, reason, content_length_or_none)
        """
        # Check if domain is known problematic
        if self.state and self.state.problematic_domains_enabled:
            domain = urlparse(url).netloc
            if self.state.is_problematic_domain(domain):
                self.logger.debug(f"⏭️  Skipping known problematic domain: {domain}")
                return False, 'problematic_domain', None

        try:
            session = self._get_session()

            # HEAD request with retry on timeout
            @retry_async(
                max_attempts=2,
                backoff_base=0.3,  # Increased from 0.1s to give slow servers more time
                backoff_multiplier=2.0,  # Increased from 1.5 for better backoff
                retry_on=(asyncio.TimeoutError,),
                operation_name=f"head_check({url[:50]}...)"
            )
            async def _do_head():
                return await asyncio.wait_for(
                    session.head(url, allow_redirects=True),
                    timeout=5.0  # Increased from 3.0s to handle slow domains
                )

            try:
                resp = await _do_head()
            except asyncio.TimeoutError:
                # After retries, allow download with full timeout as fallback
                self.logger.debug(f"HEAD timeout after retries, allowing GET fallback: {url[:80]}")
                # Mark domain as potentially problematic for future
                if self.state:
                    domain = urlparse(url).netloc
                    self.state.mark_domain_problematic(domain)
                return True, 'head_timeout_fallback', None

            # Check HTTP status
            status = getattr(resp, 'status_code', None)
            if status is None or status >= 400:
                return False, f'http_{status}', None

            # Content-Length check
            content_length = None
            cl = resp.headers.get('Content-Length') if getattr(resp, 'headers', None) else None
            if cl:
                try:
                    content_length = int(cl)
                except Exception:
                    content_length = None

                if content_length:
                    size_mb = content_length / (1024 * 1024)
                    # Hard reject very large files (vendor bundles)
                    if size_mb > self.config.get('max_file_size_mb_reject', 5.0):
                        self.logger.info(f"⏭️  Skipping large file: {url[:80]} ({size_mb:.1f}MB)")
                        return False, f'too_large_{size_mb:.1f}MB', content_length
                    if size_mb > 2.0:
                        self.logger.warning(f"⚠️  Large file detected: {url[:80]} ({size_mb:.1f}MB) - may be vendor code")

            # Content-Type validation
            ctype = resp.headers.get('Content-Type', '').lower() if getattr(resp, 'headers', None) else ''
            valid_types = ['javascript', 'ecmascript', 'text/plain', 'application/json']
            if ctype and not any(t in ctype for t in valid_types):
                return False, f'invalid_content_type_{ctype}', content_length

            return True, 'ok', content_length

        except Exception as e:
            # Preflight should never block download on unexpected errors - allow fallback
            self.logger.debug(f"Preflight check error: {e}")
            return True, 'preflight_error', None
    
    def _get_session(self) -> AsyncSession:
        """Get next session from pool using round-robin selection"""
        if not self.session_pool:
            raise RuntimeError("Session pool not initialized!")
        
        session = self.session_pool[self.session_counter % len(self.session_pool)]
        self.session_counter += 1
        return session
    
    async def _rotate_session(self, session_index: int) -> None:
        """Rotate a specific session in the pool to prevent staleness"""
        try:
            timeout_val = self.config.get('timeouts', {}).get('http_request', 15)
            old_session = self.session_pool[session_index]
            
            # Close old session
            try:
                await asyncio.wait_for(old_session.close(), timeout=2.0)
            except Exception as e:
                self.logger.debug(f"Error closing old session: {str(e)}")
            
            # Create new session with same config
            new_session = AsyncSession(
                impersonate="chrome120",
                timeout=timeout_val,
                verify=self.ssl_verify,
                http_version="1.1"  # Force HTTP/1.1 for maximum speed
            )
            
            self.session_pool[session_index] = new_session
            
            # Update primary session if rotating first one
            if session_index == 0:
                self.session = new_session
            
            self.logger.debug(f"✅ Rotated session {session_index} (downloads: {self.download_counter})")
        except Exception as e:
            self.logger.error(f"Failed to rotate session {session_index}: {str(e)}")
    
    async def _smart_interactions(self, page) -> None:
        """Trigger lazy loaders through smart interactions"""
        try:
            # Respect config toggle to disable interactions on unstable SPAs
            if not self.config.get('playwright', {}).get('enable_interactions', True):
                self.logger.debug("Playwright interactions disabled by config")
                return

            # Check if page is closed before starting
            if page.is_closed():
                self.logger.debug("⚠️  Page already closed, skipping interactions")
                return

            # 1. Progressive scroll
            self.logger.debug("🖱️  Progressive scrolling to trigger lazy content...")
            try:
                # Use bounded timeout for evaluate to avoid hangs
                await asyncio.wait_for(page.evaluate("""
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
                """), timeout=2.0)
            except asyncio.TimeoutError:
                self.logger.debug("⚠️  Scroll interaction timed out, continuing...")
            except Exception as e:
                # Gracefully handle page closure during scroll
                if any(msg in str(e) for msg in ["Target closed", "browser has been closed", "Page.evaluate"]):
                    self.logger.debug("⚠️  Page closed during scroll interaction, continuing...")
                    return
                raise

            # 2. Hover on interactive elements
            self.logger.debug("🖱️  Hovering on interactive elements...")
            try:
                await asyncio.wait_for(page.evaluate("""
                    () => {
                        const selectors = [
                            '[data-tooltip]',
                            '[data-popover]',
                            '[aria-haspopup]',
                            '.dropdown-toggle',
                            '[role="button"]',
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
                """), timeout=2.0)
            except asyncio.TimeoutError:
                self.logger.debug("⚠️  Hover interaction timed out, continuing...")
            except Exception as e:
                # Gracefully handle page closure during hover
                if any(msg in str(e) for msg in ["Target closed", "browser has been closed", "Page.evaluate"]):
                    self.logger.debug("⚠️  Page closed during hover interaction, continuing...")
                    return
                raise

            # 3. Trigger tab switches
            self.logger.debug("🖱️  Activating tabs...")
            try:
                await asyncio.wait_for(page.evaluate("""
                    () => {
                        document.querySelectorAll('[role="tab"]').forEach((tab, i) => {
                            try {
                                setTimeout(() => {
                                    tab.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                                }, i * 100);
                            } catch(e) {
                                // Ignore errors
                            }
                        });
                    }
                """), timeout=2.0)
            except asyncio.TimeoutError:
                self.logger.debug("⚠️  Tab-activation interaction timed out, continuing...")
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
                # Traceback Pattern: Clean console + forensic log
                self.logger.error(f"⚠️  Interaction triggers failed: {str(e)}")
                self.logger.debug("Full interaction failure traceback:", exc_info=True)
    
    async def cleanup(self) -> None:
        """Cleanup HTTP session pool and Playwright resources - thread-safe with lock"""
        async with self._browser_lock:
            # Close all sessions in the pool
            if self.session_pool:
                for i, session in enumerate(self.session_pool):
                    if session and not getattr(session, 'closed', False):
                        try:
                            loop = asyncio.get_event_loop()
                            if not loop.is_closed():
                                await asyncio.wait_for(session.close(), timeout=2.0)
                        except asyncio.TimeoutError:
                            self.logger.debug(f"Session {i} close timeout (acceptable during shutdown)")
                        except RuntimeError as e:
                            if 'Event loop is closed' not in str(e):
                                self.logger.debug(f"Session {i} cleanup error: {str(e)}")
                        except Exception as e:
                            self.logger.debug(f"Session {i} cleanup error: {str(e)}")
                
                self.logger.info(f"HTTP Session pool closed successfully ({len(self.session_pool)} sessions)")
                self.session_pool = []
                self.session = None
            
            # Then close Playwright with proper waiting
            if self.browser_manager:
                try:
                    try:
                        await asyncio.wait_for(self.browser_manager.close(), timeout=5.0)
                    except asyncio.TimeoutError:
                        self.logger.warning("⚠️  BrowserManager.close() timed out during cleanup")
                    self.logger.info("Browser manager closed successfully")
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"❌ Browser manager cleanup error: {str(e)}")
                    self.logger.debug("Full browser manager cleanup traceback:", exc_info=True)
            
            if self.playwright:
                try:
                    try:
                        await asyncio.wait_for(self.playwright.stop(), timeout=5.0)
                    except asyncio.TimeoutError:
                        self.logger.warning("⚠️  Playwright.stop() timed out during cleanup")

                    # Give playwright time to terminate processes
                    await asyncio.sleep(0.5)
                    self.logger.info("Playwright stopped successfully")
                except Exception as e:
                    # Traceback Pattern: Clean console + forensic log
                    self.logger.error(f"❌ Playwright cleanup error: {str(e)}")
                    self.logger.debug("Full playwright cleanup traceback:", exc_info=True)
    
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

                # Strict validation: MUST have .js extension or be resource_type='script' with .js
                parsed = urlparse(url)
                path = parsed.path.lower()
                query = parsed.query.lower()
                
                # Valid JS files must have .js somewhere meaningful
                is_valid_js = (
                    path.endswith('.js') or 
                    path.endswith('.mjs') or
                    '.js?' in url.lower() or
                    (resource_type == 'script' and ('.js' in path or '.js' in query))
                )
                
                if not is_valid_js:
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
                    if path.endswith('.js') or path.endswith('.mjs') or '.js?' in url.lower():
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
                
                # 🍪 SESSION INHERITANCE: Extract cookies after Cloudflare challenge is solved
                try:
                    cookies = await context.cookies()
                    self.valid_cookies = {c['name']: c['value'] for c in cookies}
                    # Store target domain for Referer header
                    parsed = urlparse(target)
                    self.target_domain = f"{parsed.scheme}://{parsed.netloc}"
                    
                    # Log cookie capture (useful for debugging Cloudflare bypass)
                    cf_cookies = [name for name in self.valid_cookies.keys() if 'cf' in name.lower()]
                    if cf_cookies:
                        self.logger.info(f"🍪 Captured {len(self.valid_cookies)} cookies (Cloudflare: {', '.join(cf_cookies)})")
                    else:
                        self.logger.debug(f"🍪 Captured {len(self.valid_cookies)} cookies from Playwright session")
                except Exception as cookie_error:
                    self.logger.debug(f"Cookie extraction error (non-critical): {cookie_error}")
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
        Fetches the content of a JavaScript file with PROGRESSIVE TIMEOUT on retries.
        
        CRITICAL FIX: Each retry attempt gets progressively longer timeout to handle
        VPS resource saturation. Base timeout increases by 50% per attempt:
        - Attempt 1: base_timeout (e.g., 45s)
        - Attempt 2: base_timeout * 1.5 (e.g., 67.5s)
        - Attempt 3: base_timeout * 2.0 (e.g., 90s)
        
        Retries on:
        - Network timeouts (asyncio.TimeoutError)
        - Connection errors (curl_cffi exceptions)
        - DNS resolution failures
        
        Does NOT retry on:
        - Rate limiting (429, 503) - to avoid API bans
        - Client errors (4xx) - won't be fixed by retry
        """
        # 🔍 DIAGNOSTIC: Log every fetch attempt in verbose mode
        verbose_mode = self.config.get('verbose', False)
        if verbose_mode:
            self.logger.info(f"📥 Fetch: {url[:80]}")
        
        # Pre-flight noise filter check (no network call)
        should_skip, reason = self.noise_filter.should_skip_url(url)
        if should_skip:
            if verbose_mode:
                self.logger.info(f"⏭️  Filtered (noise): {url[:80]} - {reason}")
            else:
                self.logger.debug(f"⏭️  Filtered (noise): {url} - {reason}")
            self.last_failure_reason = 'filtered_noise'
            return None

        self.last_failure_reason = None
        
        # Get retry config from global config
        retry_config = self.config.get('retry', {})
        max_attempts = retry_config.get('http_requests', 3)
        backoff_base = retry_config.get('backoff_base', 2.0)
        jitter_enabled = retry_config.get('jitter', True)
        
        # Define retry exceptions (network-related only)
        retry_exceptions = (
            asyncio.TimeoutError,
            ConnectionError,
            TimeoutError,
            OSError,
            IncompleteDownloadError,  # Retry on incomplete downloads
        )
        
        # Get base timeout from config
        base_timeout = self.download_timeout if self.download_timeout is not None else self.config.get('session_management', {}).get('download_timeout', 45)
        
        # MANUAL RETRY LOOP with PROGRESSIVE TIMEOUT (boss's recommended approach)
        last_exception = None
        for attempt in range(max_attempts):
            try:
                # CRITICAL: Increase timeout by 50% on each retry
                # This solves the VPS saturation problem where requests queue locally
                current_timeout = base_timeout * (1 + (0.5 * attempt))
                
                if attempt > 0:
                    # Log retry with new timeout
                    self.logger.warning(
                        f"⚠ Retry {attempt + 1}/{max_attempts} for {url[:50]}... "
                        f"(timeout increased to {current_timeout:.1f}s)"
                    )
                
                # Try to fetch with progressive timeout
                result = await self._fetch_content_impl(url, timeout_override=current_timeout)
                
                # Success!
                if attempt > 0:
                    self.logger.info(f"✓ {url[:50]}... succeeded on attempt {attempt + 1}/{max_attempts}")
                
                return result
                
            except retry_exceptions as e:
                last_exception = e
                
                # Check if we have more attempts left
                if attempt < max_attempts - 1:
                    # Calculate backoff delay with optional jitter
                    delay = backoff_base * (2.0 ** attempt)
                    if jitter_enabled:
                        import random
                        jitter_amount = delay * 0.2
                        delay += random.uniform(-jitter_amount, jitter_amount)
                    
                    delay = max(0.1, delay)  # Minimum 100ms
                    
                    self.logger.warning(
                        f"⚠ {url[:50]}... failed (attempt {attempt + 1}/{max_attempts}): {str(e)[:100]} "
                        f"- retrying in {delay:.1f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    self.logger.error(
                        f"✗ {url[:50]}... failed after {max_attempts} attempts: {str(e)[:200]}"
                    )
            
            except Exception as e:
                # Non-retryable error - fail immediately
                if verbose_mode:
                    self.logger.error(f"❌ [NON-RETRYABLE ERROR] {url[:80]}: {str(e)[:50]}")
                else:
                    self.logger.error(f"❌ [NON-RETRYABLE ERROR] {url}: {str(e)}")
                self.logger.debug("Full fetch error traceback:", exc_info=True)
                self.last_failure_reason = 'non_retryable_error'
                self.error_stats['http_errors'] += 1
                return None
        
        # All retry attempts exhausted - categorize the final error
        if isinstance(last_exception, asyncio.TimeoutError):
            if verbose_mode:
                self.logger.warning(f"❌ [TIMEOUT] {url[:80]}")
            else:
                self.logger.debug(f"❌ [TIMEOUT] {url}")
            self.last_failure_reason = 'timeout'
            self.error_stats['timeouts'] += 1
            return None
        elif isinstance(last_exception, (ConnectionError, OSError)):
            if verbose_mode:
                self.logger.warning(f"❌ [NETWORK ERROR] {url[:80]}: {str(last_exception)[:50]}")
            else:
                self.logger.debug(f"❌ [NETWORK ERROR] {url}: {str(last_exception)}")
            self.last_failure_reason = 'network_error'
            
            # Classify the specific network error
            error_str = str(last_exception)
            if 'Name or service not known' in error_str or 'getaddrinfo failed' in error_str:
                self.error_stats['dns_errors'] += 1
            elif 'Connection refused' in error_str:
                self.error_stats['connection_refused'] += 1
            elif 'SSL' in error_str or 'certificate' in error_str.lower():
                self.error_stats['ssl_errors'] += 1
            else:
                self.error_stats['timeouts'] += 1  # Generic network failure
            return None
        else:
            # Unknown retry exception
            self.last_failure_reason = 'unknown_retry_error'
            self.error_stats['http_errors'] += 1
            return None
    
    async def _fetch_content_impl(self, url: str, timeout_override: Optional[float] = None) -> Optional[str]:
        """
        Internal implementation of fetch_content (separated for retry logic).
        This method may raise exceptions that trigger retries.
        Uses the SHARED session to prevent connection exhaustion.
        
        Args:
            url: URL to fetch
            timeout_override: If provided, overrides calculated timeout (used for progressive timeouts)
        """
        if not self.session_pool:
            raise RuntimeError("Fetcher not initialized! Call initialize() first.")
        
        max_size = self.config.get('max_file_size', 10485760)
        
        # Preflight check to reject vendor/huge files quickly
        should_download, reason, preflight_content_length = await self._preflight_check(url)
        if not should_download:
            self.logger.debug(f"⏭️  Preflight rejected: {url} - {reason}")
            self.last_failure_reason = f'preflight_{reason}'
            return None

        # Get session from pool using round-robin
        session = self._get_session()
        
        # Increment download counter and check for rotation
        self.download_counter += 1
        if self.download_counter % self.rotate_after == 0:
            # Rotate the session that was just used
            session_index = (self.session_counter - 1) % len(self.session_pool)
            await self._rotate_session(session_index)
        
        # 🛡️ SESSION INHERITANCE: Build headers with Referer to bypass hotlink protection
        parsed_url = urlparse(url)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # More realistic browser headers to bypass 403 (anti-bot) protection
        # Key changes: Remove Sec-Fetch headers (bot detection), add realistic Accept header
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/javascript, */*;q=0.8',  # More specific than '*/*'
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',  # Browsers send this
            'Pragma': 'no-cache',  # Legacy but many servers expect it
            # Removed Sec-Fetch-* headers - bot fingerprints that trigger 403
        }
        
        # Add Referer and Origin if we have a target domain (from browser scan)
        if self.target_domain:
            headers['Referer'] = self.target_domain
            headers['Origin'] = self.target_domain
        else:
            # Fallback: use the URL's origin as Referer
            headers['Referer'] = origin
        
        # 🍪 Use curl_cffi with inherited cookies from Playwright (Cloudflare bypass)
        # Apply download_timeout for large file downloads - progressive based on preflight
        # PERFORMANCE: Follow redirects automatically (301/302/308) to avoid treating them as errors
        
        # PROGRESSIVE TIMEOUT LOGIC: Use override if provided (for retry attempts)
        if timeout_override is not None:
            download_timeout = timeout_override
            self.logger.debug(f"Using override timeout: {download_timeout:.1f}s for {url[:80]}")
        else:
            # Determine progressive timeout (prioritize configured `self.download_timeout`)
            download_timeout = self.download_timeout if self.download_timeout is not None else self.config.get('session_management', {}).get('download_timeout', 45)
            
            # Domain-specific timeout handling for known slow domains
            slow_domains = ['getsentry.net', 'guildwars2.com', 'seagroup.com', 'garena.vn', 
                           'garenanow.com', 'freefiremobile.com', 'watsonsestore.com.cn', 'watsons.com']
            
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                is_slow_domain = any(slow_dom in domain for slow_dom in slow_domains)
                
                if is_slow_domain:
                    # Slow domains get 2x timeout multiplier
                    download_timeout = download_timeout * 2
                    self.logger.debug(f"Slow domain detected ({domain}): doubling timeout to {download_timeout}s")
            except Exception:
                pass
            
            # Progressive timeout based on file size - more lenient for slow domains
            if preflight_content_length:
                try:
                    size_mb = int(preflight_content_length) / (1024 * 1024)
                except Exception:
                    size_mb = 0

                if size_mb < 0.5:
                    download_timeout = max(30, download_timeout)  # Small files: min 30s
                elif size_mb < 2.0:
                    download_timeout = max(60, download_timeout)  # Medium files: min 60s
                else:
                    download_timeout = max(120, download_timeout)  # Large files: min 120s
            else:
                # No content-length header - use generous timeout for unknown sizes
                download_timeout = max(45, download_timeout)

            self.logger.debug(f"Download timeout: {download_timeout}s for {url}")

        try:
            response = await asyncio.wait_for(
                session.get(
                    url,
                    headers=headers,
                    cookies=self.valid_cookies if self.valid_cookies else None,
                    allow_redirects=True,  # CRITICAL: Follow redirects for performance
                    max_redirects=5  # Reasonable limit to prevent redirect loops
                ),
                timeout=download_timeout
            )
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Download timeout after {download_timeout}s: {url}")
        
        try:
                # ========== PHASE 3: Strategic Error Detection (Vulnerability Hinting) ==========
                # Differentiate between "Network Failure" (Retry) and "Server Crash" (Vulnerability)
                
                # Server Error (Potential Vulnerability)
                if response.status_code >= 500:
                    # Use correct attribute name - avoid AttributeError
                    self.logger.warning(f"🔥 HTTP {response.status_code} at {url} - Potential Injection Point/DoS Vector")
                    self.last_failure_reason = 'server_error'
                    self.error_stats['http_errors'] += 1
                    return None
                
                # Auth Error (Interesting but not critical)
                if response.status_code in [401, 403]:
                    # 🔍 DIAGNOSTIC: Log HTTP 403/401 with details for troubleshooting
                    self.http_status_breakdown[response.status_code] = self.http_status_breakdown.get(response.status_code, 0) + 1
                    if self.verbose or response.status_code == 403:
                        self.logger.warning(f"🚫 HTTP {response.status_code} (Access Denied): {url[:80]}")
                        self.logger.debug(f"   Headers sent: {headers}")
                        self.logger.debug(f"   Cookies: {list(self.valid_cookies.keys()) if self.valid_cookies else 'None'}")
                    else:
                        self.logger.debug(f"🔒 Access Denied (HTTP {response.status_code}): {url}")
                    self.last_failure_reason = 'auth_error'
                    self.error_stats['http_errors'] += 1
                    return None
                
                # Rate Limiting (No retries - fail fast)
                if response.status_code in [429, 503]:
                    self.logger.debug(f"[RATE LIMITED] {url} (status {response.status_code})")
                    self.last_failure_reason = 'rate_limit'
                    self.error_stats['rate_limits'] += 1
                    return None
                
                # 🔍 DIAGNOSTIC: Handle 404 and other non-success status codes
                if response.status_code == 404:
                    self.http_status_breakdown[404] = self.http_status_breakdown.get(404, 0) + 1
                    if self.verbose:
                        self.logger.warning(f"📉 HTTP 404 (Not Found): {url[:80]}")
                    else:
                        self.logger.debug(f"📉 HTTP 404 (Not Found): {url[:80]}")
                    self.last_failure_reason = 'not_found'
                    self.error_stats['http_errors'] += 1
                    return None
                
                # Any other non-200 status
                if response.status_code != 200:
                    self.http_status_breakdown[response.status_code] = self.http_status_breakdown.get(response.status_code, 0) + 1
                    if self.verbose:
                        self.logger.warning(f"⚠️  HTTP {response.status_code}: {url[:80]}")
                    else:
                        self.logger.debug(f"HTTP {response.status_code}: {url[:80]}")
                    self.last_failure_reason = f'http_{response.status_code}'
                    self.error_stats['http_errors'] += 1
                    return None


                if response.status_code == 200:
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > max_size:
                        self.logger.warning(
                            f"❌ File too large: {url} ({int(content_length) / 1024 / 1024:.2f} MB)"
                        )
                        self.last_failure_reason = 'too_large'
                        return None

                    # Streaming download with Content-Length validation
                    # Fixes: curl error (18) "end of response with X bytes missing"
                    try:
                        # Check if response has content attribute for streaming
                        if hasattr(response, 'content') and hasattr(response.content, 'iter_chunked'):
                            # Stream the response in chunks
                            chunks = []
                            async for chunk in response.content.iter_chunked(8192):
                                chunks.append(chunk)
                            
                            content_bytes = b''.join(chunks)
                            
                            # Validate Content-Length if provided
                            # NOTE: Content-Length represents the compressed size if gzip is used
                            # We receive uncompressed data, so actual size may be larger
                            if content_length:
                                expected_size = int(content_length)
                                actual_size = len(content_bytes)
                                
                                # Only validate if we got LESS than expected (missing data)
                                # If we got MORE, it means the server used compression (this is normal)
                                if actual_size < expected_size:
                                    missing_bytes = expected_size - actual_size
                                    # Allow small discrepancies (chunking boundaries)
                                    if missing_bytes > 100:
                                        raise IncompleteDownloadError(
                                            f"Incomplete download: expected {expected_size} bytes, "
                                            f"got {actual_size} bytes ({missing_bytes} bytes missing)"
                                        )
                            
                            # Decode to string
                            content = content_bytes.decode('utf-8', errors='ignore')
                        else:
                            # Fallback to response.text if streaming not available
                            content = response.text
                            
                            # Validate size if Content-Length was provided
                            # NOTE: Content-Length may represent compressed size
                            if content_length:
                                expected_size = int(content_length)
                                actual_size = len(content.encode('utf-8'))
                                
                                # Only flag as error if we got significantly LESS than expected
                                if actual_size < expected_size:
                                    missing_bytes = expected_size - actual_size
                                    # Allow small discrepancies (compression, encoding differences)
                                    if missing_bytes > 100:  # More than 100 bytes difference
                                        raise IncompleteDownloadError(
                                            f"Incomplete download: expected {expected_size} bytes, "
                                            f"got {actual_size} bytes ({missing_bytes} bytes missing)"
                                        )
                    
                    except IncompleteDownloadError:
                        # Re-raise to trigger retry
                        raise
                    except Exception as e:
                        self.logger.warning(f"Streaming download error, falling back to text: {str(e)}")
                        content = response.text
                    
                    if len(content.encode('utf-8')) > max_size:
                        self.logger.warning(
                            f"❌ File exceeded size: {url}"
                        )
                        self.last_failure_reason = 'too_large'
                        return None

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
                        self.logger.warning(f"❌ HTTP {response.status_code}: {url}")
                    else:
                        self.logger.debug(f"HTTP {response.status_code}: {url}")
                    self.last_failure_reason = 'http_error'
                    self.error_stats['http_errors'] += 1
                    return None
        finally:
            # curl_cffi responses are auto-closed, but explicit is better
            pass
    
    async def validate_url_exists(self, url: str) -> Tuple[bool, int]:
        """
        Validate if URL exists using HEAD request (fast existence check for 2nd/3rd level JS)
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (exists: bool, status_code: int)
        """
        if not self.session:
            raise RuntimeError("Fetcher not initialized! Call initialize() first.")
        
        headers = {
            'User-Agent': self._get_random_user_agent()
        }
        
        try:
            response = await self.session.head(url, headers=headers, allow_redirects=True, timeout=10)
            exists = response.status_code == 200
            return (exists, response.status_code)
        except Exception as e:
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"HEAD request failed for {url}: {str(e)}")
            self.logger.debug("Full HEAD request traceback:", exc_info=True)
            return (False, 0)
    
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
            # Traceback Pattern: Clean console + forensic log
            self.logger.error(f"❌ Playwright error {url}: {str(e)}")
            self.logger.debug("Full Playwright fetch traceback:", exc_info=True)
            return None
        finally:
            if page:
                await page.close()
            if context:
                await context.close()

    async def fetch_and_write(self, url: str, out_path: str) -> bool:
        """
        Stream a remote resource directly to disk to avoid holding content in memory.

        Returns True on success, False on failure.
        """
        if not self.session_pool:
            raise RuntimeError("Fetcher not initialized! Call initialize() first.")

        # Skip preflight check for maximum speed if configured
        skip_preflight = self.config.get('download', {}).get('skip_preflight', False)
        preflight_content_length = None

        if not skip_preflight:
            # Preflight check
            should_download, reason, preflight_content_length = await self._preflight_check(url)
            if not should_download:
                self.logger.debug(f"⏭️  Preflight rejected: {url} - {reason}")
                self.last_failure_reason = f'preflight_{reason}'
                return False

        session = self._get_session()

        # Basic headers
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'application/javascript, */*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
        }
        if self.target_domain:
            headers['Referer'] = self.target_domain
        else:
            headers['Referer'] = origin

        try:
            response = await asyncio.wait_for(
                session.get(url, headers=headers, cookies=self.valid_cookies if self.valid_cookies else None, allow_redirects=True, max_redirects=5),
                timeout=self.download_timeout
            )
        except asyncio.TimeoutError:
            self.last_failure_reason = 'timeout'
            return False
        except Exception as e:
            self.last_failure_reason = 'network_error'
            return False

        # Handle non-200 statuses
        if response.status_code != 200:
            self.last_failure_reason = f'http_{response.status_code}'
            return False

        # Stream to disk
        try:
            # Open file in binary mode and write chunks
            with open(out_path, 'wb') as wf:
                if hasattr(response, 'content') and hasattr(response.content, 'iter_chunked'):
                    async for chunk in response.content.iter_chunked(8192):
                        if not chunk:
                            continue
                        wf.write(chunk)
                else:
                    # Fallback
                    wf.write(response.content or b'')

            # Basic size check
            if preflight_content_length:
                try:
                    expected = int(preflight_content_length)
                    actual = Path(out_path).stat().st_size
                    if actual < expected - 100:
                        self.last_failure_reason = 'incomplete'
                        return False
                except Exception:
                    pass

            return True
        except Exception as e:
            self.last_failure_reason = 'write_error'
            return False
