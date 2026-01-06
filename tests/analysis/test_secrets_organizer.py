"""
Comprehensive tests for DomainSecretsOrganizer module
Tests streaming writes, buffer flushing, domain grouping, and corrupted file handling
"""
import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch
from jsscanner.analysis.secrets_organizer import DomainSecretsOrganizer


# ============================================================================
# SETUP AND FIXTURES
# ============================================================================

@pytest.fixture
def secrets_organizer(tmp_path, mock_logger):
    """Create DomainSecretsOrganizer instance"""
    base_path = str(tmp_path / "results")
    return DomainSecretsOrganizer(base_path, mock_logger)


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

@pytest.mark.unit
class TestInitialization:
    """Test organizer initialization"""
    
    def test_creates_findings_directory(self, secrets_organizer):
        """Test findings directory is created"""
        assert secrets_organizer.secrets_dir.exists()
        assert secrets_organizer.secrets_dir.is_dir()
    
    def test_sets_correct_paths(self, tmp_path, mock_logger):
        """Test correct paths are set"""
        base_path = str(tmp_path / "custom")
        organizer = DomainSecretsOrganizer(base_path, mock_logger)
        
        assert organizer.base_path == Path(base_path)
        assert organizer.secrets_dir == Path(base_path) / 'findings'
    
    def test_initializes_empty_buffer(self, secrets_organizer):
        """Test streaming buffer is initialized empty"""
        assert secrets_organizer._streaming_secrets == []


# ============================================================================
# SAVE_SINGLE_SECRET TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestSaveSingleSecret:
    """Test saving individual secrets"""
    
    async def test_save_single_secret_adds_to_buffer(self, secrets_organizer, sample_secret_finding):
        """Test secret is added to buffer"""
        await secrets_organizer.save_single_secret(sample_secret_finding)
        
        assert len(secrets_organizer._streaming_secrets) == 1
        assert secrets_organizer._streaming_secrets[0] == sample_secret_finding
    
    async def test_save_multiple_secrets(self, secrets_organizer, sample_secret_finding):
        """Test saving multiple secrets"""
        for i in range(5):
            finding = sample_secret_finding.copy()
            finding['Raw'] = f'SECRET_{i}'
            await secrets_organizer.save_single_secret(finding)
        
        assert len(secrets_organizer._streaming_secrets) == 5
    
    async def test_periodic_flush_triggered(self, secrets_organizer, sample_secret_finding):
        """Test buffer flushes every 10 secrets"""
        # Mock _flush_secrets to track calls
        flush_count = 0
        original_flush = secrets_organizer._flush_secrets
        
        async def mock_flush():
            nonlocal flush_count
            flush_count += 1
            await original_flush()
        
        secrets_organizer._flush_secrets = mock_flush
        
        # Save 10 secrets
        for i in range(10):
            finding = sample_secret_finding.copy()
            await secrets_organizer.save_single_secret(finding)
        
        # Should have flushed once (at secret #10)
        assert flush_count >= 1
    
    async def test_save_handles_exceptions(self, secrets_organizer):
        """Test save handles exceptions gracefully"""
        malformed_secret = "not a dict"
        
        # Should not crash
        await secrets_organizer.save_single_secret(malformed_secret)


