"""
Test runner and analysis tools for the book-writing system.
"""
import pytest
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRunner:
    """Comprehensive test runner for the book-writing system."""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("test_results")
        self.output_dir.mkdir(exist_ok=True)
        self.results = {
            "test_suite": "book_writing_system",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": [],
            "summary": {},
            "failures": [],
            "warnings": [],
            "performance_metrics": {}
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in the test suite."""
        print("🚀 Starting comprehensive test suite...")
        
        # Test categories
        test_categories = [
            "unit_tests",
            "integration_tests", 
            "system_tests",
            "performance_tests",
            "stress_tests"
        ]
        
        for category in test_categories:
            print(f"\n📋 Running {category}...")
            await self._run_test_category(category)
        
        # Generate summary
        self._generate_summary()
        
        # Save results
        await self._save_results()
        
        print(f"\n✅ Test suite completed. Results saved to {self.output_dir}")
        return self.results
    
    async def _run_test_category(self, category: str):
        """Run tests for a specific category."""
        category_results = {
            "category": category,
            "start_time": time.time(),
            "tests": [],
            "failures": [],
            "warnings": []
        }
        
        try:
            if category == "unit_tests":
                await self._run_unit_tests(category_results)
            elif category == "integration_tests":
                await self._run_integration_tests(category_results)
            elif category == "system_tests":
                await self._run_system_tests(category_results)
            elif category == "performance_tests":
                await self._run_performance_tests(category_results)
            elif category == "stress_tests":
                await self._run_stress_tests(category_results)
            
            category_results["end_time"] = time.time()
            category_results["duration"] = category_results["end_time"] - category_results["start_time"]
            
        except Exception as e:
            category_results["error"] = str(e)
            category_results["end_time"] = time.time()
            category_results["duration"] = category_results["end_time"] - category_results["start_time"]
        
        self.results["tests"].append(category_results)
    
    async def _run_unit_tests(self, results: Dict[str, Any]):
        """Run unit tests."""
        unit_test_modules = [
            "test_document_ingestor",
            "test_memory_manager", 
            "test_llm_client",
            "test_tool_manager",
            "test_agents",
            "test_full_book_generator",
            "test_cli",
            "test_gui"
        ]
        
        for module in unit_test_modules:
            try:
                print(f"  Running {module}...")
                start_time = time.time()
                
                # Run pytest for the module
                result = await self._run_pytest_module(module)
                
                end_time = time.time()
                duration = end_time - start_time
                
                results["tests"].append({
                    "module": module,
                    "status": "passed" if result["returncode"] == 0 else "failed",
                    "duration": duration,
                    "output": result["stdout"],
                    "errors": result["stderr"]
                })
                
                if result["returncode"] != 0:
                    results["failures"].append({
                        "module": module,
                        "error": result["stderr"]
                    })
                
            except Exception as e:
                results["failures"].append({
                    "module": module,
                    "error": str(e)
                })
    
    async def _run_integration_tests(self, results: Dict[str, Any]):
        """Run integration tests."""
        try:
            print("  Running integration tests...")
            start_time = time.time()
            
            result = await self._run_pytest_module("test_integration")
            
            end_time = time.time()
            duration = end_time - start_time
            
            results["tests"].append({
                "module": "test_integration",
                "status": "passed" if result["returncode"] == 0 else "failed",
                "duration": duration,
                "output": result["stdout"],
                "errors": result["stderr"]
            })
            
            if result["returncode"] != 0:
                results["failures"].append({
                    "module": "test_integration",
                    "error": result["stderr"]
                })
                
        except Exception as e:
            results["failures"].append({
                "module": "test_integration",
                "error": str(e)
            })
    
    async def _run_system_tests(self, results: Dict[str, Any]):
        """Run system tests."""
        try:
            print("  Running system tests...")
            start_time = time.time()
            
            result = await self._run_pytest_module("test_system")
            
            end_time = time.time()
            duration = end_time - start_time
            
            results["tests"].append({
                "module": "test_system",
                "status": "passed" if result["returncode"] == 0 else "failed",
                "duration": duration,
                "output": result["stdout"],
                "errors": result["stderr"]
            })
            
            if result["returncode"] != 0:
                results["failures"].append({
                    "module": "test_system",
                    "error": result["stderr"]
                })
                
        except Exception as e:
            results["failures"].append({
                "module": "test_system",
                "error": str(e)
            })
    
    async def _run_performance_tests(self, results: Dict[str, Any]):
        """Run performance tests."""
        try:
            print("  Running performance tests...")
            start_time = time.time()
            
            # Run performance-specific tests
            result = await self._run_pytest_module("test_system", "-k", "performance")
            
            end_time = time.time()
            duration = end_time - start_time
            
            results["tests"].append({
                "module": "performance_tests",
                "status": "passed" if result["returncode"] == 0 else "failed",
                "duration": duration,
                "output": result["stdout"],
                "errors": result["stderr"]
            })
            
            if result["returncode"] != 0:
                results["failures"].append({
                    "module": "performance_tests",
                    "error": result["stderr"]
                })
                
        except Exception as e:
            results["failures"].append({
                "module": "performance_tests",
                "error": str(e)
            })
    
    async def _run_stress_tests(self, results: Dict[str, Any]):
        """Run stress tests."""
        try:
            print("  Running stress tests...")
            start_time = time.time()
            
            # Run stress-specific tests
            result = await self._run_pytest_module("test_system", "-k", "stress")
            
            end_time = time.time()
            duration = end_time - start_time
            
            results["tests"].append({
                "module": "stress_tests",
                "status": "passed" if result["returncode"] == 0 else "failed",
                "duration": duration,
                "output": result["stdout"],
                "errors": result["stderr"]
            })
            
            if result["returncode"] != 0:
                results["failures"].append({
                    "module": "stress_tests",
                    "error": result["stderr"]
                })
                
        except Exception as e:
            results["failures"].append({
                "module": "stress_tests",
                "error": str(e)
            })
    
    async def _run_pytest_module(self, module: str, *args) -> Dict[str, Any]:
        """Run a specific pytest module."""
        import subprocess
        
        cmd = [
            sys.executable, "-m", "pytest",
            f"tests/{module}.py",
            "-v",
            "--tb=short",
            *args
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def _generate_summary(self):
        """Generate test summary."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        total_duration = 0
        
        for category in self.results["tests"]:
            for test in category["tests"]:
                total_tests += 1
                if test["status"] == "passed":
                    passed_tests += 1
                else:
                    failed_tests += 1
                total_duration += test.get("duration", 0)
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "categories": len(self.results["tests"])
        }
    
    async def _save_results(self):
        """Save test results to files."""
        # Save JSON results
        json_file = self.output_dir / "test_results.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save human-readable report
        report_file = self.output_dir / "test_report.md"
        await self._generate_markdown_report(report_file)
    
    async def _generate_markdown_report(self, report_file: Path):
        """Generate a markdown test report."""
        report = f"""# Test Report - Book Writing System

**Generated:** {self.results['timestamp']}

## Summary

- **Total Tests:** {self.results['summary']['total_tests']}
- **Passed:** {self.results['summary']['passed_tests']}
- **Failed:** {self.results['summary']['failed_tests']}
- **Success Rate:** {self.results['summary']['success_rate']:.1f}%
- **Total Duration:** {self.results['summary']['total_duration']:.2f} seconds

## Test Categories

"""
        
        for category in self.results["tests"]:
            report += f"### {category['category'].replace('_', ' ').title()}\n\n"
            report += f"- **Duration:** {category.get('duration', 0):.2f} seconds\n"
            report += f"- **Tests Run:** {len(category['tests'])}\n"
            
            if category.get('failures'):
                report += f"- **Failures:** {len(category['failures'])}\n"
                for failure in category['failures']:
                    report += f"  - {failure['module']}: {failure['error']}\n"
            
            report += "\n"
        
        # Add detailed test results
        report += "## Detailed Results\n\n"
        
        for category in self.results["tests"]:
            report += f"### {category['category'].replace('_', ' ').title()}\n\n"
            
            for test in category['tests']:
                status_emoji = "✅" if test['status'] == "passed" else "❌"
                report += f"- {status_emoji} **{test['module']}** ({test.get('duration', 0):.2f}s)\n"
                
                if test['status'] == "failed" and test.get('errors'):
                    report += f"  - Error: {test['errors']}\n"
            
            report += "\n"
        
        # Add recommendations
        report += "## Recommendations\n\n"
        
        if self.results['summary']['failed_tests'] > 0:
            report += "### Failed Tests\n"
            report += "- Review failed test modules and fix issues\n"
            report += "- Check error messages for specific problems\n"
            report += "- Ensure all dependencies are properly installed\n\n"
        
        if self.results['summary']['success_rate'] < 80:
            report += "### Low Success Rate\n"
            report += "- Consider running tests in isolation to identify issues\n"
            report += "- Check for missing dependencies or configuration\n"
            report += "- Review test setup and fixtures\n\n"
        
        report += "### Performance\n"
        report += "- Monitor test execution times\n"
        report += "- Consider parallel test execution for faster runs\n"
        report += "- Optimize slow tests if needed\n\n"
        
        with open(report_file, 'w') as f:
            f.write(report)


