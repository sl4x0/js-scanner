"""
Secret Scanner Module
Integrates with TruffleHog for streaming secret detection
"""
import subprocess
import json
import asyncio
import time
from typing import Optional


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
    
    async def scan_file(self, file_path: str, source_url: str) -> int:
        """
        Scans a file for secrets using TruffleHog (streaming)
        
        Args:
            file_path: Path to the file to scan
            source_url: Original URL of the file
            
        Returns:
            Number of verified secrets found
        """
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
