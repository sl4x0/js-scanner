import asyncio
from typing import List, Optional
from pathlib import Path

class DiscoveryEngine:
    """Thin wrapper to encapsulate discovery-related orchestration."""

    def __init__(self, scan_engine):
        self.engine = scan_engine

    async def discover_urls(self, inputs: List[str], use_subjs: bool = False, subjs_only: bool = False) -> List[str]:
        # Delegate to existing ScanEngine method for discovery
        return await self.engine._discover_all_domains_concurrent(inputs, use_subjs, subjs_only)

    async def discover_with_katana(self, inputs: List[str], scope_domains=None) -> List[str]:
        """
        Migrated from ScanEngine._strategy_katana
        Katana-based URL discovery (fast pass).
        """
        # Keep original logic but executed from the DiscoveryEngine
        targets = [item for item in inputs if not self.engine._is_valid_js_url(item)]
        if not targets:
            return []

        # Respect scope_domains if provided, otherwise compute fallback
        if scope_domains is None:
            scope_domains = self.engine._get_scope_domains() if not self.engine.config.get('no_scope_filter', False) else None

        self.engine.logger.info(f"\n{'='*70}")
        self.engine.logger.info("⚡ STRATEGY: KATANA FAST-PASS (Speed Layer)")
        self.engine.logger.info(f"{'='*70}")

        katana_urls = await asyncio.to_thread(
            self.engine.katana_fetcher.fetch_urls,
            targets,
            scope_domains
        )

        if katana_urls:
            self.engine.logger.info(f"✓ Katana complete: {len(katana_urls)} JS files discovered\n")

        return katana_urls or []

    async def discover_with_subjs(self, inputs: List[str], scope_domains=None) -> List[str]:
        """
        Migrated from ScanEngine._strategy_subjs
        SubJS-based historical URL discovery.
        """
        from ..strategies.passive import PassiveFetcher

        targets = [item for item in inputs if not self.engine._is_valid_js_url(item)]
        if not targets:
            return []

        subjs_fetcher = PassiveFetcher(self.engine.config, self.engine.logger)
        if not PassiveFetcher.is_installed():
            self.engine.logger.warning("⚠️  SubJS not installed, skipping SubJS strategy")
            return []

        self.engine.logger.info(f"\n{'='*70}")
        self.engine.logger.info("📚 STRATEGY: SUBJS HISTORICAL SCAN (History Layer)")
        self.engine.logger.info(f"{'='*70}")

        subjs_urls = await subjs_fetcher.fetch_batch(targets)

        if subjs_urls:
            self.engine.logger.info(f"✓ SubJS complete: {len(subjs_urls)} JS files discovered\n")

        return subjs_urls or []

    async def discover_with_browser(self, inputs: List[str]) -> List[str]:
        """
        Migrated from ScanEngine._strategy_live_browser
        Live browser-based discovery using the fetcher/playwright.
        """
        self.engine.logger.info(f"\n{'='*70}")
        self.engine.logger.info("🌐 STRATEGY: LIVE BROWSER SCAN")
        self.engine.logger.info(f"{'='*70}")

        all_urls = []
        max_concurrent = self.engine.config.get('max_concurrent_domains', 10)
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scan_one(item: str) -> List[str]:
            async with semaphore:
                if self.engine._is_valid_js_url(item):
                    return [item]

                is_valid, reason = await self.engine.fetcher.validate_domain(item)
                if not is_valid:
                    return []

                result = await self.engine.fetcher.fetch_live(item)
                return result if isinstance(result, list) else []

        tasks = [scan_one(item) for item in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_urls.extend(result)

        if all_urls:
            self.engine.logger.info(f"✓ Live browser complete: {len(all_urls)} JS files discovered\n")

        return all_urls


class DownloadEngine:
    """Thin wrapper to encapsulate download orchestration."""

    def __init__(self, scan_engine):
        self.engine = scan_engine

    async def download_all(self, urls: List[str]) -> List[dict]:
        """
        Migrated from ScanEngine._download_all_files
        Streams downloads to disk, hashes, deduplicates and returns metadata.
        """
        engine = self.engine
        downloaded_files = []
        semaphore = asyncio.Semaphore(engine.config.get('threads', 50))
        total_urls = len(urls)
        completed = 0
        failed_breakdown = {
            'invalid_url': 0,
            'out_of_scope': 0,
            'fetch_failed': 0,
            'filtered': 0,
            'duplicate': 0
        }
        lock = asyncio.Lock()

        async def download_one(url: str) -> Optional[dict]:
            nonlocal completed
            async with semaphore:
                try:
                    verbose_mode = engine.config.get('verbose', False)
                    if verbose_mode:
                        engine.logger.info(f"📥 Download: {url[:80]}")

                    if not engine._is_valid_js_url(url):
                        if verbose_mode:
                            engine.logger.info(f"❌ Invalid URL: {url[:80]}")
                        else:
                            engine.logger.debug(f"Invalid URL: {url}")
                        async with lock:
                            failed_breakdown['invalid_url'] += 1
                        return None

                    if not engine._is_target_domain(url):
                        if verbose_mode:
                            engine.logger.info(f"❌ Out of scope: {url[:80]}")
                        else:
                            engine.logger.debug(f"Out of scope: {url}")
                        async with lock:
                            failed_breakdown['out_of_scope'] += 1
                        return None

                    from uuid import uuid4
                    from ..utils.hashing import calculate_file_hash

                    tmp_filename = f"tmp_{uuid4().hex}.tmp"
                    tmp_path = Path(engine.paths['unique_js']) / tmp_filename

                    success = await engine.fetcher.fetch_and_write(url, str(tmp_path))
                    if not success:
                        reason = getattr(engine.fetcher, 'last_failure_reason', None)
                        async with lock:
                            if reason and str(reason).startswith('filtered'):
                                failed_breakdown['filtered'] += 1
                            else:
                                failed_breakdown['fetch_failed'] += 1

                        if reason:
                            if reason in ('timeout',):
                                engine.stats['network_errors']['timeouts'] += 1
                                engine.stats['failures']['timeout'] += 1
                            elif reason in ('dns_errors', 'dns'):
                                engine.stats['network_errors']['dns_errors'] += 1
                            elif reason in ('connection_refused',):
                                engine.stats['network_errors']['connection_refused'] += 1
                            elif reason in ('ssl_errors',):
                                engine.stats['network_errors']['ssl_errors'] += 1
                            elif reason in ('rate_limit', 'rate_limits'):
                                engine.stats['network_errors']['rate_limits'] += 1
                            elif reason in ('not_found',) or str(reason).startswith('http_') or reason in ('http_errors','non_retryable_error'):
                                engine.stats['network_errors']['http_errors'] += 1
                                engine.stats['failures']['http_error'] += 1

                        if verbose_mode:
                            engine.logger.info(f"❌ Fetch failed ({reason}) {url[:80]}")

                        return None

                    file_hash = await calculate_file_hash(str(tmp_path))

                    force_rescan = engine.config.get('force_rescan', False)
                    if not force_rescan:
                        if not engine.state.mark_as_scanned_if_new(file_hash, url):
                            engine.logger.debug(f"Duplicate (already scanned): {url}")
                            engine.stats['failures']['duplicates'] += 1
                            async with lock:
                                failed_breakdown['duplicate'] += 1
                            try:
                                tmp_path.unlink(missing_ok=True)
                            except Exception:
                                pass
                            return None
                    else:
                        engine.state.mark_as_scanned_if_new(file_hash, url)

                    hash_filename = f"{file_hash}.js"
                    file_path = Path(engine.paths['unique_js']) / hash_filename
                    try:
                        tmp_path.replace(file_path)
                    except Exception:
                        try:
                            with open(str(tmp_path), 'rb') as r, open(str(file_path), 'wb') as w:
                                w.write(r.read())
                            tmp_path.unlink(missing_ok=True)
                        except Exception:
                            pass

                    sample = ""
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            sample = f.read(engine.config.get('minification_detection', {}).get('sample_size', 10000))
                    except Exception:
                        sample = ""

                    is_minified = engine._is_minified(sample)

                    async with lock:
                        engine._save_file_manifest(url, file_hash, hash_filename, is_minified)

                        engine.stats['total_files'] += 1
                        completed += 1
                        success_count = len(downloaded_files) + 1

                        if completed % 50 == 0 or completed == total_urls:
                            total_skipped = sum(failed_breakdown.values())
                            extra = f"{success_count} saved, {total_skipped} skipped"
                            if total_skipped > 0 and failed_breakdown['duplicate'] > total_skipped * 0.9:
                                extra += " (mostly cached)"
                            engine._log_progress("Download Files", completed, total_urls, extra)
                        else:
                            engine._log_progress("Download Files", completed, total_urls, f"{success_count} saved")

                    return {
                        'url': url,
                        'hash': file_hash,
                        'filename': hash_filename,
                        'file_path': str(file_path),
                        'minified_path': str(file_path),
                        'is_minified': is_minified
                    }

                except Exception as e:
                    engine.logger.error(f"❌ Download failed for {url[:100]}: {str(e)}")
                    engine.logger.debug("Full download error traceback:", exc_info=True)
                    return None

        async def task_wrapper(url: str):
            try:
                result = await download_one(url)
                if result:
                    downloaded_files.append(result)
            except Exception as e:
                engine.logger.error(f"Task wrapper exception for {url}: {e}")

        if engine.shutdown_requested:
            engine.logger.warning("⚠️  Download interrupted - shutting down")
            return []

        try:
            async with asyncio.TaskGroup() as tg:
                for url in urls:
                    tg.create_task(task_wrapper(url))
        except* Exception as eg:
            engine.logger.error(f"Critical batch download error: {eg}")

        if engine.shutdown_requested:
            engine.logger.warning("⚠️  Download processing interrupted - shutting down")
            return downloaded_files

        total_filtered = sum(failed_breakdown.values())
        engine.logger.info(f"\n{'='*60}")
        engine.logger.info(f"✅ Downloaded {len(downloaded_files)} files (skipped {total_filtered})")

        if total_filtered > 0:
            engine.logger.info(f"   📊 Breakdown:")
            if failed_breakdown['invalid_url'] > 0:
                engine.logger.info(f"      • Invalid URLs: {failed_breakdown['invalid_url']}")
            if failed_breakdown['out_of_scope'] > 0:
                engine.logger.info(f"      • Out of scope: {failed_breakdown['out_of_scope']}")
            if failed_breakdown['fetch_failed'] > 0:
                engine.logger.info(f"      • Fetch failed: {failed_breakdown['fetch_failed']}")
            if failed_breakdown['duplicate'] > 0:
                engine.logger.info(f"      • Duplicates (cached): {failed_breakdown['duplicate']}")

        if hasattr(engine.fetcher, 'error_stats') and failed_breakdown['fetch_failed'] > 0:
            error_stats = engine.fetcher.error_stats
            total_errors = sum(error_stats.values())

            engine.logger.info(f"\n   🔍 Fetch Failure Analysis:")

            if error_stats['http_errors'] > 0:
                engine.logger.info(f"      • HTTP errors (403/404/etc): {error_stats['http_errors']}")
                if hasattr(engine.fetcher, 'http_status_breakdown') and engine.fetcher.http_status_breakdown:
                    status_summary = ", ".join([f"{code}: {count}" for code, count in sorted(engine.fetcher.http_status_breakdown.items())])
                    engine.logger.info(f"        └─ Status codes: {status_summary}")

            if error_stats['timeouts'] > 0:
                engine.logger.info(f"      • Timeouts: {error_stats['timeouts']}")
            if error_stats['rate_limits'] > 0:
                engine.logger.info(f"      • Rate limited: {error_stats['rate_limits']}")
            if error_stats['dns_errors'] > 0:
                engine.logger.info(f"      • DNS errors: {error_stats['dns_errors']}")
            if error_stats['ssl_errors'] > 0:
                engine.logger.info(f"      • SSL errors: {error_stats['ssl_errors']}")
            if error_stats['connection_refused'] > 0:
                engine.logger.info(f"      • Connection refused: {error_stats['connection_refused']}")

            unaccounted = failed_breakdown['fetch_failed'] - total_errors
            if unaccounted > 0:
                engine.logger.info(f"      • ⚠️  Untracked failures: {unaccounted}")
                engine.logger.info(f"        └─ These failed before HTTP request or weren't logged")

            verbose_mode = engine.config.get('verbose', False)
            if verbose_mode or unaccounted > 0:
                engine.logger.info(f"      💡 Run with --verbose to see each failure as it happens")

        engine.logger.info(f"{'='*60}\n")

        return downloaded_files

    async def validate_urls_with_head(self, urls: List[str]) -> List[str]:
        """
        Migrated from ScanEngine._validate_urls_with_head
        Validate URLs using HEAD requests before downloading.
        """
        engine = self.engine
        validated_urls = []
        semaphore = asyncio.Semaphore(20)

        async def validate_one(url: str) -> Optional[str]:
            async with semaphore:
                try:
                    exists, status_code = await engine.fetcher.validate_url_exists(url)
                    if exists:
                        return url
                    else:
                        engine.logger.debug(f"HEAD validation failed: {url} (status {status_code})")
                        return None
                except Exception as e:
                    engine.logger.error(f"HEAD request error for {url}: {str(e)}")
                    engine.logger.debug("Full HEAD validation traceback:", exc_info=True)
                    return None

        tasks = [validate_one(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, str):
                validated_urls.append(result)

        return validated_urls


class AnalysisEngine:
    """Thin wrapper to encapsulate analysis phases (secrets, AST, semgrep, etc.)."""

    def __init__(self, scan_engine):
        self.engine = scan_engine
    async def run_secrets_scan(self, unique_js_dir: str):
        return await self.engine.secret_scanner.scan_directory(unique_js_dir)

    async def run_semgrep(self, directory_path: str):
        """
        Migrated from ScanEngine._run_semgrep_analysis
        """
        engine = self.engine
        # Validate Semgrep is available
        if not engine.semgrep_analyzer.validate():
            engine.logger.warning("⚠️  Semgrep validation failed, skipping static analysis")
            return

        engine.logger.info("🔍 Running Semgrep static analysis...")
        engine.logger.info(f"📂 Target: {directory_path}")

        findings = await engine.semgrep_analyzer.scan_directory(directory_path)

        engine.stats['semgrep_findings'] = len(findings)

        if findings:
            findings_path = Path(engine.paths['base']) / 'findings' / 'semgrep.json'
            engine.semgrep_analyzer.save_findings(findings, str(findings_path))

            engine.logger.info(f"✅ Semgrep analysis complete: {len(findings)} findings")
            engine.logger.info(f"💾 Results saved to: {findings_path}")
        else:
            engine.logger.info("✅ Semgrep analysis complete: No findings")

        engine.logger.info("")

    async def process_files(self, files: List[dict]):
        """
        Migrated from ScanEngine._process_all_files_parallel
        Run AST analysis on downloaded files in parallel.
        """
        engine = self.engine
        semaphore = asyncio.Semaphore(engine.config.get('threads', 50))
        processed_count = 0
        total_files = len(files)
        progress_lock = asyncio.Lock()

        async def process_one(file_info: dict):
            nonlocal processed_count
            async with semaphore:
                try:
                    url = file_info['url']
                    file_path = file_info.get('file_path') or file_info.get('minified_path')
                    content = ""
                    if file_path:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as _f:
                                content = _f.read()
                        except Exception:
                            content = ""

                    should_skip, reason = engine.fetcher.noise_filter.should_skip_content(content, url)
                    if should_skip:
                        engine.logger.debug(f"⏭️  Skipping AST analysis for vendor lib: {url} ({reason})")
                        async with progress_lock:
                            processed_count += 1
                        return

                    await engine.ast_analyzer.analyze(content, url)

                    if engine.config.get('spa_intelligence', {}).get('enabled', True):
                        try:
                            predicted_chunks = engine.ast_analyzer.predict_chunks(content, url)
                            if predicted_chunks:
                                for chunk_url in predicted_chunks:
                                    if not engine.state.is_processed(chunk_url):
                                        engine.logger.debug(f"🧩 Queued chunk: {chunk_url}")
                        except Exception as e:
                            engine.logger.debug(f"Chunk prediction failed for {url}: {e}")

                    async with progress_lock:
                        processed_count += 1
                        if processed_count % 30 == 0 or processed_count == total_files:
                            percent = (processed_count / total_files * 100) if total_files > 0 else 0
                            engine.logger.info(f"⚙️  Extracting: {processed_count}/{total_files} files ({percent:.1f}%)")

                except Exception as e:
                    engine.logger.error(f"❌ Processing failed {file_info.get('url','unknown')}: {str(e)}")
                    engine.logger.debug("Full processing error traceback:", exc_info=True)

        if engine.shutdown_requested:
            engine.logger.warning("⚠️  Extraction interrupted - shutting down")
            return

        try:
            async with asyncio.TaskGroup() as tg:
                for f in files:
                    tg.create_task(process_one(f))
        except* Exception as eg:
            engine.logger.error(f"Critical batch processing error: {eg}")

        if engine.shutdown_requested:
            engine.logger.warning("⚠️  Skipping extract save - shutting down")
            return

        await engine.ast_analyzer.save_organized_extracts()

        extracts_with_sources = engine.ast_analyzer.get_extracts_with_sources()
        engine.stats['extracts_detailed'] = extracts_with_sources

        domain_summary = engine.ast_analyzer.get_domain_summary()
        engine.stats['domain_summary'] = domain_summary

        engine.logger.info(f"✅ Processed {len(files)} files")

    async def unminify_all_files(self, files: List[dict]):
        """
        Migrated from ScanEngine._unminify_all_files
        Beautify all files in parallel and save unminified results.
        """
        engine = self.engine
        timeout_count = 0
        max_timeout_logs = 3
        semaphore = asyncio.Semaphore(engine.config.get('threads', 50))

        async def unminify_one(file_info: dict):
            nonlocal timeout_count
            async with semaphore:
                try:
                    if not file_info.get('is_minified', True):
                        return

                    minified_path = file_info.get('minified_path') or file_info.get('file_path')
                    filename = file_info.get('filename')
                    content = ""
                    if minified_path:
                        try:
                            with open(minified_path, 'r', encoding='utf-8', errors='ignore') as _f:
                                content = _f.read()
                        except Exception:
                            content = ""

                    if not minified_path:
                        return

                    processed = await engine.processor.process(content, minified_path)

                    unminified_path = Path(engine.paths['files_unminified']) / filename
                    with open(unminified_path, 'w', encoding='utf-8') as f:
                        f.write(processed)

                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count <= max_timeout_logs:
                        engine.logger.warning(f"Beautification timed out after 30s, using original content")
                    elif timeout_count == max_timeout_logs + 1:
                        engine.logger.warning(f"... suppressing further timeout warnings ...")
                except Exception as e:
                    engine.logger.error(f"❌ Unminify failed {file_info.get('url','unknown')}: {str(e)}")
                    engine.logger.debug("Full beautification error traceback:", exc_info=True)

        if engine.shutdown_requested:
            engine.logger.warning("⚠️  Beautification interrupted - shutting down")
            return

        tasks = [unminify_one(f) for f in files]
        await asyncio.gather(*tasks, return_exceptions=True)

        engine.logger.info(f"✅ Beautified {len(files)} files")

        if timeout_count > 0:
            engine.logger.info(f"ℹ️  {timeout_count} files timed out during beautification (using original)")
