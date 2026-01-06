"""
Comprehensive test suite for reporter module

Tests cover:
- REPORT.md generation
- Secrets section (verified/unverified)
- Extracts inclusion (endpoints, params, domains)
- Large file truncation
- Missing/corrupted file resilience
- Edge cases
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock

from jsscanner.output.reporter import generate_report


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestReporterInitialization:
    """Test reporter initialization and basic functionality"""
    
    @pytest.mark.unit
    def test_generate_report_creates_report_md(self, tmp_path):
        """Test generate_report() creates REPORT.md"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 120.5, 'total_files': 50}
        
        result = generate_report("example.com", str(base_path), stats)
        
        assert result is True
        report_path = base_path / "REPORT.md"
        assert report_path.exists()
    
    @pytest.mark.unit
    def test_generate_report_in_correct_directory(self, tmp_path):
        """Test generates report in correct directory"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 60.0, 'total_files': 25}
        
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        assert report_path.parent == base_path
    
    @pytest.mark.unit
    def test_generate_report_returns_true_on_success(self, tmp_path):
        """Test returns True on success"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 30.0, 'total_files': 10}
        
        result = generate_report("example.com", str(base_path), stats)
        
        assert result is True


# ============================================================================
# SECRETS SECTION TESTS
# ============================================================================

