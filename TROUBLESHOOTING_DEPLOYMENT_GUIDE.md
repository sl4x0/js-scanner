# 🔧 JS Scanner - Troubleshooting & Deployment Guide

**Version:** 1.0  
**Last Updated:** December 16, 2025  
**Estimated Implementation Time:** 3-4 hours  
**Expected Performance Improvement:** 80-90% faster execution

---

## 🔧 Common Issues & Solutions

### Issue 1: "scan_directory method not found"
**Symptom:** `AttributeError: 'SecretScanner' object has no attribute 'scan_directory'`

**Solution:**
1. Verify the `scan_directory()` method was added to `secret_scanner.py`
2. Check indentation - the method must be at class level (not nested inside another method)
3. Restart Python interpreter if testing interactively

**Verification:**
```bash
python -c "from jsscanner.modules.secret_scanner import SecretScanner; print(hasattr(SecretScanner, 'scan_directory'))"
```
Expected output: `True`

---

### Issue 2: "Files not being deleted from minified folder"
**Symptom:** Files remain in `results/target/files/minified/` after scan completion

**Solution:**
1. Verify `_cleanup_minified_files()` method is called in the `run()` method
2. Check for exceptions in Phase 6 execution logs
3. Verify file permissions on the minified folder allow deletion

**Check configuration:**
```yaml
batch_processing:
  cleanup_minified: true  # Must be set to true
```

**Manual cleanup test:**
```bash
# Check if files exist
ls -la results/*/files/minified/

# If needed, manually delete
rm -rf results/*/files/minified/*
```

---

### Issue 3: "TruffleHog not finding any secrets"
**Symptom:** Phase 3 completes successfully but reports 0 secrets when secrets are known to exist

**Solution:**
1. Test TruffleHog manually with:
   ```bash
   trufflehog filesystem results/target/files/minified/ --json --only-verified
   ```
2. Confirm files are present in the minified folder during Phase 3 execution
3. Verify TruffleHog version with `trufflehog --version` (must be 3.x or higher)

**Debugging:**
```bash
# Check TruffleHog installation
which trufflehog
trufflehog --version

# Test with a known secret file
echo 'const key = "AKIAIOSFODNN7EXAMPLE";' > test.js
trufflehog filesystem . --json --only-verified
```

---

### Issue 4: "Memory usage is too high"
**Symptom:** System runs out of memory during file processing

**Solution:**
1. Reduce thread count in configuration file:
   ```yaml
   batch_processing:
     download_threads: 25  # Reduced from 50
     process_threads: 25   # Reduced from 50
   ```
2. Monitor memory usage with:
   ```bash
   # Windows PowerShell
   Get-Process python | Select-Object ProcessName, @{Name="Memory(MB)";Expression={$_.WorkingSet / 1MB}}
   
   # Linux/macOS
   top -p $(pgrep -f jsscanner)
   ps aux | grep jsscanner
   ```

**Memory recommendations by system:**
- 2GB RAM: Set threads to 10-15
- 4GB RAM: Set threads to 25-30
- 8GB RAM: Set threads to 50
- 16GB+ RAM: Set threads to 50-100

---

### Issue 5: "Some files are missing from unminified folder"
**Symptom:** Fewer files in `unminified/` directory than expected

**Solution:**
1. Review Phase 2 logs to verify all downloads completed successfully
2. Review Phase 5 logs for beautification errors
3. Check `results/target/logs/scan.log` for errors:
   ```bash
   # View recent logs
   tail -f results/*/logs/scan.log
   
   # Search for errors
   grep -i "error\|failed" results/*/logs/scan.log
   ```

**Check file counts:**
```bash
# Count downloaded files
ls -1 results/*/files/minified/ | wc -l

# Count unminified files
ls -1 results/*/files/unminified/ | wc -l

# Compare manifest entries
cat results/*/file_manifest.json | jq 'keys | length'
```

---

## 📊 Performance Expectations

### Scan Speed Comparison

| File Count | Old Workflow Time | New Workflow Time | Performance Improvement |
|------------|-------------------|-------------------|------------------------|
| 10 files   | 1-2 minutes       | 20-30 seconds     | 66-75% faster          |
| 50 files   | 5-10 minutes      | 1-2 minutes       | 80-90% faster          |
| 100 files  | 10-20 minutes     | 2-4 minutes       | 80-90% faster          |
| 500 files  | 50-100 minutes    | 10-20 minutes     | 80-90% faster          |

### Phase Breakdown (100 files example)

