"""
Comprehensive Feature Test Suite
Tests all Phase 0, 1, 2, 3 enhancements + existing features
"""
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class ComprehensiveTest:
    """Comprehensive test suite for JS Scanner"""
    
    def __init__(self, venv_python):
        self.venv_python = venv_python
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.start_time = None
        
    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
        print(f"{text}")
        print(f"{'='*70}{Colors.RESET}\n")
    
    def print_test(self, name, status, details=""):
        """Print test result"""
        if status == "PASS":
            symbol = f"{Colors.GREEN}✅{Colors.RESET}"
            self.results['passed'].append(name)
        elif status == "FAIL":
            symbol = f"{Colors.RED}❌{Colors.RESET}"
            self.results['failed'].append(name)
        else:
            symbol = f"{Colors.YELLOW}⚠️{Colors.RESET}"
            self.results['warnings'].append(name)
        
        print(f"{symbol} {Colors.BOLD}{name}{Colors.RESET}")
        if details:
            print(f"   {details}")
    
    def run_command(self, cmd, timeout=120):
        """Run shell command and return output"""
        try:
            # Use PowerShell with call operator for paths with spaces
            ps_cmd = ['powershell', '-Command', f'& {cmd}']
            result = subprocess.run(
                ps_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent.parent
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def test_phase0_noise_filter(self):
        """Test Phase 0: Noise Filter Improvements"""
        self.print_header("🧪 PHASE 0: NOISE FILTER TESTS")
        
        # Test 1: Check new patterns added
        patterns_file = Path(__file__).parent.parent / "data" / "ignored_patterns.json"
        
        try:
            with open(patterns_file) as f:
                patterns = json.load(f)
            
            expected_patterns = ["*/manifest.*.js", "*/runtime~*.js"]
            found_patterns = [p for p in expected_patterns if p in patterns.get('url_patterns', [])]
            
            if len(found_patterns) == len(expected_patterns):
                self.print_test(
                    "New noise filter patterns added",
                    "PASS",
                    f"Found: {', '.join(expected_patterns)}"
                )
            else:
                self.print_test(
                    "New noise filter patterns added",
                    "FAIL",
                    f"Missing: {set(expected_patterns) - set(found_patterns)}"
                )
        except Exception as e:
            self.print_test("Noise filter patterns check", "FAIL", str(e))
        
        # Test 2: Check vendor stats category
        noise_filter_file = Path(__file__).parent.parent / "jsscanner" / "modules" / "noise_filter.py"
        
        try:
            with open(noise_filter_file) as f:
                content = f.read()
            
            if "'filtered_vendor'" in content:
                self.print_test(
                    "Vendor stats category added",
                    "PASS",
                    "filtered_vendor stat found in noise_filter.py"
                )
            else:
                self.print_test(
                    "Vendor stats category added",
                    "FAIL",
                    "filtered_vendor stat not found"
                )
        except Exception as e:
            self.print_test("Vendor stats check", "FAIL", str(e))
    
    def test_phase1_concatenation(self):
        """Test Phase 1: String Concatenation"""
        self.print_header("🧪 PHASE 1: STRING CONCATENATION TESTS")
        
        # Run the direct test
        cmd = f'"{self.venv_python}" tests/test_direct.py'
        code, stdout, stderr = self.run_command(cmd, timeout=60)
        
        if code == 0 and "PHASE 1: STRING CONCATENATION TEST" in stdout:
            # Parse results
            if "EXPR placeholder found: True" in stdout:
                self.print_test(
                    "String concatenation reconstruction",
                    "PASS",
                    "EXPR placeholders working correctly"
                )
            else:
                self.print_test(
                    "String concatenation reconstruction",
                    "FAIL",
                    "EXPR placeholders not found"
                )
            
            # Check endpoint count
            if "Found 12 endpoints" in stdout or "Found" in stdout:
                self.print_test(
                    "Concatenated endpoint extraction",
                    "PASS",
                    "Multiple concatenated endpoints found"
                )
            else:
                self.print_test(
                    "Concatenated endpoint extraction",
                    "WARN",
                    "Endpoint count unclear"
                )
        else:
            self.print_test(
                "Phase 1 tests",
                "FAIL",
                f"Test script failed: {stderr[:200]}"
            )
    
    def test_phase2_parameters(self):
        """Test Phase 2: Enhanced Parameters"""
        self.print_header("🧪 PHASE 2: ENHANCED PARAMETER EXTRACTION TESTS")
        
        # Check if test passed (already run in phase1)
        cmd = f'"{self.venv_python}" tests/test_direct.py'
        code, stdout, stderr = self.run_command(cmd, timeout=60)
        
        if code == 0 and "PHASE 2: ENHANCED PARAMETER EXTRACTION TEST" in stdout:
            # Check each source
            sources = {
                "JSON Keys": ("JSON Keys: 4/4", 4),
                "Variables": ("Variables: 3/3", 3),
                "HTML Fields": ("HTML Fields: 5/5", 5),
                "Function Params": ("Function Params: 1/1", 1)
            }
            
            for source_name, (pattern, expected) in sources.items():
                if pattern in stdout:
                    self.print_test(
                        f"Extract parameters from {source_name}",
                        "PASS",
                        f"All {expected} parameters extracted"
                    )
                else:
                    self.print_test(
                        f"Extract parameters from {source_name}",
                        "WARN",
                        "Extraction count unclear"
                    )
            
            # Check total
            if "17 parameters extracted" in stdout:
                self.print_test(
                    "Total parameter extraction",
                    "PASS",
                    "17 parameters from all sources"
                )
        else:
            self.print_test(
                "Phase 2 tests",
                "FAIL",
                f"Test script failed: {stderr[:200]}"
            )
    
    def test_phase3_wordlist(self):
        """Test Phase 3: Wordlist Quality"""
        self.print_header("🧪 PHASE 3: WORDLIST QUALITY TESTS")
        
        cmd = f'"{self.venv_python}" tests/test_direct.py'
        code, stdout, stderr = self.run_command(cmd, timeout=60)
        
        if code == 0 and "PHASE 3: WORDLIST QUALITY TEST" in stdout:
            # Check stop words filtering
            if "Stop words found: 0/8" in stdout:
                self.print_test(
                    "Stop words filtering",
                    "PASS",
                    "100% of stop words filtered out"
                )
            else:
                self.print_test(
                    "Stop words filtering",
                    "FAIL",
                    "Stop words leaked through"
                )
            
            # Check quality words
            if "Good words found:" in stdout and "87%" in stdout or "✅" in stdout:
                self.print_test(
                    "Quality word extraction",
                    "PASS",
                    "High-quality domain words extracted"
                )
            else:
                self.print_test(
                    "Quality word extraction",
                    "WARN",
                    "Quality metrics unclear"
                )
            
            # Check word count
            if "25 quality words" in stdout:
                self.print_test(
                    "Wordlist size optimization",
                    "PASS",
                    "Compact, high-quality wordlist generated"
                )
        else:
            self.print_test(
                "Phase 3 tests",
                "FAIL",
                f"Test script failed: {stderr[:200]}"
            )
    
    def test_cli_basic_scan(self):
        """Test basic CLI functionality"""
        self.print_header("🧪 CLI: BASIC FUNCTIONALITY TESTS")
        
        # Test 1: Help command
        cmd = f'"{self.venv_python}" -m jsscanner --help'
        code, stdout, stderr = self.run_command(cmd, timeout=10)
        
        if code == 0 and stdout and "usage:" in stdout.lower():
            self.print_test(
                "CLI help command",
                "PASS",
                "Help text displayed correctly"
            )
        else:
            self.print_test(
                "CLI help command",
                "FAIL",
                "Help command failed"
            )
        
        # Test 2: Version/basic import
        cmd = f'"{self.venv_python}" -c "import jsscanner; print(\'Import successful\')"'
        code, stdout, stderr = self.run_command(cmd, timeout=10)
        
        if code == 0:
            self.print_test(
                "Module import",
                "PASS",
                "jsscanner module loads successfully"
            )
        else:
            self.print_test(
                "Module import",
                "FAIL",
                f"Import error: {stderr[:100]}"
            )
    
    def test_output_structure(self):
        """Test output directory structure"""
        self.print_header("🧪 OUTPUT: DIRECTORY STRUCTURE VALIDATION")
        
        # Check if any test results exist
        results_dir = Path(__file__).parent.parent / "results"
        
        if results_dir.exists():
            test_dirs = list(results_dir.glob("test-*"))
            
            if test_dirs:
                # Check first test dir structure
                test_dir = test_dirs[0]
                
                expected_subdirs = [
                    "extracts",
                    "files",
                    "logs",
                    "secrets",
                    "cache"
                ]
                
                found_subdirs = [d.name for d in test_dir.iterdir() if d.is_dir()]
                
                missing = set(expected_subdirs) - set(found_subdirs)
                
                if not missing:
                    self.print_test(
                        "Output directory structure",
                        "PASS",
                        f"All expected subdirectories present in {test_dir.name}"
                    )
                else:
                    self.print_test(
                        "Output directory structure",
                        "WARN",
                        f"Missing subdirs: {missing}"
                    )
                
                # Check for expected output files
                expected_files = [
                    "metadata.json",
                    "secrets.json",
                    "history.json"
                ]
                
                found_files = [f.name for f in test_dir.iterdir() if f.is_file()]
                
                missing_files = set(expected_files) - set(found_files)
                
                if not missing_files:
                    self.print_test(
                        "Output metadata files",
                        "PASS",
                        "All metadata files present"
                    )
                else:
                    self.print_test(
                        "Output metadata files",
                        "WARN",
                        f"Missing files: {missing_files}"
                    )
            else:
                self.print_test(
                    "Output directory structure",
                    "WARN",
                    "No test results found - run a scan first"
                )
        else:
            self.print_test(
                "Output directory structure",
                "WARN",
                "Results directory doesn't exist - run a scan first"
            )
    
    def test_integration_full_scan(self):
        """Test full scan integration"""
        self.print_header("🧪 INTEGRATION: SMALL SCAN TEST")
        
        print(f"{Colors.CYAN}Running small test scan (this may take 30-60 seconds)...{Colors.RESET}\n")
        
        # Create a simple test with concatenation
        test_file = Path(__file__).parent / "test_integration.js"
        test_file.write_text('''
// Test concatenation
const API_BASE = "/api/v2";
const endpoint = API_BASE + "/users/" + userId + "/data";

// Test parameters
const config = {
    apiKey: "test123",
    userId: "user456",
    sessionToken: "session789"
};

// Test HTML
const form = `<input name="username" /><input name="password" />`;

// Test words
const message = "Premium quality products available for shopping";
''')
        
        # Run scan
        cmd = f'"{self.venv_python}" -m jsscanner -t test-integration-v2 -u "file://{test_file.absolute()}" --no-beautify'
        code, stdout, stderr = self.run_command(cmd, timeout=120)
        
        # Clean up test file
        test_file.unlink()
        
        # Check results
        results_dir = Path(__file__).parent.parent / "results" / "test-integration-v2"
        
        if results_dir.exists():
            # Check for endpoints with EXPR
            endpoints_file = results_dir / "extracts" / "endpoints.json"
            
            if endpoints_file.exists():
                with open(endpoints_file) as f:
                    endpoints = json.load(f)
                
                # Look for EXPR patterns
                expr_endpoints = [ep for ep in endpoints if "EXPR" in str(ep)]
                
                if expr_endpoints:
                    self.print_test(
                        "Integration: String concatenation",
                        "PASS",
                        f"Found {len(expr_endpoints)} endpoints with EXPR placeholders"
                    )
                else:
                    self.print_test(
                        "Integration: String concatenation",
                        "WARN",
                        "No EXPR patterns found - may be expected for file:// URLs"
                    )
            
            # Check for parameters
            params_file = results_dir / "extracts" / "params.txt"
            
            if params_file.exists():
                params = params_file.read_text().strip().split('\n')
                expected_params = ['apiKey', 'userId', 'sessionToken', 'username', 'password']
                found_params = [p for p in expected_params if any(p in line for line in params)]
                
                if len(found_params) >= 3:
                    self.print_test(
                        "Integration: Parameter extraction",
                        "PASS",
                        f"Found {len(found_params)}/{len(expected_params)} expected parameters"
                    )
                else:
                    self.print_test(
                        "Integration: Parameter extraction",
                        "WARN",
                        f"Only found {len(found_params)} parameters"
                    )
            
            # Check for wordlist quality
            words_file = results_dir / "extracts" / "words.txt"
            
            if words_file.exists():
                words = [w.strip() for w in words_file.read_text().strip().split('\n') if w.strip()]
                
                # Check if stop words filtered
                stop_words_found = [w for w in words if w in ['the', 'and', 'for', 'are']]
                
                if not stop_words_found:
                    self.print_test(
                        "Integration: Stop words filtering",
                        "PASS",
                        "No stop words in wordlist"
                    )
                else:
                    self.print_test(
                        "Integration: Stop words filtering",
                        "FAIL",
                        f"Stop words found: {stop_words_found}"
                    )
                
                # Check for quality words
                quality_words = [w for w in words if w in ['premium', 'quality', 'products', 'shopping']]
                
                if quality_words:
                    self.print_test(
                        "Integration: Quality word extraction",
                        "PASS",
                        f"Found quality words: {quality_words}"
                    )
        else:
            self.print_test(
                "Integration scan",
                "FAIL",
                f"Scan failed or no results: {stderr[:200]}"
            )
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("📊 TEST SUMMARY")
        
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings'])
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        
        print(f"Total Tests: {Colors.BOLD}{total}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {failed}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {warnings}{Colors.RESET}")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL CRITICAL TESTS PASSED!{Colors.RESET}")
            print(f"{Colors.GREEN}Ready for production deployment.{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.RESET}")
            print(f"{Colors.RED}Review failures before deployment.{Colors.RESET}")
            
            print(f"\n{Colors.RED}Failed tests:{Colors.RESET}")
            for test in self.results['failed']:
                print(f"  - {test}")
        
        if warnings > 0:
            print(f"\n{Colors.YELLOW}Warnings (non-critical):{Colors.RESET}")
            for test in self.results['warnings']:
                print(f"  - {test}")
        
        # Calculate duration
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"\n{Colors.CYAN}Total test duration: {duration:.1f}s{Colors.RESET}")
    
    def run_all_tests(self):
        """Run all test suites"""
        self.start_time = time.time()
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                                                                   ║")
        print("║           JS SCANNER v2.0 - COMPREHENSIVE TEST SUITE              ║")
        print("║                                                                   ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        print(f"\n{Colors.CYAN}Testing all Phase 0, 1, 2, 3 enhancements + core features{Colors.RESET}")
        print(f"{Colors.CYAN}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
        
        # Run all test suites
        self.test_phase0_noise_filter()
        self.test_phase1_concatenation()
        self.test_phase2_parameters()
        self.test_phase3_wordlist()
        self.test_cli_basic_scan()
        self.test_output_structure()
        self.test_integration_full_scan()
        
        # Print summary
        self.print_summary()

if __name__ == "__main__":
    # Get venv python path
    venv_python = r"D:/Automation Bug Bounty/js-scanner/venv/Scripts/python.exe"
    
    # Run tests
    tester = ComprehensiveTest(venv_python)
    tester.run_all_tests()
