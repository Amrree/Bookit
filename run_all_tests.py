#!/usr/bin/env python3
"""
Comprehensive test runner for the book-writing system.
Runs all tests and provides detailed analysis and improvement recommendations.
"""
import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime


class TestRunner:
    """Comprehensive test runner for the book-writing system."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": [],
            "summary": {},
            "recommendations": []
        }
        self.test_suites = [
            {
                "name": "Core Functionality",
                "file": "tests/test_core_functionality.py",
                "description": "Basic imports, instantiation, and core operations"
            },
            {
                "name": "Memory Operations",
                "file": "tests/test_memory_operations.py", 
                "description": "Memory manager operations and data validation"
            },
            {
                "name": "Simple Tests",
                "file": "tests/test_simple.py",
                "description": "Basic functionality verification"
            }
        ]
    
    def run_test_suite(self, suite):
        """Run a single test suite."""
        print(f"\n🧪 Running {suite['name']}...")
        print(f"   {suite['description']}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                suite["file"],
                "-v",
                "--tb=short"
            ], capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse test results using regex
            import re
            
            # Count test results by looking for the pattern: test_name PASSED/FAILED/SKIPPED/ERROR
            passed = len(re.findall(r'PASSED\s*\[', result.stdout))
            failed = len(re.findall(r'FAILED\s*\[', result.stdout))
            skipped = len(re.findall(r'SKIPPED\s*\[', result.stdout))
            errors = len(re.findall(r'ERROR\s*\[', result.stdout))
            
            
            suite_result = {
                "name": suite["name"],
                "file": suite["file"],
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "duration": duration,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "errors": errors,
                "total": passed + failed + skipped + errors,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            self.results["test_suites"].append(suite_result)
            
            if result.returncode == 0:
                print(f"   ✅ {suite['name']} - PASSED ({passed} tests)")
            else:
                print(f"   ❌ {suite['name']} - FAILED ({failed} failed, {errors} errors)")
            
            return suite_result
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {suite['name']} - TIMEOUT")
            return {
                "name": suite["name"],
                "status": "TIMEOUT",
                "duration": 300,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 1,
                "total": 1
            }
        except Exception as e:
            print(f"   ❌ {suite['name']} - ERROR: {e}")
            return {
                "name": suite["name"],
                "status": "ERROR",
                "duration": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 1,
                "total": 1,
                "error": str(e)
            }
    
    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Starting Comprehensive Test Suite for Book Writing System")
        print("=" * 70)
        
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_errors = 0
        total_duration = 0
        
        for suite in self.test_suites:
            result = self.run_test_suite(suite)
            total_passed += result.get("passed", 0)
            total_failed += result.get("failed", 0)
            total_skipped += result.get("skipped", 0)
            total_errors += result.get("errors", 0)
            total_duration += result.get("duration", 0)
        
        # Generate summary
        self.results["summary"] = {
            "total_tests": total_passed + total_failed + total_skipped + total_errors,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "errors": total_errors,
            "success_rate": (total_passed / (total_passed + total_failed + total_errors) * 100) if (total_passed + total_failed + total_errors) > 0 else 0,
            "total_duration": total_duration,
            "test_suites": len(self.test_suites)
        }
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Display summary
        self.display_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def generate_recommendations(self):
        """Generate improvement recommendations based on test results."""
        recommendations = []
        
        # Analyze test results
        total_tests = self.results["summary"]["total_tests"]
        passed_tests = self.results["summary"]["passed"]
        failed_tests = self.results["summary"]["failed"]
        success_rate = self.results["summary"]["success_rate"]
        
        if success_rate >= 90:
            recommendations.append({
                "priority": "low",
                "category": "performance",
                "issue": "High Success Rate",
                "solution": "System is performing well. Consider adding more edge case tests.",
                "impact": "maintenance"
            })
        elif success_rate >= 70:
            recommendations.append({
                "priority": "medium",
                "category": "reliability",
                "issue": "Moderate Success Rate",
                "solution": "Review failed tests and fix critical issues. Add more comprehensive error handling tests.",
                "impact": "stability"
            })
        else:
            recommendations.append({
                "priority": "high",
                "category": "reliability",
                "issue": "Low Success Rate",
                "solution": "Critical issues need immediate attention. Review and fix all failing tests.",
                "impact": "functionality"
            })
        
        # Analyze specific test suites
        for suite in self.results["test_suites"]:
            if suite["status"] == "FAILED":
                recommendations.append({
                    "priority": "high",
                    "category": "testing",
                    "issue": f"Failed Test Suite: {suite['name']}",
                    "solution": f"Review and fix issues in {suite['file']}. Check error messages for specific problems.",
                    "impact": "testing"
                })
            elif suite["status"] == "TIMEOUT":
                recommendations.append({
                    "priority": "medium",
                    "category": "performance",
                    "issue": f"Timeout in Test Suite: {suite['name']}",
                    "solution": f"Optimize performance in {suite['file']} or increase timeout limits.",
                    "impact": "performance"
                })
        
        # Add general recommendations
        recommendations.extend([
            {
                "priority": "medium",
                "category": "testing",
                "issue": "Test Coverage",
                "solution": "Add integration tests for complete workflows and edge cases.",
                "impact": "quality"
            },
            {
                "priority": "low",
                "category": "documentation",
                "issue": "Test Documentation",
                "solution": "Add comprehensive test documentation and examples.",
                "impact": "maintainability"
            },
            {
                "priority": "medium",
                "category": "automation",
                "issue": "Continuous Integration",
                "solution": "Set up automated testing pipeline for continuous validation.",
                "impact": "development"
            }
        ])
        
        self.results["recommendations"] = recommendations
    
    def display_summary(self):
        """Display test summary."""
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        summary = self.results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Skipped: {summary['skipped']} ⚠️")
        print(f"Errors: {summary['errors']} 🔥")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f} seconds")
        
        print("\n📋 TEST SUITE BREAKDOWN")
        print("-" * 70)
        for suite in self.results["test_suites"]:
            status_emoji = "✅" if suite["status"] == "PASSED" else "❌" if suite["status"] == "FAILED" else "⏰" if suite["status"] == "TIMEOUT" else "🔥"
            print(f"{status_emoji} {suite['name']:<25} {suite.get('passed', 0):>3} passed, {suite.get('failed', 0):>3} failed ({suite.get('duration', 0):.2f}s)")
        
        print("\n🎯 RECOMMENDATIONS")
        print("-" * 70)
        for i, rec in enumerate(self.results["recommendations"], 1):
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            print(f"{i}. {priority_emoji} {rec['issue']}")
            print(f"   Solution: {rec['solution']}")
            print(f"   Impact: {rec['impact']}")
            print()
    
    def save_results(self):
        """Save test results to files."""
        # Create results directory
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        json_file = results_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save markdown report
        md_file = results_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self.generate_markdown_report(md_file)
        
        print(f"\n📁 Results saved to:")
        print(f"   JSON: {json_file}")
        print(f"   Markdown: {md_file}")
    
    def generate_markdown_report(self, file_path):
        """Generate markdown test report."""
        report = f"""# Test Report - Book Writing System

