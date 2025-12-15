# JS Scanner - Discovery Mode Update

## New `--discovery` Flag

The JS Scanner now includes a `--discovery` flag that controls whether active discovery (Wayback Machine + Live crawling) is performed.

### Quick Reference

| Use Case                  | Command                                                      | Discovery Mode | Behavior                |
| ------------------------- | ------------------------------------------------------------ | -------------- | ----------------------- |
| **Scan httpx output**     | `python -m jsscanner -t example.com -i subs.txt`             | OFF            | Live pages only, fast   |
| **Full domain discovery** | `python -m jsscanner -t example.com --discovery`             | ON             | Wayback + Live          |
| **Subdomain discovery**   | `python -m jsscanner -t example.com -i subs.txt --discovery` | ON             | Wayback + Live for each |
| **Direct JS URLs**        | `python -m jsscanner -t example.com -i urls.txt`             | OFF            | Download and scan       |

### Default Behavior

- **Discovery is OFF by default** when using `-i` (input file) or `-u` (specific URLs)
- **Discovery is AUTO-ENABLED** when no input file or URLs are provided (scanning a single domain)

### Examples

#### 1. Scan httpx Output (Fast - No Wayback) ⚡

```bash
# Read subdomains from httpx, scan live pages only
python -m jsscanner -t example.com -i live-subdomains.txt
```

**Output:**

```
🎯 Project Scope: example.com
📂 Input Items: 25
🔍 Discovery Mode: OFF (Direct scan only)
```

#### 2. Full Discovery on Single Domain 🔍

```bash
# Comprehensive discovery (Wayback + Live)
python -m jsscanner -t example.com --discovery
```

**Output:**

```
🎯 Project Scope: example.com
📂 Input Items: 1
🔍 Discovery Mode: ON (Wayback + Live)
```

#### 3. Multiple Domains with Discovery 🌐

```bash
# Discover JS from multiple domains
python -m jsscanner -t "my-program" -i domains.txt --discovery
```

**Output:**

```
🎯 Project Scope: my-program
📂 Input Items: 5
🔍 Discovery Mode: ON (Wayback + Live)
```

#### 4. Scan Specific JS URLs 📄

```bash
# Direct scan of known JS files
python -m jsscanner -t example.com -u https://example.com/app.js https://example.com/bundle.js
```

**Output:**

```
🎯 Project Scope: example.com
📂 Input Items: 2
🔍 Discovery Mode: OFF (Direct scan only)
```

### Migration from Old Behavior

**Before (automatic discovery):**

```bash
# This used to trigger Wayback for every subdomain
python -m jsscanner -t example.com -i subdomains.txt
```

**After (explicit control):**

```bash
# Now only scans live pages (faster)
python -m jsscanner -t example.com -i subdomains.txt

# Add --discovery if you want full discovery
python -m jsscanner -t example.com -i subdomains.txt --discovery
```

### Benefits

✅ **Faster scans** when you only need live content  
✅ **Explicit control** over when Wayback is queried  
✅ **Reduced API usage** for focused scans  
✅ **Clear feedback** about what's being scanned

### Technical Details

See [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) for complete implementation details.
