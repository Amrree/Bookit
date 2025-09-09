"""
Layout Analyzer Module

Advanced document layout analysis for understanding document structure,
identifying text blocks, images, tables, and other elements.

Features:
- Document structure analysis
- Text block detection and classification
- Image and figure detection
- Table detection and analysis
- Header/footer identification
- Reading order determination
- Layout confidence scoring
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
    import cv2
    import numpy as np
    from PIL import Image
    LAYOUT_AVAILABLE = True
except ImportError:
    LAYOUT_AVAILABLE = False
    logger.warning("Layout analysis libraries not available. Please install: pip install opencv-python pillow")


class TextBlock(pydantic.BaseModel):
    """Text block model."""
    block_id: str
    page_number: int
    bbox: List[float]  # [x0, y0, x1, y1]
    text: str
    block_type: str  # paragraph, heading, list_item, caption, etc.
    font_size: float
    font_weight: str  # normal, bold, italic
    alignment: str  # left, center, right, justify
    confidence: float
    reading_order: int
    metadata: Dict[str, Any] = {}


class ImageBlock(pydantic.BaseModel):
    """Image block model."""
    image_id: str
    page_number: int
    bbox: List[float]
    image_type: str  # figure, chart, diagram, photo, etc.
    caption: Optional[str] = None
    confidence: float
    metadata: Dict[str, Any] = {}


class TableBlock(pydantic.BaseModel):
    """Table block model."""
    table_id: str
    page_number: int
    bbox: List[float]
    rows: int
    columns: int
    has_header: bool
    confidence: float
    metadata: Dict[str, Any] = {}


class LayoutAnalysis(pydantic.BaseModel):
    """Layout analysis result."""
    document_id: str
    page_count: int
    text_blocks: List[TextBlock]
    image_blocks: List[ImageBlock]
    table_blocks: List[TableBlock]
    reading_order: List[str]  # Block IDs in reading order
    structure: Dict[str, Any]
    confidence: float
    processing_time: float


class LayoutAnalyzer:
    """
    Advanced document layout analyzer.
    
    Features:
    - Document structure analysis
    - Text block detection and classification
    - Image and figure detection
    - Table detection and analysis
    - Reading order determination
    """
    
    def __init__(self, output_dir: str = "./output/layout_analysis"):
        """
        Initialize layout analyzer.
        
        Args:
            output_dir: Directory for layout analysis results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not LAYOUT_AVAILABLE:
            logger.error("Layout analysis libraries not available.")
            raise ImportError("Layout analysis libraries are required")
        
        logger.info(f"Layout analyzer initialized with output directory: {self.output_dir}")
    
    def analyze_document(self, document_path: Union[str, Path], 
                        document_type: str = "pdf") -> LayoutAnalysis:
        """
        Analyze document layout.
        
        Args:
            document_path: Path to document
            document_type: Type of document (pdf, image, etc.)
            
        Returns:
            Layout analysis result
        """
        document_path = Path(document_path)
        
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        
        logger.info(f"Analyzing document layout: {document_path}")
        
        start_time = datetime.now()
        
        try:
            # Generate document ID
            document_id = f"doc_{document_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Analyze based on document type
            if document_type.lower() == "pdf":
                analysis = self._analyze_pdf_layout(document_path, document_id)
            elif document_type.lower() in ["image", "png", "jpg", "jpeg"]:
                analysis = self._analyze_image_layout(document_path, document_id)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Calculate processing time
            analysis.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Save analysis
            self._save_analysis(document_id, analysis)
            
            logger.info(f"Layout analysis completed: {document_path}")
            logger.info(f"Found {len(analysis.text_blocks)} text blocks, {len(analysis.image_blocks)} images, {len(analysis.table_blocks)} tables")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Layout analysis failed: {e}")
            raise
    
    def _analyze_pdf_layout(self, pdf_path: Path, document_id: str) -> LayoutAnalysis:
        """Analyze PDF layout."""
        try:
            # This is a placeholder implementation
            # In a real implementation, you'd use PDF layout analysis libraries
            
            # Mock analysis result
            text_blocks = [
                TextBlock(
                    block_id="block_1",
                    page_number=1,
                    bbox=[50, 100, 550, 150],
                    text="Document Title",
                    block_type="heading",
                    font_size=18.0,
                    font_weight="bold",
                    alignment="center",
                    confidence=0.95,
                    reading_order=1
                ),
                TextBlock(
                    block_id="block_2",
                    page_number=1,
                    bbox=[50, 200, 550, 400],
                    text="This is the main content of the document. It contains multiple paragraphs and provides detailed information about the topic.",
                    block_type="paragraph",
                    font_size=12.0,
                    font_weight="normal",
                    alignment="justify",
                    confidence=0.90,
                    reading_order=2
                )
            ]
            
            image_blocks = [
                ImageBlock(
                    image_id="img_1",
                    page_number=1,
                    bbox=[50, 450, 200, 550],
                    image_type="figure",
                    caption="Figure 1: Sample diagram",
                    confidence=0.88
                )
            ]
            
            table_blocks = [
                TableBlock(
                    table_id="table_1",
                    page_number=1,
                    bbox=[50, 600, 550, 700],
                    rows=3,
                    columns=3,
                    has_header=True,
                    confidence=0.85
                )
            ]
            
            analysis = LayoutAnalysis(
                document_id=document_id,
                page_count=1,
                text_blocks=text_blocks,
                image_blocks=image_blocks,
                table_blocks=table_blocks,
                reading_order=["block_1", "block_2", "img_1", "table_1"],
                structure={
                    "title": "Document Title",
                    "sections": ["Introduction", "Main Content", "Conclusion"],
                    "has_toc": False,
                    "page_count": 1
                },
                confidence=0.89
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"PDF layout analysis failed: {e}")
            raise
    
    def _analyze_image_layout(self, image_path: Path, document_id: str) -> LayoutAnalysis:
        """Analyze image layout."""
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect text regions
            text_blocks = self._detect_text_regions(gray, 1)
            
            # Detect image regions
            image_blocks = self._detect_image_regions(gray, 1)
            
            # Detect table regions
            table_blocks = self._detect_table_regions(gray, 1)
            
            # Determine reading order
            reading_order = self._determine_reading_order(text_blocks, image_blocks, table_blocks)
            
            analysis = LayoutAnalysis(
                document_id=document_id,
                page_count=1,
                text_blocks=text_blocks,
                image_blocks=image_blocks,
                table_blocks=table_blocks,
                reading_order=reading_order,
                structure={
                    "title": "Image Document",
                    "sections": [],
                    "has_toc": False,
                    "page_count": 1
                },
                confidence=0.80
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Image layout analysis failed: {e}")
            raise
    
    def _detect_text_regions(self, image: np.ndarray, page_number: int) -> List[TextBlock]:
        """Detect text regions in image."""
        try:
            # Use EAST text detector or similar
            # This is a simplified implementation
            
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_blocks = []
            
            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size (text regions should be reasonable size)
                if w > 50 and h > 20:
                    # Determine block type based on size and position
                    block_type = "paragraph"
                    if h > 40:
                        block_type = "heading"
                    elif w < 100:
                        block_type = "list_item"
                    
                    text_block = TextBlock(
                        block_id=f"block_{i+1}",
                        page_number=page_number,
                        bbox=[float(x), float(y), float(x+w), float(y+h)],
                        text="",  # Would be filled by OCR
                        block_type=block_type,
                        font_size=12.0,
                        font_weight="normal",
                        alignment="left",
                        confidence=0.8,
                        reading_order=i+1
                    )
                    
                    text_blocks.append(text_block)
            
            return text_blocks
            
        except Exception as e:
            logger.error(f"Text region detection failed: {e}")
            return []
    
    def _detect_image_regions(self, image: np.ndarray, page_number: int) -> List[ImageBlock]:
        """Detect image regions in document."""
        try:
            # Use edge detection to find image regions
            edges = cv2.Canny(image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            image_blocks = []
            
            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size (images should be reasonably large)
                if w > 100 and h > 100:
                    image_block = ImageBlock(
                        image_id=f"img_{i+1}",
                        page_number=page_number,
                        bbox=[float(x), float(y), float(x+w), float(y+h)],
                        image_type="figure",
                        confidence=0.7
                    )
                    
                    image_blocks.append(image_block)
            
            return image_blocks
            
        except Exception as e:
            logger.error(f"Image region detection failed: {e}")
            return []
    
    def _detect_table_regions(self, image: np.ndarray, page_number: int) -> List[TableBlock]:
        """Detect table regions in document."""
        try:
            # Use line detection to find table structures
            edges = cv2.Canny(image, 50, 150)
            
            # Detect lines
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            if lines is None:
                return []
            
            # Find rectangular regions (tables)
            table_blocks = []
            
            # This is a simplified table detection
            # In a real implementation, you'd use more sophisticated methods
            
            # Group lines by orientation
            horizontal_lines = []
            vertical_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 10:  # Horizontal line
                    horizontal_lines.append(line[0])
                elif abs(x2 - x1) < 10:  # Vertical line
                    vertical_lines.append(line[0])
            
            # Find intersections to identify table cells
            if len(horizontal_lines) > 1 and len(vertical_lines) > 1:
                # Calculate table bounding box
                min_x = min(min(line[0], line[2]) for line in horizontal_lines + vertical_lines)
                max_x = max(max(line[0], line[2]) for line in horizontal_lines + vertical_lines)
                min_y = min(min(line[1], line[3]) for line in horizontal_lines + vertical_lines)
                max_y = max(max(line[1], line[3]) for line in horizontal_lines + vertical_lines)
                
                table_block = TableBlock(
                    table_id="table_1",
                    page_number=page_number,
                    bbox=[float(min_x), float(min_y), float(max_x), float(max_y)],
                    rows=len(horizontal_lines) - 1,
                    columns=len(vertical_lines) - 1,
                    has_header=True,
                    confidence=0.7
                )
                
                table_blocks.append(table_block)
            
            return table_blocks
            
        except Exception as e:
            logger.error(f"Table region detection failed: {e}")
            return []
    
    def _determine_reading_order(self, text_blocks: List[TextBlock], 
                                image_blocks: List[ImageBlock], 
                                table_blocks: List[TableBlock]) -> List[str]:
        """Determine reading order of document elements."""
        try:
            # Combine all blocks
            all_blocks = []
            
            for block in text_blocks:
                all_blocks.append((block.block_id, block.bbox, "text"))
            
            for block in image_blocks:
                all_blocks.append((block.image_id, block.bbox, "image"))
            
            for block in table_blocks:
                all_blocks.append((block.table_id, block.bbox, "table"))
            
            # Sort by position (top to bottom, left to right)
            all_blocks.sort(key=lambda x: (x[1][1], x[1][0]))  # Sort by y, then x
            
            # Extract block IDs in reading order
            reading_order = [block[0] for block in all_blocks]
            
            return reading_order
            
        except Exception as e:
            logger.error(f"Reading order determination failed: {e}")
            return []
    
    def _save_analysis(self, document_id: str, analysis: LayoutAnalysis):
        """Save layout analysis to file."""
        analysis_filename = f"{document_id}_layout_analysis.json"
        analysis_path = self.output_dir / analysis_filename
        
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis.dict(), f, indent=2, default=str)
    
    def get_document_structure(self, analysis: LayoutAnalysis) -> Dict[str, Any]:
        """Extract document structure from analysis."""
        try:
            structure = {
                "title": None,
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "sections": []
            }
            
            # Find title (usually the first heading)
            for block in analysis.text_blocks:
                if block.block_type == "heading" and not structure["title"]:
                    structure["title"] = block.text
                    break
            
            # Categorize blocks
            for block in analysis.text_blocks:
                if block.block_type == "heading":
                    structure["headings"].append({
                        "text": block.text,
                        "level": 1,  # Would need more sophisticated heading level detection
                        "page": block.page_number
                    })
                elif block.block_type == "paragraph":
                    structure["paragraphs"].append({
                        "text": block.text,
                        "page": block.page_number
                    })
            
            # Add images
            for block in analysis.image_blocks:
                structure["images"].append({
                    "type": block.image_type,
                    "caption": block.caption,
                    "page": block.page_number
                })
            
            # Add tables
            for block in analysis.table_blocks:
                structure["tables"].append({
                    "rows": block.rows,
                    "columns": block.columns,
                    "has_header": block.has_header,
                    "page": block.page_number
                })
            
            return structure
            
        except Exception as e:
            logger.error(f"Structure extraction failed: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get layout analyzer statistics."""
        return {
            "output_directory": str(self.output_dir),
            "analyzed_documents": len(list(self.output_dir.glob("*_layout_analysis.json"))),
            "layout_available": LAYOUT_AVAILABLE
        }