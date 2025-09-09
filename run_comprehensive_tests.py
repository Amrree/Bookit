#!/usr/bin/env python3
"""
Comprehensive test runner for the book-writing system.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_runner import TestRunner, TestAnalyzer


async def main():
    """Main function to run comprehensive tests."""
    print("🚀 Starting Comprehensive Test Suite for Book Writing System")
    print("=" * 60)
    
    # Create test runner
    runner = TestRunner(Path("test_results"))
    
    try:
        # Run all tests
        print("\n📋 Running all test categories...")
        results = await runner.run_all_tests()
        
        # Display summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed_tests']}")
        print(f"Failed: {results['summary']['failed_tests']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"Total Duration: {results['summary']['total_duration']:.2f} seconds")
        
        # Analyze results
        print("\n🔍 Analyzing test results...")
        analyzer = TestAnalyzer(runner.output_dir / "test_results.json")
        optimization_report = await analyzer.generate_optimization_report()
        
        # Save optimization report
        report_file = runner.output_dir / "optimization_report.md"
        with open(report_file, 'w') as f:
            f.write(optimization_report)
        
        print(f"\n📁 Results saved to: {runner.output_dir}")
        print(f"📄 Test Report: {runner.output_dir / 'test_report.md'}")
        print(f"📈 Optimization Report: {report_file}")
        
        # Display key recommendations
        print("\n🎯 KEY RECOMMENDATIONS")
        print("=" * 60)
        
        if results['summary']['failed_tests'] > 0:
            print("❌ Some tests failed. Check the optimization report for details.")
        else:
            print("✅ All tests passed!")
        
        if results['summary']['success_rate'] < 80:
            print("⚠️  Low success rate. Review failed tests and fix issues.")
        
        if results['summary']['total_duration'] > 300:
            print("⏱️  Test suite is slow. Consider performance optimizations.")
        
        print("\n🎉 Test suite completed successfully!")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error running test suite: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(main())