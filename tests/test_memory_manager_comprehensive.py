"""
Comprehensive tests for the memory manager module.
Tests all memory operations, RAG pipeline, and integration scenarios.
"""
import pytest
import os
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys
from datetime import datetime

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory_manager import MemoryManager, MemoryEntry, RetrievalResult
from document_ingestor import DocumentMetadata, DocumentChunk


class TestMemoryManagerCore:
    """Test core memory manager functionality."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    def test_memory_manager_initialization(self, memory_manager):
        """Test memory manager initialization."""
        assert memory_manager is not None
        assert hasattr(memory_manager, 'collection')
        assert hasattr(memory_manager, 'client')
        assert hasattr(memory_manager, 'persist_directory')
    
    def test_memory_manager_configuration(self, memory_manager):
        """Test memory manager configuration."""
        assert memory_manager.persist_directory is not None
        assert memory_manager.collection is not None
        assert memory_manager.embedding_model is not None
    
    def test_memory_manager_stats(self, memory_manager):
        """Test memory manager statistics."""
        stats = memory_manager.get_stats()
        assert isinstance(stats, dict)
        assert 'total_chunks' in stats
        assert 'collection_name' in stats


class TestMemoryEntry:
    """Test memory entry functionality."""
    
    def test_memory_entry_creation(self):
        """Test memory entry creation."""
        entry = MemoryEntry(
            source_id="test_source",
            chunk_id="test_chunk",
            original_filename="test.pdf",
            ingestion_timestamp=datetime.now(),
            content="Test content",
            metadata={"key": "value"}
        )
        
        assert entry.source_id == "test_source"
        assert entry.chunk_id == "test_chunk"
        assert entry.original_filename == "test.pdf"
        assert entry.content == "Test content"
        assert entry.metadata == {"key": "value"}
    
    def test_memory_entry_validation(self):
        """Test memory entry validation."""
        # Test valid entry
        entry = MemoryEntry(
            source_id="test_source",
            chunk_id="test_chunk",
            original_filename="test.pdf",
            ingestion_timestamp=datetime.now(),
            content="Test content"
        )
        
        assert entry.source_id == "test_source"
        assert entry.chunk_id == "test_chunk"
        
        # Test invalid entry (missing required fields)
        with pytest.raises(Exception):
            MemoryEntry(
                source_id="test_source"
            )
    
    def test_memory_entry_metadata(self):
        """Test memory entry metadata handling."""
        entry = MemoryEntry(
            source_id="test_source",
            chunk_id="test_chunk",
            original_filename="test.pdf",
            ingestion_timestamp=datetime.now(),
            content="Test content",
            metadata={
                "page_number": "1",
                "tags": "important,reference",
                "confidence": "0.95"
            }
        )
        
        assert entry.metadata["page_number"] == "1"
        assert entry.metadata["tags"] == "important,reference"
        assert entry.metadata["confidence"] == "0.95"


class TestRetrievalResult:
    """Test retrieval result functionality."""
    
    def test_retrieval_result_creation(self):
        """Test retrieval result creation."""
        result = RetrievalResult(
            content="Test content",
            chunk_id="test_chunk",
            source_id="test_source",
            score=0.95,
            metadata={"key": "value"}
        )
        
        assert result.content == "Test content"
        assert result.chunk_id == "test_chunk"
        assert result.source_id == "test_source"
        assert result.score == 0.95
        assert result.metadata == {"key": "value"}
    
    def test_retrieval_result_validation(self):
        """Test retrieval result validation."""
        # Test valid result
        result = RetrievalResult(
            content="Test content",
            chunk_id="test_chunk",
            source_id="test_source",
            score=0.95
        )
        
        assert result.content == "Test content"
        assert result.score == 0.95
        
        # Test invalid result (missing required fields)
        with pytest.raises(Exception):
            RetrievalResult(
                content="Test content"
            )


class TestDocumentStorage:
    """Test document storage functionality."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample document metadata."""
        return DocumentMetadata(
            source_id="test_source",
            original_filename="test.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=2,
            checksum="test_checksum"
        )
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample document chunks."""
        return [
            DocumentChunk(
                chunk_id="chunk_1",
                source_id="test_source",
                chunk_index=0,
                content="First chunk content",
                metadata={"chunk_index": "0"},
                word_count=3,
                char_count=20
            ),
            DocumentChunk(
                chunk_id="chunk_2",
                source_id="test_source",
                chunk_index=1,
                content="Second chunk content",
                metadata={"chunk_index": "1"},
                word_count=3,
                char_count=21
            )
        ]
    
    @pytest.mark.asyncio
    async def test_store_document_chunks(self, memory_manager, sample_metadata, sample_chunks):
        """Test storing document chunks."""
        result = await memory_manager.store_document_chunks(sample_metadata, sample_chunks)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert "chunk_1" in result
        assert "chunk_2" in result
    
    @pytest.mark.asyncio
    async def test_store_single_chunk(self, memory_manager, sample_metadata):
        """Test storing a single chunk."""
        chunk = DocumentChunk(
            chunk_id="single_chunk",
            source_id="test_source",
            chunk_index=0,
            content="Single chunk content",
            metadata={"chunk_index": "0"},
            word_count=3,
            char_count=20
        )
        
        result = await memory_manager.store_document_chunks(sample_metadata, [chunk])
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert "single_chunk" in result
    
    @pytest.mark.asyncio
    async def test_store_empty_chunks(self, memory_manager, sample_metadata):
        """Test storing empty chunks list."""
        result = await memory_manager.store_document_chunks(sample_metadata, [])
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestDocumentRetrieval:
    """Test document retrieval functionality."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    @pytest.fixture
    def populated_memory_manager(self, memory_manager):
        """Create memory manager with test data."""
        async def _populate():
            metadata = DocumentMetadata(
                source_id="test_source",
                original_filename="test.pdf",
                file_type=".pdf",
                file_size=100,
                ingestion_timestamp=datetime.now(),
                chunk_count=2,
                checksum="test_checksum"
            )
            
            chunks = [
                DocumentChunk(
                    chunk_id="chunk_1",
                    source_id="test_source",
                    chunk_index=0,
                    content="First chunk about artificial intelligence",
                    metadata={"chunk_index": "0"},
                    word_count=5,
                    char_count=40
                ),
                DocumentChunk(
                    chunk_id="chunk_2",
                    source_id="test_source",
                    chunk_index=1,
                    content="Second chunk about machine learning",
                    metadata={"chunk_index": "1"},
                    word_count=5,
                    char_count=40
                )
            ]
            
            await memory_manager.store_document_chunks(metadata, chunks)
            return memory_manager
        
        return _populate
    
    @pytest.mark.asyncio
    async def test_retrieve_relevant_chunks(self, populated_memory_manager):
        """Test retrieving relevant chunks."""
        memory_manager = await populated_memory_manager()
        results = await memory_manager.retrieve_relevant_chunks("artificial intelligence")
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(result, RetrievalResult) for result in results)
        assert any("artificial intelligence" in result.content for result in results)
    
    @pytest.mark.asyncio
    async def test_retrieve_with_filters(self, populated_memory_manager):
        """Test retrieving with metadata filters."""
        memory_manager = await populated_memory_manager()
        results = await memory_manager.retrieve_relevant_chunks(
            "machine learning",
            filter_metadata={"chunk_index": "1"}
        )
        
        assert isinstance(results, list)
        # Should find the second chunk
        assert any("machine learning" in result.content for result in results)
    
    @pytest.mark.asyncio
    async def test_retrieve_empty_database(self, memory_manager):
        """Test retrieving from empty database."""
        results = await memory_manager.retrieve_relevant_chunks("test query")
        
        assert isinstance(results, list)
        assert len(results) == 0


