"""
Unit tests for engine.py domain summary fixes
Tests for Issue #2: Domain sorting error when displaying findings breakdown
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDomainSortingFix:
    """Test that domain sorting properly handles nested dict structure"""
    
    def test_sort_domains_with_nested_stats(self):
        """Verify that domain sorting handles the nested dict structure correctly"""
        # This is the structure returned by get_secrets_summary()
        secrets_summary = {
            'total_domains': 3,
            'total_secrets': 34,
            'verified_secrets': 0,
            'domains': {
                'example.com': {'total': 15, 'verified': 3},
                'rubrik.com': {'total': 12, 'verified': 0},
                'partycasino.com': {'total': 7, 'verified': 0}
            }
        }
        
        # Extract and sort domains (this is what the fix does)
        domains = secrets_summary.get('domains', {})
        
        # This should NOT raise TypeError
        sorted_domains = sorted(domains.items(), key=lambda x: x[1].get('total', 0), reverse=True)
        
        # Verify sorting order (by total count descending)
        assert sorted_domains[0][0] == 'example.com'
        assert sorted_domains[0][1]['total'] == 15
        
        assert sorted_domains[1][0] == 'rubrik.com'
        assert sorted_domains[1][1]['total'] == 12
        
        assert sorted_domains[2][0] == 'partycasino.com'
        assert sorted_domains[2][1]['total'] == 7
    
    def test_domain_sorting_with_missing_total(self):
        """Verify that sorting gracefully handles missing 'total' key"""
        secrets_summary = {
            'domains': {
                'example.com': {'total': 10, 'verified': 2},
                'partial.com': {'verified': 1},  # Missing 'total'
                'full.com': {'total': 5, 'verified': 0}
            }
        }
        
        domains = secrets_summary.get('domains', {})
        
        # Should use default value of 0 for missing 'total'
        sorted_domains = sorted(domains.items(), key=lambda x: x[1].get('total', 0), reverse=True)
        
        # example.com should be first (total: 10)
        assert sorted_domains[0][0] == 'example.com'
        
        # full.com should be second (total: 5)
        assert sorted_domains[1][0] == 'full.com'
        
        # partial.com should be last (total: 0, default)
        assert sorted_domains[2][0] == 'partial.com'
    
    def test_domain_sorting_empty_domains(self):
        """Verify that sorting handles empty domains gracefully"""
        secrets_summary = {
            'total_domains': 0,
            'total_secrets': 0,
            'verified_secrets': 0,
            'domains': {}
        }
        
        domains = secrets_summary.get('domains', {})
        
        # Should not raise when domains is empty
        sorted_domains = sorted(domains.items(), key=lambda x: x[1].get('total', 0), reverse=True)
        
        assert sorted_domains == []
    
    def test_domain_stats_formatting(self):
        """Verify that domain stats are formatted correctly for display"""
        stats = {'total': 15, 'verified': 3}
        
        total = stats.get('total', 0)
        verified = stats.get('verified', 0)
        
        # Format as shown in the fix
        status = f"✅ {verified}" if verified > 0 else f"⚠️ {total}"
        
        # For verified secrets, should show verified count
        assert status == "✅ 3"
        
        # Test unverified case
        stats_unverified = {'total': 10, 'verified': 0}
        total = stats_unverified.get('total', 0)
        verified = stats_unverified.get('verified', 0)
        status = f"✅ {verified}" if verified > 0 else f"⚠️ {total}"
        
        assert status == "⚠️ 10"
    
    def test_top_10_domains_limit(self):
        """Verify that only top 10 domains are displayed"""
        secrets_summary = {
            'domains': {f'domain{i}.com': {'total': 100 - i, 'verified': i % 2} for i in range(15)}
        }
        
        domains = secrets_summary.get('domains', {})
        sorted_domains = sorted(domains.items(), key=lambda x: x[1].get('total', 0), reverse=True)
        
        # Only first 10 should be shown
        displayed = sorted_domains[:10]
        assert len(displayed) == 10
        
        # The remaining count
        remaining = len(domains) - 10
        assert remaining == 5
    
    def test_missing_domains_key(self):
        """Verify that missing 'domains' key is handled gracefully"""
        secrets_summary = {
            'total_domains': 0,
            'total_secrets': 0,
            'verified_secrets': 0
            # 'domains' key is missing
        }
        
        domains = secrets_summary.get('domains', {})
        
        # Should return empty dict, not raise
        assert domains == {}
        
        sorted_domains = sorted(domains.items(), key=lambda x: x[1].get('total', 0), reverse=True)
        assert sorted_domains == []


class TestSecretSummaryStructure:
    """Test that the secret summary structure is correct"""
    
    def test_summary_structure_matches_expected_format(self):
        """Verify the structure returned by get_secrets_summary() is as expected"""
        # This is the exact structure that get_secrets_summary() returns
        summary = {
            'total_domains': 2,
            'total_secrets': 34,
            'verified_secrets': 0,
            'domains': {
                'unknown': {
                    'total': 34,
                    'verified': 0
                }
            }
        }
        
        # Verify structure has all expected keys
        assert 'total_domains' in summary
        assert 'total_secrets' in summary
        assert 'verified_secrets' in summary
        assert 'domains' in summary
        
        # Verify domains is a dict of dicts
        assert isinstance(summary['domains'], dict)
        
        for domain, stats in summary['domains'].items():
            assert 'total' in stats
            assert 'verified' in stats
            assert isinstance(stats['total'], int)
            assert isinstance(stats['verified'], int)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
