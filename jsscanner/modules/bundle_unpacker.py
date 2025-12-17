"""
Bundle Unpacker Module (v3.0)
Reconstructs original directory structure from Webpack/Vite/Parcel bundles
"""
import subprocess
import asyncio
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List


class BundleUnpacker:
    """Unpacks modern JavaScript bundles into original structure"""
    
    def __init__(self, logger, temp_dir: str = 'temp/unpacked'):
        """
        Initialize bundle unpacker
        
        Args:
            logger: Logger instance
            temp_dir: Temporary directory for unpacked files
        """
        self.logger = logger
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if webcrack is installed
        self.webcrack_available = self._check_webcrack()
    
    def _check_webcrack(self) -> bool:
        """Check if webcrack is installed"""
        try:
            result = subprocess.run(
                ['webcrack', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.decode().strip()
                self.logger.info(f"✓ webcrack available: {version}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.logger.warning(
                "⚠️  webcrack not found. Bundle unpacking disabled.\n"
                "   Install: npm install -g webcrack"
            )
        return False
    
    async def should_unpack(self, content: str, file_size: int) -> bool:
        """
        Determine if file should be unpacked vs beautified
        
        Args:
            content: File content
            file_size: Size in bytes
        
        Returns:
            True if should unpack, False for regular beautification
        """
        # Only unpack large files (>100KB)
        if file_size < 100 * 1024:
            return False
        
        # Check for bundle signatures
        bundle_signatures = [
            'webpack',
            '__webpack_require__',
            'webpackChunk',
            '__vite__',
            'parcelRequire',
            'System.register',
            'define.amd'
        ]
        
        # Check first 5000 chars for signatures
        sample = content[:5000].lower()
        for sig in bundle_signatures:
            if sig.lower() in sample:
                self.logger.info(f"Detected bundle signature: {sig}")
                return True
        
        return False
    
    async def unpack_bundle(self, input_file: str, output_dir: str) -> Optional[Dict]:
        """
        Unpack a JavaScript bundle using webcrack
        
        Args:
            input_file: Path to minified bundle
            output_dir: Directory to extract files to
        
        Returns:
            Dictionary with extraction info or None
        """
        if not self.webcrack_available:
            return None
        
        try:
            self.logger.info(f"🔓 Unpacking bundle: {Path(input_file).name}")
            
            # Create output directory (clean if exists)
            output_path = Path(output_dir)
            
            # Force cleanup of existing directory
            if output_path.exists():
                self.logger.debug(f"Cleaning existing directory: {output_path}")
                try:
                    shutil.rmtree(output_path, ignore_errors=False)
                    # Wait for filesystem to sync
                    await asyncio.sleep(0.2)
                except Exception as e:
                    self.logger.warning(f"Could not clean directory: {e}")
                    # Try harder - rename and delete
                    temp_name = output_path.with_suffix('.old')
                    if temp_name.exists():
                        shutil.rmtree(temp_name, ignore_errors=True)
                    output_path.rename(temp_name)
                    shutil.rmtree(temp_name, ignore_errors=True)
                    await asyncio.sleep(0.2)
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Run webcrack
            cmd = [
                'webcrack',
                input_file,
                '--output', str(output_path)
            ]
            
            self.logger.debug(f"Running: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 minutes max
            )
            
            if process.returncode == 0:
                # Count extracted files
                extracted_files = list(output_path.rglob('*.js'))
                
                self.logger.info(
                    f"✅ Bundle unpacked successfully\n"
                    f"   Input: {Path(input_file).name}\n"
                    f"   Output: {output_path}\n"
                    f"   Files extracted: {len(extracted_files)}"
                )
                
                return {
                    'success': True,
                    'input_file': input_file,
                    'output_dir': str(output_path),
                    'extracted_files': [str(f) for f in extracted_files],
                    'file_count': len(extracted_files)
                }
            else:
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                # Parse common webcrack errors
                if "already exists" in error_msg.lower():
                    self.logger.warning(
                        f"⚠️  webcrack failed: Output directory conflict\n"
                        f"   Directory: {output_path}\n"
                        f"   Attempting to clean and retry..."
                    )
                    # Force cleanup and don't retry (will fallback to beautification)
                    if output_path.exists():
                        shutil.rmtree(output_path, ignore_errors=True)
                else:
                    self.logger.warning(f"⚠️  webcrack failed: {error_msg}")
                return None
                
        except asyncio.TimeoutError:
            self.logger.warning(f"⚠️  Bundle unpacking timed out (5 min limit)")
            return None
        except Exception as e:
            self.logger.error(f"❌ Bundle unpacking error: {e}")
            return None
    
    async def process_unpacked_files(self, unpacked_dir: str, source_url: str) -> Dict:
        """
        Process unpacked files for analysis
        
        Args:
            unpacked_dir: Directory containing unpacked files
            source_url: Original bundle URL
        
        Returns:
            Dictionary with processed file info
        """
        unpacked_path = Path(unpacked_dir)
        
        if not unpacked_path.exists():
            return {'files': [], 'total_size': 0}
        
        # Collect all JS files
        js_files = list(unpacked_path.rglob('*.js'))
        total_size = sum(f.stat().st_size for f in js_files)
        
        # Create file manifest
        file_info = []
        for js_file in js_files:
            rel_path = js_file.relative_to(unpacked_path)
            file_info.append({
                'path': str(rel_path),
                'size': js_file.stat().st_size,
                'source_bundle': source_url
            })
        
        return {
            'files': file_info,
            'total_files': len(js_files),
            'total_size': total_size,
            'source_bundle': source_url
        }
