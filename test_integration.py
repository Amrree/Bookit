#!/usr/bin/env python3
"""
Integration Test

Tests the integrated system to ensure all components work together.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """Test basic imports."""
    print("Testing basic imports...")
    
    try:
        import json
        import datetime
        import pathlib
        print("✓ Basic Python modules imported")
        
        import tkinter as tk
        print("✓ Tkinter imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_integrated_system():
    """Test integrated system."""
    print("\nTesting integrated system...")
    
    try:
        from integrated_system import IntegratedSystem
        
        # Initialize system
        system = IntegratedSystem("./test_data")
        print("✓ Integrated system initialized")
        
        # Test template manager
        template = system.get_template("business_report")
        if template:
            print("✓ Template manager working")
        else:
            print("✗ Template manager failed")
            return False
        
        # Test research assistant
        results = system.search_research("test query")
        if results:
            print("✓ Research assistant working")
        else:
            print("✗ Research assistant failed")
            return False
        
        # Test export manager
        file_path = system.export_content("Test content", "test_file", "text")
        if file_path and Path(file_path).exists():
            print("✓ Export manager working")
            # Clean up
            Path(file_path).unlink()
        else:
            print("✗ Export manager failed")
            return False
        
        # Test statistics
        stats = system.get_statistics()
        if stats:
            print("✓ Statistics working")
        else:
            print("✗ Statistics failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Integrated system test failed: {e}")
        return False

def test_stitch_like_gui():
    """Test Stitch-like GUI."""
    print("\nTesting Stitch-like GUI...")
    
    try:
        from gui.stitch_like_app import StitchLikeApp
        
        # Create app (but don't run it)
        app = StitchLikeApp()
        print("✓ Stitch-like GUI created")
        
        # Test basic functionality
        app._new_document()
        print("✓ New document functionality working")
        
        app._apply_template("business")
        print("✓ Template application working")
        
        # Clean up
        app.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Stitch-like GUI test failed: {e}")
        return False

def test_file_operations():
    """Test file operations."""
    print("\nTesting file operations...")
    
    try:
        from integrated_system import IntegratedSystem
        
        system = IntegratedSystem("./test_data")
        
        # Create a test file
        test_file = Path("./test_data/test_document.txt")
        test_file.parent.mkdir(exist_ok=True)
        
        with open(test_file, 'w') as f:
            f.write("This is a test document for processing.")
        
        # Process the document
        result = system.process_document(str(test_file))
        
        if result["success"]:
            print("✓ Document processing working")
        else:
            print("✗ Document processing failed")
            return False
        
        # Clean up
        test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("BookWriter Pro - Integration Test")
    print("=" * 40)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Integrated System", test_integrated_system),
        ("Stitch-like GUI", test_stitch_like_gui),
        ("File Operations", test_file_operations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print("Test Results Summary")
    print("=" * 40)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nTo run the system:")
        print("  python3 launcher.py")
    else:
        print(f"\n✗ {total - passed} tests failed.")
        print("Please check the errors above and try again.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)