class TestRAGPipeline:
    """Test RAG pipeline functionality."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_rag_pipeline(self, memory_manager):
        """Test complete RAG pipeline."""
        # Create knowledge chunks
        metadata = DocumentMetadata(
            source_id="knowledge_source",
            original_filename="knowledge.pdf",
            file_type=".pdf",
            file_size=200,
            ingestion_timestamp=datetime.now(),
            chunk_count=3,
            checksum="knowledge_checksum"
        )
        
        knowledge_chunks = [
            DocumentChunk(
                chunk_id="knowledge_1",
                source_id="knowledge_source",
                chunk_index=0,
                content="Knowledge about artificial intelligence and its applications",
                metadata={"chunk_index": "0"},
                word_count=8,
                char_count=60
            ),
            DocumentChunk(
                chunk_id="knowledge_2",
                source_id="knowledge_source",
                chunk_index=1,
                content="Information about machine learning algorithms and techniques",
                metadata={"chunk_index": "1"},
                word_count=7,
                char_count=65
            )
        ]
        
        # Store knowledge
        await memory_manager.store_document_chunks(metadata, knowledge_chunks)
        
        # Retrieve relevant context
        results = await memory_manager.retrieve_relevant_chunks("AI applications")
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert any("artificial intelligence" in result.content for result in results)
    
    @pytest.mark.asyncio
    async def test_context_assembly(self, memory_manager):
        """Test context assembly for generation."""
        # Store test chunks
        metadata = DocumentMetadata(
            source_id="context_source",
            original_filename="context.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=2,
            checksum="context_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id="context_1",
                source_id="context_source",
                chunk_index=0,
                content="Context about data science and analytics",
                metadata={"chunk_index": "0", "relevance": "0.9"},
                word_count=6,
                char_count=40
            )
        ]
        
        await memory_manager.store_document_chunks(metadata, chunks)
        
        # Get context for generation
        context, results = await memory_manager.get_context_for_generation("data science")
        
        assert isinstance(context, str)
        assert isinstance(results, list)
        assert "data science" in context
    
    @pytest.mark.asyncio
    async def test_context_length_management(self, memory_manager):
        """Test context length management."""
        # Store multiple chunks
        metadata = DocumentMetadata(
            source_id="length_source",
            original_filename="length.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=5,
            checksum="length_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id=f"length_{i}",
                source_id="length_source",
                chunk_index=i,
                content=f"Chunk {i} content for length testing",
                metadata={"chunk_index": str(i)},
                word_count=5,
                char_count=30
            )
            for i in range(5)
        ]
        
        await memory_manager.store_document_chunks(metadata, chunks)
        
        # Test with different top_k values
        results_3 = await memory_manager.retrieve_relevant_chunks("testing", top_k=3)
        results_5 = await memory_manager.retrieve_relevant_chunks("testing", top_k=5)
        
        assert len(results_3) <= 3
        assert len(results_5) <= 5


class TestMemoryOperations:
    """Test memory operations."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    @pytest.mark.asyncio
    async def test_add_agent_notes(self, memory_manager):
        """Test adding agent notes."""
        result = await memory_manager.add_agent_notes(
            content="Agent note about the process",
            agent_id="research_agent",
            tags=["important", "process"],
            provenance_notes="Test note for process documentation"
        )
        
        assert result is not None
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_search_by_tags(self, memory_manager):
        """Test searching by tags."""
        # Store chunks with tags
        metadata = DocumentMetadata(
            source_id="tagged_source",
            original_filename="tagged.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=2,
            checksum="tagged_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id="tagged_1",
                source_id="tagged_source",
                chunk_index=0,
                content="Content about AI and technology",
                metadata={"chunk_index": "0", "tags": "AI,technology,important"},
                word_count=5,
                char_count=35
            )
        ]
        
        await memory_manager.store_document_chunks(metadata, chunks)
        
        # Search by tags (ChromaDB stores tags as comma-separated string in metadata)
        results = await memory_manager.retrieve_relevant_chunks(
            "AI technology"
        )
        
        assert isinstance(results, list)
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_get_stats(self, memory_manager):
        """Test getting memory statistics."""
        # Store some chunks first
        metadata = DocumentMetadata(
            source_id="stats_source",
            original_filename="stats.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=2,
            checksum="stats_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id="stats_1",
                source_id="stats_source",
                chunk_index=0,
                content="Stats test content",
                metadata={"chunk_index": "0"},
                word_count=3,
                char_count=18
            )
        ]
        
        await memory_manager.store_document_chunks(metadata, chunks)
        
        stats = memory_manager.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_chunks' in stats
        assert stats['total_chunks'] >= 1
    
    @pytest.mark.asyncio
    async def test_clear_memory(self, memory_manager):
        """Test clearing memory."""
        # Store some chunks first
        metadata = DocumentMetadata(
            source_id="clear_source",
            original_filename="clear.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=1,
            checksum="clear_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id="clear_1",
                source_id="clear_source",
                chunk_index=0,
                content="Clear test content",
                metadata={"chunk_index": "0"},
                word_count=3,
                char_count=18
            )
        ]
        
        await memory_manager.store_document_chunks(metadata, chunks)
        
        # Clear memory
        await memory_manager.clear_memory()
        
        # Verify memory is cleared
        stats = memory_manager.get_stats()
        assert stats['total_chunks'] == 0


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    @pytest.mark.asyncio
    async def test_invalid_chunk_data(self, memory_manager):
        """Test handling of invalid chunk data."""
        # Test with None metadata and chunks - should return empty list
        result = await memory_manager.store_document_chunks(None, None)
        assert result == []
    
    @pytest.mark.asyncio
    async def test_retrieval_with_invalid_query(self, memory_manager):
        """Test retrieval with invalid query."""
        # Test with empty query
        results = await memory_manager.retrieve_relevant_chunks("")
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_retrieval_with_invalid_parameters(self, memory_manager):
        """Test retrieval with invalid parameters."""
        # Test with negative top_k - should raise an exception
        with pytest.raises(Exception):
            await memory_manager.retrieve_relevant_chunks("test", top_k=-1)


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    @pytest.mark.asyncio
    async def test_large_document_handling(self, memory_manager):
        """Test handling of large documents."""
        # Create a large document with many chunks
        metadata = DocumentMetadata(
            source_id="large_source",
            original_filename="large.pdf",
            file_type=".pdf",
            file_size=10000,
            ingestion_timestamp=datetime.now(),
            chunk_count=100,
            checksum="large_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id=f"large_{i}",
                source_id="large_source",
                chunk_index=i,
                content=f"Large document chunk {i} with substantial content",
                metadata={"chunk_index": str(i), "size": str(7)},
                word_count=6,
                char_count=50
            )
            for i in range(50)  # Create 50 chunks
        ]
        
        result = await memory_manager.store_document_chunks(metadata, chunks)
        
        assert isinstance(result, list)
        assert len(result) == 50
    
    @pytest.mark.asyncio
    async def test_retrieval_performance(self, memory_manager):
        """Test retrieval performance."""
        # Store test data
        metadata = DocumentMetadata(
            source_id="perf_source",
            original_filename="perf.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=10,
            checksum="perf_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id=f"perf_{i}",
                source_id="perf_source",
                chunk_index=i,
                content=f"Performance test chunk {i}",
                metadata={"chunk_index": str(i)},
                word_count=4,
                char_count=25
            )
            for i in range(10)
        ]
        
        await memory_manager.store_document_chunks(metadata, chunks)
        
        # Test retrieval performance
        import time
        start_time = time.time()
        results = await memory_manager.retrieve_relevant_chunks("performance test")
        end_time = time.time()
        
        assert isinstance(results, list)
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, memory_manager):
        """Test concurrent memory operations."""
        async def store_chunks(i):
            metadata = DocumentMetadata(
                source_id=f"concurrent_{i}",
                original_filename=f"concurrent_{i}.pdf",
                file_type=".pdf",
                file_size=100,
                ingestion_timestamp=datetime.now(),
                chunk_count=1,
                checksum=f"concurrent_checksum_{i}"
            )
            
            chunks = [
                DocumentChunk(
                    chunk_id=f"concurrent_{i}_1",
                    source_id=f"concurrent_{i}",
                    chunk_index=0,
                    content=f"Concurrent test chunk {i}",
                    metadata={"chunk_index": "0", "concurrent_test": "true"},
                    word_count=4,
                    char_count=25
                )
            ]
            
            return await memory_manager.store_document_chunks(metadata, chunks)
        
        # Run concurrent operations
        tasks = [store_chunks(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(isinstance(result, list) for result in results)


class TestIntegration:
    """Test integration with other components."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield MemoryManager(persist_directory=temp_dir)
    
    @pytest.mark.asyncio
    async def test_llm_client_integration(self, memory_manager):
        """Test integration with LLM client."""
        # Store test content
        metadata = DocumentMetadata(
            source_id="llm_source",
            original_filename="llm.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=1,
            checksum="llm_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id="llm_1",
                source_id="llm_source",
                chunk_index=0,
                content="Test content for LLM integration",
                metadata={"chunk_index": "0"},
                word_count=5,
                char_count=30
            )
        ]
        
        await memory_manager.store_document_chunks(metadata, chunks)
        
        # Get context for LLM
        context, results = await memory_manager.get_context_for_generation("LLM integration")
        
        assert isinstance(context, str)
        assert isinstance(results, list)
        assert "Test content for LLM" in context
    
    @pytest.mark.asyncio
    async def test_agent_integration(self, memory_manager):
        """Test integration with agents."""
        # Store agent notes
        result = await memory_manager.add_agent_notes(
            content="Agent note for integration testing",
            agent_id="test_agent",
            tags=["integration", "test"],
            provenance_notes="Integration test note"
        )
        
        assert result is not None
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_document_ingestor_integration(self, memory_manager):
        """Test integration with document ingestor."""
        # Simulate document ingestor output
        metadata = DocumentMetadata(
            source_id="ingestor_source",
            original_filename="ingestor.pdf",
            file_type=".pdf",
            file_size=100,
            ingestion_timestamp=datetime.now(),
            chunk_count=2,
            checksum="ingestor_checksum"
        )
        
        chunks = [
            DocumentChunk(
                chunk_id="ingestor_1",
                source_id="ingestor_source",
                chunk_index=0,
                content="Document ingestor test content",
                metadata={"chunk_index": "0"},
                word_count=4,
                char_count=30
            )
        ]
        
        result = await memory_manager.store_document_chunks(metadata, chunks)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert "ingestor_1" in result