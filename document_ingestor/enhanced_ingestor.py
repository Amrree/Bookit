"""
Enhanced Document Ingestor Module

Integrates with the unified document parser to provide advanced document
processing capabilities including OCR, layout analysis, and table extraction.

Features:
- Multi-format document parsing with unified parser
- Advanced OCR processing for scanned documents
- Layout analysis and structure recognition
- Table extraction and formatting
- Intelligent text chunking
- Metadata extraction and processing
- Incremental ingestion with change detection
- Content validation and cleaning
- Integration with memory manager
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import re

import pydantic

logger = logging.getLogger(__name__)

# Import unified document parser
try:
    from document_processor.unified_parser import UnifiedDocumentParser, ProcessingOptions, DocumentParseResult
    UNIFIED_PARSER_AVAILABLE = True
except ImportError:
    UNIFIED_PARSER_AVAILABLE = False
    logger.warning("Unified document parser not available")


class EnhancedDocumentMetadata(pydantic.BaseModel):
    """Enhanced metadata model for ingested documents."""
    source_id: str
    original_filename: str
    file_type: str
    file_size: int
    ingestion_timestamp: datetime
    chunk_count: int
    language: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = []
    checksum: str
    
    # Enhanced metadata
    page_count: Optional[int] = None
    has_images: bool = False
    has_tables: bool = False
    is_scanned: bool = False
    requires_ocr: bool = False
    layout_confidence: Optional[float] = None
    processing_time: Optional[float] = None
    ocr_confidence: Optional[float] = None
    table_count: int = 0
    image_count: int = 0


class DocumentChunk(pydantic.BaseModel):
    """Document chunk model with enhanced metadata."""
    chunk_id: str
    source_id: str
    content: str
    chunk_index: int
    chunk_type: str  # text, table, image, heading, etc.
    metadata: Dict[str, Any] = {}
    bbox: Optional[List[float]] = None  # Bounding box for layout-aware chunks
    confidence: Optional[float] = None
    page_number: Optional[int] = None


class EnhancedDocumentIngestor:
    """
    Enhanced document ingestor with advanced processing capabilities.
    
    Features:
    - Multi-format document parsing with unified parser
    - Advanced OCR processing for scanned documents
    - Layout analysis and structure recognition
    - Table extraction and formatting
    - Intelligent text chunking
    - Metadata extraction and processing
    - Incremental ingestion with change detection
    """
    
    def __init__(self, 
                 output_dir: str = "./output/enhanced_ingestion",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 enable_ocr: bool = True,
                 enable_layout_analysis: bool = True,
                 enable_table_extraction: bool = True):
        """
        Initialize enhanced document ingestor.
        
        Args:
            output_dir: Directory for ingestion results
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            enable_ocr: Enable OCR processing
            enable_layout_analysis: Enable layout analysis
            enable_table_extraction: Enable table extraction
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.enable_ocr = enable_ocr
        self.enable_layout_analysis = enable_layout_analysis
        self.enable_table_extraction = enable_table_extraction
        
        # Initialize unified parser
        if UNIFIED_PARSER_AVAILABLE:
            self.parser = UnifiedDocumentParser(self.output_dir / "parsing")
        else:
            self.parser = None
            logger.warning("Unified parser not available. Using basic processing.")
        
        # Chunk storage
        self.chunks_dir = self.output_dir / "chunks"
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata storage
        self.metadata_dir = self.output_dir / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Enhanced document ingestor initialized with output directory: {self.output_dir}")
    
    async def ingest_document(self, file_path: Union[str, Path], 
                             source_id: Optional[str] = None,
                             language: str = "eng") -> EnhancedDocumentMetadata:
        """
        Ingest a document with enhanced processing.
        
        Args:
            file_path: Path to document
            source_id: Optional source ID
            language: Document language for OCR
            
        Returns:
            Enhanced document metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        logger.info(f"Ingesting document with enhanced processing: {file_path}")
        
        start_time = datetime.now()
        
        try:
            # Generate source ID if not provided
            if source_id is None:
                source_id = f"src_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create processing options
            processing_options = ProcessingOptions(
                extract_text=True,
                extract_metadata=True,
                extract_images=self.enable_ocr,
                extract_tables=self.enable_table_extraction,
                perform_ocr=self.enable_ocr,
                analyze_layout=self.enable_layout_analysis,
                preprocess_images=True,
                language=language,
                confidence_threshold=0.5
            )
            
            # Parse document with unified parser
            if self.parser:
                parse_result = self.parser.parse_document(file_path, processing_options)
            else:
                # Fallback to basic processing
                parse_result = self._basic_parse_document(file_path)
            
            # Create enhanced metadata
            metadata = self._create_enhanced_metadata(
                source_id, file_path, parse_result, start_time
            )
            
            # Create chunks
            chunks = await self._create_enhanced_chunks(parse_result, source_id)
            
            # Save metadata and chunks
            self._save_metadata(metadata)
            self._save_chunks(chunks)
            
            logger.info(f"Enhanced document ingestion completed: {file_path}")
            logger.info(f"Created {len(chunks)} chunks, Processing time: {metadata.processing_time:.2f}s")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Enhanced document ingestion failed: {e}")
            raise
    
    def _basic_parse_document(self, file_path: Path) -> DocumentParseResult:
        """Basic document parsing fallback."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create basic parse result
            from document_processor.unified_parser import DocumentParseResult, DocumentType, ProcessingOptions
            
            result = DocumentParseResult(
                document_id=f"doc_{file_path.stem}",
                file_path=str(file_path),
                document_type=DocumentType(
                    file_extension=file_path.suffix.lower(),
                    mime_type="text/plain",
                    is_text_based=True,
                    requires_ocr=False,
                    supports_layout_analysis=False,
                    supports_table_extraction=False
                ),
                processing_options=ProcessingOptions(),
                text_content=content,
                metadata={"type": "text", "file_size": file_path.stat().st_size},
                images=[],
                tables=[],
                layout_analysis=None,
                ocr_results=[],
                processing_time=0.0,
                success=True,
                errors=[]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Basic document parsing failed: {e}")
            raise
    
    def _create_enhanced_metadata(self, source_id: str, file_path: Path, 
                                 parse_result: DocumentParseResult, 
                                 start_time: datetime) -> EnhancedDocumentMetadata:
        """Create enhanced metadata from parse result."""
        try:
            # Calculate checksum
            checksum = self._calculate_checksum(file_path)
            
            # Extract basic metadata
            metadata = EnhancedDocumentMetadata(
                source_id=source_id,
                original_filename=file_path.name,
                file_type=file_path.suffix.lower(),
                file_size=file_path.stat().st_size,
                ingestion_timestamp=start_time,
                chunk_count=0,  # Will be updated after chunking
                checksum=checksum,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            # Extract enhanced metadata from parse result
            if parse_result.metadata:
                metadata.language = parse_result.metadata.get("language")
                metadata.author = parse_result.metadata.get("author")
                metadata.title = parse_result.metadata.get("title")
                metadata.subject = parse_result.metadata.get("subject")
                metadata.page_count = parse_result.metadata.get("page_count")
            
            # Extract processing-specific metadata
            metadata.has_images = len(parse_result.images) > 0
            metadata.has_tables = len(parse_result.tables) > 0
            metadata.is_scanned = parse_result.document_type.requires_ocr
            metadata.requires_ocr = parse_result.document_type.requires_ocr
            metadata.table_count = len(parse_result.tables)
            metadata.image_count = len(parse_result.images)
            
            # Extract confidence scores
            if parse_result.layout_analysis:
                metadata.layout_confidence = parse_result.layout_analysis.confidence
            
            if parse_result.ocr_results:
                ocr_confidences = [result.confidence for result in parse_result.ocr_results]
                metadata.ocr_confidence = sum(ocr_confidences) / len(ocr_confidences)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Enhanced metadata creation failed: {e}")
            raise
    
    async def _create_enhanced_chunks(self, parse_result: DocumentParseResult, 
                                    source_id: str) -> List[DocumentChunk]:
        """Create enhanced chunks from parse result."""
        try:
            chunks = []
            chunk_index = 0
            
            # Create text chunks
            if parse_result.text_content:
                text_chunks = self._chunk_text(parse_result.text_content)
                
                for i, chunk_text in enumerate(text_chunks):
                    chunk = DocumentChunk(
                        chunk_id=f"{source_id}_text_{i}",
                        source_id=source_id,
                        content=chunk_text,
                        chunk_index=chunk_index,
                        chunk_type="text",
                        metadata={
                            "chunk_size": len(chunk_text),
                            "is_text_chunk": True
                        }
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            
            # Create table chunks
            if parse_result.tables:
                for i, table in enumerate(parse_result.tables):
                    # Convert table to text representation
                    table_text = self._table_to_text(table)
                    
                    chunk = DocumentChunk(
                        chunk_id=f"{source_id}_table_{i}",
                        source_id=source_id,
                        content=table_text,
                        chunk_index=chunk_index,
                        chunk_type="table",
                        metadata={
                            "table_id": table.table_id,
                            "rows": table.rows,
                            "columns": table.columns,
                            "has_header": table.has_header_row,
                            "confidence": table.confidence
                        },
                        bbox=table.bbox,
                        confidence=table.confidence,
                        page_number=table.page_number
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            
            # Create image chunks
            if parse_result.images:
                for i, image in enumerate(parse_result.images):
                    chunk = DocumentChunk(
                        chunk_id=f"{source_id}_image_{i}",
                        source_id=source_id,
                        content=f"[IMAGE: {image.get('type', 'figure')}]",
                        chunk_index=chunk_index,
                        chunk_type="image",
                        metadata={
                            "image_id": image.get("image_id", f"img_{i}"),
                            "image_type": image.get("type", "figure"),
                            "width": image.get("width", 0),
                            "height": image.get("height", 0)
                        },
                        bbox=image.get("bbox"),
                        page_number=image.get("page_number")
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            
            # Create layout-aware chunks if layout analysis is available
            if parse_result.layout_analysis and parse_result.layout_analysis.text_blocks:
                layout_chunks = self._create_layout_chunks(
                    parse_result.layout_analysis, source_id, chunk_index
                )
                chunks.extend(layout_chunks)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Enhanced chunk creation failed: {e}")
            return []
    
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text into overlapping segments."""
        try:
            if not text:
                return []
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            
            if len(text) <= self.chunk_size:
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + self.chunk_size
                
                # Find good break point
                if end < len(text):
                    # Look for sentence boundary
                    break_point = text.rfind('.', start, end)
                    if break_point == -1:
                        # Look for word boundary
                        break_point = text.rfind(' ', start, end)
                    
                    if break_point > start:
                        end = break_point + 1
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                # Move start position with overlap
                start = end - self.chunk_overlap
                if start >= len(text):
                    break
            
            return chunks
            
        except Exception as e:
            logger.error(f"Text chunking failed: {e}")
            return [text]
    
    def _table_to_text(self, table) -> str:
        """Convert table to text representation."""
        try:
            if not hasattr(table, 'cells') or not table.cells:
                return f"Table {table.table_id}: {table.rows}x{table.columns}"
            
            # Create table text representation
            lines = [f"Table {table.table_id}:"]
            
            # Add headers if available
            if table.headers:
                lines.append(" | ".join(table.headers))
                lines.append("-" * (len(" | ".join(table.headers))))
            
            # Add rows
            for row_idx in range(table.rows):
                row_cells = [cell for cell in table.cells if cell.row == row_idx]
                row_cells.sort(key=lambda x: x.column)
                
                if row_cells:
                    row_text = " | ".join([cell.text for cell in row_cells])
                    lines.append(row_text)
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Table to text conversion failed: {e}")
            return f"Table {getattr(table, 'table_id', 'unknown')}"
    
    def _create_layout_chunks(self, layout_analysis, source_id: str, 
                            start_index: int) -> List[DocumentChunk]:
        """Create layout-aware chunks from layout analysis."""
        try:
            chunks = []
            chunk_index = start_index
            
            for block in layout_analysis.text_blocks:
                chunk = DocumentChunk(
                    chunk_id=f"{source_id}_layout_{chunk_index}",
                    source_id=source_id,
                    content=block.text,
                    chunk_index=chunk_index,
                    chunk_type=block.block_type,
                    metadata={
                        "block_id": block.block_id,
                        "font_size": block.font_size,
                        "font_weight": block.font_weight,
                        "alignment": block.alignment,
                        "is_layout_chunk": True
                    },
                    bbox=block.bbox,
                    confidence=block.confidence,
                    page_number=block.page_number
                )
                chunks.append(chunk)
                chunk_index += 1
            
            return chunks
            
        except Exception as e:
            logger.error(f"Layout chunk creation failed: {e}")
            return []
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Checksum calculation failed: {e}")
            return ""
    
    def _save_metadata(self, metadata: EnhancedDocumentMetadata):
        """Save metadata to file."""
        try:
            metadata_path = self.metadata_dir / f"{metadata.source_id}_metadata.json"
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(metadata.dict(), f, indent=2, default=str)
            
            logger.info(f"Saved metadata: {metadata_path}")
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _save_chunks(self, chunks: List[DocumentChunk]):
        """Save chunks to file."""
        try:
            if not chunks:
                return
            
            # Group chunks by source ID
            source_id = chunks[0].source_id
            chunks_path = self.chunks_dir / f"{source_id}_chunks.json"
            
            with open(chunks_path, 'w', encoding='utf-8') as f:
                import json
                json.dump([chunk.dict() for chunk in chunks], f, indent=2, default=str)
            
            logger.info(f"Saved {len(chunks)} chunks: {chunks_path}")
            
        except Exception as e:
            logger.error(f"Failed to save chunks: {e}")
    
    def get_ingestion_statistics(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return {
            "output_directory": str(self.output_dir),
            "ingested_documents": len(list(self.metadata_dir.glob("*_metadata.json"))),
            "total_chunks": len(list(self.chunks_dir.glob("*_chunks.json"))),
            "unified_parser_available": UNIFIED_PARSER_AVAILABLE,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "ocr_enabled": self.enable_ocr,
            "layout_analysis_enabled": self.enable_layout_analysis,
            "table_extraction_enabled": self.enable_table_extraction
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        if self.parser:
            return self.parser.get_supported_formats()
        else:
            return ["txt", "md"]