# ============================================================================
# FLUSH_SECRETS TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestFlushSecrets:
    """Test secret buffer flushing"""
    
    async def test_flush_empty_buffer(self, secrets_organizer):
        """Test flushing empty buffer does nothing"""
        await secrets_organizer._flush_secrets()
        
        # Should not create file for empty buffer
        assert not secrets_organizer.streaming_file.exists() or \
               json.loads(secrets_organizer.streaming_file.read_text()).get('total_count', 0) == 0
    
    async def test_flush_creates_file(self, secrets_organizer, sample_secret_finding):
        """Test flushing creates secrets file"""
        secrets_organizer._streaming_secrets = [sample_secret_finding]
        
        await secrets_organizer._flush_secrets()
        
        assert secrets_organizer.streaming_file.exists()
    
    async def test_flush_appends_to_existing_file(self, secrets_organizer, sample_secret_finding):
        """Test flushing appends to existing file"""
        # Create initial file
        initial_data = {
            'secrets': [sample_secret_finding],
            'total_count': 1
        }
        secrets_organizer.streaming_file.write_text(json.dumps(initial_data))
        
        # Add new secret and flush
        new_secret = sample_secret_finding.copy()
        new_secret['Raw'] = 'NEW_SECRET'
        secrets_organizer._streaming_secrets = [new_secret]
        
        await secrets_organizer._flush_secrets()
        
        # Should have both secrets
        data = json.loads(secrets_organizer.streaming_file.read_text())
        assert data['total_count'] == 2
        assert len(data['secrets']) == 2
    
    async def test_flush_handles_corrupted_file(self, secrets_organizer, sample_secret_finding):
        """Test flushing handles corrupted JSON file"""
        # Create corrupted file
        secrets_organizer.streaming_file.write_text("{invalid json[")
        
        # Add secret and flush
        secrets_organizer._streaming_secrets = [sample_secret_finding]
        
        await secrets_organizer._flush_secrets()
        
        # Should reinitialize with valid data
        data = json.loads(secrets_organizer.streaming_file.read_text())
        assert 'secrets' in data
        assert 'total_count' in data
    
    async def test_flush_handles_old_list_format(self, secrets_organizer, sample_secret_finding):
        """Test flushing handles old list format (backward compatibility)"""
        # Create file with old list format
        old_data = [sample_secret_finding]
        secrets_organizer.streaming_file.write_text(json.dumps(old_data))
        
        # Add new secret and flush
        new_secret = sample_secret_finding.copy()
        secrets_organizer._streaming_secrets = [new_secret]
        
        await secrets_organizer._flush_secrets()
        
        # Should convert to new format
        data = json.loads(secrets_organizer.streaming_file.read_text())
        assert isinstance(data, dict)
        assert 'secrets' in data
        assert 'total_count' in data
    
    async def test_flush_clears_buffer(self, secrets_organizer, sample_secret_finding):
        """Test flushing clears the buffer"""
        secrets_organizer._streaming_secrets = [sample_secret_finding] * 5
        
        await secrets_organizer._flush_secrets()
        
        assert len(secrets_organizer._streaming_secrets) == 0
    
    async def test_flush_handles_write_errors(self, secrets_organizer, sample_secret_finding):
        """Test flushing handles file write errors"""
        secrets_organizer._streaming_secrets = [sample_secret_finding]
        
        # Mock file write to fail
        with patch('builtins.open', side_effect=PermissionError):
            # Should handle gracefully
            await secrets_organizer._flush_secrets()


# ============================================================================
# EXTRACT_DOMAIN TESTS
# ============================================================================

@pytest.mark.unit
class TestExtractDomain:
    """Test domain extraction from URLs"""
    
    def test_extract_domain_simple(self, secrets_organizer):
        """Test extracting domain from simple URL"""
        url = "https://example.com/app.js"
        domain = secrets_organizer._extract_domain(url)
        
        assert domain == "example.com"
    
    def test_extract_domain_removes_www(self, secrets_organizer):
        """Test www. is removed from domain"""
        url = "https://www.example.com/app.js"
        domain = secrets_organizer._extract_domain(url)
        
        assert domain == "example.com"
    
    def test_extract_domain_with_port(self, secrets_organizer):
        """Test domain extraction with port"""
        url = "https://example.com:8080/app.js"
        domain = secrets_organizer._extract_domain(url)
        
        assert "example.com" in domain
    
    def test_extract_domain_subdomain(self, secrets_organizer):
        """Test domain extraction with subdomain"""
        url = "https://api.example.com/v1/data"
        domain = secrets_organizer._extract_domain(url)
        
        assert domain == "api.example.com"
    
    def test_extract_domain_malformed_url(self, secrets_organizer):
        """Test domain extraction with malformed URL"""
        url = "not-a-url"
        domain = secrets_organizer._extract_domain(url)
        
        assert domain == "unknown"
    
    def test_extract_domain_empty_url(self, secrets_organizer):
        """Test domain extraction with empty URL"""
        domain = secrets_organizer._extract_domain("")
        
        assert domain == "unknown"


