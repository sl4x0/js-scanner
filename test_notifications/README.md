# Discord Notification Testing Infrastructure

This directory contains test files and scripts for validating Discord webhook functionality.

## Test Files

### JavaScript Test Files (Fake Secrets)

All test files contain **FAKE** credentials that are publicly known examples and should never be used in production:

1. **test_secrets_aws.js** - Fake AWS credentials

   - Example AWS access key and secret key
   - API endpoints and parameters

2. **test_secrets_github.js** - Fake GitHub token

   - Example GitHub personal access token
   - GitHub API endpoints

3. **test_secrets_multiple.js** - Multiple fake secrets in one file

   - Database password
   - Stripe API keys
   - JWT secret
   - Slack webhook
   - SendGrid API key
   - Multiple API endpoints and parameters

4. **test_clean_api.js** - No secrets, just API structure
   - Clean file with endpoints and parameters only
   - Used to test extraction without triggering secret alerts

## Test Scripts

### test_server.py - Local HTTP Server

Simple HTTP server to serve test JavaScript files for scanning.

**Usage:**

```bash
python test_server.py [--port PORT]
```

**Default port:** 8000

**Available test URLs:**

- http://localhost:8000/test_secrets_aws.js
- http://localhost:8000/test_secrets_github.js
- http://localhost:8000/test_secrets_multiple.js
- http://localhost:8000/test_clean_api.js

### webhook_validator.py - Discord Webhook Validator

Validates Discord webhook functionality with various test scenarios.

**Usage:**

```bash
python webhook_validator.py <discord_webhook_url>
```

**Tests performed:**

1. Basic text message
2. Embed message (secret notification format)
3. Batch notification (multiple secrets)
4. Rate limiting behavior

**Example:**

```bash
python webhook_validator.py "https://discord.com/api/webhooks/123456/abcdef"
```

## Testing Workflow

### 1. Start the Test Server

```bash
cd test_notifications
python test_server.py
```

### 2. Validate Discord Webhook (Optional)

Before running the scanner, validate your webhook:

```bash
python webhook_validator.py "YOUR_WEBHOOK_URL"
```

### 3. Run Scanner Against Test Server

Create a test input file with the test URLs:

```bash
# test_urls.txt
http://localhost:8000/test_secrets_aws.js
http://localhost:8000/test_secrets_github.js
http://localhost:8000/test_secrets_multiple.js
http://localhost:8000/test_clean_api.js
```

Run the scanner:

```bash
cd ..
python -m jsscanner -t test-notifications -i test_notifications/test_urls.txt
```

### 4. Verify Results

Check the results directory:

```
results/test-notifications/
├── extracts/
│   ├── localhost/                    # Domain-specific extracts
│   │   ├── endpoints.json
│   │   ├── params.txt
│   │   └── words.txt
│   ├── endpoints.txt                 # Legacy format
│   └── params.txt                    # Legacy format
├── secrets/
│   ├── localhost/                    # Domain-specific secrets
│   │   └── secrets.json
│   └── trufflehog_full.json         # All findings
└── scan_results.json
```

## Test Scenarios

### Scenario 1: Single Secret Detection

**File:** test_secrets_aws.js  
**Expected:** 1 AWS credential detected  
**Notification:** Single secret embed

### Scenario 2: GitHub Token

**File:** test_secrets_github.js  
**Expected:** 1 GitHub token detected  
**Notification:** Single secret embed

### Scenario 3: Multiple Secrets

**File:** test_secrets_multiple.js  
**Expected:** 5+ secrets detected  
**Notification:** Batch notification with multiple embeds

### Scenario 4: No Secrets

**File:** test_clean_api.js  
**Expected:** 0 secrets, multiple endpoints/params extracted  
**Notification:** None (only extracts)

### Scenario 5: Multi-Domain Test

**Setup:** Mix of localhost and external URLs  
**Expected:** Secrets and extracts organized by domain  
**Verification:** Check domain-specific directories

## Expected Secrets

The test files contain these known fake secrets:

1. **AWS** (test_secrets_aws.js)

   - Access Key ID: AKIAIOSFODNN7EXAMPLE
   - Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

2. **GitHub** (test_secrets_github.js)

   - Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz

3. **Multiple** (test_secrets_multiple.js)
   - Database password: SuperSecret123!@#Password
   - Stripe publishable: pk_test_51234567890abcdefghijklmnopqrstuvwxyz
   - Stripe secret: sk_test_51234567890abcdefghijklmnopqrstuvwxyz
   - JWT secret: my-super-secret-jwt-key-that-should-not-be-hardcoded
   - Slack webhook: https://example.com/fake-webhook-url-for-testing-only
   - SendGrid API key: SG.FAKE_API_KEY_FOR_TESTING_ONLY

**Note:** These are all publicly known example credentials and pose no security risk.

## Troubleshooting

### Webhook Not Working

1. Verify webhook URL is correct
2. Run webhook_validator.py to test connectivity
3. Check Discord server settings for webhook permissions

### No Secrets Detected

1. Ensure TruffleHog is installed and configured
2. Check that test files contain the expected patterns
3. Verify scanner is not skipping files due to size/type filters

### Server Connection Errors

1. Ensure test_server.py is running
2. Check firewall settings for port 8000
3. Try different port with `--port` flag

## Cleanup

After testing, you can delete the test results:

```bash
rm -rf results/test-notifications
```

## Safety Notes

⚠️ **Important:**

- All secrets in test files are FAKE and publicly known examples
- Never commit real credentials to test files
- Use a dedicated test Discord channel for webhook testing
- Clean up test results after validation
