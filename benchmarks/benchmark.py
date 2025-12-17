#!/usr/bin/env python3
"""
JS Scanner Benchmark Suite (v3.0)
Compare against other tools on real targets
"""
import asyncio
import time
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jsscanner.core.engine import ScanEngine
from jsscanner.utils.logger import setup_logger


class BenchmarkRunner:
    """Run comparative benchmarks"""
    
    def __init__(self, targets_file: str):
        """Initialize benchmark runner"""
        self.targets_file = Path(targets_file)
        self.logger = setup_logger('benchmark')
        self.results = {
            'js-scanner': {},
            'xnLinkFinder': {},
            'jsluice': {}
        }
    
    def load_targets(self) -> List[str]:
        """Load targets from file"""
        if not self.targets_file.exists():
            self.logger.error(f"Targets file not found: {self.targets_file}")
            return []
        
        with open(self.targets_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    async def benchmark_js_scanner(self, target: str) -> Dict:
        """Benchmark JS Scanner"""
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"🔍 JS Scanner: {target}")
        self.logger.info(f"{'='*70}")
        
        start = time.time()
        
        config = {
            'threads': 50,
            'recover_source_maps': True,
            'skip_beautification': False,
            'force_rescan': True
        }
        
        engine = ScanEngine(config, f"benchmark-{target.replace('https://', '').replace('http://', '')}")
        
        try:
            await engine.run([target], use_subjs=True, subjs_only=False)
            
            duration = time.time() - start
            
            # Collect metrics
            result_path = Path(f"results/benchmark-{target.replace('https://', '').replace('http://', '')}")
            
            endpoints = self._count_lines(result_path / 'extracts' / 'endpoints.txt')
            params = self._count_lines(result_path / 'extracts' / 'params.txt')
            secrets = self._count_secrets(result_path / 'trufflehog_full.json')
            domains = len(list((result_path / 'extracts').glob('*/endpoints.json')))
            
            return {
                'success': True,
                'duration': duration,
                'endpoints': endpoints,
                'params': params,
                'secrets': secrets,
                'domain_files': domains,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"❌ JS Scanner failed: {e}")
            return {
                'success': False,
                'duration': time.time() - start,
                'error': str(e)
            }
    
    def benchmark_xnLinkFinder(self, target: str) -> Dict:
        """Benchmark xnLinkFinder (if installed)"""
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"🔍 xnLinkFinder: {target}")
        self.logger.info(f"{'='*70}")
        
        # Check if installed
        if not shutil.which('xnLinkFinder'):
            self.logger.warning("⚠️  xnLinkFinder not installed, skipping")
            return {'success': False, 'error': 'Not installed'}
        
        start = time.time()
        output_file = Path('benchmark_xnl.txt')
        
        try:
            result = subprocess.run(
                ['xnLinkFinder', '-i', target, '-o', str(output_file)],
                capture_output=True,
                timeout=300
            )
            
            duration = time.time() - start
            
            if result.returncode == 0 and output_file.exists():
                endpoints = self._count_lines(output_file)
                output_file.unlink()  # Cleanup
                
                return {
                    'success': True,
                    'duration': duration,
                    'endpoints': endpoints,
                    'params': 0,  # xnLinkFinder doesn't separate params
                    'secrets': 0,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'duration': duration,
                    'error': result.stderr.decode()
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': 300,
                'error': 'Timeout after 5 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'duration': time.time() - start,
                'error': str(e)
            }
    
    async def run_benchmark(self):
        """Run full benchmark suite"""
        targets = self.load_targets()
        
        if not targets:
            self.logger.error("No targets to benchmark")
            return
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info(f"🏁 Starting benchmark: {len(targets)} targets")
        self.logger.info(f"{'='*70}")
        
        for target in targets:
            # Benchmark JS Scanner
            self.results['js-scanner'][target] = await self.benchmark_js_scanner(target)
            
            # Benchmark competitors (if installed)
            self.results['xnLinkFinder'][target] = self.benchmark_xnLinkFinder(target)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate benchmark report"""
        print("\n" + "="*70)
        print("📊 BENCHMARK RESULTS")
        print("="*70)
        
        # Aggregate totals
        totals = {
            'js-scanner': {'endpoints': 0, 'params': 0, 'secrets': 0, 'time': 0, 'count': 0},
            'xnLinkFinder': {'endpoints': 0, 'params': 0, 'secrets': 0, 'time': 0, 'count': 0}
        }
        
        for tool in ['js-scanner', 'xnLinkFinder']:
            for target, result in self.results[tool].items():
                if result.get('success'):
                    totals[tool]['endpoints'] += result.get('endpoints', 0)
                    totals[tool]['params'] += result.get('params', 0)
                    totals[tool]['secrets'] += result.get('secrets', 0)
                    totals[tool]['time'] += result.get('duration', 0)
                    totals[tool]['count'] += 1
        
        # Display comparison table
        print(f"\n{'Tool':<15} | {'Endpoints':<10} | {'Params':<10} | {'Secrets':<8} | {'Avg Time':<10}")
        print("-" * 70)
        
        for tool, data in totals.items():
            if data['count'] > 0:
                avg_time = data['time'] / data['count']
                print(
                    f"{tool:<15} | "
                    f"{data['endpoints']:<10} | "
                    f"{data['params']:<10} | "
                    f"{data['secrets']:<8} | "
                    f"{avg_time:<10.2f}s"
                )
        
        # Save detailed results
        output_file = Path('benchmarks') / 'benchmark_results.json'
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Detailed results saved to: {output_file}")
    
    def _count_lines(self, filepath: Path) -> int:
        """Count non-empty lines in file"""
        if not filepath.exists():
            return 0
        try:
            with open(filepath) as f:
                return len([line for line in f if line.strip()])
        except:
            return 0
    
    def _count_secrets(self, filepath: Path) -> int:
        """Count secrets in TruffleHog output"""
        if not filepath.exists():
            return 0
        try:
            with open(filepath) as f:
                data = json.load(f)
                if isinstance(data, list):
                    return len(data)
                return 0
        except:
            return 0


async def main():
    """Main benchmark entry point"""
    if len(sys.argv) < 2:
        print("Usage: python benchmarks/benchmark.py targets.txt")
        sys.exit(1)
    
    runner = BenchmarkRunner(sys.argv[1])
    await runner.run_benchmark()


if __name__ == '__main__':
    asyncio.run(main())
