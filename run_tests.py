#!/usr/bin/env python3
"""
Comprehensive test runner for Malta Tax AI Backend
Runs all test suites and generates detailed reports
"""
import subprocess
import sys
import os
import time
import json
from datetime import datetime


class TestRunner:
    """Comprehensive test runner with reporting"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "overall_status": "unknown",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "coverage_percentage": 0
        }
    
    def run_test_suite(self, suite_name, test_path, markers=None):
        """Run a specific test suite"""
        print(f"\n{'='*60}")
        print(f"Running {suite_name}")
        print(f"{'='*60}")
        
        cmd = ["python", "-m", "pytest", test_path, "-v"]
        
        if markers:
            cmd.extend(["-m", markers])
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            
            # Extract test results
            passed = 0
            failed = 0
            errors = 0
            
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Parse summary line like "5 passed, 2 failed in 1.23s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            passed = int(parts[i-1])
                        elif part == "failed":
                            failed = int(parts[i-1])
                        elif part == "error" or part == "errors":
                            errors = int(parts[i-1])
                elif line.strip().endswith(" passed"):
                    # Parse line like "5 passed in 1.23s"
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "passed":
                        passed = int(parts[0])
            
            success = result.returncode == 0
            
            self.results["test_suites"][suite_name] = {
                "status": "passed" if success else "failed",
                "duration": duration,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "total": passed + failed + errors,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            self.results["total_tests"] += passed + failed + errors
            self.results["passed_tests"] += passed
            self.results["failed_tests"] += failed + errors
            
            print(f"✅ {suite_name}: {passed} passed, {failed} failed, {errors} errors")
            print(f"⏱️  Duration: {duration:.2f}s")
            
            if not success:
                print(f"❌ {suite_name} FAILED")
                print("STDERR:", result.stderr)
                
            return success
            
        except Exception as e:
            print(f"❌ Error running {suite_name}: {e}")
            self.results["test_suites"][suite_name] = {
                "status": "error",
                "error": str(e),
                "duration": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "total": 1
            }
            return False
    
    def run_coverage_report(self):
        """Generate coverage report"""
        print(f"\n{'='*60}")
        print("Generating Coverage Report")
        print(f"{'='*60}")
        
        try:
            # Run tests with coverage
            result = subprocess.run([
                "python", "-m", "pytest",
                "tests/unit/",
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=json:coverage.json"
            ], capture_output=True, text=True)
            
            # Parse coverage from JSON report
            try:
                with open("coverage.json", "r") as f:
                    coverage_data = json.load(f)
                    self.results["coverage_percentage"] = coverage_data["totals"]["percent_covered"]
            except:
                # Parse from stdout
                for line in result.stdout.split('\n'):
                    if "TOTAL" in line and "%" in line:
                        parts = line.split()
                        for part in parts:
                            if part.endswith('%'):
                                self.results["coverage_percentage"] = float(part[:-1])
                                break
            
            print(f"📊 Coverage: {self.results['coverage_percentage']:.1f}%")
            
        except Exception as e:
            print(f"❌ Error generating coverage report: {e}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Test Suite for Malta Tax AI Backend")
        print(f"Timestamp: {self.results['timestamp']}")
        
        # Test suites to run
        test_suites = [
            ("Unit Tests", "tests/unit/", "unit"),
            ("Integration Tests", "tests/integration/", "integration"),
            ("Security Tests", "tests/security_tests.py", "security"),
            ("Performance Tests", "tests/performance_tests.py", "performance")
        ]
        
        all_passed = True
        
        # Run each test suite
        for suite_name, test_path, markers in test_suites:
            if os.path.exists(test_path):
                success = self.run_test_suite(suite_name, test_path, markers)
                if not success:
                    all_passed = False
            else:
                print(f"⚠️  Skipping {suite_name} - path not found: {test_path}")
        
        # Generate coverage report
        self.run_coverage_report()
        
        # Determine overall status
        if all_passed and self.results["failed_tests"] == 0:
            self.results["overall_status"] = "passed"
        else:
            self.results["overall_status"] = "failed"
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        return all_passed
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        
        print(f"Overall Status: {'✅ PASSED' if self.results['overall_status'] == 'passed' else '❌ FAILED'}")
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed_tests']}")
        print(f"Failed: {self.results['failed_tests']}")
        print(f"Success Rate: {(self.results['passed_tests'] / max(self.results['total_tests'], 1)) * 100:.1f}%")
        print(f"Coverage: {self.results['coverage_percentage']:.1f}%")
        
        print(f"\nTest Suite Results:")
        for suite_name, suite_result in self.results["test_suites"].items():
            status_icon = "✅" if suite_result["status"] == "passed" else "❌"
            print(f"  {status_icon} {suite_name}: {suite_result['passed']} passed, {suite_result['failed']} failed ({suite_result['duration']:.2f}s)")
        
        # Quality gates
        print(f"\n{'='*60}")
        print("QUALITY GATES")
        print(f"{'='*60}")
        
        gates = [
            ("All tests pass", self.results["failed_tests"] == 0),
            ("Coverage >= 80%", self.results["coverage_percentage"] >= 80),
            ("No security vulnerabilities", self.results["test_suites"].get("Security Tests", {}).get("failed", 1) == 0),
            ("Performance requirements met", self.results["test_suites"].get("Performance Tests", {}).get("failed", 1) == 0)
        ]
        
        for gate_name, gate_passed in gates:
            status_icon = "✅" if gate_passed else "❌"
            print(f"  {status_icon} {gate_name}")
    
    def save_results(self):
        """Save test results to file"""
        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Test results saved to test_results.json")
        print(f"📊 Coverage report available in htmlcov/index.html")


def main():
    """Main test runner function"""
    runner = TestRunner()
    
    # Check if API server is running
    try:
        import requests
        response = requests.get("http://localhost:5004/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  Warning: API server not responding. Some tests may fail.")
    except:
        print("⚠️  Warning: Cannot connect to API server. Integration and performance tests will be skipped.")
    
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! System is ready for production.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please review and fix issues before production deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()

