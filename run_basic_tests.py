#!/usr/bin/env python3
"""
Basic test runner for the book-writing system.
"""
import subprocess
import sys
from pathlib import Path


def run_basic_tests():
    """Run basic tests to verify system functionality."""
    print("🧪 Running Basic Tests for Book Writing System")
    print("=" * 50)
    
    # Test categories to run
    test_categories = [
        {
            "name": "Basic Functionality",
            "file": "tests/test_simple.py",
            "description": "Core module imports and basic functionality"
        }
    ]
    
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "skipped_tests": 0,
        "categories": []
    }
    
    for category in test_categories:
        print(f"\n📋 Running {category['name']}...")
        print(f"   {category['description']}")
        
        try:
            # Run pytest for the category
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                category["file"],
                "-v",
                "--tb=short"
            ], capture_output=True, text=True, timeout=60)
            
            # Parse results
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "PASSED" in line:
                    results["passed_tests"] += 1
                    results["total_tests"] += 1
                elif "FAILED" in line:
                    results["failed_tests"] += 1
                    results["total_tests"] += 1
                elif "SKIPPED" in line:
                    results["skipped_tests"] += 1
                    results["total_tests"] += 1
            
            category_result = {
                "name": category["name"],
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "returncode": result.returncode,
                "output": result.stdout,
                "errors": result.stderr
            }
            
            results["categories"].append(category_result)
            
            if result.returncode == 0:
                print(f"   ✅ {category['name']} - PASSED")
            else:
                print(f"   ❌ {category['name']} - FAILED")
                if result.stderr:
                    print(f"   Error: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {category['name']} - TIMEOUT")
            results["failed_tests"] += 1
            results["total_tests"] += 1
        except Exception as e:
            print(f"   ❌ {category['name']} - ERROR: {e}")
            results["failed_tests"] += 1
            results["total_tests"] += 1
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Skipped: {results['skipped_tests']}")
    
    if results['total_tests'] > 0:
        success_rate = (results['passed_tests'] / results['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    # Display recommendations
    print("\n🎯 RECOMMENDATIONS")
    print("=" * 50)
    
    if results['failed_tests'] == 0:
        print("✅ All tests passed! System is functioning correctly.")
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
    
    if results['skipped_tests'] > 0:
        print("ℹ️  Some tests were skipped (likely due to missing dependencies).")
    
    print("\n📈 NEXT STEPS")
    print("=" * 50)
    print("1. Review the test analysis report: test_analysis_report.md")
    print("2. Implement recommended optimizations")
    print("3. Add more comprehensive tests as needed")
    print("4. Set up continuous integration")
    
    return results


if __name__ == "__main__":
    results = run_basic_tests()
    sys.exit(0 if results['failed_tests'] == 0 else 1)