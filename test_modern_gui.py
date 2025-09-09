#!/usr/bin/env python3
"""
Test Script for Modern GUI Application

Tests the modern Mac-style GUI application and all its components.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_gui_imports():
    """Test that all GUI modules can be imported."""
    print("Testing GUI Module Imports")
    print("=" * 30)
    
    try:
        # Test main GUI imports
        from gui.modern_main import ModernBookWriterApp
        print("✓ ModernBookWriterApp imported successfully")
        
        # Test panel imports
        from gui.panels.document_processor_panel import DocumentProcessorPanel
        print("✓ DocumentProcessorPanel imported successfully")
        
        from gui.panels.research_panel import ResearchPanel
        print("✓ ResearchPanel imported successfully")
        
        from gui.panels.collaboration_panel import CollaborationPanel
        print("✓ CollaborationPanel imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_gui_components():
    """Test GUI component creation."""
    print("\nTesting GUI Component Creation")
    print("=" * 35)
    
    try:
        import customtkinter as ctk
        
        # Test CustomTkinter availability
        print("✓ CustomTkinter available")
        
        # Test basic window creation
        root = ctk.CTk()
        root.withdraw()  # Hide window for testing
        
        # Test frame creation
        frame = ctk.CTkFrame(root)
        print("✓ CTkFrame created successfully")
        
        # Test button creation
        button = ctk.CTkButton(frame, text="Test")
        print("✓ CTkButton created successfully")
        
        # Test textbox creation
        textbox = ctk.CTkTextbox(frame)
        print("✓ CTkTextbox created successfully")
        
        # Test tabview creation
        tabview = ctk.CTkTabview(frame)
        print("✓ CTkTabview created successfully")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ Component creation error: {e}")
        return False


def test_system_integration():
    """Test integration with system modules."""
    print("\nTesting System Integration")
    print("=" * 30)
    
    try:
        # Test document processor integration
        from document_processor.unified_parser import UnifiedDocumentParser
        print("✓ UnifiedDocumentParser imported")
        
        from document_ingestor.enhanced_ingestor import EnhancedDocumentIngestor
        print("✓ EnhancedDocumentIngestor imported")
        
        from research_assistant.research_assistant import ResearchAssistant
        print("✓ ResearchAssistant imported")
        
        from collaboration.collaboration_manager import CollaborationManager
        print("✓ CollaborationManager imported")
        
        return True
        
    except ImportError as e:
        print(f"✗ System integration error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_gui_functionality():
    """Test GUI functionality without displaying windows."""
    print("\nTesting GUI Functionality")
    print("=" * 30)
    
    try:
        import customtkinter as ctk
        
        # Create a test root window (hidden)
        root = ctk.CTk()
        root.withdraw()
        
        # Test main app creation
        from gui.modern_main import ModernBookWriterApp
        app = ModernBookWriterApp()
        print("✓ ModernBookWriterApp created successfully")
        
        # Test panel creation
        from gui.panels.document_processor_panel import DocumentProcessorPanel
        doc_panel = DocumentProcessorPanel(root)
        print("✓ DocumentProcessorPanel created successfully")
        
        from gui.panels.research_panel import ResearchPanel
        research_panel = ResearchPanel(root)
        print("✓ ResearchPanel created successfully")
        
        from gui.panels.collaboration_panel import CollaborationPanel
        collab_panel = CollaborationPanel(root)
        print("✓ CollaborationPanel created successfully")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI functionality error: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are available."""
    print("\nTesting Dependencies")
    print("=" * 20)
    
    dependencies = [
        ("customtkinter", "CustomTkinter GUI framework"),
        ("tkinter", "Tkinter GUI framework"),
        ("pydantic", "Data validation"),
        ("asyncio", "Asynchronous programming"),
        ("threading", "Threading support"),
        ("pathlib", "Path handling"),
        ("logging", "Logging support")
    ]
    
    all_available = True
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {module} - {description}")
        except ImportError:
            print(f"✗ {module} - {description} (MISSING)")
            all_available = False
    
    return all_available


def test_gui_structure():
    """Test GUI file structure."""
    print("\nTesting GUI Structure")
    print("=" * 25)
    
    required_files = [
        "gui/modern_main.py",
        "gui/panels/document_processor_panel.py",
        "gui/panels/research_panel.py",
        "gui/panels/collaboration_panel.py",
        "test_modern_gui.py"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def test_gui_configuration():
    """Test GUI configuration and theming."""
    print("\nTesting GUI Configuration")
    print("=" * 30)
    
    try:
        import customtkinter as ctk
        
        # Test appearance modes
        modes = ["light", "dark"]
        for mode in modes:
            ctk.set_appearance_mode(mode)
            print(f"✓ Appearance mode '{mode}' set successfully")
        
        # Test color themes
        themes = ["blue", "green", "dark-blue"]
        for theme in themes:
            ctk.set_default_color_theme(theme)
            print(f"✓ Color theme '{theme}' set successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def main():
    """Run all GUI tests."""
    print("Modern GUI Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("GUI Imports", test_gui_imports),
        ("GUI Components", test_gui_components),
        ("System Integration", test_system_integration),
        ("GUI Functionality", test_gui_functionality),
        ("Dependencies", test_dependencies),
        ("GUI Structure", test_gui_structure),
        ("GUI Configuration", test_gui_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print results
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Modern GUI is ready to use.")
        print("\nTo run the GUI application:")
        print("  python3 gui/modern_main.py")
    else:
        print(f"\n✗ {total - passed} tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)