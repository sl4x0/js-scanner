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
    
    def __init__(self, playwright_instance, max_concurrent: int = 3, restart_after: int = 100, headless: bool = True):
        self.playwright = playwright_instance
        self.browser = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.page_count = 0
        self.restart_after = restart_after
        self.headless = headless
        self.lock = asyncio.Lock()
    
    async def _ensure_browser(self):
        """Ensures browser is running, restarts if needed"""
        async with self.lock:
            if self.browser is None or self.page_count >= self.restart_after:
                if self.browser:
                    await self.browser.close()
                    self.page_count = 0
                
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-dev-tools'
                    ]
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
                headless=self.headless
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
            'url': f'*.{clean_target}',
            'matchType': 'domain',
            'fl': 'original',
            'collapse': 'digest',
            'filter': 'statuscode:200',
            'limit': self.wayback_max_results
        }
        
        js_urls = set()  # Use set for automatic deduplication
        
        try:
            # Apply rate limiting
            await self.wayback_limiter.acquire()
            
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
                    else:
                        self.logger.warning(f"Wayback returned status {response.status}")
                        
        except asyncio.TimeoutError:
            self.logger.warning(f"Wayback request timed out after 120s")
        except Exception as e:
            self.logger.error(f"Error fetching from Wayback: {e}")
        
        # Filter to only target domain before returning
        filtered_urls = []
        for url in js_urls:
            if self._is_in_scope(url, target):
                filtered_urls.append(url)
            else:
                self.logger.debug(f"[WAYBACK] Filtered out-of-scope URL: {url}")
        
        if len(js_urls) > len(filtered_urls):
            self.logger.info(f"Filtered {len(js_urls) - len(filtered_urls)} out-of-scope URLs from Wayback")
        
        return filtered_urls
    
    async def fetch_live(self, target: str) -> List[str]:
        """
        Fetch JavaScript URLs from live site using Playwright
        Enhanced to detect scripts on modern SPAs
        
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
                bypass_csp=True
            )
            
            page = await context.new_page()
            # Increase timeout to 60 seconds for sites with anti-bot protection
            page.set_default_timeout(60000)
            
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
            
            # Navigate and wait longer for SPAs
            self.logger.info(f"Navigating to {target}...")
            await page.goto(target, wait_until='networkidle')
            self.logger.info(f"Page loaded, waiting for dynamic content...")
            
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
            return list(js_urls)  # Return what we found so far
        except Exception as e:
            error_msg = str(e)
            
            # Detect specific error types and provide helpful messages
            if "Download is starting" in error_msg or "download" in error_msg.lower():
                self.logger.info(f"⚠️  URL triggers a download (not a page): {target}")
                self.logger.info(f"   This is expected for API endpoints or direct file downloads")
                # If the URL itself looks like a JS file, we could try fetching it directly
                if target.endswith('.js') or target.endswith('.mjs') or '.js?' in target:
                    self.logger.info(f"   URL appears to be a JS file - it will be fetched directly later")
                    js_urls.add(target)
            elif "net::ERR_NAME_NOT_RESOLVED" in error_msg or "NS_ERROR_UNKNOWN_HOST" in error_msg:
                self.logger.warning(f"[DNS ERROR] Could not resolve domain: {target}")
            elif "net::ERR_CONNECTION_REFUSED" in error_msg or "ERR_CONNECTION_CLOSED" in error_msg:
                self.logger.warning(f"[CONNECTION REFUSED] Server rejected connection: {target}")
            elif "net::ERR_CERT" in error_msg or "SSL" in error_msg or "certificate" in error_msg.lower():
                self.logger.warning(f"[SSL ERROR] Certificate validation failed: {target}")
            elif "net::ERR_ABORTED" in error_msg:
                self.logger.info(f"⚠️  Navigation aborted (redirect or client-side routing): {target}")
            elif "Target closed" in error_msg or "Protocol error" in error_msg:
                self.logger.warning(f"[BROWSER ERROR] Browser/page closed unexpectedly: {target}")
            else:
                # Generic error for unexpected cases
                self.logger.warning(f"[ERROR] Live scan failed for {target}: {error_msg[:150]}")
            
            return list(js_urls)  # Return what we found so far
        finally:
            if page:
                await page.close()
            if context:
                await context.close()
        
        # Convert set to list (deduplication already done)
        js_urls = list(js_urls)
        
        self.logger.info(f"🎯 Live scan complete: Found {len(js_urls)} JavaScript files")
        
        return js_urls
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """
        Fetches the content of a JavaScript file
        Uses streaming to prevent loading large files into memory at once
        
        Args:
            url: URL of the JavaScript file
            
        Returns:
            Content of the file, or None if failed
        """
        max_size = self.config.get('max_file_size', 10485760)  # 10MB default
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        # Check content length header first
                        content_length = response.headers.get('Content-Length')
                        if content_length and int(content_length) > max_size:
                            self.logger.warning(
                                f"File too large: {url} ({int(content_length) / 1024 / 1024:.2f} MB, "
                                f"max: {max_size / 1024 / 1024:.2f} MB)"
                            )
                            return None
                        
                        # ✅ OPTIMIZATION: Stream and check size incrementally (prevents memory overflow)
                        chunks = []
                        total_size = 0
                        
                        async for chunk in response.content.iter_chunked(8192):
                            total_size += len(chunk)
                            if total_size > max_size:
                                self.logger.warning(
                                    f"File exceeded size during download: {url} ({total_size / 1024 / 1024:.2f} MB)"
                                )
                                return None
                            chunks.append(chunk)
                        
                        content = b''.join(chunks).decode('utf-8', errors='ignore')
                        
                        # Detect soft 404s - HTML error pages with 200 status
                        content_start = content.strip()[:500].lower()
                        if ('<!doctype html' in content_start or 
                            '<html' in content_start or
                            '<head>' in content_start or
                            content_start.startswith('<!')):
                            self.logger.debug(f"Skipping {url}: Content is HTML, not JS")
                            return None
                        
                        # Check if content is actually empty or whitespace only (allow minified JS)
                        if not content or len(content.strip()) < 50:
                            self.logger.debug(f"Skipping {url}: Content is empty or too short")
                            return None
                        
                        return content
                    else:
                        # Only log WARNING for unexpected status codes
                        if response.status not in [403, 404, 503]:
                            self.logger.warning(f"Failed to fetch {url}: status {response.status}")
                        else:
                            self.logger.debug(f"Skipping {url}: status {response.status}")
                        return None
        except asyncio.TimeoutError:
            self.logger.warning(
                f"[TIMEOUT] {url}\n"
                f"  Error: Request exceeded 30 second timeout\n"
                f"  Possible causes: Slow server, network congestion, or firewall blocking"
            )
            return None
        except aiohttp.ClientConnectorError as e:
            self.logger.warning(
                f"[CONNECTION FAILED] {url}\n"
                f"  Error: {str(e)[:100]}\n"
                f"  Possible causes: DNS failure, network block, or invalid domain"
            )
            return None
        except aiohttp.ClientError as e:
            self.logger.warning(
                f"[HTTP ERROR] {url}\n"
                f"  Error: {str(e)[:100]}\n"
                f"  Possible causes: Invalid response, connection reset, or server error"
            )
            return None
        except Exception as e:
            self.logger.warning(
                f"[UNEXPECTED ERROR] {url}\n"
                f"  Error: {str(e)[:100]}\n"
                f"  Type: {type(e).__name__}"
            )
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
