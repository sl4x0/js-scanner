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
    
    async def acquire(self):
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
    """Fetches JavaScript files from various sources"""
    
    def __init__(self, config: dict, logger):
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
    
    async def initialize(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser_manager = BrowserManager(
            self.playwright,
            max_concurrent=self.max_concurrent,
            restart_after=self.restart_after,
            headless=self.headless
        )
        self.logger.info("Playwright browser manager initialized")
    
    async def cleanup(self):
        """Cleanup Playwright resources"""
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
            List of JavaScript URLs
        """
        self.logger.info(f"Fetching from Wayback Machine: {target}")
        
        # Wayback CDX API - get timestamp and original URL to construct archive URLs
        cdx_url = "http://web.archive.org/cdx/search/cdx"
        params = {
            'url': f'*.{target}',
            'fl': 'timestamp,original',  # Need timestamp to construct archive URLs
            'collapse': 'urlkey',
            'limit': str(self.wayback_max_results)  # Prevent overwhelming responses
        }
        
        js_urls = set()  # Use set to avoid duplicates
        
        try:
            # Apply rate limiting
            await self.wayback_limiter.acquire()
            
            # Log the actual query for debugging
            query_url = f"{cdx_url}?url={params['url']}&fl={params['fl']}&collapse={params['collapse']}&limit={params['limit']}"
            self.logger.info(f"Wayback query: {query_url}")
            
            async with aiohttp.ClientSession() as session:
                # Increase timeout for large responses and use streaming
                timeout = aiohttp.ClientTimeout(total=300, sock_read=120)
                async with session.get(cdx_url, params=params, timeout=timeout) as response:
                    self.logger.info(f"Wayback API response status: {response.status}")
                    
                    if response.status == 200:
                        # Stream the response to avoid loading huge responses into memory
                        line_count = 0
                        async for line in response.content:
                            line_count += 1
                            line_text = line.decode('utf-8', errors='ignore').strip()
                            
                            if line_text:
                                # CDX format with fl=timestamp,original: "timestamp original_url"
                                parts = line_text.split(' ', 1)
                                if len(parts) != 2:
                                    continue
                                
                                timestamp, original_url = parts
                                
                                # Filter for JS files only
                                if not ('.js' in original_url.lower() or original_url.endswith('.mjs')):
                                    continue
                                
                                # Construct Wayback archive URL: https://web.archive.org/web/{timestamp}/{original_url}
                                wayback_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
                                js_urls.add(wayback_url)
                        
                        self.logger.info(f"Wayback processed {line_count} lines, found {len(js_urls)} JS URLs")
                        
                        self.logger.info(f"Found {len(js_urls)} URLs from Wayback")
                    else:
                        self.logger.warning(f"Wayback returned status {response.status}")
                        
            # Also try with extended search if first query didn't find much
            if len(js_urls) < 100:  # Only do second query if first didn't find much
                # Try without collapse to get more results
                params_extended = params.copy()
                params_extended.pop('collapse', None)  # Remove collapse
                
                self.logger.info("Running extended Wayback search without collapse")
                self.logger.info(f"Extended query URL: {cdx_url}?url={params_extended['url']}")
                await self.wayback_limiter.acquire()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(cdx_url, params=params_extended, timeout=aiohttp.ClientTimeout(total=60)) as response:
                        self.logger.info(f"Extended search response status: {response.status}")
                        
                        if response.status == 200:
                            text = await response.text()
                            self.logger.info(f"Extended search response length: {len(text)} chars")
                            
                            for line in text.strip().split('\n'):
                                line = line.strip()
                                if line:
                                    # Filter for JS files
                                    if not ('.js' in line.lower() or line.endswith('.mjs')):
                                        continue
                                    
                                    if not line.startswith(('http://', 'https://')):
                                        line = f"https://{line}"
                                    
                                    js_urls.add(line)
                            
                            self.logger.info(f"Total {len(js_urls)} URLs from Wayback after extended search")
                            
        except Exception as e:
            self.logger.error(f"Error fetching from Wayback: {e}", exc_info=True)
        
        return list(js_urls)
    
    async def fetch_live(self, target: str) -> List[str]:
        """
        Fetch JavaScript URLs from live site using Playwright
        Enhanced to detect scripts on modern SPAs
        
        Args:
            target: Target URL
            
        Returns:
            List of JavaScript URLs
        """
        self.logger.info(f"Fetching from live site: {target}")
        
        if not target.startswith('http'):
            target = f'https://{target}'
        
        js_urls = set()
        context = None
        page = None
        
        try:
            await self.browser_manager._ensure_browser()
            context = await self.browser_manager.browser.new_context()
            page = await context.new_page()
            page.set_default_timeout(self.page_timeout)
            
            # Track all JS requests
            async def handle_request(request):
                url = request.url
                if url.endswith('.js') or 'javascript' in request.resource_type:
                    js_urls.add(url)
                    self.logger.debug(f"Found JS: {url}")
            
            page.on('request', handle_request)
            
            # Navigate and wait longer for SPAs
            await page.goto(target, wait_until='networkidle')
            
            # Wait extra time for dynamic content
            await asyncio.sleep(3)
            
            # Scroll to trigger lazy-loaded scripts
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
            
            # Also extract from DOM
            scripts = await page.query_selector_all('script[src]')
            for script in scripts:
                src = await script.get_attribute('src')
                if src:
                    absolute_url = urljoin(target, src)
                    if '.js' in absolute_url:  # More flexible matching
                        js_urls.add(absolute_url)
            
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
            
        except Exception as e:
            self.logger.error(f"Error fetching live site: {e}")
            return []
        finally:
            if page:
                await page.close()
            if context:
                await context.close()
        
        # Remove duplicates and filter
        js_urls = [url for url in js_urls if '.js' in url]
        
        self.logger.info(f"Found {len(js_urls)} scripts on live site")
        
        # Log first few for debugging
        if js_urls and len(js_urls) > 0:
            self.logger.debug(f"Sample URLs: {js_urls[:3]}")
        
        return list(js_urls)
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """
        Fetches the content of a JavaScript file
        
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
                        
                        # Stream and check size incrementally
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
                        
                        content = b''.join(chunks).decode('utf-8')
                        return content
                    else:
                        # Only log WARNING for unexpected status codes
                        if response.status not in [403, 404, 503]:
                            self.logger.warning(f"Failed to fetch {url}: status {response.status}")
                        else:
                            self.logger.debug(f"Skipping {url}: status {response.status}")
                        return None
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching {url}")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
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
            
        except Exception as e:
            self.logger.error(f"Error fetching with Playwright {url}: {e}")
            return None
        finally:
            # CRITICAL: Always close
            if page:
                await page.close()
            if context:
                await context.close()
