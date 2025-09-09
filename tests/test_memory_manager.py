"""
Tests for memory manager module.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from memory_manager import MemoryManager, MemoryEntry, RetrievalResult


class TestMemoryManager:
    """Test cases for MemoryManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def memory_manager(self, temp_dir):
        """Create a memory manager instance."""
        return MemoryManager(
            persist_directory=temp_dir,
            use_remote_embeddings=False
        )
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample document metadata."""
        from document_ingestor import DocumentMetadata
        return DocumentMetadata(
            source_id="test_source_123",
            original_filename="test.txt",
            file_type=".txt",
            file_size=1000,
            ingestion_timestamp="2024-01-01T00:00:00",
            chunk_count=3,
            checksum="test_checksum"
        )
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample document chunks."""
        from document_ingestor import DocumentChunk
        return [
            DocumentChunk(
                chunk_id="test_source_123_chunk_0",
                source_id="test_source_123",
                chunk_index=0,
                content="This is the first chunk of content.",
                metadata={"word_count": "7"},
                word_count=7,
                char_count=35
            ),
            DocumentChunk(
                chunk_id="test_source_123_chunk_1",
                source_id="test_source_123",
                chunk_index=1,
                content="This is the second chunk of content.",
                metadata={"word_count": "7"},
                word_count=7,
                char_count=36
            )
        ]
    
    @pytest.mark.asyncio
    async def test_store_document_chunks(self, memory_manager, sample_metadata, sample_chunks):
        """Test storing document chunks."""
        chunk_ids = await memory_manager.store_document_chunks(
            sample_metadata, sample_chunks, "test_agent"
        )
        
        assert len(chunk_ids) == len(sample_chunks)
        assert all(isinstance(chunk_id, str) for chunk_id in chunk_ids)
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks(self, memory_manager, sample_metadata, sample_chunks):
        """Test retrieving relevant chunks."""
        # Store chunks first
        await memory_manager.store_document_chunks(
            sample_metadata, sample_chunks, "test_agent"
        )
        
        # Retrieve chunks
        results = await memory_manager.retrieve_relevant_chunks(
            query="first chunk content",
            top_k=5
        )
        
        assert len(results) > 0
        assert all(isinstance(result, RetrievalResult) for result in results)
        assert all(result.score >= 0.0 for result in results)
    
    @pytest.mark.asyncio
    async def test_get_context_for_generation(self, memory_manager, sample_metadata, sample_chunks):
        """Test getting context for generation."""
        # Store chunks first
        await memory_manager.store_document_chunks(
            sample_metadata, sample_chunks, "test_agent"
        )
        
        # Get context
        context, results = await memory_manager.get_context_for_generation(
            query="test content",
            max_tokens=1000
        )
        
        assert isinstance(context, str)
        assert len(context) > 0
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_add_agent_notes(self, memory_manager):
        """Test adding agent notes."""
        content = "This is a test agent note."
        agent_id = "test_agent"
        tags = ["test", "note"]
        
        note_id = await memory_manager.add_agent_notes(
            content=content,
            agent_id=agent_id,
            tags=tags,
            provenance_notes="Test note"
        )
        
        assert isinstance(note_id, str)
        assert len(note_id) > 0
    
    @pytest.mark.asyncio
    async def test_search_by_tags(self, memory_manager):
        """Test searching by tags."""
        # Add some notes with tags
        await memory_manager.add_agent_notes(
            content="Test content 1",
            agent_id="test_agent",
            tags=["test", "content"]
        )
        
        await memory_manager.add_agent_notes(
            content="Test content 2",
            agent_id="test_agent",
            tags=["test", "example"]
        )
        
        # Search by tags
        results = await memory_manager.search_by_tags(["test"], top_k=10)
        
        assert len(results) >= 2
        assert all(isinstance(result, RetrievalResult) for result in results)
    
    def test_get_stats(self, memory_manager):
        """Test getting memory statistics."""
        stats = memory_manager.get_stats()
        
        assert isinstance(stats, dict)
        assert "total_chunks" in stats
        assert "collection_name" in stats
        assert stats["total_chunks"] >= 0
    
    @pytest.mark.asyncio
    async def test_generate_local_embedding(self, memory_manager):
        """Test generating local embeddings."""
        text = "This is a test text for embedding generation."
        
        embedding = await memory_manager._generate_local_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(dim, float) for dim in embedding)
    
    @pytest.mark.asyncio
    async def test_clear_memory(self, memory_manager, sample_metadata, sample_chunks):
        """Test clearing memory."""
        # Store some data first
        await memory_manager.store_document_chunks(
            sample_metadata, sample_chunks, "test_agent"
        )
        
        # Clear memory
        await memory_manager.clear_memory()
        
        # Check that memory is cleared
        stats = memory_manager.get_stats()
        assert stats["total_chunks"] == 0