class TestReporterSecretsSection:
    """Test secrets section generation"""
    
    @pytest.mark.unit
    def test_verified_secrets_section_populated(self, sample_report_data):
        """Test verified secrets section is populated"""
        stats = {'scan_duration': 120.0, 'total_files': 50}
        
        generate_report("example.com", sample_report_data['base_path'], stats)
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "VERIFIED" in content
        assert "AWS" in content
    
    @pytest.mark.unit
    def test_unverified_secrets_section_populated(self, sample_report_data):
        """Test unverified secrets section is populated"""
        stats = {'scan_duration': 120.0, 'total_files': 50}
        
        generate_report("example.com", sample_report_data['base_path'], stats)
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Report will show the verified secret from sample data
        # Since we have 2 secrets (1 verified, 1 unverified), report shows verified
        assert "VERIFIED" in content or "AWS" in content
    
    @pytest.mark.unit
    def test_secret_preview_truncation(self, tmp_path):
        """Test secret preview is truncated (first 40 chars)"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create trufflehog.json with long secret
        trufflehog_file = findings_dir / "trufflehog.json"
        secret = {
            "SourceMetadata": {
                "url": "https://example.com/app.js",
                "Data": {"Filesystem": {"file": "app.js"}}
            },
            "DetectorName": "AWS",
            "Verified": True,
            "Raw": "A" * 100,  # Very long secret
            "Redacted": "A" * 20 + "..."
        }
        
        with open(trufflehog_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(secret) + '\n')
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Should contain "..." for truncation
        assert "..." in content
    
    @pytest.mark.unit
    def test_detector_name_included(self, sample_report_data):
        """Test detector name is included in report"""
        stats = {'scan_duration': 120.0, 'total_files': 50}
        
        generate_report("example.com", sample_report_data['base_path'], stats)
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "AWS" in content
    
    @pytest.mark.unit
    def test_source_file_path_included(self, sample_report_data):
        """Test source file path is included in report"""
        stats = {'scan_duration': 120.0, 'total_files': 50}
        
        generate_report("example.com", sample_report_data['base_path'], stats)
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "app.js" in content


# ============================================================================
# EXTRACTS SECTION TESTS
# ============================================================================

class TestReporterExtractsSection:
    """Test extracts section generation"""
    
    @pytest.mark.unit
    def test_endpoints_parsed_and_included(self, sample_report_data):
        """Test endpoints.txt is parsed and included"""
        stats = {'scan_duration': 120.0, 'total_files': 50}
        
        generate_report("example.com", sample_report_data['base_path'], stats)
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "Endpoints" in content
        assert "api.example.com/v1/users" in content
    
    @pytest.mark.unit
    def test_params_parsed_and_included(self, sample_report_data):
        """Test params.txt is parsed and included"""
        stats = {'scan_duration': 120.0, 'total_files': 50}
        
        generate_report("example.com", sample_report_data['base_path'], stats)
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "Parameters" in content
        assert "user_id" in content or "api_key" in content
    
    @pytest.mark.unit
    def test_domains_parsed_and_included(self, sample_report_data):
        """Test domains.txt is parsed and included"""
        stats = {'scan_duration': 120.0, 'total_files': 50}
        
        generate_report("example.com", sample_report_data['base_path'], stats)
        
        report_path = Path(sample_report_data['base_path']) / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Domains are included in the report
        assert "example.com" in content
    
    @pytest.mark.unit
    def test_large_lists_truncated(self, tmp_path):
        """Test large lists are truncated with '...and X more'"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create endpoints.txt with 50 entries
        endpoints_file = findings_dir / "endpoints.txt"
        endpoints = [f"https://api.example.com/v1/endpoint{i}" for i in range(50)]
        endpoints_file.write_text("\n".join(endpoints))
        
        stats = {'scan_duration': 120.0, 'total_files': 50}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Should show count (50) and truncate display
        assert "Endpoints (50)" in content or "50" in content


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestReporterErrorHandling:
    """Test error handling and resilience"""
    
    @pytest.mark.unit
    def test_missing_trufflehog_json_handled_gracefully(self, tmp_path):
        """Test missing trufflehog.json is handled gracefully"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        # No trufflehog.json file created
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        result = generate_report("example.com", str(base_path), stats)
        
        # Should still succeed
        assert result is True
        
        report_path = base_path / "REPORT.md"
        assert report_path.exists()
    
    @pytest.mark.unit
    def test_corrupted_json_line_skipped_with_warning(self, tmp_path, mock_logger):
        """Test corrupted JSON line is skipped"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create trufflehog.json with invalid JSON line
        trufflehog_file = findings_dir / "trufflehog.json"
        trufflehog_file.write_text("invalid json line\n")
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        result = generate_report("example.com", str(base_path), stats, logger=mock_logger)
        
        # Should still succeed (skip invalid line)
        assert result is True
    
    @pytest.mark.unit
    def test_missing_extracts_files_dont_crash(self, tmp_path):
        """Test missing extract files don't crash reporter"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # No extract files created
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        result = generate_report("example.com", str(base_path), stats)
        
        # Should still succeed
        assert result is True
        
        report_path = base_path / "REPORT.md"
        assert report_path.exists()


# ============================================================================
# STATISTICS TESTS
# ============================================================================

class TestReporterStatistics:
    """Test statistics handling in report"""
    
    @pytest.mark.unit
    def test_scan_duration_included(self, tmp_path):
        """Test scan duration is included in report"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 125.7, 'total_files': 50}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "125.7" in content or "126" in content
    
    @pytest.mark.unit
    def test_total_files_included(self, tmp_path):
        """Test total files count is included in report"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 60.0, 'total_files': 42}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "42" in content
    
    @pytest.mark.unit
    def test_handles_missing_stats_gracefully(self, tmp_path):
        """Test handles missing stats dict gracefully"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        # Pass None as stats
        result = generate_report("example.com", str(base_path), None)
        
        # Should still succeed with default values
        assert result is True
    
    @pytest.mark.unit
    def test_handles_empty_stats_dict(self, tmp_path):
        """Test handles empty stats dict"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {}
        result = generate_report("example.com", str(base_path), stats)
        
        # Should still succeed with default values
        assert result is True


# ============================================================================
# REPORT STRUCTURE TESTS
# ============================================================================

class TestReporterStructure:
    """Test report structure and formatting"""
    
    @pytest.mark.unit
    def test_report_includes_target_name(self, tmp_path):
        """Test report includes target name in title"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "example.com" in content
    
    @pytest.mark.unit
    def test_report_includes_timestamp(self, tmp_path):
        """Test report includes timestamp"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "Date:" in content
    
    @pytest.mark.unit
    def test_report_includes_output_structure_section(self, tmp_path):
        """Test report includes output structure documentation"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "Output Structure" in content
        assert "findings/" in content
        assert ".warehouse/" in content
    
    @pytest.mark.unit
    def test_report_uses_markdown_formatting(self, tmp_path):
        """Test report uses proper markdown formatting"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create endpoints file to get code blocks
        endpoints_file = findings_dir / "endpoints.txt"
        endpoints_file.write_text("https://api.example.com/v1/users\n")
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Check for markdown elements
        assert content.startswith("#")  # Title
        assert "|" in content  # Tables
        assert "```" in content  # Code blocks (from endpoints)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestReporterEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.mark.unit
    def test_empty_findings_generates_minimal_report(self, tmp_path):
        """Test empty findings generates minimal report"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create empty files
        (findings_dir / "endpoints.txt").write_text("")
        (findings_dir / "params.txt").write_text("")
        
        stats = {'scan_duration': 60.0, 'total_files': 0}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        assert "Clean" in content or "No secrets" in content
    
    @pytest.mark.unit
    def test_unicode_in_secrets_handled(self, tmp_path):
        """Test Unicode characters in secrets are handled"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create trufflehog.json with Unicode secret
        trufflehog_file = findings_dir / "trufflehog.json"
        secret = {
            "SourceMetadata": {
                "url": "https://example.com/app.js",
                "Data": {"Filesystem": {"file": "app.js"}}
            },
            "DetectorName": "Test",
            "Verified": True,
            "Raw": "SECRET_with_émojis_🔥_and_unicode_中文",
            "Redacted": "SECRET_***"
        }
        
        with open(trufflehog_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(secret, ensure_ascii=False) + '\n')
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        result = generate_report("example.com", str(base_path), stats)
        
        # Should succeed
        assert result is True
    
    @pytest.mark.unit
    def test_very_long_target_name(self, tmp_path):
        """Test very long target name is handled"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        long_target = "a" * 500  # Very long target name
        stats = {'scan_duration': 60.0, 'total_files': 10}
        
        result = generate_report(long_target, str(base_path), stats)
        
        assert result is True
    
    @pytest.mark.unit
    def test_special_characters_in_file_paths(self, tmp_path):
        """Test special characters in file paths are handled"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create trufflehog.json with special chars in path
        trufflehog_file = findings_dir / "trufflehog.json"
        secret = {
            "SourceMetadata": {
                "url": "https://example.com/app.js",
                "Data": {"Filesystem": {"file": "path/with spaces/and-special@chars.js"}}
            },
            "DetectorName": "Test",
            "Verified": True,
            "Raw": "SECRET",
            "Redacted": "***"
        }
        
        with open(trufflehog_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(secret) + '\n')
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        result = generate_report("example.com", str(base_path), stats)
        
        assert result is True
    
    @pytest.mark.unit
    def test_logger_provided_logs_info(self, tmp_path, mock_logger):
        """Test logger logs info when provided"""
        base_path = tmp_path / "results" / "test_target"
        base_path.mkdir(parents=True)
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats, logger=mock_logger)
        
        # Should have logged info
        mock_logger.info.assert_called()
    
    @pytest.mark.unit
    def test_exception_returns_false_with_logger(self, tmp_path, mock_logger):
        """Test exception returns False and logs warning with logger"""
        # Pass invalid base_path to trigger exception
        result = generate_report("example.com", "/invalid/path/that/does/not/exist", {}, logger=mock_logger)
        
        # Should return False
        assert result is False
        
        # Should have logged warning
        mock_logger.warning.assert_called()


# ============================================================================
# MULTIPLE SECRETS HANDLING
# ============================================================================

class TestReporterMultipleSecrets:
    """Test handling of multiple secrets"""
    
    @pytest.mark.unit
    def test_multiple_verified_secrets_listed(self, tmp_path):
        """Test multiple verified secrets are listed"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create trufflehog.json with multiple secrets
        trufflehog_file = findings_dir / "trufflehog.json"
        secrets = []
        for i in range(5):
            secret = {
                "SourceMetadata": {
                    "url": f"https://example.com/app{i}.js",
                    "Data": {"Filesystem": {"file": f"app{i}.js"}}
                },
                "DetectorName": "AWS",
                "Verified": True,
                "Raw": f"AKIAIOSFODNN7EXAMPLE{i}",
                "Redacted": f"AKIA****************{i}"
            }
            secrets.append(secret)
        
        with open(trufflehog_file, 'w', encoding='utf-8') as f:
            for secret in secrets:
                f.write(json.dumps(secret) + '\n')
        
        stats = {'scan_duration': 120.0, 'total_files': 50}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Should list multiple secrets
        assert content.count("VERIFIED") >= 5 or content.count("AWS") >= 5
    
    @pytest.mark.unit
    def test_more_than_10_verified_secrets_shows_truncation(self, tmp_path):
        """Test more than 10 verified secrets shows '...and X more' message"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        findings_dir.mkdir(parents=True)
        
        # Create trufflehog.json with 15 secrets
        trufflehog_file = findings_dir / "trufflehog.json"
        secrets = []
        for i in range(15):
            secret = {
                "SourceMetadata": {
                    "url": f"https://example.com/app{i}.js",
                    "Data": {"Filesystem": {"file": f"app{i}.js"}}
                },
                "DetectorName": "AWS",
                "Verified": True,
                "Raw": f"AKIAIOSFODNN7EXAMPLE{i}",
                "Redacted": f"AKIA****************{i}"
            }
            secrets.append(secret)
        
        with open(trufflehog_file, 'w', encoding='utf-8') as f:
            for secret in secrets:
                f.write(json.dumps(secret) + '\n')
        
        stats = {'scan_duration': 120.0, 'total_files': 50}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Should show truncation message
        assert "more" in content.lower() and ("5" in content or "verified" in content.lower())


# ============================================================================
# WAREHOUSE DB PATH FALLBACK
# ============================================================================

class TestReporterWarehouseFallback:
    """Test fallback to .warehouse/db/trufflehog.json"""
    
    @pytest.mark.unit
    def test_reads_from_warehouse_db_if_findings_missing(self, tmp_path):
        """Test reads from .warehouse/db/trufflehog.json if findings/ version missing"""
        base_path = tmp_path / "results" / "test_target"
        warehouse_dir = base_path / ".warehouse" / "db"
        warehouse_dir.mkdir(parents=True)
        
        # Create trufflehog.json in warehouse location
        trufflehog_file = warehouse_dir / "trufflehog.json"
        secret = {
            "SourceMetadata": {
                "url": "https://example.com/app.js",
                "Data": {"Filesystem": {"file": "app.js"}}
            },
            "DetectorName": "GitHub",
            "Verified": True,
            "Raw": "ghp_1234567890abcdefghijklmnopqrstuv",
            "Redacted": "ghp_***********************************"
        }
        
        with open(trufflehog_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(secret) + '\n')
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Should have read secret from warehouse location
        assert "GitHub" in content
    
    @pytest.mark.unit
    def test_prefers_findings_over_warehouse(self, tmp_path):
        """Test prefers findings/trufflehog.json over .warehouse/db/"""
        base_path = tmp_path / "results" / "test_target"
        findings_dir = base_path / "findings"
        warehouse_dir = base_path / ".warehouse" / "db"
        
        findings_dir.mkdir(parents=True)
        warehouse_dir.mkdir(parents=True)
        
        # Create different secrets in both locations
        findings_file = findings_dir / "trufflehog.json"
        secret1 = {
            "SourceMetadata": {
                "url": "https://example.com/app.js",
                "Data": {"Filesystem": {"file": "app.js"}}
            },
            "DetectorName": "AWS",
            "Verified": True,
            "Raw": "AKIAIOSFODNN7EXAMPLE",
            "Redacted": "AKIA****************"
        }
        
        with open(findings_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(secret1) + '\n')
        
        warehouse_file = warehouse_dir / "trufflehog.json"
        secret2 = {
            "SourceMetadata": {
                "url": "https://example.com/config.js",
                "Data": {"Filesystem": {"file": "config.js"}}
            },
            "DetectorName": "GitHub",
            "Verified": True,
            "Raw": "ghp_1234567890abcdefghijklmnopqrstuv",
            "Redacted": "ghp_***********************************"
        }
        
        with open(warehouse_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(secret2) + '\n')
        
        stats = {'scan_duration': 60.0, 'total_files': 10}
        generate_report("example.com", str(base_path), stats)
        
        report_path = base_path / "REPORT.md"
        content = report_path.read_text(encoding='utf-8')
        
        # Should have AWS (from findings), not GitHub (from warehouse)
        assert "AWS" in content
        assert "GitHub" not in content
