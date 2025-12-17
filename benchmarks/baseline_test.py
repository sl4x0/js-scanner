#!/usr/bin/env python3
"""
Baseline performance test for v2.0
Run this BEFORE implementing fixes to establish comparison metrics
"""
import asyncio
import time
import json
from pathlib import Path
from jsscanner.core.engine import ScanEngine

async def run_baseline_scan():
    """Run baseline scan on test targets"""
    
    targets = [
        "https://hackerone.com",
        "https://target.com",
        "https://kick.com"
    ]
    
    results = {
        'version': 'v2.0-baseline',
        'timestamp': time.time(),
        'targets': []
    }
    
    for target in targets:
        print(f"\n{'='*60}")
        print(f"Scanning: {target}")
        print(f"{'='*60}")
        
        start = time.time()
        
        config = {
            'threads': 50,
            'recover_source_maps': True,
            'skip_beautification': False,
            'force_rescan': True
        }
        
        engine = ScanEngine(config, target)
        
        try:
            await engine.run([target], use_subjs=True, subjs_only=False)
            
            # Collect metrics
            result_path = Path(f"results/{target.replace('https://', '').replace('http://', '')}")
            
            endpoints_file = result_path / 'extracts' / 'endpoints.txt'
            params_file = result_path / 'extracts' / 'params.txt'
            words_file = result_path / 'extracts' / 'wordlist.txt'
            
            metrics = {
                'target': target,
                'duration': time.time() - start,
                'endpoints': len(open(endpoints_file).readlines()) if endpoints_file.exists() else 0,
                'params': len(open(params_file).readlines()) if params_file.exists() else 0,
                'words': len(open(words_file).readlines()) if words_file.exists() else 0,
                'domain_extracts_populated': len(list((result_path / 'extracts').glob('*/endpoints.json')))
            }
            
            results['targets'].append(metrics)
            
            print(f"\n✅ Baseline Metrics:")
            print(f"   Endpoints: {metrics['endpoints']}")
            print(f"   Parameters: {metrics['params']}")
            print(f"   Words: {metrics['words']}")
            print(f"   Duration: {metrics['duration']:.2f}s")
            print(f"   Domain files: {metrics['domain_extracts_populated']}")
            
        except Exception as e:
            print(f"❌ Baseline scan failed: {e}")
            results['targets'].append({
                'target': target,
                'error': str(e)
            })
    
    # Save baseline
    baseline_file = Path('benchmarks') / 'baseline_v2.0.json'
    baseline_file.parent.mkdir(exist_ok=True)
    
    with open(baseline_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Baseline saved to: {baseline_file}")
    return results

if __name__ == '__main__':
    asyncio.run(run_baseline_scan())
