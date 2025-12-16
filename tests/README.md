# JS-Scanner Test Suite

Comprehensive testing infrastructure for the js-scanner project.

## Test Structure

```
tests/
├── integration_tests.py       # Main integration test suite
├── test_extraction.py          # Extraction accuracy tests
├── test_beautification.py      # Beautification tests
└── README.md                   # This file
```

## Running Tests

### All Tests

Run the complete integration test suite:

```bash
python tests/integration_tests.py
```

### Individual Test Components

```bash
# Extraction tests
python tests/test_extraction.py

# Beautification tests
python tests/test_beautification.py
```

## Test Suites

### 1. Integration Tests (integration_tests.py)

Comprehensive end-to-end tests covering:

- **Multi-Domain Test**: Scans 10+ diverse domains
- **Extraction Accuracy**: Validates endpoint and parameter detection
- **Beautification Test**: Verifies minified JS handling
- **Domain Organization**: Tests domain-specific directory structure

**Usage:**
```bash
python tests/integration_tests.py
```

**Expected Output:**
```
🧪 JS-SCANNER INTEGRATION TEST SUITE
================================================================================

TEST 1: Multi-Domain Integration Test (10+ domains)
✅ Scanner completed in 45.32s
   - Base directory: ✓
   - Domain extracts: 8 domains
   - Total endpoints: 156
   - Total params: 234
   - Legacy format: ✓

TEST 2: Extraction Accuracy Validation
✅ Extraction completed
   - Endpoints found: 12
   - Params found: 18

TEST 3: Beautification Test
✅ Beautification test completed
   - Unminified files: ✓

TEST 4: Domain-Specific Organization
✅ Organization verified
   - Domain-specific extracts: ✓
   - Multiple domains: 8
   - Legacy format: ✓
   - Backward compatible: ✓

📊 TEST SUMMARY
================================================================================
✅ PASS: Multi-Domain Test
✅ PASS: Extraction Accuracy
✅ PASS: Beautification Test
✅ PASS: Domain Organization

Result: 4/4 tests passed
```

### 2. Extraction Accuracy Tests (test_extraction.py)

Detailed tests for AST analysis and extraction:

- Endpoint detection patterns
- Parameter extraction
- Domain extraction
- Link discovery
- Wordlist generation

### 3. Beautification Tests (test_beautification.py)

Tests for JavaScript processing:

- Minified code detection
- Beautification accuracy
- Source map extraction
- Large file handling
- Timeout handling

## Test Data

### Test Domains (Multi-Domain Test)

The integration tests use these public domains:
- google.com
- github.com
- stackoverflow.com
- reddit.com
- twitter.com
- facebook.com
- amazon.com
- youtube.com
- wikipedia.org
- linkedin.com
- instagram.com
- netflix.com

### Test Files (Extraction Tests)

Local test server files (requires test_server.py running):
- test_clean_api.js - Clean API endpoints
- test_secrets_aws.js - Fake AWS credentials
- test_secrets_github.js - Fake GitHub token
- test_secrets_multiple.js - Multiple fake secrets

## Verification Checks

### Directory Structure Verification

```python
{
    'base_dir_exists': bool,
    'extracts_dir_exists': bool,
    'secrets_dir_exists': bool,
    'has_domain_extracts': bool,
    'domain_extract_count': int,
    'has_domain_secrets': bool,
    'domain_secret_count': int,
    'has_legacy_endpoints': bool,  # Backward compatibility
    'has_legacy_params': bool
}
```

### Extraction Validation

```python
{
    'total_endpoints': int,
    'total_params': int,
    'domain_specific_data': {
        'example.com': {
            'endpoints': int,
            'params': int
        }
    },
    'legacy_endpoints_count': int,  # Should match total
    'legacy_params_count': int
}
```

### Secrets Validation

```python
{
    'total_secrets': int,
    'verified_secrets': int,
    'domain_specific_data': {
        'example.com': {
            'total': int,
            'verified': int
        }
    },
    'full_results_count': int  # Should match total
}
```

## Expected Results

### Successful Test Run

All tests should pass with:
- ✅ Multi-domain scanning with 5+ domains processed
- ✅ Domain-specific extracts created
- ✅ Legacy format files created (backward compatibility)
- ✅ Domain-specific secrets organized
- ✅ Full results file created
- ✅ Beautification successful for minified files

### Directory Structure After Tests

```
results/
├── test-multi-domain/
│   ├── extracts/
│   │   ├── google.com/
│   │   │   ├── endpoints.json
│   │   │   ├── params.txt
│   │   │   └── words.txt
│   │   ├── github.com/
│   │   │   └── ...
│   │   ├── endpoints.txt          # Legacy format
│   │   └── params.txt              # Legacy format
│   ├── secrets/
│   │   ├── google.com/
│   │   │   └── secrets.json
│   │   └── trufflehog_full.json   # All results
│   ├── files/
│   │   ├── minified/
│   │   └── unminified/
│   └── scan_results.json
├── test-extraction/
│   └── ...
└── test-beautification/
    └── ...
```

## Backward Compatibility Tests

The test suite verifies backward compatibility by:

1. **Legacy Format Files**: Checking that `endpoints.txt`, `params.txt` exist in base extracts directory
2. **Data Consistency**: Verifying legacy files contain same data as domain-specific files
3. **Full Results**: Ensuring `trufflehog_full.json` contains all secrets

## Troubleshooting

### Tests Failing

1. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify TruffleHog is installed:**
   ```bash
   trufflehog --version
   ```

3. **Check configuration:**
   ```bash
   cat config.yaml
   ```

### Extraction Test Requires Server

If extraction accuracy test fails:

```bash
# Terminal 1: Start test server
cd test_notifications
python test_server.py

# Terminal 2: Run tests
python tests/integration_tests.py
```

### Network Timeouts

Multi-domain test may timeout on slow connections:
- Adjust timeout in `integration_tests.py` (default: 300s)
- Reduce number of test domains
- Use `--threads` to control concurrency

## Performance Benchmarks

Expected performance on modern hardware:

- **Multi-Domain (12 domains)**: 30-60 seconds
- **Extraction Test**: 5-10 seconds
- **Beautification Test**: 10-20 seconds

## Continuous Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions
- name: Run Integration Tests
  run: |
    python tests/integration_tests.py
```

## Contributing

When adding new tests:

1. Follow existing test structure
2. Add verification checks
3. Update this README
4. Ensure backward compatibility is maintained
