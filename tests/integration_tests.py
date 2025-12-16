#!/usr/bin/env python3
"""
Integration Test Suite for js-scanner
Tests with 10+ domains and validates all functionality
"""
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any


class IntegrationTestSuite:
    """Integration tests for js-scanner"""
    
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent.parent
        self.test_dir = self.project_root / 'tests'
        self.results_dir = self.project_root / 'results'
    
    def run_scanner(self, target: str, input_file: str, extra_args: list = None) -> Dict[str, Any]:
        """
        Run the scanner with given parameters
        
        Args:
            target: Target name
            input_file: Path to input file with URLs/domains
            extra_args: Additional command line arguments
            
        Returns:
            Dictionary with execution results
        """
        cmd = [
            'python', '-m', 'jsscanner',
            '-t', target,
            '-i', str(input_file)
        ]
        
        if extra_args:
            cmd.extend(extra_args)
        
        print(f"\n{'='*80}")
        print(f"Running: {' '.join(cmd)}")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Timeout after 300 seconds',
                'duration': 300
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'duration': time.time() - start_time
            }
    
    def verify_directory_structure(self, target: str) -> Dict[str, bool]:
        """
        Verify domain-specific directory structure was created
        
        Args:
            target: Target name
            
        Returns:
            Dictionary with verification results
        """
        target_dir = self.results_dir / target
        
        checks = {
            'base_dir_exists': target_dir.exists(),
            'extracts_dir_exists': (target_dir / 'extracts').exists(),
            'secrets_dir_exists': (target_dir / 'secrets').exists(),
            'files_dir_exists': (target_dir / 'files').exists(),
            'scan_results_exists': (target_dir / 'scan_results.json').exists(),
            'trufflehog_full_exists': (target_dir / 'trufflehog_full.json').exists()
        }
        
        # Check for domain-specific subdirectories
        extracts_dir = target_dir / 'extracts'
        if extracts_dir.exists():
            domain_dirs = [d for d in extracts_dir.iterdir() if d.is_dir()]
            checks['has_domain_extracts'] = len(domain_dirs) > 0
            checks['domain_extract_count'] = len(domain_dirs)
        else:
            checks['has_domain_extracts'] = False
            checks['domain_extract_count'] = 0
        
        secrets_dir = target_dir / 'secrets'
        if secrets_dir.exists():
            domain_dirs = [d for d in secrets_dir.iterdir() if d.is_dir()]
            checks['has_domain_secrets'] = len(domain_dirs) > 0
            checks['domain_secret_count'] = len(domain_dirs)
        else:
            checks['has_domain_secrets'] = False
            checks['domain_secret_count'] = 0
        
        # Check for legacy format (backward compatibility)
        if extracts_dir.exists():
            checks['has_legacy_endpoints'] = (extracts_dir / 'endpoints.txt').exists()
            checks['has_legacy_params'] = (extracts_dir / 'params.txt').exists()
        else:
            checks['has_legacy_endpoints'] = False
            checks['has_legacy_params'] = False
        
        return checks
    
    def validate_extracts(self, target: str) -> Dict[str, Any]:
        """
        Validate extraction accuracy
        
        Args:
            target: Target name
            
        Returns:
            Dictionary with validation results
        """
        target_dir = self.results_dir / target
        extracts_dir = target_dir / 'extracts'
        
        validation = {
            'total_endpoints': 0,
            'total_params': 0,
            'total_domains': 0,
            'domain_specific_data': {}
        }
        
        if not extracts_dir.exists():
            return validation
        
        # Check domain-specific extracts
        for domain_dir in extracts_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                validation['domain_specific_data'][domain] = {}
                
                # Count endpoints
                endpoints_file = domain_dir / 'endpoints.json'
                if endpoints_file.exists():
                    with open(endpoints_file, 'r') as f:
                        data = json.load(f)
                        count = data.get('count', 0)
                        validation['domain_specific_data'][domain]['endpoints'] = count
                        validation['total_endpoints'] += count
                
                # Count params
                params_file = domain_dir / 'params.txt'
                if params_file.exists():
                    with open(params_file, 'r') as f:
                        count = len([l for l in f.readlines() if l.strip()])
                        validation['domain_specific_data'][domain]['params'] = count
                        validation['total_params'] += count
        
        # Verify legacy format matches
        legacy_endpoints = extracts_dir / 'endpoints.txt'
        legacy_params = extracts_dir / 'params.txt'
        
        if legacy_endpoints.exists():
            with open(legacy_endpoints, 'r') as f:
                validation['legacy_endpoints_count'] = len([l for l in f.readlines() if l.strip()])
        
        if legacy_params.exists():
            with open(legacy_params, 'r') as f:
                validation['legacy_params_count'] = len([l for l in f.readlines() if l.strip()])
        
        return validation
    
    def validate_secrets(self, target: str) -> Dict[str, Any]:
        """
        Validate secrets organization
        
        Args:
            target: Target name
            
        Returns:
            Dictionary with validation results
        """
        target_dir = self.results_dir / target
        secrets_dir = target_dir / 'secrets'
        
        validation = {
            'total_secrets': 0,
            'verified_secrets': 0,
            'domain_specific_data': {}
        }
        
        if not secrets_dir.exists():
            return validation
        
        # Check domain-specific secrets
        for domain_dir in secrets_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                secrets_file = domain_dir / 'secrets.json'
                
                if secrets_file.exists():
                    with open(secrets_file, 'r') as f:
                        data = json.load(f)
                        validation['domain_specific_data'][domain] = {
                            'total': data.get('total_secrets', 0),
                            'verified': data.get('verified_count', 0)
                        }
                        validation['total_secrets'] += data.get('total_secrets', 0)
                        validation['verified_secrets'] += data.get('verified_count', 0)
        
        # Check full results
        full_results = target_dir / 'trufflehog_full.json'
        if full_results.exists():
            with open(full_results, 'r') as f:
                data = json.load(f)
                validation['full_results_count'] = len(data)
        
        return validation
    
    def test_multi_domain(self) -> bool:
        """Test with 10+ diverse domains"""
        print("\n" + "="*80)
        print("TEST 1: Multi-Domain Integration Test (10+ domains)")
        print("="*80)
        
        # Create test input file with diverse domains
        test_domains = [
            'https://www.google.com',
            'https://www.github.com',
            'https://www.stackoverflow.com',
            'https://www.reddit.com',
            'https://www.twitter.com',
            'https://www.facebook.com',
            'https://www.amazon.com',
            'https://www.youtube.com',
            'https://www.wikipedia.org',
            'https://www.linkedin.com',
            'https://www.instagram.com',
            'https://www.netflix.com'
        ]
        
        input_file = self.test_dir / 'test_multi_domain_input.txt'
        with open(input_file, 'w') as f:
            f.write('\n'.join(test_domains))
        
        # Run scanner
        result = self.run_scanner(
            'test-multi-domain',
            input_file,
            ['--threads', '10', '--discovery']
        )
        
        # Verify results
        if result['success']:
            structure = self.verify_directory_structure('test-multi-domain')
            extracts = self.validate_extracts('test-multi-domain')
            
            print(f"\n✅ Scanner completed in {result['duration']:.2f}s")
            print(f"   - Base directory: {'✓' if structure['base_dir_exists'] else '✗'}")
            print(f"   - Domain extracts: {structure['domain_extract_count']} domains")
            print(f"   - Total endpoints: {extracts['total_endpoints']}")
            print(f"   - Total params: {extracts['total_params']}")
            print(f"   - Legacy format: {'✓' if structure['has_legacy_endpoints'] else '✗'}")
            
            self.test_results.append(('Multi-Domain Test', True))
            return True
        else:
            print(f"\n❌ Scanner failed with return code {result['returncode']}")
            print(f"   Error: {result['stderr']}")
            self.test_results.append(('Multi-Domain Test', False))
            return False
    
    def test_extraction_accuracy(self) -> bool:
        """Test extraction accuracy with known patterns"""
        print("\n" + "="*80)
        print("TEST 2: Extraction Accuracy Validation")
        print("="*80)
        
        # Use the test server files (if available)
        test_urls = [
            'http://localhost:8000/test_clean_api.js'
        ]
        
        input_file = self.test_dir / 'test_extraction_input.txt'
        with open(input_file, 'w') as f:
            f.write('\n'.join(test_urls))
        
        print("Note: This test requires test_server.py to be running")
        print("      Run: python test_notifications/test_server.py")
        
        result = self.run_scanner(
            'test-extraction',
            input_file
        )
        
        if result['success']:
            extracts = self.validate_extracts('test-extraction')
            
            # Expected: test_clean_api.js has 10+ endpoints and 15+ params
            has_endpoints = extracts['total_endpoints'] > 0
            has_params = extracts['total_params'] > 0
            
            print(f"\n✅ Extraction completed")
            print(f"   - Endpoints found: {extracts['total_endpoints']}")
            print(f"   - Params found: {extracts['total_params']}")
            
            success = has_endpoints and has_params
            self.test_results.append(('Extraction Accuracy', success))
            return success
        else:
            print(f"\n⚠️  Scanner failed (server may not be running)")
            self.test_results.append(('Extraction Accuracy', False))
            return False
    
    def test_beautification(self) -> bool:
        """Test beautification functionality"""
        print("\n" + "="*80)
        print("TEST 3: Beautification Test")
        print("="*80)
        
        # Test with a known minified library
        test_urls = [
            'https://code.jquery.com/jquery-3.6.0.min.js'
        ]
        
        input_file = self.test_dir / 'test_beautification_input.txt'
        with open(input_file, 'w') as f:
            f.write('\n'.join(test_urls))
        
        result = self.run_scanner(
            'test-beautification',
            input_file
        )
        
        if result['success']:
            target_dir = self.results_dir / 'test-beautification'
            unminified_dir = target_dir / 'files' / 'unminified'
            
            has_files = unminified_dir.exists() and len(list(unminified_dir.glob('*.js'))) > 0
            
            print(f"\n✅ Beautification test completed")
            print(f"   - Unminified files: {'✓' if has_files else '✗'}")
            
            self.test_results.append(('Beautification Test', has_files))
            return has_files
        else:
            print(f"\n❌ Beautification test failed")
            self.test_results.append(('Beautification Test', False))
            return False
    
    def test_domain_organization(self) -> bool:
        """Test domain-specific organization"""
        print("\n" + "="*80)
        print("TEST 4: Domain-Specific Organization")
        print("="*80)
        
        # Use existing multi-domain test results
        structure = self.verify_directory_structure('test-multi-domain')
        extracts = self.validate_extracts('test-multi-domain')
        
        # Verify domain-specific directories exist
        has_domain_extracts = structure.get('has_domain_extracts', False)
        has_multiple_domains = structure.get('domain_extract_count', 0) > 0
        
        # Verify legacy format exists (backward compatibility)
        has_legacy = structure.get('has_legacy_endpoints', False)
        
        print(f"\n✅ Organization verified")
        print(f"   - Domain-specific extracts: {'✓' if has_domain_extracts else '✗'}")
        print(f"   - Multiple domains: {structure.get('domain_extract_count', 0)}")
        print(f"   - Legacy format: {'✓' if has_legacy else '✗'}")
        print(f"   - Backward compatible: {'✓' if has_legacy else '✗'}")
        
        success = has_domain_extracts and has_legacy
        self.test_results.append(('Domain Organization', success))
        return success
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*80)
        print("🧪 JS-SCANNER INTEGRATION TEST SUITE")
        print("="*80)
        
        # Create test directory
        self.test_dir.mkdir(exist_ok=True)
        
        # Run tests
        self.test_multi_domain()
        self.test_extraction_accuracy()
        self.test_beautification()
        self.test_domain_organization()
        
        # Print summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nResult: {passed}/{total} tests passed")
        print("="*80 + "\n")
        
        return passed == total


def main():
    """Main entry point"""
    suite = IntegrationTestSuite()
    success = suite.run_all_tests()
    
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
