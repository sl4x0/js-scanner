"""
Secret Scanner Module
Integrates with TruffleHog for streaming secret detection
"""
import subprocess
import json
import asyncio
import time
from typing import Optional, List


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
        self.trufflehog_path = config.get('trufflehog_path', 'trufflehog')
        
        # Rate limit concurrent TruffleHog processes (Issue #2)
        max_concurrent = config.get('trufflehog_max_concurrent', 5)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Validate TruffleHog installation (Issue #7)
        self._validate_trufflehog()
    
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
    
    async def scan_directory(self, directory_path: str) -> List[dict]:
        """
        Scan an entire directory of files with TruffleHog (BATCH MODE)
        
        Args:
            directory_path: Path to directory containing files to scan
            
        Returns:
            List of secret findings
        """
        findings = []
        
        try:
            # Run TruffleHog on entire directory
            cmd = [
                self.trufflehog_path,
                'filesystem',
                directory_path,
                '--json',
                '--only-verified',
                '--no-update'
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
                return findings
            
            # Parse JSON output
            for line in stdout.decode().splitlines():
                if line.strip():
                    try:
                        finding = json.loads(line)
                        findings.append(finding)
                        
                        # Add to state manager
                        self.state.add_secret(finding)
                        
                        # Send to Discord
                        if self.notifier:
                            # Extract file info for Discord notification
                            source_metadata = finding.get('SourceMetadata', {})
                            file_path = source_metadata.get('Data', {}).get('Filesystem', {}).get('file', 'unknown')
                            await self.notifier.queue_batch_alert([finding], file_path)
                        
                    except json.JSONDecodeError:
                        continue
            
            self.logger.info(f"Found {len(findings)} secrets in directory")
            
        except Exception as e:
            self.logger.error(f"Directory scan failed: {e}")
        
        return findings
    
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
