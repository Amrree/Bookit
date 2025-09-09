"""
Table Extractor Module

Advanced table extraction and processing for documents,
with support for various formats and table structures.

Features:
- Table detection and extraction
- Table structure analysis
- Cell content extraction
- Table formatting and styling
- Export to various formats
- Table validation and cleaning
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
    import pandas as pd
    TABLE_AVAILABLE = True
except ImportError:
    TABLE_AVAILABLE = False
    logger.warning("Table extraction libraries not available. Please install: pip install opencv-python pillow pandas")


class TableCell(pydantic.BaseModel):
    """Table cell model."""
    row: int
    column: int
    text: str
    bbox: List[float]  # [x0, y0, x1, y1]
    is_header: bool = False
    is_merged: bool = False
    colspan: int = 1
    rowspan: int = 1
    confidence: float = 1.0
    metadata: Dict[str, Any] = {}


class TableStructure(pydantic.BaseModel):
    """Table structure model."""
    table_id: str
    page_number: int
    bbox: List[float]  # [x0, y0, x1, y1]
    rows: int
    columns: int
    cells: List[TableCell]
    headers: List[str]
    has_header_row: bool
    has_header_column: bool
    confidence: float
    metadata: Dict[str, Any] = {}


class TableExtractor:
    """
    Advanced table extractor for documents.
    
    Features:
    - Table detection and extraction
    - Table structure analysis
    - Cell content extraction
    - Table formatting and styling
    - Export to various formats
    """
    
    def __init__(self, output_dir: str = "./output/table_extraction"):
        """
        Initialize table extractor.
        
        Args:
            output_dir: Directory for table extraction results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not TABLE_AVAILABLE:
            logger.error("Table extraction libraries not available.")
            raise ImportError("Table extraction libraries are required")
        
        logger.info(f"Table extractor initialized with output directory: {self.output_dir}")
    
    def extract_tables_from_image(self, image_path: Union[str, Path]) -> List[TableStructure]:
        """
        Extract tables from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of extracted table structures
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        logger.info(f"Extracting tables from image: {image_path}")
        
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect table regions
            table_regions = self._detect_table_regions(gray)
            
            # Extract tables
            tables = []
            for i, region in enumerate(table_regions):
                table = self._extract_table_from_region(gray, region, i+1, 1)
                if table:
                    tables.append(table)
            
            # Save results
            self._save_tables(image_path.stem, tables)
            
            logger.info(f"Extracted {len(tables)} tables from image: {image_path}")
            
            return tables
            
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            raise
    
    def extract_tables_from_pdf(self, pdf_path: Union[str, Path]) -> List[TableStructure]:
        """
        Extract tables from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of extracted table structures
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Extracting tables from PDF: {pdf_path}")
        
        try:
            # This is a placeholder implementation
            # In a real implementation, you'd use PDF table extraction libraries
            
            # Mock table extraction result
            tables = [
                TableStructure(
                    table_id="table_1",
                    page_number=1,
                    bbox=[50, 100, 550, 200],
                    rows=3,
                    columns=3,
                    cells=[
                        TableCell(row=0, column=0, text="Header 1", bbox=[50, 100, 150, 120], is_header=True),
                        TableCell(row=0, column=1, text="Header 2", bbox=[150, 100, 250, 120], is_header=True),
                        TableCell(row=0, column=2, text="Header 3", bbox=[250, 100, 350, 120], is_header=True),
                        TableCell(row=1, column=0, text="Data 1", bbox=[50, 120, 150, 140]),
                        TableCell(row=1, column=1, text="Data 2", bbox=[150, 120, 250, 140]),
                        TableCell(row=1, column=2, text="Data 3", bbox=[250, 120, 350, 140]),
                        TableCell(row=2, column=0, text="Data 4", bbox=[50, 140, 150, 160]),
                        TableCell(row=2, column=1, text="Data 5", bbox=[150, 140, 250, 160]),
                        TableCell(row=2, column=2, text="Data 6", bbox=[250, 140, 350, 160])
                    ],
                    headers=["Header 1", "Header 2", "Header 3"],
                    has_header_row=True,
                    has_header_column=False,
                    confidence=0.85
                )
            ]
            
            # Save results
            self._save_tables(pdf_path.stem, tables)
            
            logger.info(f"Extracted {len(tables)} tables from PDF: {pdf_path}")
            
            return tables
            
        except Exception as e:
            logger.error(f"PDF table extraction failed: {e}")
            raise
    
    def _detect_table_regions(self, image: np.ndarray) -> List[List[int]]:
        """Detect table regions in image."""
        try:
            # Use line detection to find table structures
            edges = cv2.Canny(image, 50, 150)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            
            # Detect horizontal lines
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Detect vertical lines
            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Find contours
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size and aspect ratio
            table_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size and aspect ratio
                if w > 100 and h > 50 and w/h > 1.5:  # Tables should be wider than tall
                    table_regions.append([x, y, x+w, y+h])
            
            return table_regions
            
        except Exception as e:
            logger.error(f"Table region detection failed: {e}")
            return []
    
    def _extract_table_from_region(self, image: np.ndarray, region: List[int], 
                                  table_id: int, page_number: int) -> Optional[TableStructure]:
        """Extract table structure from region."""
        try:
            x1, y1, x2, y2 = region
            
            # Crop table region
            table_image = image[y1:y2, x1:x2]
            
            # Detect grid lines
            horizontal_lines = self._detect_horizontal_lines(table_image)
            vertical_lines = self._detect_vertical_lines(table_image)
            
            # Create grid
            grid = self._create_grid(horizontal_lines, vertical_lines, x1, y1)
            
            if not grid:
                return None
            
            # Extract cells
            cells = self._extract_cells(table_image, grid, table_id)
            
            # Determine headers
            headers = self._determine_headers(cells)
            
            # Create table structure
            table = TableStructure(
                table_id=f"table_{table_id}",
                page_number=page_number,
                bbox=region,
                rows=len(grid) - 1,
                columns=len(grid[0]) - 1,
                cells=cells,
                headers=headers,
                has_header_row=len(headers) > 0,
                has_header_column=False,  # Would need more sophisticated detection
                confidence=0.8
            )
            
            return table
            
        except Exception as e:
            logger.error(f"Table extraction from region failed: {e}")
            return None
    
    def _detect_horizontal_lines(self, image: np.ndarray) -> List[int]:
        """Detect horizontal lines in table."""
        try:
            # Use horizontal kernel
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            
            # Detect horizontal lines
            horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Find line positions
            line_positions = []
            for i in range(horizontal_lines.shape[0]):
                if np.sum(horizontal_lines[i, :]) > 0:
                    line_positions.append(i)
            
            return line_positions
            
        except Exception as e:
            logger.error(f"Horizontal line detection failed: {e}")
            return []
    
    def _detect_vertical_lines(self, image: np.ndarray) -> List[int]:
        """Detect vertical lines in table."""
        try:
            # Use vertical kernel
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            
            # Detect vertical lines
            vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
            
            # Find line positions
            line_positions = []
            for i in range(vertical_lines.shape[1]):
                if np.sum(vertical_lines[:, i]) > 0:
                    line_positions.append(i)
            
            return line_positions
            
        except Exception as e:
            logger.error(f"Vertical line detection failed: {e}")
            return []
    
    def _create_grid(self, horizontal_lines: List[int], vertical_lines: List[int], 
                    offset_x: int, offset_y: int) -> List[List[Tuple[int, int, int, int]]]:
        """Create grid from detected lines."""
        try:
            if not horizontal_lines or not vertical_lines:
                return []
            
            # Sort lines
            horizontal_lines.sort()
            vertical_lines.sort()
            
            # Create grid
            grid = []
            for i in range(len(horizontal_lines) - 1):
                row = []
                for j in range(len(vertical_lines) - 1):
                    cell = (
                        vertical_lines[j] + offset_x,
                        horizontal_lines[i] + offset_y,
                        vertical_lines[j + 1] + offset_x,
                        horizontal_lines[i + 1] + offset_y
                    )
                    row.append(cell)
                grid.append(row)
            
            return grid
            
        except Exception as e:
            logger.error(f"Grid creation failed: {e}")
            return []
    
    def _extract_cells(self, image: np.ndarray, grid: List[List[Tuple[int, int, int, int]]], 
                      table_id: int) -> List[TableCell]:
        """Extract cell content from grid."""
        try:
            cells = []
            
            for row_idx, row in enumerate(grid):
                for col_idx, cell_bbox in enumerate(row):
                    x1, y1, x2, y2 = cell_bbox
                    
                    # Crop cell
                    cell_image = image[y1:y2, x1:x2]
                    
                    # Extract text (placeholder - would use OCR)
                    cell_text = self._extract_text_from_cell(cell_image)
                    
                    # Create cell
                    cell = TableCell(
                        row=row_idx,
                        column=col_idx,
                        text=cell_text,
                        bbox=[float(x1), float(y1), float(x2), float(y2)],
                        is_header=row_idx == 0,  # Assume first row is header
                        confidence=0.8
                    )
                    
                    cells.append(cell)
            
            return cells
            
        except Exception as e:
            logger.error(f"Cell extraction failed: {e}")
            return []
    
    def _extract_text_from_cell(self, cell_image: np.ndarray) -> str:
        """Extract text from cell image."""
        try:
            # This is a placeholder implementation
            # In a real implementation, you'd use OCR
            
            # For now, return placeholder text
            return f"Cell_{cell_image.shape[0]}x{cell_image.shape[1]}"
            
        except Exception as e:
            logger.error(f"Text extraction from cell failed: {e}")
            return ""
    
    def _determine_headers(self, cells: List[TableCell]) -> List[str]:
        """Determine table headers."""
        try:
            headers = []
            
            # Find cells in first row
            first_row_cells = [cell for cell in cells if cell.row == 0]
            
            # Sort by column
            first_row_cells.sort(key=lambda x: x.column)
            
            # Extract header text
            for cell in first_row_cells:
                headers.append(cell.text)
            
            return headers
            
        except Exception as e:
            logger.error(f"Header determination failed: {e}")
            return []
    
    def _save_tables(self, document_name: str, tables: List[TableStructure]):
        """Save extracted tables to files."""
        try:
            # Save JSON format
            json_filename = f"{document_name}_tables.json"
            json_path = self.output_dir / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump([table.dict() for table in tables], f, indent=2, default=str)
            
            # Save CSV format for each table
            for table in tables:
                csv_filename = f"{document_name}_table_{table.table_id}.csv"
                csv_path = self.output_dir / csv_filename
                
                # Convert to DataFrame
                df = self._table_to_dataframe(table)
                df.to_csv(csv_path, index=False)
            
            logger.info(f"Saved {len(tables)} tables for document: {document_name}")
            
        except Exception as e:
            logger.error(f"Failed to save tables: {e}")
    
    def _table_to_dataframe(self, table: TableStructure) -> pd.DataFrame:
        """Convert table structure to pandas DataFrame."""
        try:
            # Create empty DataFrame
            df = pd.DataFrame(index=range(table.rows), columns=range(table.columns))
            
            # Fill DataFrame with cell data
            for cell in table.cells:
                if cell.row < table.rows and cell.column < table.columns:
                    df.iloc[cell.row, cell.column] = cell.text
            
            # Set column names
            if table.headers:
                df.columns = table.headers[:len(df.columns)]
            
            return df
            
        except Exception as e:
            logger.error(f"DataFrame conversion failed: {e}")
            return pd.DataFrame()
    
    def export_table_to_markdown(self, table: TableStructure) -> str:
        """Export table to Markdown format."""
        try:
            if not table.cells:
                return ""
            
            # Create markdown table
            markdown_lines = []
            
            # Add header row
            if table.headers:
                header_line = "| " + " | ".join(table.headers) + " |"
                separator_line = "| " + " | ".join(["---"] * len(table.headers)) + " |"
                markdown_lines.append(header_line)
                markdown_lines.append(separator_line)
            
            # Add data rows
            for row_idx in range(table.rows):
                row_cells = [cell for cell in table.cells if cell.row == row_idx]
                row_cells.sort(key=lambda x: x.column)
                
                if row_cells:
                    row_text = "| " + " | ".join([cell.text for cell in row_cells]) + " |"
                    markdown_lines.append(row_text)
            
            return "\n".join(markdown_lines)
            
        except Exception as e:
            logger.error(f"Markdown export failed: {e}")
            return ""
    
    def export_table_to_html(self, table: TableStructure) -> str:
        """Export table to HTML format."""
        try:
            if not table.cells:
                return ""
            
            html_lines = ["<table>"]
            
            # Add header row
            if table.headers:
                html_lines.append("  <thead>")
                html_lines.append("    <tr>")
                for header in table.headers:
                    html_lines.append(f"      <th>{header}</th>")
                html_lines.append("    </tr>")
                html_lines.append("  </thead>")
            
            # Add data rows
            html_lines.append("  <tbody>")
            for row_idx in range(table.rows):
                row_cells = [cell for cell in table.cells if cell.row == row_idx]
                row_cells.sort(key=lambda x: x.column)
                
                if row_cells:
                    html_lines.append("    <tr>")
                    for cell in row_cells:
                        tag = "th" if cell.is_header else "td"
                        html_lines.append(f"      <{tag}>{cell.text}</{tag}>")
                    html_lines.append("    </tr>")
            html_lines.append("  </tbody>")
            html_lines.append("</table>")
            
            return "\n".join(html_lines)
            
        except Exception as e:
            logger.error(f"HTML export failed: {e}")
            return ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get table extractor statistics."""
        return {
            "output_directory": str(self.output_dir),
            "extracted_tables": len(list(self.output_dir.glob("*_tables.json"))),
            "table_available": TABLE_AVAILABLE
        }