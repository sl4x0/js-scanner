"""
Semgrep Analyzer Module
Integrates Semgrep for static analysis of JavaScript files to identify security patterns
"""
import subprocess
import json
import asyncio
import sys
import shutil
from pathlib import Path
from typing import Optional, List, Dict


class SemgrepAnalyzer:
    """Static analysis using Semgrep for JavaScript security patterns"""
    
    def __init__(self, config: dict, logger, paths: dict):
        """
        Initialize Semgrep analyzer
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
            paths: Dictionary of result paths (base, findings, etc.)
        """
        self.config = config
        self.logger = logger
        self.paths = paths
        
        # Extract semgrep config with defaults
        semgrep_config = config.get('semgrep', {})
        self.enabled = semgrep_config.get('enabled', False)
        self.timeout = semgrep_config.get('timeout', 600)  # 10 minutes default
        self.max_target_bytes = semgrep_config.get('max_target_bytes', 5000000)  # 5MB per file
        self.jobs = semgrep_config.get('jobs', 4)  # Parallel jobs
        
        # Semgrep binary detection
        self.semgrep_path = self._find_semgrep_binary(config)
        
        # Track if Semgrep is available (graceful degradation)
        self.semgrep_available = False
        
        # Findings counter
        self.findings_count = 0
    
    def _find_semgrep_binary(self, config: dict) -> str:
        """
        Find Semgrep binary with cross-platform support
        
        Priority:
        1. Config file path (if specified)
        2. System PATH
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Path to Semgrep binary or 'semgrep' for PATH lookup
        """
        # 1. Check config
        semgrep_config = config.get('semgrep', {})
        config_path = semgrep_config.get('binary_path')
        if config_path:
            # Expand relative paths from project root
            if not Path(config_path).is_absolute():
                project_root = Path(__file__).parent.parent.parent
                config_path = str(project_root / config_path)
            
            if Path(config_path).exists():
                return config_path
        
        # 2. Default to PATH lookup (most common after `pip install semgrep`)
        return 'semgrep'
    
    def validate(self) -> bool:
        """
        Validate Semgrep installation (graceful degradation)
        
        Returns:
            True if Semgrep is available, False otherwise
        """
        if not self.enabled:
            self.logger.info("ℹ️  Semgrep analysis is disabled in config")
            return False
        
        # Check if binary exists
        if not shutil.which(self.semgrep_path):
            self.logger.warning("⚠️  Semgrep not found. Static analysis will be SKIPPED.")
            self.logger.warning("   Install: pip install semgrep")
            self.logger.warning("   Or set semgrep.binary_path in config.yaml")
            self.semgrep_available = False
            return False
        
        # Verify version (ensure it's working)
        try:
            result = subprocess.run(
                [self.semgrep_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.debug(f"✓ Semgrep found: {version}")
                self.semgrep_available = True
                return True
            else:
                self.logger.warning(f"⚠️  Semgrep binary exists but failed to run: {result.stderr}")
                self.semgrep_available = False
                return False
        except subprocess.TimeoutExpired:
            self.logger.warning("⚠️  Semgrep version check timed out")
            self.semgrep_available = False
            return False
        except Exception as e:
            self.logger.warning(f"⚠️  Semgrep validation failed: {e}")
            self.semgrep_available = False
            return False
    
    async def scan_directory(self, directory_path: str) -> List[Dict]:
        """
        Run Semgrep on JavaScript files in directory
        
        Uses `semgrep scan` with JSON output for fast, comprehensive analysis.
        
        Args:
            directory_path: Path to directory containing JS files (e.g., unique_js/)
            
        Returns:
            List of Semgrep findings with metadata
        """
        if not self.semgrep_available:
            self.logger.warning("Semgrep is not available, skipping scan")
            return []
        
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            self.logger.warning(f"Directory does not exist: {directory_path}")
            return []
        
        self.logger.info(f"📂 Scanning directory: {directory_path}")
        
        # Build Semgrep command for maximum speed
        cmd = [
            self.semgrep_path,
            'scan',
            '--config=auto',  # Use registry rules (requires login)
            '--json',  # JSON output for parsing
            '--timeout', str(self.timeout),
            '--max-target-bytes', str(self.max_target_bytes),
            '--jobs', str(self.jobs),  # Parallel processing
            '--no-git-ignore',  # Scan all files, ignore .gitignore
            '--skip-unknown-extensions',  # Only JS files
            str(directory)
        ]
        
        self.logger.debug(f"Running: {' '.join(cmd)}")
        
        try:
            # Run Semgrep with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout + 60  # Extra buffer for process cleanup
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"⚠️  Semgrep scan timed out after {self.timeout}s")
                process.kill()
                await process.wait()
                return []
            
            # Parse JSON output
            if process.returncode == 0:
                output_json = json.loads(stdout.decode('utf-8'))
                findings = output_json.get('results', [])
                self.findings_count = len(findings)
                
                self.logger.info(f"✅ Semgrep scan complete: {self.findings_count} findings")
                
                # Log stderr if there are warnings (but don't fail)
                if stderr:
                    stderr_text = stderr.decode('utf-8').strip()
                    if stderr_text:
                        self.logger.debug(f"Semgrep warnings:\n{stderr_text}")
                
                return findings
            else:
                error_msg = stderr.decode('utf-8') if stderr else 'Unknown error'
                self.logger.error(f"❌ Semgrep scan failed (exit {process.returncode}):")
                self.logger.error(error_msg)
                return []
                
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse Semgrep JSON output: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Semgrep scan error: {e}")
            self.logger.debug("Full error traceback:", exc_info=True)
            return []
    
    def save_findings(self, findings: List[Dict], output_path: Optional[str] = None):
        """
        Save Semgrep findings to JSON file
        
        Args:
            findings: List of finding dictionaries from Semgrep
            output_path: Optional custom output path (defaults to findings/semgrep.json)
        """
        if not findings:
            self.logger.info("ℹ️  No Semgrep findings to save")
            return
        
        # Default output path
        if output_path is None:
            findings_dir = Path(self.paths.get('findings', self.paths['base'])) / 'findings'
            findings_dir.mkdir(parents=True, exist_ok=True)
            output_path = findings_dir / 'semgrep.json'
        
        output_file = Path(output_path)
        
        # Prepare output structure with metadata
        output_data = {
            'scan_info': {
                'total_findings': len(findings),
                'semgrep_version': self._get_semgrep_version(),
                'config': 'auto'  # Using auto config (registry rules)
            },
            'findings': findings
        }
        
        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Semgrep findings saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save Semgrep findings: {e}")
    
    def _get_semgrep_version(self) -> str:
        """Get Semgrep version string"""
        try:
            result = subprocess.run(
                [self.semgrep_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return 'unknown'
    
    def get_stats(self) -> Dict:
        """
        Get scan statistics
        
        Returns:
            Dictionary with scan statistics
        """
        return {
            'enabled': self.enabled,
            'available': self.semgrep_available,
            'findings_count': self.findings_count
        }