class TestAnalyzer:
    """Analyze test results and provide optimization recommendations."""
    
    def __init__(self, results_file: Path):
        self.results_file = results_file
        self.results = None
        self.analysis = {}
    
    async def load_results(self):
        """Load test results from file."""
        with open(self.results_file, 'r') as f:
            self.results = json.load(f)
    
    async def analyze_failures(self) -> Dict[str, Any]:
        """Analyze test failures and provide recommendations."""
        if not self.results:
            await self.load_results()
        
        failure_analysis = {
            "common_issues": [],
            "module_issues": {},
            "recommendations": []
        }
        
        # Analyze failures by category
        for category in self.results["tests"]:
            if category.get('failures'):
                for failure in category['failures']:
                    module = failure['module']
                    error = failure['error']
                    
                    if module not in failure_analysis["module_issues"]:
                        failure_analysis["module_issues"][module] = []
                    
                    failure_analysis["module_issues"][module].append(error)
        
        # Identify common issues
        all_errors = []
        for module_errors in failure_analysis["module_issues"].values():
            all_errors.extend(module_errors)
        
        # Count error patterns
        error_patterns = {}
        for error in all_errors:
            # Extract common error patterns
            if "ImportError" in error:
                error_patterns["ImportError"] = error_patterns.get("ImportError", 0) + 1
            elif "ModuleNotFoundError" in error:
                error_patterns["ModuleNotFoundError"] = error_patterns.get("ModuleNotFoundError", 0) + 1
            elif "AttributeError" in error:
                error_patterns["AttributeError"] = error_patterns.get("AttributeError", 0) + 1
            elif "ConnectionError" in error:
                error_patterns["ConnectionError"] = error_patterns.get("ConnectionError", 0) + 1
            elif "TimeoutError" in error:
                error_patterns["TimeoutError"] = error_patterns.get("TimeoutError", 0) + 1
        
        failure_analysis["common_issues"] = error_patterns
        
        # Generate recommendations
        if "ImportError" in error_patterns or "ModuleNotFoundError" in error_patterns:
            failure_analysis["recommendations"].append({
                "issue": "Missing Dependencies",
                "solution": "Install missing packages using pip install -r requirements.txt",
                "priority": "high"
            })
        
        if "ConnectionError" in error_patterns:
            failure_analysis["recommendations"].append({
                "issue": "Network/Service Issues",
                "solution": "Check external service availability (Ollama, OpenAI API)",
                "priority": "medium"
            })
        
        if "AttributeError" in error_patterns:
            failure_analysis["recommendations"].append({
                "issue": "Code Structure Issues",
                "solution": "Review method names and object attributes",
                "priority": "high"
            })
        
        if "TimeoutError" in error_patterns:
            failure_analysis["recommendations"].append({
                "issue": "Performance Issues",
                "solution": "Optimize slow operations and increase timeouts",
                "priority": "medium"
            })
        
        return failure_analysis
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze test performance and provide optimization recommendations."""
        if not self.results:
            await self.load_results()
        
        performance_analysis = {
            "slow_tests": [],
            "performance_metrics": {},
            "recommendations": []
        }
        
        # Find slow tests
        for category in self.results["tests"]:
            for test in category['tests']:
                duration = test.get('duration', 0)
                if duration > 10:  # Tests taking more than 10 seconds
                    performance_analysis["slow_tests"].append({
                        "module": test['module'],
                        "duration": duration,
                        "category": category['category']
                    })
        
        # Calculate performance metrics
        total_duration = sum(
            test.get('duration', 0) 
            for category in self.results["tests"] 
            for test in category['tests']
        )
        
        performance_analysis["performance_metrics"] = {
            "total_duration": total_duration,
            "average_test_duration": total_duration / self.results['summary']['total_tests'] if self.results['summary']['total_tests'] > 0 else 0,
            "slow_test_count": len(performance_analysis["slow_tests"])
        }
        
        # Generate performance recommendations
        if performance_analysis["slow_test_count"] > 0:
            performance_analysis["recommendations"].append({
                "issue": "Slow Tests",
                "solution": "Optimize slow tests or run them in parallel",
                "priority": "medium"
            })
        
        if total_duration > 300:  # More than 5 minutes
            performance_analysis["recommendations"].append({
                "issue": "Long Test Suite Duration",
                "solution": "Consider parallel test execution or test splitting",
                "priority": "low"
            })
        
        return performance_analysis
    
    async def generate_optimization_report(self) -> str:
        """Generate a comprehensive optimization report."""
        if not self.results:
            await self.load_results()
        
        failure_analysis = await self.analyze_failures()
        performance_analysis = await self.analyze_performance()
        
        report = f"""# Test Analysis and Optimization Report

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

