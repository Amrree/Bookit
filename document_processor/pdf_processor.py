"""
PDF Processor Module

Specialized PDF processing using PyMuPDF (fitz) for high-performance
PDF text extraction, metadata processing, and image extraction.

Features:
- High-performance PDF text extraction
- Metadata extraction and processing
- Image extraction and processing
- Table detection and extraction
- Page-by-page processing
- OCR integration for scanned PDFs
- Bookmark and outline extraction
- Form field extraction
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import json

import pydantic

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF not available. PDF processing will be limited.")


class PDFMetadata(pydantic.BaseModel):
    """PDF metadata model."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    keywords: Optional[str] = None
    page_count: int = 0
    file_size: int = 0
    pdf_version: Optional[str] = None
    is_encrypted: bool = False
    has_forms: bool = False
    has_bookmarks: bool = False


class PDFTextBlock(pydantic.BaseModel):
    """PDF text block model."""
    page_number: int
    block_number: int
    text: str
    bbox: List[float]  # [x0, y0, x1, y1]
    font_size: float
    font_name: str
    is_bold: bool = False
    is_italic: bool = False
    color: int = 0
    block_type: str = "text"  # text, image, table, header, footer


class PDFImage(pydantic.BaseModel):
    """PDF image model."""
    page_number: int
    image_number: int
    bbox: List[float]
    width: int
    height: int
    colorspace: str
    bits_per_component: int
    image_data: Optional[bytes] = None
    file_path: Optional[str] = None


class PDFTable(pydantic.BaseModel):
    """PDF table model."""
    page_number: int
    table_number: int
    bbox: List[float]
    rows: List[List[str]]
    headers: List[str]
    confidence: float
    cell_count: int


class PDFBookmark(pydantic.BaseModel):
    """PDF bookmark model."""
    title: str
    page: int
    level: int
    children: List['PDFBookmark'] = []