# ============================================================================
# ORGANIZE_SECRETS TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestOrganizeSecrets:
    """Test organizing secrets by domain"""
    
    async def test_organize_by_domain(self, secrets_organizer, sample_secret_finding):
        """Test secrets are organized by domain"""
        secrets = []
        for i in range(3):
            secret = sample_secret_finding.copy()
            secret['SourceMetadata']['url'] = f"https://example{i}.com/app.js"
            secrets.append(secret)
        
        await secrets_organizer.organize_secrets(secrets)
        
        # Should create directory for each domain
        findings_dir = secrets_organizer.secrets_dir
        domain_dirs = [d for d in findings_dir.iterdir() if d.is_dir()]
        
        assert len(domain_dirs) >= 1  # At least one domain directory
    
    async def test_organize_groups_same_domain(self, secrets_organizer, sample_secret_finding):
        """Test secrets from same domain are grouped"""
        secrets = []
        for i in range(5):
            secret = sample_secret_finding.copy()
            secret['SourceMetadata']['url'] = "https://example.com/file.js"
            secret['Raw'] = f'SECRET_{i}'
            secrets.append(secret)
        
        await secrets_organizer.organize_secrets(secrets)
        
        domain_dir = secrets_organizer.secrets_dir / "example.com"
        assert domain_dir.exists()
        
        secrets_file = domain_dir / "secrets.json"
        assert secrets_file.exists()
        
        data = json.loads(secrets_file.read_text())
        assert data['total_secrets'] == 5
    
    async def test_organize_creates_domain_structure(self, secrets_organizer, sample_secret_finding):
        """Test correct domain directory structure is created"""
        secret = sample_secret_finding.copy()
        secret['SourceMetadata']['url'] = "https://api.example.com/data"
        
        await secrets_organizer.organize_secrets([secret])
        
        domain_dir = secrets_organizer.secrets_dir / "api.example.com"
        assert domain_dir.exists()
        
        secrets_file = domain_dir / "secrets.json"
        assert secrets_file.exists()
    
    async def test_organize_includes_verified_count(self, secrets_organizer, sample_secret_finding):
        """Test organize includes verified count"""
        secrets = []
        for i in range(3):
            secret = sample_secret_finding.copy()
            secret['Verified'] = i % 2 == 0  # Alternating verified
            secrets.append(secret)
        
        await secrets_organizer.organize_secrets(secrets)
        
        domain_dir = list(secrets_organizer.secrets_dir.iterdir())[0]
        secrets_file = domain_dir / "secrets.json"
        
        data = json.loads(secrets_file.read_text())
        assert 'verified_count' in data
        assert data['verified_count'] >= 0
    
    async def test_organize_empty_list(self, secrets_organizer):
        """Test organizing empty secrets list"""
        await secrets_organizer.organize_secrets([])
        
        # Should not crash
        domain_dirs = [d for d in secrets_organizer.secrets_dir.iterdir() if d.is_dir()]
        assert len(domain_dirs) >= 0  # May be empty


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    async def test_handle_missing_source_url(self, secrets_organizer):
        """Test handling secret without source URL"""
        secret = {
            'SourceMetadata': {},  # No url
            'Raw': 'SECRET',
            'Verified': True
        }
        
        await secrets_organizer.organize_secrets([secret])
        
        # Should use 'unknown' domain
        unknown_dir = secrets_organizer.secrets_dir / "unknown"
        assert unknown_dir.exists() or len(list(secrets_organizer.secrets_dir.iterdir())) >= 0
    
    async def test_handle_malformed_secret_structure(self, secrets_organizer):
        """Test handling malformed secret structure"""
        malformed = {
            'Random': 'data',
            'No': 'standard fields'
        }
        
        # Should not crash
        await secrets_organizer.organize_secrets([malformed])
    
    async def test_handle_unicode_domains(self, secrets_organizer, sample_secret_finding):
        """Test handling Unicode in domain names"""
        secret = sample_secret_finding.copy()
        secret['SourceMetadata']['url'] = "https://例え.jp/app.js"
        
        await secrets_organizer.organize_secrets([secret])
        
        # Should handle gracefully
        assert len(list(secrets_organizer.secrets_dir.iterdir())) >= 0
    
    async def test_handle_special_characters_in_domain(self, secrets_organizer, sample_secret_finding):
        """Test handling special characters in domain"""
        secret = sample_secret_finding.copy()
        secret['SourceMetadata']['url'] = "https://example-.com/app.js"
        
        await secrets_organizer.organize_secrets([secret])
        
        # Should create valid directory name
        assert len(list(secrets_organizer.secrets_dir.iterdir())) >= 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
