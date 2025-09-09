"""
Unit tests for the MemoryManager module.
"""
import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from memory_manager import MemoryManager, MemoryEntry, RetrievalResult


class TestMemoryManager:
    """Test cases for MemoryManager functionality."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, memory_manager):
        """Test memory manager initialization."""
        assert memory_manager is not None
        assert memory_manager.vector_store is not None
    
    @pytest.mark.asyncio
    async def test_store_chunk(self, memory_manager):
        """Test storing a memory chunk."""
        chunk = MemoryEntry(
            source_id="test_source",
            chunk_id="test_chunk_001",
            original_filename="test.txt",
            ingestion_timestamp=datetime.now(),
            content="Test content for memory storage",
            metadata={"source": "test", "type": "document"}
        )
        
        result = await memory_manager.store_chunk(chunk)
        assert result is True
        
        # Verify chunk was stored
        retrieved = await memory_manager.get_chunk("test_chunk_001")
        assert retrieved is not None
        assert retrieved.content == chunk.content
    
    @pytest.mark.asyncio
    async def test_retrieve_chunks(self, memory_manager):
        """Test retrieving chunks by query."""
        # Store multiple chunks
        chunks = [
            MemoryEntry(
                source_id="test_source",
                chunk_id="chunk_001",
                original_filename="test.txt",
                ingestion_timestamp=datetime.now(),
                content="Machine learning algorithms",
                metadata={"topic": "AI", "type": "concept"}
            ),
            MemoryEntry(
                source_id="test_source",
                chunk_id="chunk_002",
                original_filename="test.txt",
                ingestion_timestamp=datetime.now(),
                content="Deep learning neural networks",
                metadata={"topic": "AI", "type": "concept"}
            ),
            MemoryEntry(
                source_id="test_source",
                chunk_id="chunk_003",
                original_filename="test.txt",
                ingestion_timestamp=datetime.now(),
                content="Data preprocessing techniques",
                metadata={"topic": "Data Science", "type": "method"}
            )
        ]
        
        for chunk in chunks:
            await memory_manager.store_chunk(chunk)
        
        # Test semantic search
        results = await memory_manager.search_chunks("artificial intelligence", limit=2)
        assert len(results) > 0
        assert any("machine learning" in result.content.lower() for result in results)
        
        # Test metadata filtering
        ai_results = await memory_manager.search_chunks(
            "learning", 
            metadata_filter={"topic": "AI"},
            limit=10
        )
        assert len(ai_results) == 2
    
    @pytest.mark.asyncio
    async def test_tag_management(self, memory_manager):
        """Test memory tag management."""
        # Create tags
        tag1 = MemoryTag(name="AI", description="Artificial Intelligence")
        tag2 = MemoryTag(name="ML", description="Machine Learning")
        
        await memory_manager.create_tag(tag1)
        await memory_manager.create_tag(tag2)
        
        # Test tag retrieval
        tags = await memory_manager.get_tags()
        assert len(tags) >= 2
        assert any(tag.name == "AI" for tag in tags)
        
        # Test tag search
        ai_tag = await memory_manager.get_tag("AI")
        assert ai_tag is not None
        assert ai_tag.name == "AI"
    
    @pytest.mark.asyncio
    async def test_provenance_tracking(self, memory_manager):
        """Test provenance tracking for memory chunks."""
        chunk = MemoryEntry(
            content="Test content with provenance",
            metadata={
                "source": "test_document.pdf",
                "page": 1,
                "author": "Test Author",
                "created_at": "2024-01-01T00:00:00Z"
            },
            chunk_id="provenance_test_001"
        )
        
        await memory_manager.store_chunk(chunk)
        
        # Test provenance retrieval
        retrieved = await memory_manager.get_chunk("provenance_test_001")
        assert retrieved.metadata["source"] == "test_document.pdf"
        assert retrieved.metadata["page"] == 1
        assert retrieved.metadata["author"] == "Test Author"
    
    @pytest.mark.asyncio
    async def test_memory_cleanup(self, memory_manager):
        """Test memory cleanup operations."""
        # Store test chunks
        for i in range(5):
            chunk = MemoryEntry(
                content=f"Test content {i}",
                metadata={"test": True, "index": i},
                chunk_id=f"cleanup_test_{i}"
            )
            await memory_manager.store_chunk(chunk)
        
        # Test cleanup by metadata
        cleaned = await memory_manager.cleanup_chunks(metadata_filter={"test": True})
        assert cleaned > 0
        
        # Verify chunks are removed
        for i in range(5):
            retrieved = await memory_manager.get_chunk(f"cleanup_test_{i}")
            assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_memory_statistics(self, memory_manager):
        """Test memory statistics collection."""
        # Store some chunks
        for i in range(3):
            chunk = MemoryEntry(
                content=f"Statistics test content {i}",
                metadata={"test": True},
                chunk_id=f"stats_test_{i}"
            )
            await memory_manager.store_chunk(chunk)
        
        # Get statistics
        stats = await memory_manager.get_memory_statistics()
        assert stats["total_chunks"] >= 3
        assert stats["total_size"] > 0
        assert "average_chunk_size" in stats
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, memory_manager):
        """Test concurrent memory operations."""
        async def store_chunk(index):
            chunk = MemoryEntry(
                content=f"Concurrent test content {index}",
                metadata={"concurrent": True, "index": index},
                chunk_id=f"concurrent_test_{index}"
            )
            return await memory_manager.store_chunk(chunk)
        
        # Run concurrent operations
        tasks = [store_chunk(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert all(results)
        
        # Verify all chunks were stored
        for i in range(10):
            retrieved = await memory_manager.get_chunk(f"concurrent_test_{i}")
            assert retrieved is not None
    
    @pytest.mark.asyncio
    async def test_error_handling(self, memory_manager):
        """Test error handling in memory operations."""
        # Test storing chunk with invalid data
        with pytest.raises(ValueError):
            await memory_manager.store_chunk(None)
        
        # Test retrieving non-existent chunk
        result = await memory_manager.get_chunk("nonexistent_chunk")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, memory_manager, performance_metrics):
        """Test performance metrics collection."""
        import time
        
        # Test storage performance
        start_time = time.time()
        chunk = MemoryEntry(
            content="Performance test content",
            metadata={"test": True},
            chunk_id="perf_test_001"
        )
        await memory_manager.store_chunk(chunk)
        storage_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        await memory_manager.get_chunk("perf_test_001")
        retrieval_time = time.time() - start_time
        
        performance_metrics["memory_storage_time"] = storage_time
        performance_metrics["memory_retrieval_time"] = retrieval_time
        
        assert storage_time > 0
        assert retrieval_time > 0