class PDFProcessor:
    """
    High-performance PDF processor using PyMuPDF.
    
    Features:
    - Text extraction with formatting preservation
    - Metadata extraction
    - Image extraction and processing
    - Table detection and extraction
    - Bookmark and outline extraction
    - OCR integration for scanned PDFs
    """
    
    def __init__(self, output_dir: str = "./output/pdf_processing"):
        """
        Initialize PDF processor.
        
        Args:
            output_dir: Directory for processed PDF data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not PYMUPDF_AVAILABLE:
            logger.error("PyMuPDF not available. Please install with: pip install PyMuPDF")
            raise ImportError("PyMuPDF is required for PDF processing")
        
        logger.info(f"PDF processor initialized with output directory: {self.output_dir}")
    
    def process_pdf(self, pdf_path: Union[str, Path], 
                   extract_images: bool = True,
                   extract_tables: bool = True,
                   extract_bookmarks: bool = True,
                   ocr_enabled: bool = False) -> Dict[str, Any]:
        """
        Process a PDF file comprehensively.
        
        Args:
            pdf_path: Path to PDF file
            extract_images: Whether to extract images
            extract_tables: Whether to extract tables
            extract_bookmarks: Whether to extract bookmarks
            ocr_enabled: Whether to use OCR for scanned pages
            
        Returns:
            Processing results
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            # Open PDF document
            doc = fitz.open(str(pdf_path))
            
            # Extract metadata
            metadata = self._extract_metadata(doc, pdf_path)
            
            # Extract text blocks
            text_blocks = self._extract_text_blocks(doc)
            
            # Extract images if requested
            images = []
            if extract_images:
                images = self._extract_images(doc, pdf_path)
            
            # Extract tables if requested
            tables = []
            if extract_tables:
                tables = self._extract_tables(doc)
            
            # Extract bookmarks if requested
            bookmarks = []
            if extract_bookmarks:
                bookmarks = self._extract_bookmarks(doc)
            
            # Process with OCR if enabled
            ocr_results = {}
            if ocr_enabled:
                ocr_results = self._process_ocr(doc)
            
            # Close document
            doc.close()
            
            # Compile results
            results = {
                "pdf_path": str(pdf_path),
                "metadata": metadata.dict(),
                "text_blocks": [block.dict() for block in text_blocks],
                "images": [img.dict() for img in images],
                "tables": [table.dict() for table in tables],
                "bookmarks": [bm.dict() for bm in bookmarks],
                "ocr_results": ocr_results,
                "processing_time": datetime.now().isoformat(),
                "page_count": metadata.page_count,
                "total_text_blocks": len(text_blocks),
                "total_images": len(images),
                "total_tables": len(tables),
                "total_bookmarks": len(bookmarks)
            }
            
            # Save results
            self._save_results(pdf_path, results)
            
            logger.info(f"PDF processing completed: {pdf_path}")
            logger.info(f"Extracted {len(text_blocks)} text blocks, {len(images)} images, {len(tables)} tables")
            
            return results
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise
    
    def _extract_metadata(self, doc: fitz.Document, pdf_path: Path) -> PDFMetadata:
        """Extract PDF metadata."""
        try:
            metadata = doc.metadata
            
            # Get file size
            file_size = pdf_path.stat().st_size
            
            # Check if PDF is encrypted
            is_encrypted = doc.is_encrypted
            
            # Check for forms
            has_forms = len(doc.get_pdf_widgets()) > 0
            
            # Check for bookmarks
            has_bookmarks = len(doc.get_toc()) > 0
            
            return PDFMetadata(
                title=metadata.get("title"),
                author=metadata.get("author"),
                subject=metadata.get("subject"),
                creator=metadata.get("creator"),
                producer=metadata.get("producer"),
                creation_date=metadata.get("creationDate"),
                modification_date=metadata.get("modDate"),
                keywords=metadata.get("keywords"),
                page_count=doc.page_count,
                file_size=file_size,
                pdf_version=doc.pdf_version(),
                is_encrypted=is_encrypted,
                has_forms=has_forms,
                has_bookmarks=has_bookmarks
            )
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return PDFMetadata(page_count=doc.page_count, file_size=pdf_path.stat().st_size)
    
    def _extract_text_blocks(self, doc: fitz.Document) -> List[PDFTextBlock]:
        """Extract text blocks from PDF."""
        text_blocks = []
        
        try:
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Get text blocks with formatting
                blocks = page.get_text("dict")
                
                for block_num, block in enumerate(blocks["blocks"]):
                    if "lines" in block:  # Text block
                        # Combine all lines in the block
                        block_text = ""
                        for line in block["lines"]:
                            for span in line["spans"]:
                                block_text += span["text"]
                            block_text += "\n"
                        
                        # Get first span for formatting info
                        if block["lines"] and block["lines"][0]["spans"]:
                            first_span = block["lines"][0]["spans"][0]
                            
                            text_block = PDFTextBlock(
                                page_number=page_num + 1,
                                block_number=block_num + 1,
                                text=block_text.strip(),
                                bbox=block["bbox"],
                                font_size=first_span["size"],
                                font_name=first_span["font"],
                                is_bold="Bold" in first_span["font"],
                                is_italic="Italic" in first_span["font"],
                                color=first_span["color"],
                                block_type="text"
                            )
                            
                            text_blocks.append(text_block)
                    
                    elif "image" in block:  # Image block
                        text_block = PDFTextBlock(
                            page_number=page_num + 1,
                            block_number=block_num + 1,
                            text="[IMAGE]",
                            bbox=block["bbox"],
                            font_size=0,
                            font_name="",
                            block_type="image"
                        )
                        
                        text_blocks.append(text_block)
            
            return text_blocks
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return []
    
    def _extract_images(self, doc: fitz.Document, pdf_path: Path) -> List[PDFImage]:
        """Extract images from PDF."""
        images = []
        
        try:
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Get image list
                image_list = page.get_images()
                
                for img_num, img in enumerate(image_list):
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Convert to bytes
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                    else:  # CMYK
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                        img_data = pix.tobytes("png")
                    
                    # Save image
                    img_filename = f"{pdf_path.stem}_page{page_num + 1}_img{img_num + 1}.png"
                    img_path = self.output_dir / "images" / img_filename
                    img_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    
                    # Get image info
                    img_info = {
                        "width": pix.width,
                        "height": pix.height,
                        "colorspace": pix.colorspace.name if pix.colorspace else "Unknown",
                        "bits_per_component": pix.n
                    }
                    
                    pdf_image = PDFImage(
                        page_number=page_num + 1,
                        image_number=img_num + 1,
                        bbox=[0, 0, pix.width, pix.height],  # Placeholder bbox
                        width=pix.width,
                        height=pix.height,
                        colorspace=img_info["colorspace"],
                        bits_per_component=img_info["bits_per_component"],
                        file_path=str(img_path)
                    )
                    
                    images.append(pdf_image)
                    
                    pix = None  # Free memory
            
            return images
            
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            return []
    
    def _extract_tables(self, doc: fitz.Document) -> List[PDFTable]:
        """Extract tables from PDF."""
        tables = []
        
        try:
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Find tables using text blocks
                # This is a simplified table detection
                # In a real implementation, you'd use more sophisticated table detection
                
                # Get text blocks
                blocks = page.get_text("dict")
                
                for block_num, block in enumerate(blocks["blocks"]):
                    if "lines" in block:
                        # Check if block looks like a table
                        lines = block["lines"]
                        if len(lines) > 1:
                            # Count tabs or spaces to detect table structure
                            tab_count = 0
                            for line in lines:
                                for span in line["spans"]:
                                    tab_count += span["text"].count("\t")
                            
                            if tab_count > len(lines) * 0.5:  # Heuristic for table detection
                                # Extract table data
                                table_rows = []
                                for line in lines:
                                    row = []
                                    for span in line["spans"]:
                                        row.append(span["text"].strip())
                                    table_rows.append(row)
                                
                                if table_rows:
                                    # Use first row as headers
                                    headers = table_rows[0] if table_rows else []
                                    data_rows = table_rows[1:] if len(table_rows) > 1 else []
                                    
                                    pdf_table = PDFTable(
                                        page_number=page_num + 1,
                                        table_number=len(tables) + 1,
                                        bbox=block["bbox"],
                                        rows=table_rows,
                                        headers=headers,
                                        confidence=0.7,  # Placeholder confidence
                                        cell_count=sum(len(row) for row in table_rows)
                                    )
                                    
                                    tables.append(pdf_table)
            
            return tables
            
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return []
    
    def _extract_bookmarks(self, doc: fitz.Document) -> List[PDFBookmark]:
        """Extract bookmarks from PDF."""
        bookmarks = []
        
        try:
            toc = doc.get_toc()
            
            for item in toc:
                bookmark = PDFBookmark(
                    title=item[1],
                    page=item[2],
                    level=item[0]
                )
                bookmarks.append(bookmark)
            
            return bookmarks
            
        except Exception as e:
            logger.error(f"Bookmark extraction failed: {e}")
            return []
    
    def _process_ocr(self, doc: fitz.Document) -> Dict[str, Any]:
        """Process OCR for scanned pages."""
        ocr_results = {}
        
        try:
            # This is a placeholder for OCR processing
            # In a real implementation, you'd integrate with Tesseract or similar
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Check if page has text
                text = page.get_text()
                
                if not text.strip():  # No text found, might be scanned
                    # Placeholder for OCR processing
                    ocr_results[f"page_{page_num + 1}"] = {
                        "has_text": False,
                        "ocr_text": "OCR processing would be performed here",
                        "confidence": 0.0
                    }
                else:
                    ocr_results[f"page_{page_num + 1}"] = {
                        "has_text": True,
                        "ocr_text": text,
                        "confidence": 1.0
                    }
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return {}
    
    def _save_results(self, pdf_path: Path, results: Dict[str, Any]):
        """Save processing results to file."""
        results_filename = f"{pdf_path.stem}_processing_results.json"
        results_path = self.output_dir / results_filename
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
    
    def extract_text_only(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract plain text from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        pdf_path = Path(pdf_path)
        
        try:
            doc = fitz.open(str(pdf_path))
            text = ""
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()
                text += "\n\n"  # Add page break
            
            doc.close()
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    def get_page_count(self, pdf_path: Union[str, Path]) -> int:
        """Get page count of PDF."""
        try:
            doc = fitz.open(str(pdf_path))
            page_count = doc.page_count
            doc.close()
            return page_count
        except Exception as e:
            logger.error(f"Failed to get page count: {e}")
            return 0
    
    def is_scanned_pdf(self, pdf_path: Union[str, Path]) -> bool:
        """
        Check if PDF is scanned (no selectable text).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF appears to be scanned
        """
        try:
            doc = fitz.open(str(pdf_path))
            
            # Check first few pages for text
            text_found = False
            for page_num in range(min(3, doc.page_count)):
                page = doc[page_num]
                text = page.get_text().strip()
                if text:
                    text_found = True
                    break
            
            doc.close()
            
            return not text_found
            
        except Exception as e:
            logger.error(f"Failed to check if PDF is scanned: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get PDF processor statistics."""
        return {
            "output_directory": str(self.output_dir),
            "processed_files": len(list(self.output_dir.glob("*_processing_results.json"))),
            "extracted_images": len(list((self.output_dir / "images").glob("*.png"))) if (self.output_dir / "images").exists() else 0,
            "pymupdf_available": PYMUPDF_AVAILABLE
        }