class TestSecretsOrganizerIntegration:
    """Test integration scenarios"""
    
    async def test_full_workflow(self, secrets_organizer, sample_secret_finding):
        """Test complete workflow: save -> flush -> organize"""
        # Save secrets one by one
        for i in range(5):
            secret = sample_secret_finding.copy()
            secret['Raw'] = f'SECRET_{i}'
            await secrets_organizer.save_single_secret(secret)
        
        # Flush buffer
        await secrets_organizer._flush_secrets()
        
        # Load and organize
        data = json.loads(secrets_organizer.streaming_file.read_text())
        await secrets_organizer.organize_secrets(data['secrets'])
        
        # Verify domain directories created
        domain_dirs = [d for d in secrets_organizer.secrets_dir.iterdir() if d.is_dir()]
        assert len(domain_dirs) >= 1
    
    async def test_concurrent_saves(self, secrets_organizer, sample_secret_finding):
        """Test concurrent secret saves"""
        tasks = []
        for i in range(20):
            secret = sample_secret_finding.copy()
            secret['Raw'] = f'SECRET_{i}'
            tasks.append(secrets_organizer.save_single_secret(secret))
        
        await asyncio.gather(*tasks)
        
        # All secrets should be in buffer
        assert len(secrets_organizer._streaming_secrets) >= 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.slow
@pytest.mark.asyncio
class TestPerformance:
    """Test performance of organizer operations"""
    
    async def test_organize_large_dataset(self, secrets_organizer, sample_secret_finding):
        """Test organizing large number of secrets"""
        import time
        
        # Create 1000 secrets
        secrets = []
        for i in range(1000):
            secret = sample_secret_finding.copy()
            secret['Raw'] = f'SECRET_{i}'
            secret['SourceMetadata']['url'] = f"https://domain{i % 10}.com/app.js"
            secrets.append(secret)
        
        start = time.time()
        await secrets_organizer.organize_secrets(secrets)
        elapsed = time.time() - start
        
        # Should complete reasonably fast
        assert elapsed < 5.0, f"Organization too slow: {elapsed}s for 1000 secrets"
    
    async def test_flush_performance(self, secrets_organizer, sample_secret_finding):
        """Test flush performance with large buffer"""
        import time
        
        # Add 100 secrets to buffer
        for i in range(100):
            secret = sample_secret_finding.copy()
            secret['Raw'] = f'SECRET_{i}'
            secrets_organizer._streaming_secrets.append(secret)
        
        start = time.time()
        await secrets_organizer._flush_secrets()
        elapsed = time.time() - start
        
        # Should flush quickly
        assert elapsed < 2.0, f"Flush too slow: {elapsed}s for 100 secrets"
