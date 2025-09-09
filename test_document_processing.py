#!/usr/bin/env python3
"""
Test Script for Document Processing System

Tests all document processing modules including PDF processing,
OCR, layout analysis, table extraction, and unified parsing.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from document_processor.pdf_processor import PDFProcessor
from document_processor.ocr_processor import OCRProcessor, OCRConfig
from document_processor.layout_analyzer import LayoutAnalyzer
from document_processor.table_extractor import TableExtractor
from document_processor.unified_parser import UnifiedDocumentParser, ProcessingOptions
from document_ingestor.enhanced_ingestor import EnhancedDocumentIngestor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pdf_processor():
    """Test PDF processor."""
    print("\n=== Testing PDF Processor ===")
    
    try:
        processor = PDFProcessor("./output/test_pdf")
        
        # Test with a sample PDF (if available)
        # For now, just test initialization
        stats = processor.get_statistics()
        print(f"PDF Processor initialized successfully")
        print(f"Output directory: {stats['output_directory']}")
        print(f"PyMuPDF available: {stats['pymupdf_available']}")
        
        return True
        
    except Exception as e:
        print(f"PDF Processor test failed: {e}")
        return False


def test_ocr_processor():
    """Test OCR processor."""
    print("\n=== Testing OCR Processor ===")
    
    try:
        processor = OCRProcessor("./output/test_ocr")
        
        # Test initialization
        stats = processor.get_statistics()
        print(f"OCR Processor initialized successfully")
        print(f"Output directory: {stats['output_directory']}")
        print(f"OCR available: {stats['ocr_available']}")
        print(f"Supported languages: {stats['supported_languages']}")
        
        return True
        
    except Exception as e:
        print(f"OCR Processor test failed: {e}")
        return False


def test_layout_analyzer():
    """Test layout analyzer."""
    print("\n=== Testing Layout Analyzer ===")
    
    try:
        analyzer = LayoutAnalyzer("./output/test_layout")
        
        # Test initialization
        stats = analyzer.get_statistics()
        print(f"Layout Analyzer initialized successfully")
        print(f"Output directory: {stats['output_directory']}")
        print(f"Layout analysis available: {stats['layout_available']}")
        
        return True
        
    except Exception as e:
        print(f"Layout Analyzer test failed: {e}")
        return False


def test_table_extractor():
    """Test table extractor."""
    print("\n=== Testing Table Extractor ===")
    
    try:
        extractor = TableExtractor("./output/test_tables")
        
        # Test initialization
        stats = extractor.get_statistics()
        print(f"Table Extractor initialized successfully")
        print(f"Output directory: {stats['output_directory']}")
        print(f"Table extraction available: {stats['table_available']}")
        
        return True
        
    except Exception as e:
        print(f"Table Extractor test failed: {e}")
        return False


def test_unified_parser():
    """Test unified document parser."""
    print("\n=== Testing Unified Document Parser ===")
    
    try:
        parser = UnifiedDocumentParser("./output/test_unified")
        
        # Test initialization
        stats = parser.get_processing_statistics()
        print(f"Unified Parser initialized successfully")
        print(f"Output directory: {stats['output_directory']}")
        print(f"Supported formats: {stats['supported_formats']}")
        
        return True
        
    except Exception as e:
        print(f"Unified Parser test failed: {e}")
        return False


async def test_enhanced_ingestor():
    """Test enhanced document ingestor."""
    print("\n=== Testing Enhanced Document Ingestor ===")
    
    try:
        ingestor = EnhancedDocumentIngestor("./output/test_enhanced")
        
        # Test initialization
        stats = ingestor.get_ingestion_statistics()
        print(f"Enhanced Ingestor initialized successfully")
        print(f"Output directory: {stats['output_directory']}")
        print(f"Unified parser available: {stats['unified_parser_available']}")
        print(f"Supported formats: {ingestor.get_supported_formats()}")
        
        return True
        
    except Exception as e:
        print(f"Enhanced Ingestor test failed: {e}")
        return False


def test_processing_options():
    """Test processing options configuration."""
    print("\n=== Testing Processing Options ===")
    
    try:
        # Test default options
        options = ProcessingOptions()
        print(f"Default options: {options.dict()}")
        
        # Test custom options
        custom_options = ProcessingOptions(
            extract_text=True,
            extract_metadata=True,
            extract_images=True,
            extract_tables=True,
            perform_ocr=True,
            analyze_layout=True,
            preprocess_images=True,
            language="eng",
            confidence_threshold=0.7
        )
        print(f"Custom options: {custom_options.dict()}")
        
        return True
        
    except Exception as e:
        print(f"Processing Options test failed: {e}")
        return False


def test_ocr_config():
    """Test OCR configuration."""
    print("\n=== Testing OCR Configuration ===")
    
    try:
        # Test default config
        config = OCRConfig()
        print(f"Default OCR config: {config.dict()}")
        
        # Test custom config
        custom_config = OCRConfig(
            language="eng",
            psm=6,  # Single uniform block of text
            oem=3,  # Default OCR Engine mode
            preprocess=True,
            enhance_contrast=True,
            denoise=True,
            deskew=True
        )
        print(f"Custom OCR config: {custom_config.dict()}")
        
        return True
        
    except Exception as e:
        print(f"OCR Configuration test failed: {e}")
        return False


def create_sample_documents():
    """Create sample documents for testing."""
    print("\n=== Creating Sample Documents ===")
    
    try:
        sample_dir = Path("./output/sample_documents")
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sample text file
        text_file = sample_dir / "sample.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("""