| Phase | Description | Old Time | New Time | Improvement |
|-------|-------------|----------|----------|-------------|
| 1 | Discovery | 10s | 10s | No change |
| 2 | Download | 300s | 30s | 90% faster |
| 3 | Secret Scan | 100s | 10s | 90% faster |
| 4 | AST Analysis | 200s | 20s | 90% faster |
| 5 | Beautify | 300s | 30s | 90% faster |
| 6 | Cleanup | 5s | 1s | 80% faster |
| **Total** | | **~17 min** | **~2 min** | **88% faster** |

### Factors Affecting Scan Speed

**Network-related:**
- Network bandwidth (affects download phase)
- Network latency (affects HTTP requests)
- CDN response times
- DNS resolution speed

**System-related:**
- CPU core count (affects parallel processing phase)
- Available RAM (limits thread count)
- Disk I/O speed (affects file operations)
- Number of concurrent processes

**Content-related:**
- Individual file sizes
- Number of secrets detected
- JavaScript complexity (affects AST parsing)
- File minification level

---

## 🎯 Success Criteria

The implementation is considered successful when:

### ✅ Functional Requirements
- [ ] All 6 phases execute in the correct sequential order
- [ ] Files are downloaded in parallel during Phase 2
- [ ] TruffleHog scans all files in a single batch operation (Phase 3)
- [ ] File processing occurs in parallel (Phase 4)
- [ ] Minified files are automatically deleted after scanning (Phase 6)
- [ ] Detected secrets are successfully sent to Discord webhook
- [ ] All extract files are generated correctly (endpoints.txt, params.txt, etc.)

### ✅ Performance Requirements
- [ ] Overall scan completes at least 50% faster than the previous implementation
- [ ] Phase 2 downloads at least 10 files simultaneously
- [ ] Phase 3 completes in under 20 seconds for 100 files
- [ ] Phase 4 processes at least 10 files simultaneously
- [ ] Phase 5 beautifies at least 10 files simultaneously

### ✅ Quality Requirements
- [ ] No errors appear in log files
- [ ] No Python exceptions during normal operation
- [ ] Memory usage stays within system limits
- [ ] All files are properly saved to disk
- [ ] State management works correctly (no duplicate processing)

### ✅ Validation Tests
```bash
# Test 1: Verify all phases appear in logs
python -m jsscanner -t example.com -u https://code.jquery.com/jquery-3.6.0.min.js 2>&1 | grep "PHASE"

# Test 2: Verify minified folder is empty after scan
python -m jsscanner -t example.com -u https://code.jquery.com/jquery-3.6.0.min.js
ls results/example.com/files/minified/  # Should be empty

# Test 3: Verify parallel execution
python -m jsscanner -t example.com -i urls.txt 2>&1 | grep "✅"

# Test 4: Verify secrets are detected
python -m jsscanner -t example.com -u <URL_with_known_secret>
cat results/example.com/secrets.json
```

---

## 📚 Additional Resources

### For Team Lead

**Pre-Implementation Review:**
- Review this entire document before assigning implementation tasks
- Estimated effort: 3 hours development + 1 hour testing
- Recommended task assignment:
  - Developer 1: `secret_scanner.py` changes
  - Developer 2: `engine.py` changes
  - Developer 3: Configuration and testing
- Require peer code review between developers before merge

**Risk Assessment:**
- **Low Risk:** Configuration file changes
- **Medium Risk:** Adding new methods to existing classes
- **High Risk:** Replacing core workflow in `run()` method

**Mitigation:**
- Create feature branch for all changes
- Test each component individually
- Maintain backward compatibility where possible
- Have rollback plan ready

---

### For Developers

**Before Starting Implementation:**
1. Read the complete workflow diagram in the implementation guide
2. Understand the rationale behind each optimization change
3. Set up development environment with all dependencies
4. Create a feature branch: `git checkout -b feature/batch-processing`

**During Implementation:**
- Test each phase individually before integration testing
- Use the implementation checklist to track progress
- Ask clarifying questions before making assumptions
- Document any deviations from the plan
- Write clear commit messages for each logical change

**Code Review Checklist:**
- [ ] All new methods have docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is clear and informative
- [ ] Configuration is properly validated
- [ ] No hardcoded values
- [ ] Type hints are used where appropriate

---

### For QA Team

**Testing Responsibilities:**
1. Follow the Testing Procedures section for validation
2. Execute all 4 defined test cases
3. Record and report performance metrics
4. Document any issues discovered with reproduction steps

**Test Environment Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure test webhook
cp config.yaml.example config.yaml
# Edit config.yaml with test Discord webhook

