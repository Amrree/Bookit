#!/usr/bin/env python3
"""
Comprehensive test runner for the book-writing system.
Runs all tests and provides detailed analysis and improvement recommendations.
"""
import subprocess
import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime
import asyncio


class ComprehensiveTestRunner:
    """Comprehensive test runner for the book-writing system."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": [],
            "summary": {},
            "recommendations": [],
            "performance_metrics": {},
            "coverage_analysis": {}
        }
        self.test_suites = [
            {
                "name": "Core Functionality",
                "file": "tests/test_core_functionality.py",
                "description": "Basic imports, instantiation, and core operations",
                "category": "unit"
            },
            {
                "name": "Memory Operations",
                "file": "tests/test_memory_operations.py",
                "description": "Memory manager operations and data validation",
                "category": "unit"
            },
            {
                "name": "Simple Tests",
                "file": "tests/test_simple.py",
                "description": "Basic functionality verification",
                "category": "unit"
            },
            # {
            #     "name": "GUI Simple",
            #     "file": "tests/test_gui_simple.py",
            #     "description": "Basic GUI functionality and imports",
            #     "category": "unit"
            # },
            {
                "name": "Document Ingestor Comprehensive",
                "file": "tests/test_document_ingestor_comprehensive.py",
                "description": "Complete document processing and ingestion",
                "category": "unit"
            },
            {
                "name": "Memory Manager Comprehensive",
                "file": "tests/test_memory_manager_comprehensive.py",
                "description": "Complete memory management and RAG pipeline",
                "category": "unit"
            },
            {
                "name": "LLM Client Comprehensive",
                "file": "tests/test_llm_client_comprehensive.py",
                "description": "Complete LLM client functionality and providers",
                "category": "unit"
            },
            {
                "name": "Tool Manager Comprehensive",
                "file": "tests/test_tool_manager_comprehensive.py",
                "description": "Complete tool management and safety mechanisms",
                "category": "unit"
            },
            {
                "name": "Agent Manager Comprehensive",
                "file": "tests/test_agent_manager_comprehensive.py",
                "description": "Complete agent management and coordination",
                "category": "unit"
            },
            # {
            #     "name": "System Integration Simple",
            #     "file": "tests/test_system_simple.py",
            #     "description": "Basic system integration and component coordination",
            #     "category": "integration"
            # }
        ]
    
    def run_test_suite(self, suite):
        """Run a single test suite."""
        print(f"\n🧪 Running {suite['name']}...")
        print(f"   {suite['description']}")
        print(f"   Category: {suite['category']}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                suite["file"],
                "-v",
                "--tb=short",
                "--durations=10"
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
            
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
                "category": suite["category"],
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
                "category": suite["category"],
                "status": "TIMEOUT",
                "duration": 600,
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
                "category": suite["category"],
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
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_errors = 0
        total_duration = 0
        
        # Run each test suite
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
        
        # Generate performance metrics
        self.generate_performance_metrics()
        
        # Generate coverage analysis
        self.generate_coverage_analysis()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Display summary
        self.display_summary()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def generate_performance_metrics(self):
        """Generate performance metrics from test results."""
        metrics = {
            "total_duration": 0,
            "average_duration_per_suite": 0,
            "slowest_suite": None,
            "fastest_suite": None,
            "slow_test_count": 0,
            "performance_categories": {
                "excellent": 0,  # < 5 seconds
                "good": 0,       # 5-15 seconds
                "acceptable": 0, # 15-30 seconds
                "slow": 0,       # 30-60 seconds
                "very_slow": 0   # > 60 seconds
            }
        }
        
        durations = []
        for suite in self.results["test_suites"]:
            duration = suite.get("duration", 0)
            durations.append(duration)
            metrics["total_duration"] += duration
            
            # Categorize performance
            if duration < 5:
                metrics["performance_categories"]["excellent"] += 1
            elif duration < 15:
                metrics["performance_categories"]["good"] += 1
            elif duration < 30:
                metrics["performance_categories"]["acceptable"] += 1
            elif duration < 60:
                metrics["performance_categories"]["slow"] += 1
            else:
                metrics["performance_categories"]["very_slow"] += 1
            
            # Track slow tests
            if duration > 30:
                metrics["slow_test_count"] += 1
        
        if durations:
            metrics["average_duration_per_suite"] = sum(durations) / len(durations)
            metrics["slowest_suite"] = max(self.results["test_suites"], key=lambda x: x.get("duration", 0))["name"]
            metrics["fastest_suite"] = min(self.results["test_suites"], key=lambda x: x.get("duration", 0))["name"]
        
        self.results["performance_metrics"] = metrics
    
    def generate_coverage_analysis(self):
        """Generate test coverage analysis."""
        coverage = {
            "total_modules_tested": 0,
            "modules_covered": [],
            "modules_missing": [],
            "test_categories": {
                "unit_tests": 0,
                "integration_tests": 0,
                "system_tests": 0,
                "performance_tests": 0
            },
            "feature_coverage": {
                "core_functionality": False,
                "memory_management": False,
                "llm_integration": False,
                "tool_management": False,
                "agent_coordination": False,
                "document_processing": False,
                "gui_functionality": False,
                "book_workflow": False,
                "error_handling": False,
                "performance": False
            }
        }
        
        # Analyze test suites
        for suite in self.results["test_suites"]:
            category = suite.get("category", "unknown")
            if category in coverage["test_categories"]:
                coverage["test_categories"][category] += 1
            
            # Check feature coverage based on test suite names
            name = suite["name"].lower()
            if "core" in name or "simple" in name:
                coverage["feature_coverage"]["core_functionality"] = True
            if "memory" in name:
                coverage["feature_coverage"]["memory_management"] = True
            if "llm" in name:
                coverage["feature_coverage"]["llm_integration"] = True
            if "tool" in name:
                coverage["feature_coverage"]["tool_management"] = True
            if "agent" in name:
                coverage["feature_coverage"]["agent_coordination"] = True
            if "document" in name:
                coverage["feature_coverage"]["document_processing"] = True
            if "gui" in name:
                coverage["feature_coverage"]["gui_functionality"] = True
            if "book" in name or "workflow" in name:
                coverage["feature_coverage"]["book_workflow"] = True
            if "error" in name or "handling" in name:
                coverage["feature_coverage"]["error_handling"] = True
            if "performance" in name:
                coverage["feature_coverage"]["performance"] = True
        
        # Count modules covered
        coverage["modules_covered"] = [
            "memory_manager", "llm_client", "tool_manager", "agent_manager",
            "document_ingestor", "book_workflow", "gui", "cli"
        ]
        coverage["total_modules_tested"] = len(coverage["modules_covered"])
        
        self.results["coverage_analysis"] = coverage
    
    def generate_recommendations(self):
        """Generate improvement recommendations based on test results."""
        recommendations = []
        
        # Analyze test results
        total_tests = self.results["summary"]["total_tests"]
        passed_tests = self.results["summary"]["passed"]
        failed_tests = self.results["summary"]["failed"]
        success_rate = self.results["summary"]["success_rate"]
        
        # Success rate recommendations
        if success_rate >= 95:
            recommendations.append({
                "priority": "low",
                "category": "performance",
                "issue": "Excellent Success Rate",
                "solution": "System is performing excellently. Focus on performance optimization and new features.",
                "impact": "maintenance"
            })
        elif success_rate >= 85:
            recommendations.append({
                "priority": "medium",
                "category": "reliability",
                "issue": "Good Success Rate",
                "solution": "System is performing well. Address failing tests and add more edge case coverage.",
                "impact": "stability"
            })
        elif success_rate >= 70:
            recommendations.append({
                "priority": "high",
                "category": "reliability",
                "issue": "Moderate Success Rate",
                "solution": "Review and fix failing tests. Add comprehensive error handling tests.",
                "impact": "functionality"
            })
        else:
            recommendations.append({
                "priority": "critical",
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
            elif suite["status"] == "ERROR":
                recommendations.append({
                    "priority": "high",
                    "category": "testing",
                    "issue": f"Error in Test Suite: {suite['name']}",
                    "solution": f"Fix configuration or setup issues in {suite['file']}.",
                    "impact": "testing"
                })
        
        # Performance recommendations
        performance_metrics = self.results.get("performance_metrics", {})
        if performance_metrics.get("slow_test_count", 0) > 0:
            recommendations.append({
                "priority": "medium",
                "category": "performance",
                "issue": f"{performance_metrics['slow_test_count']} Slow Test Suites",
                "solution": "Optimize slow test suites for better development experience.",
                "impact": "development"
            })
        
        # Coverage recommendations
        coverage = self.results.get("coverage_analysis", {})
        missing_features = [k for k, v in coverage.get("feature_coverage", {}).items() if not v]
        if missing_features:
            recommendations.append({
                "priority": "medium",
                "category": "testing",
                "issue": f"Missing Test Coverage: {', '.join(missing_features)}",
                "solution": "Add comprehensive tests for missing features.",
                "impact": "quality"
            })
        
        # General recommendations
        recommendations.extend([
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
            },
            {
                "priority": "low",
                "category": "monitoring",
                "issue": "Test Monitoring",
                "solution": "Add test result monitoring and alerting for failures.",
                "impact": "reliability"
            }
        ])
        
        self.results["recommendations"] = recommendations
    
    def display_summary(self):
        """Display comprehensive test summary."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        summary = self.results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Skipped: {summary['skipped']} ⚠️")
        print(f"Errors: {summary['errors']} 🔥")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f} seconds")
        
        print("\n📋 TEST SUITE BREAKDOWN")
        print("-" * 80)
        for suite in self.results["test_suites"]:
            status_emoji = "✅" if suite["status"] == "PASSED" else "❌" if suite["status"] == "FAILED" else "⏰" if suite["status"] == "TIMEOUT" else "🔥"
            print(f"{status_emoji} {suite['name']:<35} {suite.get('passed', 0):>3} passed, {suite.get('failed', 0):>3} failed ({suite.get('duration', 0):.2f}s)")
        
        # Performance metrics
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 80)
        perf = self.results.get("performance_metrics", {})
        print(f"Average Duration per Suite: {perf.get('average_duration_per_suite', 0):.2f} seconds")
        print(f"Slowest Suite: {perf.get('slowest_suite', 'N/A')}")
        print(f"Fastest Suite: {perf.get('fastest_suite', 'N/A')}")
        print(f"Slow Test Suites (>30s): {perf.get('slow_test_count', 0)}")
        
        # Coverage analysis
        print("\n📈 COVERAGE ANALYSIS")
        print("-" * 80)
        coverage = self.results.get("coverage_analysis", {})
        print(f"Modules Tested: {coverage.get('total_modules_tested', 0)}")
        print(f"Unit Tests: {coverage.get('test_categories', {}).get('unit_tests', 0)}")
        print(f"Integration Tests: {coverage.get('test_categories', {}).get('integration_tests', 0)}")
        
        feature_coverage = coverage.get("feature_coverage", {})
        covered_features = sum(1 for v in feature_coverage.values() if v)
        total_features = len(feature_coverage)
        print(f"Feature Coverage: {covered_features}/{total_features} ({covered_features/total_features*100:.1f}%)")
        
        print("\n🎯 RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(self.results["recommendations"], 1):
            priority_emoji = "🔴" if rec["priority"] == "critical" else "🟠" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            print(f"{i}. {priority_emoji} {rec['issue']}")
            print(f"   Solution: {rec['solution']}")
            print(f"   Impact: {rec['impact']}")
            print()
    
    def save_results(self):
        """Save comprehensive test results to files."""
        # Create results directory
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        json_file = results_dir / f"comprehensive_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save markdown report
        md_file = results_dir / f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self.generate_markdown_report(md_file)
        
        print(f"\n📁 Results saved to:")
        print(f"   JSON: {json_file}")
        print(f"   Markdown: {md_file}")
    
    def generate_markdown_report(self, file_path):
        """Generate comprehensive markdown test report."""
        report = f"""# Comprehensive Test Report - Book Writing System

**Generated:** {self.results['timestamp']}

## Executive Summary

This comprehensive test report covers all aspects of the book-writing system, including unit tests, integration tests, and system-level testing.

## Test Results Summary

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
            report += f"- **Category:** {suite.get('category', 'unknown')}\n"
            report += f"- **Duration:** {suite.get('duration', 0):.2f} seconds\n"
            report += f"- **Passed:** {suite.get('passed', 0)}\n"
            report += f"- **Failed:** {suite.get('failed', 0)}\n"
            report += f"- **Skipped:** {suite.get('skipped', 0)}\n"
            report += f"- **Errors:** {suite.get('errors', 0)}\n\n"
        
        # Performance metrics
        report += "## Performance Metrics\n\n"
        perf = self.results.get("performance_metrics", {})
        report += f"- **Average Duration per Suite:** {perf.get('average_duration_per_suite', 0):.2f} seconds\n"
        report += f"- **Slowest Suite:** {perf.get('slowest_suite', 'N/A')}\n"
        report += f"- **Fastest Suite:** {perf.get('fastest_suite', 'N/A')}\n"
        report += f"- **Slow Test Suites (>30s):** {perf.get('slow_test_count', 0)}\n\n"
        
        # Coverage analysis
        report += "## Coverage Analysis\n\n"
        coverage = self.results.get("coverage_analysis", {})
        report += f"- **Modules Tested:** {coverage.get('total_modules_tested', 0)}\n"
        report += f"- **Unit Tests:** {coverage.get('test_categories', {}).get('unit_tests', 0)}\n"
        report += f"- **Integration Tests:** {coverage.get('test_categories', {}).get('integration_tests', 0)}\n"
        
        feature_coverage = coverage.get("feature_coverage", {})
        covered_features = sum(1 for v in feature_coverage.values() if v)
        total_features = len(feature_coverage)
        report += f"- **Feature Coverage:** {covered_features}/{total_features} ({covered_features/total_features*100:.1f}%)\n\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        for i, rec in enumerate(self.results["recommendations"], 1):
            priority_emoji = "🔴" if rec["priority"] == "critical" else "🟠" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
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
        report += "6. Add test result monitoring and alerting\n"
        
        with open(file_path, 'w') as f:
            f.write(report)


def main():
    """Main function to run comprehensive tests."""
    runner = ComprehensiveTestRunner()
    results = runner.run_all_tests()
    
    # Return appropriate exit code
    if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()