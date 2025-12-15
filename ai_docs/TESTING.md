# Testing Guide for JS Scanner

## Quick Test

After installation, run a quick test to verify everything works:

```bash
# Activate virtual environment
source venv/bin/activate

i wil use the tool withotu virtual environment so i will skip this step or remove it entirely

# Test with a small target
python -m jsscanner -t yourwebsite.com --no-recursion
```

## Test Components Individually

### 1. Test Configuration Loading

```bash
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('✓ Config loaded successfully')
    print(f'Discord webhook: {config.get(\"discord_webhook\")[:50]}...')
"
```

### 2. Test TruffleHog

```bash
# Create a test file with a known secret
echo 'const apiKey = "AKIAIOSFODNN7EXAMPLE";' > test_secret.js

# Run TruffleHog
trufflehog filesystem test_secret.js --only-verified --json

# Clean up
rm test_secret.js
```

### 3. Test Playwright

```bash
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        print('✓ Playwright working')
        await browser.close()

asyncio.run(test())
"
```

### 4. Test Tree-sitter

```bash
python -c "
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser

JS_LANGUAGE = Language(tsjavascript.language())
parser = Parser(JS_LANGUAGE)
tree = parser.parse(b'function test() { return 42; }')
print('✓ Tree-sitter working')
print(f'Root node: {tree.root_node.type}')
"
```

### 5. Test Discord Webhook

```bash
# Test webhook with curl
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"🧪 Test from JS Scanner"}' \
  YOUR_WEBHOOK_URL
```

## Test Full Scan Flow

### Small Test Target

```bash
# Create test URLs file
cat > test_urls.txt << EOF
https://code.jquery.com/jquery-3.6.0.min.js
https://cdn.jsdelivr.net/npm/vue@2/dist/vue.js
EOF

# Run scan
python -m jsscanner -t test-scan -i test_urls.txt --no-wayback --no-live

# Check results
ls -la results/test-scan/
cat results/test-scan/metadata.json
```

### Live Site Test

```bash
# Scan a live site (replace with your test site)
python -m jsscanner -t example.com --no-wayback

# Monitor logs in real-time
tail -f results/example.com/logs/scan.log
```

## Verify Output Files

After a scan, verify all output files are created:

```bash
TARGET="example.com"

# Check directory structure
tree results/$TARGET

# Verify JSON files
for file in secrets.json history.json metadata.json trufflehog.json; do
    if [ -f "results/$TARGET/$file" ]; then
        echo "✓ $file exists"
        python -c "import json; json.load(open('results/$TARGET/$file'))" && echo "  ✓ Valid JSON"
    else
        echo "✗ $file missing"
    fi
done

# Check extracts
ls -la results/$TARGET/extracts/
```

## Performance Testing

### Memory Usage

```bash
# Monitor memory while scanning
python -m jsscanner -t example.com &
PID=$!

# Watch memory usage
while kill -0 $PID 2>/dev/null; do
    ps aux | grep $PID | grep -v grep
    sleep 5
done
```

### Scan Speed

```bash
# Time a scan
time python -m jsscanner -t example.com
```

## Troubleshooting Tests

### If Playwright Fails

```bash
# Reinstall browsers
playwright install chromium --with-deps

# Test manually
playwright codegen https://example.com
```

### If TruffleHog Fails

```bash
# Check version
trufflehog --version

# Test on a known repository
trufflehog git https://github.com/trufflesecurity/test_keys --only-verified
```

### If Rate Limiting Occurs

Check Discord webhook rate limits:

- Expected: 30 messages per minute
- Check notifier.py logs for rate limit messages

### If Memory Issues Occur

Reduce concurrent processes in config.yaml:

```yaml
playwright:
  max_concurrent: 2 # Reduce from 3
  restart_after: 50 # Restart browser more frequently

threads: 25 # Reduce from 50
```

## Integration Testing

### Test Recursive Crawling

```bash
# Enable recursion and test
python -c "
import yaml
config = yaml.safe_load(open('config.yaml'))
config['recursion']['enabled'] = True
config['recursion']['max_depth'] = 2
yaml.dump(config, open('config.yaml', 'w'))
"

python -m jsscanner -t example.com
```

### Test Error Handling

```bash
# Test with invalid URL
python -m jsscanner -t "invalid://url" 2>&1 | tee error_test.log

# Test with unreachable domain
python -m jsscanner -t "doesnotexist.invalid" 2>&1 | tee error_test.log

# Verify errors are logged properly
cat results/*/metadata.json | jq '.errors'
```

## Continuous Monitoring Test

### systemd Service Test (Linux only)

```bash
# Create test service
sudo nano /etc/systemd/system/jsscanner-test.service

# Add:
# [Unit]
# Description=JS Scanner Test
# [Service]
# Type=simple
# User=$USER
# WorkingDirectory=$PWD
# ExecStart=$PWD/venv/bin/python -m jsscanner -t example.com
# Restart=on-failure

# Start service
sudo systemctl daemon-reload
sudo systemctl start jsscanner-test
sudo systemctl status jsscanner-test

# Check logs
sudo journalctl -u jsscanner-test -f

# Stop service
sudo systemctl stop jsscanner-test
```

## Expected Results

After a successful scan, you should see:

1. **Console Output:**

   - Colorized log messages
   - Progress indicators
   - Secret alerts (if any found)
   - Final statistics

2. **File Structure:**

   ```
   results/example.com/
   ├── secrets.json (secrets found)
   ├── history.json (file hashes)
   ├── metadata.json (scan stats)
   ├── trufflehog.json (raw output)
   ├── files/
   │   ├── minified/ (original JS)
   │   └── unminified/ (beautified JS)
   ├── extracts/
   │   ├── endpoints.txt
   │   ├── params.txt
   │   ├── links.txt
   │   ├── domains.txt
   │   └── wordlist.txt
   └── logs/
       └── scan.log
   ```

3. **Discord Notifications:**
   - Scan start message
   - Real-time secret alerts
   - Scan complete summary

## Cleanup After Testing

```bash
# Remove test results
rm -rf results/test-*

# Clean up test files
rm -f test_*.js test_urls.txt error_test.log
```

## Automated Test Script

Save as `run_tests.sh`:

```bash
#!/bin/bash

echo "Running JS Scanner Tests..."

# Test 1: Config
python -c "import yaml; yaml.safe_load(open('config.yaml'))" && echo "✓ Config valid" || echo "✗ Config invalid"

# Test 2: Dependencies
python -c "import playwright, aiohttp, yaml" && echo "✓ Dependencies OK" || echo "✗ Missing dependencies"

# Test 3: TruffleHog
command -v trufflehog && echo "✓ TruffleHog found" || echo "✗ TruffleHog missing"

# Test 4: Small scan
python -m jsscanner -t example.com --no-wayback --no-recursion && echo "✓ Scan completed" || echo "✗ Scan failed"

echo "Tests complete!"
```

Run with:

```bash
chmod +x run_tests.sh
./run_tests.sh
```