# Verify TruffleHog installation
trufflehog --version
```

**Performance Testing:**
```bash
# Create test dataset
cat > test_urls.txt << EOF
https://code.jquery.com/jquery-3.6.0.min.js
https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js
https://unpkg.com/react@18/umd/react.production.min.js
EOF

# Run performance test
time python -m jsscanner -t example.com -i test_urls.txt

# Record results
echo "Test Date: $(date)"
echo "File Count: $(wc -l < test_urls.txt)"
echo "Completion Time: [RECORD FROM ABOVE]"
```

**Bug Report Template:**
```markdown
## Bug Report

**Title:** [Brief description]

**Severity:** Critical / High / Medium / Low

**Environment:**
- OS: [Windows/Linux/macOS]
- Python Version: [3.x.x]
- Scanner Version: [Git commit hash]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Logs:**
```
[Paste relevant logs]
```

**Screenshots:**
[If applicable]
```

---

## 🚀 Deployment Plan

### Day 1 - Development Phase

**Morning (2-3 hours):**
- [ ] Create feature branch: `git checkout -b feature/batch-processing`
- [ ] Implement changes to `secret_scanner.py`
- [ ] Implement changes to `engine.py`
- [ ] Update configuration files

**Afternoon (1-2 hours):**
- [ ] Run syntax validation tests
- [ ] Run unit tests locally
- [ ] Fix any identified issues
- [ ] Commit changes with descriptive messages

**End of Day:**
- [ ] Run complete test suite
- [ ] Document any issues encountered
- [ ] Prepare for code review

---

### Day 1-2 - Code Review Phase

**Preparation:**
- [ ] Push feature branch to remote repository
- [ ] Create pull request with detailed description
- [ ] Include before/after performance metrics
- [ ] Link to implementation documentation

**Pull Request Description Template:**
```markdown
## Batch Processing Workflow Implementation

### Summary
Converts JS Scanner from sequential to batch processing for 80-90% performance improvement.

### Changes
- Added `scan_directory()` method to SecretScanner
- Refactored `run()` method with 6-phase workflow
- Added 4 new batch processing methods
- Updated configuration files

### Testing
- [x] Syntax validation passed
- [x] All imports successful
- [x] Single file test passed
- [x] Multiple files test passed
- [ ] Performance benchmark completed

### Performance Results
- Old workflow: X minutes for Y files
- New workflow: Z minutes for Y files
- Improvement: XX% faster

### Checklist
- [x] Code follows style guidelines
- [x] Tests pass locally
- [x] Documentation updated
- [x] No breaking changes
```

**Review Process:**
- [ ] Team lead performs code review
- [ ] Address all review feedback
- [ ] Re-test after making changes
- [ ] Get approval from at least 2 reviewers

---

### Day 2 - Staging Testing Phase

**Environment Setup:**
- [ ] Deploy to staging environment
- [ ] Configure staging Discord webhook
- [ ] Set up monitoring/logging

**Testing Execution:**
- [ ] Execute Test Case 1: Single file
- [ ] Execute Test Case 2: Multiple files
- [ ] Execute Test Case 3: Secret detection
- [ ] Execute Test Case 4: Performance benchmark

**Performance Testing:**
```bash
# Small dataset (10 files)
time python -m jsscanner -t staging.example.com -i small_dataset.txt

# Medium dataset (50 files)
time python -m jsscanner -t staging.example.com -i medium_dataset.txt

# Large dataset (100+ files)
time python -m jsscanner -t staging.example.com -i large_dataset.txt
```

**Validation:**
- [ ] Compare performance against baseline
- [ ] Verify all outputs are correct
- [ ] Check memory usage is acceptable
- [ ] Confirm no errors in logs

---

### Day 3 - Production Deployment Phase

**Pre-Deployment:**
- [ ] Merge approved changes to main branch
- [ ] Tag release: `git tag -a v2.0.0-batch -m "Batch processing implementation"`
- [ ] Create deployment backup
- [ ] Notify team of deployment window

**Deployment Steps:**
```bash
# 1. Backup current production
cp -r /path/to/production /path/to/backup-$(date +%Y%m%d)

# 2. Pull latest changes
cd /path/to/production
git pull origin main

# 3. Verify configuration
cat config.yaml | grep batch_processing

# 4. Restart services (if applicable)
systemctl restart jsscanner  # Adjust as needed

