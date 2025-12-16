"""
Secret Scanner Module
Integrates with TruffleHog for streaming secret detection
"""
import subprocess
import json
import asyncio
import time
import sys
from typing import Optional, List
from .secrets_organizer import DomainSecretsOrganizer


class SecretScanner:
    """Scans files for secrets using TruffleHog"""
    
    def __init__(self, config: dict, logger, state_manager, notifier):
        """
        Initialize secret scanner
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            state_manager: State manager instance
            notifier: Discord notifier instance
        """
        self.config = config
        self.logger = logger
        self.state = state_manager
        self.notifier = notifier
        
        # Cross-platform TruffleHog binary detection
        self.trufflehog_path = self._find_trufflehog_binary(config)
        
        # Rate limit concurrent TruffleHog processes (Issue #2)
        max_concurrent = config.get('trufflehog_max_concurrent', 5)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Track all secrets found for export
        self.all_secrets = []
        
        # Initialize domain organizer for secrets
        self.secrets_organizer = None  # Will be initialized with base_path
        
        # Validate TruffleHog installation (Issue #7)
        self._validate_trufflehog()
    
    def initialize_organizer(self, base_path: str):
        """
        Initialize secrets organizer with base path
        
        Args:
            base_path: Base result path for the target
        """
        self.secrets_organizer = DomainSecretsOrganizer(base_path, self.logger)
    
    def _find_trufflehog_binary(self, config: dict) -> str:
        """
        Find TruffleHog binary with cross-platform support
        
        Priority:
        1. Config file path (if specified)
        2. Platform-specific executable in project root
        3. System PATH
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Path to TruffleHog binary
        """
        import shutil
        from pathlib import Path
        
        # 1. Check config
        config_path = config.get('trufflehog_path')
        if config_path:
            # Expand relative paths from project root
            if not Path(config_path).is_absolute():
                project_root = Path(__file__).parent.parent.parent
                config_path = str(project_root / config_path)
            
            if Path(config_path).exists():
                return config_path
        
        # 2. Check project root for platform-specific binary
        project_root = Path(__file__).parent.parent.parent
        
        if sys.platform == 'win32':
            local_binary = project_root / 'trufflehog.exe'
        else:
            local_binary = project_root / 'trufflehog'
        
        if local_binary.exists():
            return str(local_binary)
        
        # 3. Check system PATH
        if sys.platform == 'win32':
            binary_name = 'trufflehog.exe'
        else:
            binary_name = 'trufflehog'
        
        system_path = shutil.which(binary_name)
        if system_path:
            return system_path
        
        # Fallback: return binary name and let validation fail with helpful error
        return binary_name
    
    def _validate_trufflehog(self):
        """Validate TruffleHog is installed and executable"""
        import shutil
        import subprocess
        
        if not shutil.which(self.trufflehog_path):
            self.logger.error(
                f"❌ TruffleHog not found at: {self.trufflehog_path}\n"
                f"   Install: curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin\n"
                f"   Or update 'trufflehog_path' in config.yaml"
            )
            raise FileNotFoundError(f"TruffleHog not found: {self.trufflehog_path}")
        
        try:
            result = subprocess.run(
                [self.trufflehog_path, '--version'],
                capture_output=True,
                timeout=5
            )
            version = result.stdout.decode().strip()
            self.logger.info(f"✅ TruffleHog validated: {version}")
        except Exception as e:
            self.logger.error(f"❌ TruffleHog is not executable: {e}")
            raise
    
    async def scan_file(self, file_path: str, source_url: str) -> int:
        """
        Scans a file for secrets using TruffleHog (streaming)
        
        Args:
            file_path: Path to the file to scan
            source_url: Original URL of the file
            
        Returns:
            Number of verified secrets found
        """
        # Rate limit concurrent TruffleHog processes (Issue #2)
        async with self.semaphore:
            return await self._scan_file_impl(file_path, source_url)
    
    async def _scan_file_impl(self, file_path: str, source_url: str) -> int:
        """Internal implementation of file scanning"""
        self.logger.info(f"Scanning for secrets: {file_path}")
        
        secrets_found = 0
        timeout = self.config.get('trufflehog_timeout', 300)
        
        try:
            # TruffleHog command with JSON output and only verified secrets
            cmd = [
                self.trufflehog_path,
                'filesystem',
                file_path,
                '--json',
                '--only-verified',
                '--no-update'
            ]
            
            # Start TruffleHog process (unbuffered for Linux compatibility)
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Read output line by line (streaming) with total timeout
            # Create async task for reading
            start_time = time.time()
            file_secrets = []  # ✅ OPTIMIZATION: Collect secrets for batch notification
            try:
                while True:
                    # Check timeout
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        self.logger.warning(f"TruffleHog scan timeout for {file_path}")
                        process.kill()
                        await process.wait()
                        break
                    
                    # Read with remaining timeout
                    remaining_timeout = timeout - elapsed
                    try:
                        line = await asyncio.wait_for(
                            process.stdout.readline(),
                            timeout=min(remaining_timeout, 5.0)  # Check every 5s max
                        )
                    except asyncio.TimeoutError:
                        # Check if process is still running
                        if process.returncode is not None:
                            break
                        continue
                    
                    if not line:
                        break
                    
                    try:
                        # Parse JSON output
                        line_str = line.decode('utf-8').strip()
                        if not line_str:
                            continue
                        
                        secret_data = json.loads(line_str)
                        
                        # Check if it's a verified secret
                        if self._is_verified(secret_data):
                            secrets_found += 1
                            
                            # Extract line number from source metadata
                            source_metadata = secret_data.get('SourceMetadata', {})
                            line_num = source_metadata.get('Data', {}).get('Filesystem', {}).get('line', 0)
                            
                            # Add enriched source metadata
                            secret_data['SourceMetadata'] = {
                                'file': file_path,
                                'url': source_url,
                                'line': line_num
                            }
                            
                            # Save to state
                            self.state.add_secret(secret_data)
                            
                            # Track all secrets for export
                            self.all_secrets.append(secret_data)
                            
                            # ✅ OPTIMIZATION: Collect secrets for batch notification
                            file_secrets.append(secret_data)
                            
                            self.logger.warning(
                                f"🔐 VERIFIED SECRET: {secret_data.get('DetectorName', 'Unknown')} "
                                f"at line {line_num} in {file_path}"
                            )
                    
                    except json.JSONDecodeError:
                        # Skip non-JSON lines (progress messages, etc.)
                        continue
                    except Exception as e:
                        self.logger.error(f"Error processing secret output: {e}")
                        continue
            
            except Exception as e:
                self.logger.error(f"Error reading TruffleHog output: {e}")
            finally:
                # Always clean up the process to prevent zombies
                if process and process.returncode is None:
                    process.kill()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        self.logger.error("TruffleHog process did not terminate, forcing kill")
                        # Force kill on Unix
                        try:
                            import signal
                            process.send_signal(signal.SIGKILL)
                            await asyncio.wait_for(process.wait(), timeout=2)
                        except Exception as e:
                            self.logger.error(f"Failed to force kill process: {e}")
            
            # ✅ OPTIMIZATION: Send batch notification instead of individual alerts
            if file_secrets:
                await self.notifier.queue_batch_alert(file_secrets, file_path)
            
            if secrets_found > 0:
                self.logger.info(f"Found {secrets_found} verified secrets in {file_path}")
            
        except FileNotFoundError:
            self.logger.error(
                f"TruffleHog not found at {self.trufflehog_path}. "
                "Please install it or configure the correct path."
            )
        except Exception as e:
            self.logger.error(f"Error running TruffleHog: {e}")
        
        return secrets_found
    
    def _is_verified(self, secret_data: dict) -> bool:
        """
        Checks if a secret is verified
        
        Args:
            secret_data: Secret data from TruffleHog
            
        Returns:
            True if verified, False otherwise
        """
        # TruffleHog includes a 'Verified' field for confirmed secrets
        verified = secret_data.get('Verified', False)
        
        # Some detectors might use different field names
        if not verified:
            # Check SourceMetadata for verification status
            source_metadata = secret_data.get('SourceMetadata', {})
            verified = source_metadata.get('Verified', False)
        
        return verified
    
    def _load_file_manifest(self, directory_path: str) -> dict:
        """Load file manifest to map filenames to original URLs"""
        import json
        from pathlib import Path
        
        # Navigate up from files/unminified to base directory
        base_dir = Path(directory_path).parent.parent
        manifest_file = base_dir / 'file_manifest.json'
        
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.debug(f"Failed to load manifest: {e}")
        
        return {}
    
    async def scan_directory(self, directory_path: str) -> List[dict]:
        """
        Scan an entire directory of files with TruffleHog (BATCH MODE)
        Saves ALL findings (verified and unverified) for manual review
        
        Args:
            directory_path: Path to directory containing files to scan
            
        Returns:
            List of verified secret findings (all findings appended to all_secrets for export)
        """
        # Don't reset all_secrets - append to existing findings
        # (allows scanning multiple directories in one session)
        verified_findings = []
        
        # Load file manifest to get original URLs
        file_manifest = self._load_file_manifest(directory_path)
        
        try:
            # Run TruffleHog to get ALL findings (verified + unverified)
            # This ensures we save everything for manual review
            cmd = [
                self.trufflehog_path,
                'filesystem',
                directory_path,
                '--json',
                '--no-update'  # Removed --only-verified to get ALL findings
            ]
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Log stderr for debugging (TruffleHog outputs progress to stderr)
            if stderr:
                stderr_text = stderr.decode().strip()
                if stderr_text:
                    self.logger.debug(f"TruffleHog stderr: {stderr_text}")
            
            if process.returncode != 0:
                self.logger.error(f"TruffleHog failed with exit code {process.returncode}")
                return findings
            
            # Handle empty results gracefully
            if not stdout or not stdout.strip():
                self.logger.info("No secrets found in directory")
                return verified_findings
            
            # Parse JSON output - save ALL findings
            for line in stdout.decode().splitlines():
                if line.strip():
                    try:
                        finding = json.loads(line)
                        
                        # Enrich finding with original URL from manifest
                        source_metadata = finding.get('SourceMetadata', {})
                        file_path = source_metadata.get('Data', {}).get('Filesystem', {}).get('file', '')
                        
                        if file_path and file_manifest:
                            from pathlib import Path
                            filename = Path(file_path).name
                            
                            # Get original URL from manifest (manifest is dict: filename -> {url, hash, timestamp})
                            if filename in file_manifest:
                                manifest_entry = file_manifest[filename]
                                # Add enriched metadata for Discord notification
                                finding['SourceMetadata'] = {
                                    'url': manifest_entry.get('url', ''),
                                    'file': filename,
                                    'line': source_metadata.get('Data', {}).get('Filesystem', {}).get('line', 0)
                                }
                        
                        # Track ALL findings for export (verified + unverified)
                        self.all_secrets.append(finding)
                        
                        # Only process VERIFIED secrets for state and notifications
                        if self._is_verified(finding):
                            verified_findings.append(finding)
                            self.state.add_secret(finding)
                            
                            # Send to Discord
                            if self.notifier:
                                # Extract file info for Discord notification
                                source_metadata = finding.get('SourceMetadata', {})
                                file_path = source_metadata.get('Data', {}).get('Filesystem', {}).get('file', 'unknown')
                                await self.notifier.queue_batch_alert([finding], file_path)
                        
                    except json.JSONDecodeError:
                        continue
            
            self.logger.info(f"TruffleHog scan complete: {len(verified_findings)} verified secrets, {len(self.all_secrets)} total findings")
            
        except Exception as e:
            self.logger.error(f"Directory scan failed: {e}")
        
        return verified_findings
    
    async def scan_content(self, content: str, source_url: str) -> int:
        """
        Scans content directly (without saving to file first)
        
        Args:
            content: Content to scan
            source_url: Source URL
            
        Returns:
            Number of verified secrets found
        """
        # Create a temporary file for scanning
        import tempfile
        import os
        
        secrets_found = 0
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            secrets_found = await self.scan_file(tmp_path, source_url)
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        return secrets_found
    
    def export_results(self, output_path: str):
        """
        Export all secrets to a JSON file
        
        Args:
            output_path: Path to save the JSON file
        """
        from pathlib import Path
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.all_secrets, f, indent=2, default=str)
            if self.all_secrets:
                self.logger.info(f"Exported {len(self.all_secrets)} secrets to {output_path}")
            else:
                self.logger.debug(f"Exported empty secrets list to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to export secrets: {e}")
    
    async def save_organized_secrets(self):
        """
        Save secrets organized by domain
        """
        if not self.secrets_organizer:
            self.logger.warning("Secrets organizer not initialized, skipping domain organization")
            return
        
        # Save full results
        await self.secrets_organizer.save_full_results(self.all_secrets)
        
        # Organize and save by domain
        await self.secrets_organizer.organize_secrets(self.all_secrets)
        
        self.logger.info("✅ Saved secrets in both domain-specific and full formats")
    
    def get_secrets_summary(self):
        """Get summary of secrets organized by domain"""
        if not self.secrets_organizer:
            return {}
        
        return self.secrets_organizer.get_secrets_summary()
