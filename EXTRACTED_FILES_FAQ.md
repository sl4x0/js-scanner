# Extracted Files FAQ

## What are "Extracted Files"?

When the scanner processes JavaScript bundles (Webpack, Vite, Parcel), it uses **webcrack** to unpack the bundled code into individual module files.

### Example:

```
Original bundle: app.bundle.js (5MB, 1 file)
↓
Extracted: 203 individual module files
```

## Are Extracted Files Scanned?

**Currently: NO** - Extracted files are **not** automatically processed by the scanner.

### Current Workflow:

1. ✅ **Phase 2**: Downloads `app.bundle.js` → Saved to `files/minified/`
2. ✅ **Phase 3**: TruffleHog scans `app.bundle.js` (the original bundle)
3. ✅ **Phase 4**: AST extracts data from `app.bundle.js`
4. ✅ **Phase 5**: Unpacks `app.bundle.js` → Creates `unpacked/app.bundle/` with 203 files
5. ❌ **Extracted files are NOT re-scanned or re-analyzed**

### What This Means:

- **Secrets**: Only detected in the original minified bundle
- **Endpoints/Domains**: Only extracted from the bundle, not individual modules
- **Extracted files**: Saved for manual review but not processed automatically

## Why Not Scan Extracted Files?

1. **Performance**: Would require re-running TruffleHog on 200+ files per bundle
2. **Redundancy**: Original bundle already contains all the code
3. **Design**: Extraction is meant for manual inspection, not automated scanning

## Should Extracted Files Be Scanned?

### Use Cases for Scanning:

✅ **Yes, if:**

- Bundle is heavily obfuscated and secrets are hidden
- You need module-level granularity for findings
- Source maps reveal developer secrets (API keys in comments)

❌ **No, if:**

- Bundle is already readable (not obfuscated)
- TruffleHog found secrets in the bundle
- You only care about endpoints/domains (already extracted)

## How to Scan Extracted Files (Workaround)

### Option 1: Manual TruffleHog Scan

```bash
# Scan extracted directory
trufflehog filesystem --directory results/target/files/unpacked/app.bundle/

# Or point scanner to extracted files
python -m jsscanner -t extracted-scan -i results/target/files/unpacked/app.bundle/*.js
```

### Option 2: Enable Recursive Processing (Future Feature)

```yaml
# config.yaml (NOT YET IMPLEMENTED)
bundle_unpacker:
  enabled: true
  process_extracted: true # Re-scan extracted files
```

## Files Location

```
results/target/
├── files/
│   ├── minified/
│   │   └── app.bundle-abc123.js          # Original downloaded bundle
│   ├── unminified/
│   │   └── app.bundle-abc123.js          # Beautified bundle
│   └── unpacked/
│       └── app.bundle-abc123/            # ⚠️ Extracted but NOT scanned
│           ├── module1.js
│           ├── module2.js
│           └── ... (200+ files)
```

## Recommendations

1. **Default Behavior**: Current design is **correct** - bundles are scanned as-is
2. **Manual Review**: Check `unpacked/` folders for interesting modules
3. **Future Enhancement**: Add `process_extracted: true` config option if needed
4. **Performance**: Only enable extracted file processing if you specifically need it

## Related Configuration

```yaml
# config.yaml
bundle_unpacker:
  enabled: false # Set true to unpack bundles
  min_file_size: 102400 # Only unpack files >100KB
  timeout: 300 # Unpacking timeout
  temp_dir: "temp/unpacked"

batch_processing:
  cleanup_minified: false # Keep original bundles for reference
```

## Summary

**Extracted files are saved for manual inspection but are NOT automatically scanned or analyzed by the tool.**

If you need extracted files to be scanned, you must:

1. Manually run TruffleHog on the `unpacked/` directory, OR
2. Re-run the scanner pointing to the extracted files as input, OR
3. Request a feature enhancement to add `process_extracted: true` configuration
