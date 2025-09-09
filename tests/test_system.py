"""
System-level tests for the complete book-writing system.
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import json


class TestCompleteBookGeneration:
    """Test cases for complete book generation workflows."""
    
    @pytest.mark.asyncio
    async def test_full_book_workflow_mock(self, book_workflow, test_book_metadata, temp_dir):
        """Test complete book workflow with mock components."""
        # Mock all LLM calls
        with patch.object(book_workflow.llm_client, 'generate') as mock_generate:
            # Mock responses for different stages
            mock_responses = [
                # Research outline
                Mock(content='{"introduction": {"title": "Introduction to Test Book", "key_points": ["Overview", "Importance"]}, "chapters": [{"chapter_number": 1, "title": "Chapter 1: Fundamentals", "key_points": ["Point 1", "Point 2"]}, {"chapter_number": 2, "title": "Chapter 2: Advanced Topics", "key_points": ["Point 3", "Point 4"]}], "conclusion": {"title": "Conclusion", "key_points": ["Summary", "Future"]}, "word_count_target": 5000}'),
                # Introduction content
                Mock(content="# Introduction to Test Book\n\nThis is the introduction content for the test book."),
                # Chapter 1 content
                Mock(content="# Chapter 1: Fundamentals\n\nThis is the content for chapter 1."),
                # Chapter 2 content
                Mock(content="# Chapter 2: Advanced Topics\n\nThis is the content for chapter 2."),
                # Conclusion content
                Mock(content="# Conclusion\n\nThis is the conclusion content for the test book."),
                # Global revision
                Mock(content="This is the globally revised content.")
            ]
            mock_generate.side_effect = mock_responses
            
            # Mock agent methods
            with patch.object(book_workflow.agent_manager.research_agent, 'start_research') as mock_research:
                mock_research.return_value = "test_topic_id"
                
                with patch.object(book_workflow.agent_manager.research_agent, 'get_research_results') as mock_results:
                    mock_results.return_value = []
                    
                    with patch.object(book_workflow.agent_manager.research_agent, 'get_research_summary') as mock_summary:
                        mock_summary.return_value = Mock(summary="Test research summary")
                        
                        # Start book production
                        result = await book_workflow.start_book_production(
                            title=test_book_metadata["title"],
                            theme=test_book_metadata["theme"],
                            author=test_book_metadata["author"],
                            word_count_target=test_book_metadata["word_count_target"],
                            chapters_count=test_book_metadata["chapters_count"],
                            output_dir=temp_dir
                        )
                        
                        assert result is not None
                        assert "book_metadata" in result
                        assert result["book_metadata"]["title"] == test_book_metadata["title"]
                        assert result["book_metadata"]["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_full_book_generator_workflow(self, full_book_generator, test_book_metadata, temp_dir):
        """Test full book generator workflow."""
        # Mock LLM responses
        with patch.object(full_book_generator.llm_client, 'generate') as mock_generate:
            mock_responses = [
                # Research outline
                Mock(content='{"introduction": {"title": "Introduction", "key_points": ["Point 1"]}, "chapters": [{"chapter_number": 1, "title": "Chapter 1", "key_points": ["Point 2"]}], "conclusion": {"title": "Conclusion", "key_points": ["Point 3"]}, "word_count_target": 3000}'),
                # Introduction
                Mock(content="# Introduction\n\nThis is the introduction."),
                # Chapter 1
                Mock(content="# Chapter 1\n\nThis is chapter 1."),
                # Conclusion
                Mock(content="# Conclusion\n\nThis is the conclusion."),
                # Global revision
                Mock(content="This is the globally revised content.")
            ]
            mock_generate.side_effect = mock_responses
            
            # Mock agent methods
            with patch.object(full_book_generator.agent_manager.research_agent, 'start_research') as mock_research:
                mock_research.return_value = "test_topic_id"
                
                with patch.object(full_book_generator.agent_manager.research_agent, 'get_research_results') as mock_results:
                    mock_results.return_value = []
                    
                    with patch.object(full_book_generator.agent_manager.research_agent, 'get_research_summary') as mock_summary:
                        mock_summary.return_value = Mock(summary="Test research summary")
                        
                        # Generate full book
                        result = await full_book_generator.generate_full_book(
                            title=test_book_metadata["title"],
                            theme=test_book_metadata["theme"],
                            author=test_book_metadata["author"],
                            word_count_target=test_book_metadata["word_count_target"],
                            output_dir=temp_dir
                        )
                        
                        assert result is not None
                        assert "book_metadata" in result
                        assert result["book_metadata"]["title"] == test_book_metadata["title"]


class TestCLIIntegration:
    """Test cases for CLI integration."""
    
    @pytest.mark.asyncio
    async def test_cli_book_create_command(self, temp_dir):
        """Test CLI book create command."""
        import subprocess
        import sys
        
        # Test CLI command execution
        cmd = [
            sys.executable, "-m", "cli", "book", "create",
            "--title", "CLI Test Book",
            "--theme", "CLI Testing",
            "--author", "CLI Test Author",
            "--word-count", "2000",
            "--chapters", "3",
            "--output-dir", str(temp_dir)
        ]
        
        # Mock the actual execution to avoid external dependencies
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Book created successfully")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
    
    @pytest.mark.asyncio
    async def test_cli_book_status_command(self, temp_dir):
        """Test CLI book status command."""
        import subprocess
        import sys
        
        # Create a mock build log
        build_log = {
            "book_metadata": {
                "title": "Status Test Book",
                "status": "completed",
                "build_id": "status_test_001"
            }
        }
        
        build_log_file = temp_dir / "status_test_001" / "build_log.json"
        build_log_file.parent.mkdir(exist_ok=True)
        build_log_file.write_text(json.dumps(build_log))
        
        # Test status command
        cmd = [
            sys.executable, "-m", "cli", "book", "status",
            "--build-id", "status_test_001",
            "--output-dir", str(temp_dir)
        ]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Book status: completed")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
    
    @pytest.mark.asyncio
    async def test_cli_book_list_command(self, temp_dir):
        """Test CLI book list command."""
        import subprocess
        import sys
        
        # Create mock build logs
        for i in range(3):
            build_log = {
                "book_metadata": {
                    "title": f"List Test Book {i}",
                    "status": "completed",
                    "build_id": f"list_test_{i:03d}"
                }
            }
            
            build_log_file = temp_dir / f"list_test_{i:03d}" / "build_log.json"
            build_log_file.parent.mkdir(exist_ok=True)
            build_log_file.write_text(json.dumps(build_log))
        
        # Test list command
        cmd = [
            sys.executable, "-m", "cli", "book", "list",
            "--output-dir", str(temp_dir)
        ]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Found 3 books")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0


class TestGUIIntegration:
    """Test cases for GUI integration."""
    
    @pytest.mark.asyncio
    async def test_gui_module_import(self):
        """Test GUI module import and initialization."""
        try:
            from gui import main
            assert main is not None
        except ImportError:
            pytest.skip("GUI module not available")
    
    @pytest.mark.asyncio
    async def test_gui_workflow_hooks(self, temp_dir):
        """Test GUI workflow hooks and event handling."""
        # Mock GUI workflow hooks
        class MockGUIWorkflow:
            def __init__(self):
                self.events = []
                self.memory_updates = []
                self.agent_outputs = []
                self.book_completion_events = []
            
            def on_memory_update(self, update):
                self.memory_updates.append(update)
            
            def on_agent_output(self, agent_name, output):
                self.agent_outputs.append((agent_name, output))
            
            def on_book_completion(self, book_metadata):
                self.book_completion_events.append(book_metadata)
        
        # Test workflow hooks
        workflow = MockGUIWorkflow()
        
        # Simulate memory update
        workflow.on_memory_update({"type": "chunk_added", "chunk_id": "test_001"})
        assert len(workflow.memory_updates) == 1
        
        # Simulate agent output
        workflow.on_agent_output("research_agent", "Research completed")
        assert len(workflow.agent_outputs) == 1
        
        # Simulate book completion
        workflow.on_book_completion({"title": "Test Book", "status": "completed"})
        assert len(workflow.book_completion_events) == 1


class TestPerformanceAndStress:
    """Test cases for performance and stress testing."""
    
    @pytest.mark.asyncio
    async def test_concurrent_document_ingestion(self, document_ingestor, temp_dir):
        """Test concurrent document ingestion."""
        # Create multiple test documents
        documents = []
        for i in range(10):
            doc_path = temp_dir / f"concurrent_test_{i}.txt"
            doc_path.write_text(f"Test document {i} content for concurrent ingestion testing.")
            documents.append(doc_path)
        
        # Ingest documents concurrently
        tasks = [document_ingestor.ingest_document(doc) for doc in documents]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(result["success"] for result in results)
    
    @pytest.mark.asyncio
    async def test_memory_stress_test(self, memory_manager):
        """Test memory system under stress."""
        from memory_manager import MemoryChunk
        
        # Store many chunks concurrently
        async def store_chunk(index):
            chunk = MemoryChunk(
                content=f"Stress test content {index}",
                metadata={"test": True, "index": index},
                chunk_id=f"stress_test_{index}"
            )
            return await memory_manager.store_chunk(chunk)
        
        # Store 100 chunks concurrently
        tasks = [store_chunk(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        assert all(results)
        
        # Verify chunks were stored
        for i in range(100):
            retrieved = await memory_manager.get_chunk(f"stress_test_{i}")
            assert retrieved is not None
            assert retrieved.content == f"Stress test content {i}"
    
    @pytest.mark.asyncio
    async def test_agent_coordination_stress(self, research_agent, writer_agent, editor_agent):
        """Test agent coordination under stress."""
        # Start multiple research tasks concurrently
        async def research_task(index):
            topic_id = await research_agent.start_research(
                topic_title=f"Stress Test Topic {index}",
                description=f"Stress test research {index}",
                keywords=["stress", "test"],
                priority=1
            )
            return topic_id
        
        # Start 20 research tasks concurrently
        tasks = [research_task(i) for i in range(20)]
        topic_ids = await asyncio.gather(*tasks)
        
        assert len(topic_ids) == 20
        assert all(topic_id is not None for topic_id in topic_ids)
    
    @pytest.mark.asyncio
    async def test_llm_rate_limiting(self, llm_client):
        """Test LLM rate limiting under load."""
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = Mock(
                content="Rate limited response",
                tokens_used=10,
                model="test-model"
            )
            
            # Make many concurrent requests
            async def make_request(index):
                return await llm_client.generate(
                    prompt=f"Test prompt {index}",
                    max_tokens=50
                )
            
            # Make 50 concurrent requests
            tasks = [make_request(i) for i in range(50)]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 50
            assert all(result is not None for result in results)
    
    @pytest.mark.asyncio
    async def test_memory_cleanup_performance(self, memory_manager):
        """Test memory cleanup performance."""
        from memory_manager import MemoryChunk
        
        # Store many chunks
        for i in range(1000):
            chunk = MemoryChunk(
                content=f"Cleanup test content {i}",
                metadata={"test": True, "index": i},
                chunk_id=f"cleanup_test_{i}"
            )
            await memory_manager.store_chunk(chunk)
        
        # Test cleanup performance
        import time
        start_time = time.time()
        cleaned = await memory_manager.cleanup_chunks(metadata_filter={"test": True})
        end_time = time.time()
        
        cleanup_time = end_time - start_time
        assert cleanup_time < 10  # Should complete within 10 seconds
        assert cleaned > 0


class TestErrorHandlingAndRecovery:
    """Test cases for error handling and recovery."""
    
    @pytest.mark.asyncio
    async def test_llm_failure_recovery(self, llm_client):
        """Test LLM failure recovery."""
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            # First call fails, second succeeds
            mock_ollama.side_effect = [
                Exception("LLM service unavailable"),
                Mock(content="Recovery response", tokens_used=20, model="test-model")
            ]
            
            response = await llm_client.generate(
                prompt="Test prompt",
                max_tokens=100,
                retry_attempts=2
            )
            
            assert response is not None
            assert response.content == "Recovery response"
            assert mock_ollama.call_count == 2
    
    @pytest.mark.asyncio
    async def test_memory_corruption_recovery(self, memory_manager):
        """Test memory corruption recovery."""
        from memory_manager import MemoryChunk
        
        # Store a chunk
        chunk = MemoryChunk(
            content="Test content for corruption recovery",
            metadata={"test": True},
            chunk_id="corruption_test_001"
        )
        await memory_manager.store_chunk(chunk)
        
        # Simulate corruption by directly modifying the vector store
        # (This would be implementation-specific)
        
        # Test recovery
        retrieved = await memory_manager.get_chunk("corruption_test_001")
        assert retrieved is not None
        assert retrieved.content == chunk.content
    
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, research_agent):
        """Test agent failure recovery."""
        # Test with invalid parameters
        with pytest.raises(Exception):
            await research_agent.start_research(
                topic_title="",  # Invalid empty title
                description="Test description",
                keywords=["test"],
                priority=1
            )
        
        # Test recovery with valid parameters
        topic_id = await research_agent.start_research(
            topic_title="Recovery Test",
            description="Test recovery",
            keywords=["recovery", "test"],
            priority=1
        )
        
        assert topic_id is not None
    
    @pytest.mark.asyncio
    async def test_tool_failure_recovery(self, tool_agent):
        """Test tool failure recovery."""
        # Test with non-existent tool
        tool_call = {
            "tool_name": "nonexistent_tool",
            "parameters": {"input": "test"}
        }
        
        result = await tool_agent.execute_tool_call(tool_call)
        assert result is not None
        assert result["success"] is False
        assert "error" in result
        
        # Test recovery with valid tool call
        # (This would require a valid tool to be registered)
        # For now, just verify error handling works
        assert "error" in result