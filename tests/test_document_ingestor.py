"""
Tests for document ingestor module.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from document_ingestor import DocumentIngestor, DocumentMetadata, DocumentChunk


class TestDocumentIngestor:
    """Test cases for DocumentIngestor."""
    
    @pytest.fixture
    def ingestor(self):
        """Create a document ingestor instance."""
        return DocumentIngestor(chunk_size=500, chunk_overlap=100)
    
    @pytest.fixture
    def sample_text_file(self):
        """Create a sample text file for testing."""
        content = """
        This is a sample document for testing the document ingestor.
        It contains multiple paragraphs with various content.
        
        The document should be chunked appropriately based on the chunk size.
        Each chunk should have proper metadata and identifiers.
        
        This is the third paragraph with more content to test chunking.
        The ingestor should handle different types of content properly.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            return f.name
    
    @pytest.mark.asyncio
    async def test_ingest_text_file(self, ingestor, sample_text_file):
        """Test ingesting a text file."""
        metadata, chunks = await ingestor.ingest_document(sample_text_file)
        
        assert isinstance(metadata, DocumentMetadata)
        assert metadata.original_filename == Path(sample_text_file).name
        assert metadata.file_type == '.txt'
        assert metadata.chunk_count == len(chunks)
        assert len(chunks) > 0
        
        for chunk in chunks:
            assert isinstance(chunk, DocumentChunk)
            assert chunk.source_id == metadata.source_id
            assert len(chunk.content) > 0
            assert chunk.word_count > 0
    
    @pytest.mark.asyncio
    async def test_chunk_content(self, ingestor):
        """Test content chunking functionality."""
        content = "This is a test content. " * 100  # Create long content
        source_id = "test_source"
        
        chunks = await ingestor._chunk_content(content, source_id)
        
        assert len(chunks) > 1  # Should be chunked
        assert all(chunk.source_id == source_id for chunk in chunks)
        assert all(len(chunk.content) <= ingestor.chunk_size for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_generate_source_id(self, ingestor):
        """Test source ID generation."""
        test_path = Path("/tmp/test_file.txt")
        source_id = ingestor._generate_source_id(test_path)
        
        assert isinstance(source_id, str)
        assert len(source_id) == 16  # SHA-256 first 16 chars
    
    @pytest.mark.asyncio
    async def test_calculate_checksum(self, ingestor, sample_text_file):
        """Test checksum calculation."""
        checksum = await ingestor._calculate_checksum(Path(sample_text_file))
        
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 hex length
    
    def test_split_into_sentences(self, ingestor):
        """Test sentence splitting."""
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = ingestor._split_into_sentences(text)
        
        assert len(sentences) == 4
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
    
    def test_create_chunk(self, ingestor):
        """Test chunk creation."""
        content = "This is test content for chunking."
        source_id = "test_source"
        chunk_index = 0
        
        chunk = ingestor._create_chunk(content, source_id, chunk_index)
        
        assert isinstance(chunk, DocumentChunk)
        assert chunk.chunk_id == f"{source_id}_chunk_{chunk_index}"
        assert chunk.content == content.strip()
        assert chunk.source_id == source_id
        assert chunk.chunk_index == chunk_index
    
    @pytest.mark.asyncio
    async def test_ingest_nonexistent_file(self, ingestor):
        """Test ingesting a non-existent file."""
        with pytest.raises(FileNotFoundError):
            await ingestor.ingest_document("/nonexistent/file.txt")
    
    @pytest.mark.asyncio
    async def test_ingest_unsupported_format(self, ingestor):
        """Test ingesting an unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"test content")
            f.flush()
            
            with pytest.raises(ValueError):
                await ingestor.ingest_document(f.name)
    
    def test_cleanup(self, sample_text_file):
        """Clean up test files."""
        Path(sample_text_file).unlink(missing_ok=True)