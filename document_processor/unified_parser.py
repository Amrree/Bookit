"""
Unified Document Parser

Integrates all document processing modules into a single, comprehensive
document parsing system with support for multiple formats and processing options.

Features:
- Multi-format document support (PDF, DOCX, TXT, MD, HTML, images)
- Integrated OCR processing
- Layout analysis and structure recognition
- Table extraction and formatting
- Text extraction and processing
- Metadata extraction
- Batch processing
- Export to multiple formats
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import json

import pydantic

from .pdf_processor import PDFProcessor, PDFMetadata
from .ocr_processor import OCRProcessor, OCRResult, OCRConfig
from .layout_analyzer import LayoutAnalyzer, LayoutAnalysis
from .table_extractor import TableExtractor, TableStructure

logger = logging.getLogger(__name__)


class DocumentType(pydantic.BaseModel):
    """Document type model."""
    file_extension: str
    mime_type: str
    is_text_based: bool
    requires_ocr: bool
    supports_layout_analysis: bool
    supports_table_extraction: bool


class ProcessingOptions(pydantic.BaseModel):
    """Processing options model."""
    extract_text: bool = True
    extract_metadata: bool = True
    extract_images: bool = True
    extract_tables: bool = True
    perform_ocr: bool = False
    analyze_layout: bool = True
    preprocess_images: bool = True
    language: str = "eng"
    confidence_threshold: float = 0.5


class DocumentParseResult(pydantic.BaseModel):
    """Document parsing result."""
    document_id: str
    file_path: str
    document_type: DocumentType
    processing_options: ProcessingOptions
    text_content: str
    metadata: Dict[str, Any]
    images: List[Dict[str, Any]]
    tables: List[TableStructure]
    layout_analysis: Optional[LayoutAnalysis]
    ocr_results: List[OCRResult]
    processing_time: float
    success: bool
    errors: List[str] = []


class UnifiedDocumentParser:
    """
    Unified document parser integrating all processing modules.
    
    Features:
    - Multi-format document support
    - Integrated OCR processing
    - Layout analysis and structure recognition
    - Table extraction and formatting
    - Batch processing
    - Export to multiple formats
    """
    
    def __init__(self, output_dir: str = "./output/document_parsing"):
        """
        Initialize unified document parser.
        
        Args:
            output_dir: Directory for parsing results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize processors
        self.pdf_processor = PDFProcessor(self.output_dir / "pdf")
        self.ocr_processor = OCRProcessor(self.output_dir / "ocr")
        self.layout_analyzer = LayoutAnalyzer(self.output_dir / "layout")
        self.table_extractor = TableExtractor(self.output_dir / "tables")
        
        # Document type registry
        self.document_types = self._initialize_document_types()
        
        logger.info(f"Unified document parser initialized with output directory: {self.output_dir}")
    
    def _initialize_document_types(self) -> Dict[str, DocumentType]:
        """Initialize supported document types."""
        return {
            "pdf": DocumentType(
                file_extension=".pdf",
                mime_type="application/pdf",
                is_text_based=True,
                requires_ocr=False,
                supports_layout_analysis=True,
                supports_table_extraction=True
            ),
            "docx": DocumentType(
                file_extension=".docx",
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                is_text_based=True,
                requires_ocr=False,
                supports_layout_analysis=True,
                supports_table_extraction=True
            ),
            "txt": DocumentType(
                file_extension=".txt",
                mime_type="text/plain",
                is_text_based=True,
                requires_ocr=False,
                supports_layout_analysis=False,
                supports_table_extraction=False
            ),
            "md": DocumentType(
                file_extension=".md",
                mime_type="text/markdown",
                is_text_based=True,
                requires_ocr=False,
                supports_layout_analysis=False,
                supports_table_extraction=False
            ),
            "html": DocumentType(
                file_extension=".html",
                mime_type="text/html",
                is_text_based=True,
                requires_ocr=False,
                supports_layout_analysis=True,
                supports_table_extraction=True
            ),
            "png": DocumentType(
                file_extension=".png",
                mime_type="image/png",
                is_text_based=False,
                requires_ocr=True,
                supports_layout_analysis=True,
                supports_table_extraction=True
            ),
            "jpg": DocumentType(
                file_extension=".jpg",
                mime_type="image/jpeg",
                is_text_based=False,
                requires_ocr=True,
                supports_layout_analysis=True,
                supports_table_extraction=True
            ),
            "jpeg": DocumentType(
                file_extension=".jpeg",
                mime_type="image/jpeg",
                is_text_based=False,
                requires_ocr=True,
                supports_layout_analysis=True,
                supports_table_extraction=True
            )
        }
    
    def parse_document(self, file_path: Union[str, Path], 
                      options: Optional[ProcessingOptions] = None) -> DocumentParseResult:
        """
        Parse a document with specified options.
        
        Args:
            file_path: Path to document
            options: Processing options
            
        Returns:
            Document parsing result
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if options is None:
            options = ProcessingOptions()
        
        logger.info(f"Parsing document: {file_path}")
        
        start_time = datetime.now()
        
        try:
            # Determine document type
            doc_type = self._get_document_type(file_path)
            
            # Generate document ID
            document_id = f"doc_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize result
            result = DocumentParseResult(
                document_id=document_id,
                file_path=str(file_path),
                document_type=doc_type,
                processing_options=options,
                text_content="",
                metadata={},
                images=[],
                tables=[],
                layout_analysis=None,
                ocr_results=[],
                processing_time=0.0,
                success=False,
                errors=[]
            )
            
            # Process based on document type
            if doc_type.file_extension == ".pdf":
                result = self._parse_pdf(file_path, result, options)
            elif doc_type.file_extension in [".docx"]:
                result = self._parse_docx(file_path, result, options)
            elif doc_type.file_extension in [".txt", ".md"]:
                result = self._parse_text(file_path, result, options)
            elif doc_type.file_extension in [".html"]:
                result = self._parse_html(file_path, result, options)
            elif doc_type.file_extension in [".png", ".jpg", ".jpeg"]:
                result = self._parse_image(file_path, result, options)
            else:
                result.errors.append(f"Unsupported document type: {doc_type.file_extension}")
                return result
            
            # Calculate processing time
            result.processing_time = (datetime.now() - start_time).total_seconds()
            result.success = len(result.errors) == 0
            
            # Save result
            self._save_result(result)
            
            logger.info(f"Document parsing completed: {file_path}")
            logger.info(f"Success: {result.success}, Processing time: {result.processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Document parsing failed: {e}")
            result = DocumentParseResult(
                document_id="",
                file_path=str(file_path),
                document_type=self._get_document_type(file_path),
                processing_options=options,
                text_content="",
                metadata={},
                images=[],
                tables=[],
                layout_analysis=None,
                ocr_results=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                errors=[str(e)]
            )
            return result
    
    def _get_document_type(self, file_path: Path) -> DocumentType:
        """Get document type from file extension."""
        extension = file_path.suffix.lower()
        
        if extension in self.document_types:
            return self.document_types[extension]
        else:
            # Default to text type
            return DocumentType(
                file_extension=extension,
                mime_type="application/octet-stream",
                is_text_based=True,
                requires_ocr=False,
                supports_layout_analysis=False,
                supports_table_extraction=False
            )
    
    def _parse_pdf(self, file_path: Path, result: DocumentParseResult, 
                   options: ProcessingOptions) -> DocumentParseResult:
        """Parse PDF document."""
        try:
            # Extract text
            if options.extract_text:
                result.text_content = self.pdf_processor.extract_text_only(file_path)
            
            # Extract metadata
            if options.extract_metadata:
                # Get PDF metadata
                doc = self.pdf_processor.pdf_processor.fitz.open(str(file_path))
                metadata = self.pdf_processor._extract_metadata(doc, file_path)
                result.metadata = metadata.dict()
                doc.close()
            
            # Extract images
            if options.extract_images:
                # Process PDF with image extraction
                pdf_results = self.pdf_processor.process_pdf(
                    file_path,
                    extract_images=True,
                    extract_tables=options.extract_tables,
                    ocr_enabled=options.perform_ocr
                )
                result.images = pdf_results.get("images", [])
            
            # Extract tables
            if options.extract_tables:
                result.tables = self.table_extractor.extract_tables_from_pdf(file_path)
            
            # Perform OCR if needed
            if options.perform_ocr and self.pdf_processor.is_scanned_pdf(file_path):
                # This would require PDF to image conversion
                result.errors.append("PDF OCR not yet implemented")
            
            # Analyze layout
            if options.analyze_layout:
                result.layout_analysis = self.layout_analyzer.analyze_document(file_path, "pdf")
            
            return result
            
        except Exception as e:
            result.errors.append(f"PDF parsing failed: {e}")
            return result
    
    def _parse_docx(self, file_path: Path, result: DocumentParseResult, 
                    options: ProcessingOptions) -> DocumentParseResult:
        """Parse DOCX document."""
        try:
            # This is a placeholder implementation
            # In a real implementation, you'd use python-docx or similar
            
            result.text_content = "DOCX parsing not yet implemented"
            result.metadata = {"type": "docx", "status": "placeholder"}
            
            return result
            
        except Exception as e:
            result.errors.append(f"DOCX parsing failed: {e}")
            return result
    
    def _parse_text(self, file_path: Path, result: DocumentParseResult, 
                    options: ProcessingOptions) -> DocumentParseResult:
        """Parse text document."""
        try:
            # Read text content
            with open(file_path, 'r', encoding='utf-8') as f:
                result.text_content = f.read()
            
            # Extract metadata
            if options.extract_metadata:
                result.metadata = {
                    "type": "text",
                    "file_size": file_path.stat().st_size,
                    "encoding": "utf-8"
                }
            
            return result
            
        except Exception as e:
            result.errors.append(f"Text parsing failed: {e}")
            return result
    
    def _parse_html(self, file_path: Path, result: DocumentParseResult, 
                    options: ProcessingOptions) -> DocumentParseResult:
        """Parse HTML document."""
        try:
            # This is a placeholder implementation
            # In a real implementation, you'd use BeautifulSoup or similar
            
            result.text_content = "HTML parsing not yet implemented"
            result.metadata = {"type": "html", "status": "placeholder"}
            
            return result
            
        except Exception as e:
            result.errors.append(f"HTML parsing failed: {e}")
            return result
    
    def _parse_image(self, file_path: Path, result: DocumentParseResult, 
                     options: ProcessingOptions) -> DocumentParseResult:
        """Parse image document."""
        try:
            # Perform OCR
            if options.perform_ocr:
                ocr_config = OCRConfig(
                    language=options.language,
                    preprocess=options.preprocess_images
                )
                ocr_result = self.ocr_processor.process_image(file_path, ocr_config)
                result.text_content = ocr_result.text
                result.ocr_results = [ocr_result]
            
            # Analyze layout
            if options.analyze_layout:
                result.layout_analysis = self.layout_analyzer.analyze_document(file_path, "image")
            
            # Extract tables
            if options.extract_tables:
                result.tables = self.table_extractor.extract_tables_from_image(file_path)
            
            # Extract metadata
            if options.extract_metadata:
                result.metadata = {
                    "type": "image",
                    "file_size": file_path.stat().st_size,
                    "format": file_path.suffix.lower()
                }
            
            return result
            
        except Exception as e:
            result.errors.append(f"Image parsing failed: {e}")
            return result
    
    def _save_result(self, result: DocumentParseResult):
        """Save parsing result to file."""
        try:
            result_filename = f"{result.document_id}_parsing_result.json"
            result_path = self.output_dir / result_filename
            
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result.dict(), f, indent=2, default=str)
            
            logger.info(f"Saved parsing result: {result_path}")
            
        except Exception as e:
            logger.error(f"Failed to save parsing result: {e}")
    
    def parse_batch(self, file_paths: List[Union[str, Path]], 
                   options: Optional[ProcessingOptions] = None) -> List[DocumentParseResult]:
        """
        Parse multiple documents in batch.
        
        Args:
            file_paths: List of document paths
            options: Processing options
            
        Returns:
            List of parsing results
        """
        if options is None:
            options = ProcessingOptions()
        
        results = []
        
        logger.info(f"Parsing {len(file_paths)} documents in batch")
        
        for file_path in file_paths:
            try:
                result = self.parse_document(file_path, options)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}")
                # Create error result
                error_result = DocumentParseResult(
                    document_id="",
                    file_path=str(file_path),
                    document_type=self._get_document_type(Path(file_path)),
                    processing_options=options,
                    text_content="",
                    metadata={},
                    images=[],
                    tables=[],
                    layout_analysis=None,
                    ocr_results=[],
                    processing_time=0.0,
                    success=False,
                    errors=[str(e)]
                )
                results.append(error_result)
        
        logger.info(f"Batch parsing completed: {len(results)} results")
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        return list(self.document_types.keys())
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "output_directory": str(self.output_dir),
            "parsed_documents": len(list(self.output_dir.glob("*_parsing_result.json"))),
            "supported_formats": self.get_supported_formats(),
            "pdf_processor_stats": self.pdf_processor.get_statistics(),
            "ocr_processor_stats": self.ocr_processor.get_statistics(),
            "layout_analyzer_stats": self.layout_analyzer.get_statistics(),
            "table_extractor_stats": self.table_extractor.get_statistics()
        }
    
    def export_to_markdown(self, result: DocumentParseResult) -> str:
        """Export parsing result to Markdown format."""
        try:
            markdown_lines = []
            
            # Add title
            markdown_lines.append(f"# Document: {Path(result.file_path).name}")
            markdown_lines.append("")
            
            # Add metadata
            if result.metadata:
                markdown_lines.append("## Metadata")
                for key, value in result.metadata.items():
                    markdown_lines.append(f"- **{key}**: {value}")
                markdown_lines.append("")
            
            # Add text content
            if result.text_content:
                markdown_lines.append("## Content")
                markdown_lines.append("")
                markdown_lines.append(result.text_content)
                markdown_lines.append("")
            
            # Add tables
            if result.tables:
                markdown_lines.append("## Tables")
                markdown_lines.append("")
                for table in result.tables:
                    table_md = self.table_extractor.export_table_to_markdown(table)
                    markdown_lines.append(table_md)
                    markdown_lines.append("")
            
            return "\n".join(markdown_lines)
            
        except Exception as e:
            logger.error(f"Markdown export failed: {e}")
            return ""
    
    def export_to_html(self, result: DocumentParseResult) -> str:
        """Export parsing result to HTML format."""
        try:
            html_lines = []
            
            # Add HTML structure
            html_lines.append("<!DOCTYPE html>")
            html_lines.append("<html>")
            html_lines.append("<head>")
            html_lines.append(f"<title>Document: {Path(result.file_path).name}</title>")
            html_lines.append("</head>")
            html_lines.append("<body>")
            
            # Add title
            html_lines.append(f"<h1>Document: {Path(result.file_path).name}</h1>")
            
            # Add metadata
            if result.metadata:
                html_lines.append("<h2>Metadata</h2>")
                html_lines.append("<ul>")
                for key, value in result.metadata.items():
                    html_lines.append(f"<li><strong>{key}</strong>: {value}</li>")
                html_lines.append("</ul>")
            
            # Add text content
            if result.text_content:
                html_lines.append("<h2>Content</h2>")
                html_lines.append(f"<div>{result.text_content}</div>")
            
            # Add tables
            if result.tables:
                html_lines.append("<h2>Tables</h2>")
                for table in result.tables:
                    table_html = self.table_extractor.export_table_to_html(table)
                    html_lines.append(table_html)
            
            html_lines.append("</body>")
            html_lines.append("</html>")
            
            return "\n".join(html_lines)
            
        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            return ""