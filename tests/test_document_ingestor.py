"""
Unit tests for the DocumentIngestor module.
"""
import pytest
import asyncio
from pathlib import Path
from document_ingestor import DocumentIngestor, DocumentMetadata


class TestDocumentIngestor:
    """Test cases for DocumentIngestor functionality."""
    
    @pytest.mark.asyncio
    async def test_ingest_pdf_document(self, document_ingestor, sample_documents):
        """Test PDF document ingestion."""
        pdf_file = sample_documents["pdf"]
        
        # Test metadata extraction
        metadata = await document_ingestor._extract_pdf_metadata(pdf_file, DocumentMetadata())
        assert metadata.title is not None
        assert metadata.author is not None
        assert metadata.file_type == "pdf"
        
        # Test text extraction
        text = await document_ingestor._extract_pdf_text(pdf_file)
        assert len(text) > 0
        assert "machine learning" in text.lower()
        
        # Test full ingestion
        result = await document_ingestor.ingest_document(pdf_file)
        assert result is not None
        assert result["chunks_created"] > 0
    
    @pytest.mark.asyncio
    async def test_ingest_markdown_document(self, document_ingestor, sample_documents):
        """Test Markdown document ingestion."""
        md_file = sample_documents["markdown"]
        
        # Test metadata extraction
        metadata = await document_ingestor._extract_markdown_metadata(md_file, DocumentMetadata())
        assert metadata.title is not None
        assert metadata.file_type == "markdown"
        
        # Test text extraction
        text = await document_ingestor._extract_markdown_text(md_file)
        assert len(text) > 0
        assert "artificial intelligence" in text.lower()
        
        # Test full ingestion
        result = await document_ingestor.ingest_document(md_file)
        assert result is not None
        assert result["chunks_created"] > 0
    
    @pytest.mark.asyncio
    async def test_ingest_txt_document(self, document_ingestor, sample_documents):
        """Test TXT document ingestion."""
        txt_file = sample_documents["txt"]
        
        # Test metadata extraction
        metadata = await document_ingestor._extract_txt_metadata(txt_file, DocumentMetadata())
        assert metadata.title is not None
        assert metadata.file_type == "txt"
        
        # Test text extraction
        text = await document_ingestor._extract_txt_text(txt_file)
        assert len(text) > 0
        assert "data science" in text.lower()
        
        # Test full ingestion
        result = await document_ingestor.ingest_document(txt_file)
        assert result is not None
        assert result["chunks_created"] > 0
    
    @pytest.mark.asyncio
    async def test_batch_ingestion(self, document_ingestor, sample_documents):
        """Test batch document ingestion."""
        files = list(sample_documents.values())
        
        results = await document_ingestor.ingest_documents(files)
        assert len(results) == len(files)
        
        for result in results:
            assert result["success"] is True
            assert result["chunks_created"] > 0
    
    @pytest.mark.asyncio
    async def test_unsupported_file_type(self, document_ingestor, temp_dir):
        """Test handling of unsupported file types."""
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("Test content")
        
        with pytest.raises(ValueError):
            await document_ingestor.ingest_document(unsupported_file)
    
    @pytest.mark.asyncio
    async def test_nonexistent_file(self, document_ingestor):
        """Test handling of nonexistent files."""
        nonexistent_file = Path("nonexistent_file.pdf")
        
        with pytest.raises(FileNotFoundError):
            await document_ingestor.ingest_document(nonexistent_file)
    
    @pytest.mark.asyncio
    async def test_chunking_strategy(self, document_ingestor, sample_documents):
        """Test document chunking strategy."""
        md_file = sample_documents["markdown"]
        
        # Test chunking with different strategies
        chunks = await document_ingestor._chunk_text("Test content for chunking. " * 100)
        assert len(chunks) > 1
        
        # Test chunk overlap
        chunked_text = " ".join(chunks)
        assert len(chunked_text) > 0
    
    @pytest.mark.asyncio
    async def test_metadata_extraction(self, document_ingestor, sample_documents):
        """Test metadata extraction from different file types."""
        for file_type, file_path in sample_documents.items():
            metadata = DocumentMetadata()
            metadata = await document_ingestor._extract_metadata(file_path, metadata)
            
            assert metadata.title is not None
            assert metadata.file_type == file_type
            assert metadata.file_path == str(file_path)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, document_ingestor, temp_dir):
        """Test error handling in document ingestion."""
        # Test corrupted file
        corrupted_file = temp_dir / "corrupted.pdf"
        corrupted_file.write_text("This is not a valid PDF")
        
        with pytest.raises(Exception):
            await document_ingestor.ingest_document(corrupted_file)
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, document_ingestor, sample_documents, performance_metrics):
        """Test performance metrics collection."""
        import time
        
        start_time = time.time()
        result = await document_ingestor.ingest_document(sample_documents["pdf"])
        end_time = time.time()
        
        processing_time = end_time - start_time
        performance_metrics["document_processing_time"] = processing_time
        
        assert processing_time > 0
        assert result["processing_time"] > 0