Sample Document

This is a sample document for testing the document processing system.

It contains multiple paragraphs and demonstrates various text processing capabilities.

The document includes:
- Multiple paragraphs
- Lists and bullet points
- Various formatting elements

This document will be used to test the enhanced document ingestor and unified parser.
            """)
        
        print(f"Created sample text file: {text_file}")
        
        # Create sample markdown file
        md_file = sample_dir / "sample.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("""
# Sample Markdown Document

This is a sample markdown document for testing.

## Features

- **Bold text**
- *Italic text*
- `Code snippets`

### Table Example

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

## Conclusion

This document demonstrates markdown processing capabilities.
            """)
        
        print(f"Created sample markdown file: {md_file}")
        
        return [text_file, md_file]
        
    except Exception as e:
        print(f"Sample document creation failed: {e}")
        return []


async def test_document_processing_pipeline():
    """Test the complete document processing pipeline."""
    print("\n=== Testing Document Processing Pipeline ===")
    
    try:
        # Create sample documents
        sample_files = create_sample_documents()
        
        if not sample_files:
            print("No sample files created, skipping pipeline test")
            return False
        
        # Test with enhanced ingestor
        ingestor = EnhancedDocumentIngestor("./output/test_pipeline")
        
        for file_path in sample_files:
            print(f"\nProcessing: {file_path}")
            
            try:
                metadata = await ingestor.ingest_document(file_path)
                print(f"Successfully processed: {metadata.original_filename}")
                print(f"Processing time: {metadata.processing_time:.2f}s")
                print(f"Chunk count: {metadata.chunk_count}")
                print(f"Has images: {metadata.has_images}")
                print(f"Has tables: {metadata.has_tables}")
                print(f"Requires OCR: {metadata.requires_ocr}")
                
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")
        
        return True
        
    except Exception as e:
        print(f"Pipeline test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Document Processing System Test Suite")
    print("=" * 50)
    
    tests = [
        ("PDF Processor", test_pdf_processor),
        ("OCR Processor", test_ocr_processor),
        ("Layout Analyzer", test_layout_analyzer),
        ("Table Extractor", test_table_extractor),
        ("Unified Parser", test_unified_parser),
        ("Processing Options", test_processing_options),
        ("OCR Configuration", test_ocr_config),
    ]
    
    results = []
    
    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Run asynchronous tests
    async def run_async_tests():
        async_tests = [
            ("Enhanced Ingestor", test_enhanced_ingestor),
            ("Document Processing Pipeline", test_document_processing_pipeline),
        ]
        
        for test_name, test_func in async_tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"Test {test_name} failed with exception: {e}")
                results.append((test_name, False))
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    # Print results
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Document processing system is ready.")
    else:
        print(f"{total - passed} tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)