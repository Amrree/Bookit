#!/usr/bin/env python3
"""
Test script to validate the repository reorganization.

This script tests that all modules can be imported correctly
and that the basic functionality works after reorganization.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    
    try:
        # Test core modules
        from memory_manager import MemoryManager
        print("✅ MemoryManager imported successfully")
        
        from llm_client import LLMClient
        print("✅ LLMClient imported successfully")
        
        from tool_manager import ToolManager
        print("✅ ToolManager imported successfully")
        
        from document_ingestor import DocumentIngestor
        print("✅ DocumentIngestor imported successfully")
        
        from book_builder import BookBuilder
        print("✅ BookBuilder imported successfully")
        
        # Test agent modules
        from agents import AgentManager, ResearchAgent, WriterAgent, EditorAgent, ToolAgent
        print("✅ Agent modules imported successfully")
        
        # Test CLI module
        from cli import main as cli_main
        print("✅ CLI module imported successfully")
        
        # Test GUI module (optional)
        try:
            from gui import main as gui_main
            print("✅ GUI module imported successfully")
        except ImportError as e:
            print(f"⚠️  GUI module not available: {e}")
        
        # Test full book generator
        from full_book_generator import FullBookWorkflow
        print("✅ FullBookWorkflow imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_directory_structure():
    """Test that the directory structure is correct."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "agents",
        "memory_manager",
        "llm_client",
        "tool_manager",
        "document_ingestor",
        "book_builder",
        "full_book_generator",
        "cli",
        "gui",
        "tests",
        "tests/fixtures",
        "docs",
        "research"
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
            return False
    
    return True

def test_init_files():
    """Test that __init__.py files exist where needed."""
    print("\nTesting __init__.py files...")
    
    required_init_files = [
        "agents/__init__.py",
        "memory_manager/__init__.py",
        "llm_client/__init__.py",
        "tool_manager/__init__.py",
        "document_ingestor/__init__.py",
        "book_builder/__init__.py",
        "full_book_generator/__init__.py",
        "cli/__init__.py",
        "gui/__init__.py",
        "tests/__init__.py",
        "tests/fixtures/__init__.py",
        "research/__init__.py"
    ]
    
    for init_file in required_init_files:
        if os.path.exists(init_file):
            print(f"✅ __init__.py exists: {init_file}")
        else:
            print(f"❌ __init__.py missing: {init_file}")
            return False
    
    return True

def test_documentation():
    """Test that documentation files exist."""
    print("\nTesting documentation files...")
    
    required_docs = [
        "docs/README.md",
        "docs/INSTALL.md",
        "docs/INTEGRATIONS.md",
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "requirements.txt"
    ]
    
    for doc_file in required_docs:
        if os.path.exists(doc_file):
            print(f"✅ Documentation exists: {doc_file}")
        else:
            print(f"❌ Documentation missing: {doc_file}")
            return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of key components."""
    print("\nTesting basic functionality...")
    
    try:
        # Test MemoryManager initialization
        from memory_manager import MemoryManager
        memory_manager = MemoryManager(persist_directory="./test_memory")
        print("✅ MemoryManager initialized successfully")
        
        # Test LLMClient initialization
        from llm_client import LLMClient
        llm_client = LLMClient(provider="ollama")
        print("✅ LLMClient initialized successfully")
        
        # Test ToolManager initialization
        from tool_manager import ToolManager
        tool_manager = ToolManager()
        print("✅ ToolManager initialized successfully")
        
        # Test BookBuilder initialization
        from book_builder import BookBuilder
        book_builder = BookBuilder(output_directory="./test_books")
        print("✅ BookBuilder initialized successfully")
        
        # Test DocumentIngestor initialization
        from document_ingestor import DocumentIngestor
        document_ingestor = DocumentIngestor()
        print("✅ DocumentIngestor initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_cli_functionality():
    """Test CLI functionality."""
    print("\nTesting CLI functionality...")
    
    try:
        from cli import cli
        print("✅ CLI module loaded successfully")
        
        # Test that CLI can be called without errors
        import click.testing
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        if result.exit_code == 0:
            print("✅ CLI help command works")
        else:
            print(f"⚠️  CLI help command failed: {result.output}")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI functionality test failed: {e}")
        return False

def test_gui_functionality():
    """Test GUI functionality."""
    print("\nTesting GUI functionality...")
    
    try:
        from gui import main as gui_main
        print("✅ GUI module loaded successfully")
        return True
        
    except ImportError as e:
        print(f"⚠️  GUI module not available: {e}")
        return True  # GUI is optional
    except Exception as e:
        print(f"❌ GUI functionality test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files."""
    print("\nCleaning up test files...")
    
    test_dirs = ["./test_memory", "./test_books"]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
            print(f"✅ Cleaned up: {test_dir}")

def main():
    """Main test function."""
    print("🧪 Testing Repository Reorganization")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Directory Structure", test_directory_structure),
        ("__init__.py Files", test_init_files),
        ("Documentation", test_documentation),
        ("Basic Functionality", test_basic_functionality),
        ("CLI Functionality", test_cli_functionality),
        ("GUI Functionality", test_gui_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Repository reorganization successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
    finally:
        cleanup_test_files()
    
    sys.exit(exit_code)