- **Test Success Rate:** {self.results['summary']['success_rate']:.1f}%
- **Total Tests:** {self.results['summary']['total_tests']}
- **Failed Tests:** {self.results['summary']['failed_tests']}
- **Total Duration:** {self.results['summary']['total_duration']:.2f} seconds

## Failure Analysis

### Common Issues
"""
        
        for issue, count in failure_analysis["common_issues"].items():
            report += f"- **{issue}:** {count} occurrences\n"
        
        report += "\n### Module-Specific Issues\n"
        
        for module, errors in failure_analysis["module_issues"].items():
            report += f"\n#### {module}\n"
            for error in errors:
                report += f"- {error}\n"
        
        report += "\n### Recommendations\n"
        
        for rec in failure_analysis["recommendations"]:
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            report += f"- {priority_emoji} **{rec['issue']}:** {rec['solution']}\n"
        
        report += "\n## Performance Analysis\n"
        
        metrics = performance_analysis.get('performance_metrics', {})
        report += f"- **Total Duration:** {metrics.get('total_duration', 0):.2f} seconds\n"
        report += f"- **Average Test Duration:** {metrics.get('average_test_duration', 0):.2f} seconds\n"
        report += f"- **Slow Tests:** {metrics.get('slow_test_count', 0)}\n"
        
        if performance_analysis["slow_tests"]:
            report += "\n### Slow Tests\n"
            for test in performance_analysis["slow_tests"]:
                report += f"- **{test['module']}:** {test['duration']:.2f}s ({test['category']})\n"
        
        report += "\n### Performance Recommendations\n"
        
        for rec in performance_analysis["recommendations"]:
            priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            report += f"- {priority_emoji} **{rec['issue']}:** {rec['solution']}\n"
        
        report += "\n## Next Steps\n"
        
        if failure_analysis["recommendations"]:
            report += "1. **Address High Priority Issues:** Fix critical failures first\n"
        
        if performance_analysis["recommendations"]:
            report += "2. **Optimize Performance:** Implement performance improvements\n"
        
        report += "3. **Re-run Tests:** Verify fixes and improvements\n"
        report += "4. **Monitor Continuously:** Set up automated testing\n"
        
        return report


async def main():
    """Main function to run tests and analysis."""
    print("🧪 Starting Book Writing System Test Suite")
    
    # Create test runner
    runner = TestRunner()
    
    # Run all tests
    results = await runner.run_all_tests()
    
    # Analyze results
    analyzer = TestAnalyzer(runner.output_dir / "test_results.json")
    optimization_report = await analyzer.generate_optimization_report()
    
    # Save optimization report
    report_file = runner.output_dir / "optimization_report.md"
    with open(report_file, 'w') as f:
        f.write(optimization_report)
    
    print(f"\n📊 Analysis complete. Reports saved to {runner.output_dir}")
    print(f"📈 Success rate: {results['summary']['success_rate']:.1f}%")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())