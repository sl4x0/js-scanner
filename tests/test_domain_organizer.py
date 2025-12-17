#!/usr/bin/env python3
"""Test domain organizer to find the bug"""
import asyncio
import json
from pathlib import Path
from jsscanner.modules.domain_organizer import DomainExtractOrganizer
from jsscanner.utils.logger import setup_logger

async def test_domain_organizer():
    """Test domain organization with mock data"""
    
    logger = setup_logger('test')
    temp_path = Path('test_output/extracts')
    temp_path.mkdir(parents=True, exist_ok=True)
    
    organizer = DomainExtractOrganizer(str(temp_path), logger)
    
    # Create mock extract database
    mock_extracts_db = {
        'endpoints': {
            '/api/users': {
                'sources': [
                    {'file': 'https://example.com/app.js', 'domain': 'example.com', 'occurrences': 1},
                    {'file': 'https://api.example.com/bundle.js', 'domain': 'api.example.com', 'occurrences': 2}
                ],
                'total_count': 3,
                'domains': {'example.com', 'api.example.com'}
            },
            '/api/EXPR/orders': {
                'sources': [
                    {'file': 'https://example.com/checkout.js', 'domain': 'example.com', 'occurrences': 1}
                ],
                'total_count': 1,
                'domains': {'example.com'}
            }
        },
        'params': {
            'userId': {
                'sources': [
                    {'file': 'https://example.com/app.js', 'domain': 'example.com', 'occurrences': 5}
                ],
                'total_count': 5,
                'domains': {'example.com'}
            }
        },
        'domains': {},
        'links': {},
        'words': {}
    }
    
    # Test domain organization
    print("Testing domain organization...")
    domain_data = await organizer.save_by_domain(mock_extracts_db)
    
    # Validate output
    print("\nValidation:")
    for domain, data in domain_data.items():
        domain_dir = temp_path / domain
        print(f"\n✓ Domain: {domain}")
        
        endpoints_file = domain_dir / 'endpoints.json'
        if endpoints_file.exists():
            print(f"  ✅ endpoints.json exists")
            with open(endpoints_file) as f:
                content = json.load(f)
                print(f"     Endpoints: {content.get('count', 0)}")
                print(f"     Content: {content.get('endpoints', [])}")
        else:
            print(f"  ❌ endpoints.json MISSING")
        
        params_file = domain_dir / 'params.txt'
        if params_file.exists():
            print(f"  ✅ params.txt exists")
        else:
            print(f"  ❌ params.txt MISSING")
    
    print(f"\n✅ Test complete. Check: {temp_path}")

if __name__ == '__main__':
    asyncio.run(test_domain_organizer())
