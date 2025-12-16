#!/usr/bin/env python3
"""
Extraction Accuracy Tests
Validates endpoint, parameter, and domain extraction
"""
import json
from pathlib import Path


class ExtractionValidator:
    """Validates extraction accuracy"""
    
    def __init__(self, test_content: str):
        """
        Initialize validator with test content
        
        Args:
            test_content: JavaScript content to analyze
        """
        self.content = test_content
        self.expected_endpoints = []
        self.expected_params = []
        self.found_endpoints = []
        self.found_params = []
    
    def add_expected_endpoint(self, endpoint: str):
        """Add expected endpoint"""
        self.expected_endpoints.append(endpoint)
    
    def add_expected_param(self, param: str):
        """Add expected parameter"""
        self.expected_params.append(param)
    
    def validate_against_results(self, results_dir: Path) -> dict:
        """
        Validate against scan results
        
        Args:
            results_dir: Path to scan results directory
            
        Returns:
            Validation report
        """
        report = {
            'endpoints': {
                'expected': len(self.expected_endpoints),
                'found': 0,
                'matched': 0,
                'missing': [],
                'extra': []
            },
            'params': {
                'expected': len(self.expected_params),
                'found': 0,
                'matched': 0,
                'missing': [],
                'extra': []
            }
        }
        
        # Read extracted endpoints
        extracts_dir = results_dir / 'extracts'
        if not extracts_dir.exists():
            return report
        
        # Check domain-specific extracts
        for domain_dir in extracts_dir.iterdir():
            if domain_dir.is_dir():
                # Read endpoints.json
                endpoints_file = domain_dir / 'endpoints.json'
                if endpoints_file.exists():
                    with open(endpoints_file, 'r') as f:
                        data = json.load(f)
                        self.found_endpoints.extend(data.get('endpoints', []))
                
                # Read params.txt
                params_file = domain_dir / 'params.txt'
                if params_file.exists():
                    with open(params_file, 'r') as f:
                        self.found_params.extend([l.strip() for l in f if l.strip()])
        
        # Calculate matches
        report['endpoints']['found'] = len(self.found_endpoints)
        report['params']['found'] = len(self.found_params)
        
        for endpoint in self.expected_endpoints:
            if endpoint in self.found_endpoints:
                report['endpoints']['matched'] += 1
            else:
                report['endpoints']['missing'].append(endpoint)
        
        for param in self.expected_params:
            if param in self.found_params:
                report['params']['matched'] += 1
            else:
                report['params']['missing'].append(param)
        
        # Find extras
        expected_set = set(self.expected_endpoints)
        found_set = set(self.found_endpoints)
        report['endpoints']['extra'] = list(found_set - expected_set)
        
        expected_set = set(self.expected_params)
        found_set = set(self.found_params)
        report['params']['extra'] = list(found_set - expected_set)
        
        return report
    
    def print_report(self, report: dict):
        """Print validation report"""
        print("\n" + "="*80)
        print("EXTRACTION VALIDATION REPORT")
        print("="*80)
        
        # Endpoints
        print("\n📍 ENDPOINTS")
        print(f"   Expected: {report['endpoints']['expected']}")
        print(f"   Found: {report['endpoints']['found']}")
        print(f"   Matched: {report['endpoints']['matched']}")
        
        if report['endpoints']['missing']:
            print(f"\n   ⚠️  Missing ({len(report['endpoints']['missing'])}):")
            for endpoint in report['endpoints']['missing'][:5]:
                print(f"      - {endpoint}")
            if len(report['endpoints']['missing']) > 5:
                print(f"      ... and {len(report['endpoints']['missing']) - 5} more")
        
        if report['endpoints']['extra']:
            print(f"\n   ℹ️  Extra found ({len(report['endpoints']['extra'])}):")
            for endpoint in report['endpoints']['extra'][:5]:
                print(f"      - {endpoint}")
            if len(report['endpoints']['extra']) > 5:
                print(f"      ... and {len(report['endpoints']['extra']) - 5} more")
        
        # Parameters
        print("\n🔧 PARAMETERS")
        print(f"   Expected: {report['params']['expected']}")
        print(f"   Found: {report['params']['found']}")
        print(f"   Matched: {report['params']['matched']}")
        
        if report['params']['missing']:
            print(f"\n   ⚠️  Missing ({len(report['params']['missing'])}):")
            for param in report['params']['missing'][:5]:
                print(f"      - {param}")
            if len(report['params']['missing']) > 5:
                print(f"      ... and {len(report['params']['missing']) - 5} more")
        
        # Accuracy
        print("\n" + "="*80)
        endpoint_accuracy = (report['endpoints']['matched'] / report['endpoints']['expected'] * 100) if report['endpoints']['expected'] > 0 else 0
        param_accuracy = (report['params']['matched'] / report['params']['expected'] * 100) if report['params']['expected'] > 0 else 0
        
        print(f"Endpoint Accuracy: {endpoint_accuracy:.1f}%")
        print(f"Parameter Accuracy: {param_accuracy:.1f}%")
        print("="*80 + "\n")
        
        return endpoint_accuracy >= 70 and param_accuracy >= 70


def test_known_patterns():
    """Test with known patterns"""
    test_js = """
    // Known endpoints
    const API_ENDPOINTS = {
        users: '/api/v1/users',
        products: '/api/v1/products',
        orders: '/api/v1/orders',
        checkout: '/api/v1/checkout'
    };
    
    // Known parameters
    fetch('/api/v1/users?userId=123&page=1&limit=10');
    
    axios.post('/api/v1/orders', {
        orderId: 'ORDER123',
        customerId: 'CUST456',
        totalAmount: 99.99,
        paymentMethod: 'credit_card'
    });
    """
    
    validator = ExtractionValidator(test_js)
    
    # Expected endpoints
    validator.add_expected_endpoint('/api/v1/users')
    validator.add_expected_endpoint('/api/v1/products')
    validator.add_expected_endpoint('/api/v1/orders')
    validator.add_expected_endpoint('/api/v1/checkout')
    
    # Expected parameters
    validator.add_expected_param('userId')
    validator.add_expected_param('page')
    validator.add_expected_param('limit')
    validator.add_expected_param('orderId')
    validator.add_expected_param('customerId')
    validator.add_expected_param('totalAmount')
    validator.add_expected_param('paymentMethod')
    
    return validator


if __name__ == '__main__':
    print("Extraction accuracy tests require scan results to validate against")
    print("Run integration tests first to generate scan results")