**Generated:** {self.results['timestamp']}

## Summary

- **Total Tests:** {self.results['summary']['total_tests']}
- **Passed:** {self.results['summary']['passed']} ✅
- **Failed:** {self.results['summary']['failed']} ❌
- **Skipped:** {self.results['summary']['skipped']} ⚠️
- **Errors:** {self.results['summary']['errors']} 🔥
- **Success Rate:** {self.results['summary']['success_rate']:.1f}%
- **Total Duration:** {self.results['summary']['total_duration']:.2f} seconds

## Test Suites

"""
        
        for suite in self.results["test_suites"]:
            status_emoji = "✅" if suite["status"] == "PASSED" else "❌" if suite["status"] == "FAILED" else "⏰" if suite["status"] == "TIMEOUT" else "🔥"
            report += f"### {status_emoji} {suite['name']}\n\n"
            report += f"- **Status:** {suite['status']}\n"
            report += f"- **Duration:** {suite.get('duration', 0):.2f} seconds\n"
            report += f"- **Passed:** {suite.get('passed', 0)}\n"
            report += f"- **Failed:** {suite.get('failed', 0)}\n"
            report += f"- **Skipped:** {suite.get('skipped', 0)}\n"
            report += f"- **Errors:** {suite.get('errors', 0)}\n\n"
        
        report += "## Recommendations\n\n"
        
        for i, rec in enumerate(self.results["recommendations"], 1):
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            report += f"### {i}. {priority_emoji} {rec['issue']}\n\n"
            report += f"**Solution:** {rec['solution']}\n\n"
            report += f"**Impact:** {rec['impact']}\n\n"
            report += f"**Priority:** {rec['priority']}\n\n"
        
        report += "## Next Steps\n\n"
        report += "1. Review failed tests and fix critical issues\n"
        report += "2. Implement high-priority recommendations\n"
        report += "3. Add more comprehensive test coverage\n"
        report += "4. Set up continuous integration\n"
        report += "5. Monitor test performance over time\n"
        
        with open(file_path, 'w') as f:
            f.write(report)


def main():
    """Main function to run all tests."""
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # Return appropriate exit code
    if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()