# 5. Verify deployment
python -c "import jsscanner.core.engine; print('OK')"
```

**Post-Deployment:**
- [ ] Monitor system for issues during first 24 hours
- [ ] Compare performance metrics against baseline
- [ ] Check error logs hourly for first 4 hours
- [ ] Verify Discord notifications are working
- [ ] Document actual performance improvements

**Rollback Plan (if needed):**
```bash
# Stop current services
systemctl stop jsscanner  # Adjust as needed

# Restore from backup
rm -rf /path/to/production
cp -r /path/to/backup-YYYYMMDD /path/to/production

# Restart services
systemctl start jsscanner  # Adjust as needed

# Verify rollback
python -c "import jsscanner.core.engine; print('OK')"
```

---

## 📞 Support & Troubleshooting Process

### If issues occur during implementation:

**Step 1: Self-Diagnosis (5-10 minutes)**
1. Consult the "Common Issues & Solutions" section above
2. Review the relevant test procedures
3. Check for typos in recent code changes

**Step 2: Log Analysis (5-10 minutes)**
1. Examine logs at `results/target/logs/scan.log`
2. Search for error messages: `grep -i error results/*/logs/scan.log`
3. Check Python traceback for root cause

**Step 3: Isolation Testing (10-15 minutes)**
1. Run TruffleHog manually to isolate scanning issues
2. Test individual methods in Python REPL
3. Verify configuration file syntax with YAML validator

**Step 4: Escalation (if unresolved)**
1. Contact the project lead with:
   - Specific error messages
   - Reproduction steps
   - What you've tried already
   - Relevant log excerpts
2. Include system information:
   ```bash
   python --version
   trufflehog --version
   cat /etc/os-release  # Linux
   # Or
   systeminfo  # Windows
   ```

### Emergency Contact Information

**Project Lead:** [Name/Email/Slack]  
**DevOps Team:** [Name/Email/Slack]  
**On-Call Support:** [Phone/Pager]

---

## ✅ Final Pre-Implementation Checklist for Project Lead

Before approving implementation to proceed:

### Team Readiness
- [ ] Development team understands the new workflow architecture
- [ ] Developers have necessary repository access and permissions
- [ ] Team has allocated 4-5 hours for implementation and testing
- [ ] Team has reviewed all documentation

### Environment Readiness
- [ ] Test environment is configured and accessible
- [ ] Discord webhook is configured for testing purposes
- [ ] TruffleHog 3.x is installed on all test systems
- [ ] Python 3.8+ is available on all systems

### Process Readiness
- [ ] Current production code backup exists
- [ ] Rollback plan is documented and tested
- [ ] Performance baseline metrics are recorded
- [ ] QA team is prepared to execute test plan
- [ ] Deployment window has been scheduled
- [ ] Stakeholders have been notified

### Risk Management
- [ ] Risk assessment completed
- [ ] Mitigation strategies identified
- [ ] Communication plan established
- [ ] Monitoring tools configured

---

## 📈 Success Metrics & KPIs

Track these metrics before and after deployment:

### Performance Metrics
- Average scan time per file
- Total scan completion time
- Phase 2 (download) completion time
- Phase 3 (TruffleHog) completion time
- Phase 4 (processing) completion time
- Phase 5 (beautify) completion time

### Quality Metrics
- Number of errors per scan
- Success rate (completed scans / total scans)
- Secret detection accuracy
- File processing accuracy

### Resource Metrics
- Peak memory usage
- Average CPU utilization
- Disk space usage
- Network bandwidth consumption

### Sample Metrics Report
```
Scan Date: 2025-12-16
Target: example.com
Files Processed: 100

Phase Timings:
- Phase 1 (Discovery): 12s
- Phase 2 (Download): 28s
- Phase 3 (TruffleHog): 9s
- Phase 4 (Processing): 22s
- Phase 5 (Beautify): 31s
- Phase 6 (Cleanup): 1s
Total Time: 103s (1m 43s)

Old Workflow Time: 15m 30s
Performance Improvement: 89% faster

Secrets Found: 3
Endpoints Extracted: 247
Parameters Extracted: 89
Domains Extracted: 12

Memory Usage: Peak 456MB
Errors: 0
Success Rate: 100%
```

---

## 📝 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-16 | Initial troubleshooting & deployment guide | Implementation Team |

---

## 🎓 Lessons Learned (Post-Deployment)

*This section should be updated after deployment with actual experiences:*

### What Went Well
- [To be filled after deployment]

### What Could Be Improved
- [To be filled after deployment]

### Unexpected Issues
- [To be filled after deployment]

### Recommendations for Future
- [To be filled after deployment]

---

**End of Document**
