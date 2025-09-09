#!/usr/bin/env python3
"""
Validation Script for Document Processing System

Validates the structure and imports of the document processing modules
without requiring all dependencies to be installed.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def validate_module_structure():
    """Validate that all modules exist and have correct structure."""
    print("Validating Document Processing Module Structure")
    print("=" * 50)
    
    modules = [
        "document_processor/__init__.py",
        "document_processor/pdf_processor.py",
        "document_processor/ocr_processor.py",
        "document_processor/layout_analyzer.py",
        "document_processor/table_extractor.py",
        "document_processor/unified_parser.py",
        "document_ingestor/enhanced_ingestor.py",
        "test_document_processing.py",
        "requirements.txt",
        "DOCUMENT_PROCESSING_SUMMARY.md"
    ]
    
    all_exist = True
    
    for module in modules:
        path = Path(module)
        if path.exists():
            print(f"✓ {module}")
        else:
            print(f"✗ {module} - MISSING")
            all_exist = False
    
    return all_exist


def validate_imports():
    """Validate that modules can be imported (without dependencies)."""
    print("\nValidating Module Imports")
    print("=" * 30)
    
    # Test basic Python syntax
    modules_to_test = [
        "document_processor.pdf_processor",
        "document_processor.ocr_processor", 
        "document_processor.layout_analyzer",
        "document_processor.table_extractor",
        "document_processor.unified_parser",
        "document_ingestor.enhanced_ingestor"
    ]
    
    import_results = []
    
    for module_name in modules_to_test:
        try:
            # Try to compile the module
            module_path = module_name.replace('.', '/') + '.py'
            with open(module_path, 'r') as f:
                code = f.read()
            
            compile(code, module_path, 'exec')
            print(f"✓ {module_name} - Syntax OK")
            import_results.append(True)
            
        except SyntaxError as e:
            print(f"✗ {module_name} - Syntax Error: {e}")
            import_results.append(False)
        except Exception as e:
            print(f"✗ {module_name} - Error: {e}")
            import_results.append(False)
    
    return all(import_results)


def validate_requirements():
    """Validate requirements.txt has necessary dependencies."""
    print("\nValidating Requirements")
    print("=" * 25)
    
    try:
        with open("requirements.txt", 'r') as f:
            content = f.read()
        
        required_deps = [
            "PyMuPDF",
            "pytesseract", 
            "opencv-python",
            "Pillow",
            "pandas"
        ]
        
        all_present = True
        
        for dep in required_deps:
            if dep in content:
                print(f"✓ {dep}")
            else:
                print(f"✗ {dep} - MISSING")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False


def validate_documentation():
    """Validate documentation exists and is comprehensive."""
    print("\nValidating Documentation")
    print("=" * 25)
    
    doc_files = [
        "DOCUMENT_PROCESSING_SUMMARY.md",
        "docs/README.md",
        "docs/INSTALL.md",
        "docs/INTEGRATIONS.md"
    ]
    
    all_exist = True
    
    for doc_file in doc_files:
        path = Path(doc_file)
        if path.exists():
            size = path.stat().st_size
            print(f"✓ {doc_file} ({size} bytes)")
        else:
            print(f"✗ {doc_file} - MISSING")
            all_exist = False
    
    return all_exist


def main():
    """Run all validation checks."""
    print("Document Processing System Validation")
    print("=" * 50)
    
    checks = [
        ("Module Structure", validate_module_structure),
        ("Module Imports", validate_imports),
        ("Requirements", validate_requirements),
        ("Documentation", validate_documentation)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"Check {check_name} failed with exception: {e}")
            results.append((check_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("Validation Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{check_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All validations passed! Document processing system is properly structured.")
        print("\nTo install dependencies and run full tests:")
        print("  pip install -r requirements.txt")
        print("  python3 test_document_processing.py")
    else:
        print(f"\n✗ {total - passed} validations failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)