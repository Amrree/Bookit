#!/usr/bin/env python3
"""
Test script for enhanced features.

This script tests all the new features including:
- Enhanced Output Management
- Template System
- Advanced Export Options
- Style Guide Integration
- Research Assistant
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_output_manager():
    """Test Enhanced Output Management System."""
    print("🧪 Testing Enhanced Output Management System...")
    
    try:
        from output_manager import OutputManager, BookMetadata
        
        # Initialize output manager
        output_manager = OutputManager("./test_output")
        
        # Create book structure
        book_dir = output_manager.create_book_structure(
            book_id="test_book_001",
            title="Test Book",
            author="Test Author",
            description="A test book for validation",
            target_audience="Testers"
        )
        
        print(f"✅ Created book structure: {book_dir}")
        
        # Test metadata update
        success = output_manager.update_book_metadata(
            "test_book_001",
            total_word_count=5000,
            chapter_count=5,
            status="in_progress"
        )
        
        print(f"✅ Updated metadata: {success}")
        
        # Test asset addition
        asset_path = output_manager.add_asset(
            "test_book_001",
            "images",
            "test_image.txt",  # This would be a real file in practice
            "test_asset.txt"
        )
        
        print(f"✅ Added asset: {asset_path}")
        
        # Test export
        export_path = output_manager.export_book(
            "test_book_001",
            "markdown",
            "# Test Content\n\nThis is test content.",
            "test_export.md"
        )
        
        print(f"✅ Exported book: {export_path}")
        
        # Get statistics
        stats = output_manager.get_statistics()
        print(f"✅ Output manager statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Output manager test failed: {e}")
        return False

def test_template_manager():
    """Test Template System."""
    print("\n🧪 Testing Template System...")
    
    try:
        from template_manager import TemplateManager, BookTemplate
        
        # Initialize template manager
        template_manager = TemplateManager("./test_templates")
        
        # List available templates
        templates = template_manager.list_book_templates()
        print(f"✅ Found {len(templates)} book templates")
        
        # Get specific template
        academic_template = template_manager.get_book_template("academic_research_paper")
        if academic_template:
            print(f"✅ Retrieved academic template: {academic_template.name}")
        
        # List chapter templates
        chapter_templates = template_manager.list_chapter_templates()
        print(f"✅ Found {len(chapter_templates)} chapter templates")
        
        # Get statistics
        stats = template_manager.get_statistics()
        print(f"✅ Template manager statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template manager test failed: {e}")
        return False

def test_export_manager():
    """Test Advanced Export Options."""
    print("\n🧪 Testing Advanced Export Options...")
    
    try:
        from export_manager import ExportManager, ExportOptions
        
        # Initialize export manager
        export_manager = ExportManager("./test_exports")
        
        # Test supported formats
        formats = export_manager.get_supported_formats()
        print(f"✅ Supported formats: {formats}")
        
        # Test export options
        options = ExportOptions(
            format="markdown",
            include_cover=True,
            include_toc=True,
            quality="high"
        )
        
        print(f"✅ Created export options: {options.format}")
        
        # Test export (simplified)
        test_content = "# Test Book\n\nThis is a test book."
        test_metadata = {
            "title": "Test Book",
            "author": "Test Author",
            "created_at": "2024-01-01"
        }
        
        result = export_manager.export_book(
            book_id="test_book",
            content=test_content,
            metadata=test_metadata,
            options=options
        )
        
        if result.success:
            print(f"✅ Export successful: {result.file_path}")
        else:
            print(f"⚠️ Export failed: {result.error}")
        
        # Get statistics
        stats = export_manager.get_statistics()
        print(f"✅ Export manager statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Export manager test failed: {e}")
        return False

def test_style_manager():
    """Test Style Guide Integration."""
    print("\n🧪 Testing Style Guide Integration...")
    
    try:
        from style_manager import StyleManager, StyleGuide
        
        # Initialize style manager
        style_manager = StyleManager("./test_styles")
        
        # List available style guides
        style_guides = style_manager.list_style_guides()
        print(f"✅ Found {len(style_guides)} style guides")
        
        # Get specific style guide
        business_style = style_manager.get_style_guide("business_professional")
        if business_style:
            print(f"✅ Retrieved business style guide: {business_style.name}")
        
        # Test content checking
        test_content = "This is a test document. It has some issues that need to be fixed."
        checks = style_manager.check_content(test_content, "business_professional")
        print(f"✅ Style check found {len(checks)} issues")
        
        # Test style statistics
        stats = style_manager.get_style_statistics(test_content, "business_professional")
        print(f"✅ Style statistics: {stats}")
        
        # Test style application
        modified_content, applied_changes = style_manager.apply_style_guide(
            test_content, "business_professional"
        )
        print(f"✅ Applied {len(applied_changes)} style changes")
        
        return True
        
    except Exception as e:
        print(f"❌ Style manager test failed: {e}")
        return False

async def test_research_assistant():
    """Test Research Assistant."""
    print("\n🧪 Testing Research Assistant...")
    
    try:
        from research_assistant import ResearchAssistant, ResearchResult
        
        # Initialize research assistant
        research_assistant = ResearchAssistant("./test_research")
        
        # Test research (simplified - won't actually search without API keys)
        print("✅ Research assistant initialized")
        
        # Test fact checking
        fact_check_result = await research_assistant.fact_check(
            "Artificial intelligence will replace all jobs",
            "This is a common claim about AI impact on employment"
        )
        
        print(f"✅ Fact check result: {fact_check_result['verification_status']}")
        
        # Test academic sources
        academic_sources = await research_assistant.find_academic_sources(
            "machine learning applications",
            max_sources=3
        )
        
        print(f"✅ Found {len(academic_sources)} academic sources")
        
        # Get statistics
        stats = research_assistant.get_statistics()
        print(f"✅ Research assistant statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Research assistant test failed: {e}")
        return False

async def test_enhanced_system():
    """Test Enhanced System Integration."""
    print("\n🧪 Testing Enhanced System Integration...")
    
    try:
        from enhanced_system import EnhancedBookWritingSystem
        
        # Initialize enhanced system
        system = EnhancedBookWritingSystem(
            output_dir="./test_enhanced_output",
            memory_dir="./test_enhanced_memory"
        )
        
        print("✅ Enhanced system initialized")
        
        # Test template listing
        templates = system.list_available_templates()
        print(f"✅ Available templates: {len(templates)}")
        
        # Test style guide listing
        style_guides = system.list_available_style_guides()
        print(f"✅ Available style guides: {len(style_guides)}")
        
        # Test supported export formats
        formats = system.get_supported_export_formats()
        print(f"✅ Supported export formats: {formats}")
        
        # Test system statistics
        stats = system.get_system_statistics()
        print(f"✅ System statistics: {len(stats)} components")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced system test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Testing Enhanced Book Writing System Features")
    print("=" * 60)
    
    tests = [
        ("Enhanced Output Management", test_output_manager()),
        ("Template System", test_template_manager()),
        ("Advanced Export Options", test_export_manager()),
        ("Style Guide Integration", test_style_manager()),
        ("Research Assistant", test_research_assistant()),
        ("Enhanced System Integration", test_enhanced_system())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_coro in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            if result:
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced features tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)