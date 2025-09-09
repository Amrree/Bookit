"""
Integration tests for the complete system.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Import system modules
from document_ingestor import DocumentIngestor
from memory_manager import MemoryManager
from llm_client import LLMClient
from tool_manager import ToolManager
from agent_manager import AgentManager
from research_agent import ResearchAgent
from writer_agent import WriterAgent, WritingStyle
from editor_agent import EditorAgent, StyleGuide
from tool_agent import ToolAgent
from book_builder import BookBuilder


class TestSystemIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    async def initialized_system(self, temp_dir):
        """Initialize a complete system for testing."""
        # Mock LLM responses
        mock_response = Mock()
        mock_response.content = "This is a test response from the LLM."
        mock_response.model = "test-model"
        mock_response.provider = "test-provider"
        mock_response.usage = {"total_tokens": 100}
        
        with patch('llm_client.OpenAIProvider') as mock_openai, \
             patch('llm_client.OllamaProvider') as mock_ollama:
            
            # Setup mock providers
            mock_openai_instance = Mock()
            mock_openai_instance.generate.return_value = mock_response
            mock_openai_instance.get_available_models.return_value = ["gpt-4"]
            mock_openai.return_value = mock_openai_instance
            
            mock_ollama_instance = Mock()
            mock_ollama_instance.generate.return_value = mock_response
            mock_ollama_instance.get_available_models.return_value = ["llama2"]
            mock_ollama.return_value = mock_ollama_instance
            
            # Initialize components
            memory_manager = MemoryManager(
                persist_directory=temp_dir,
                use_remote_embeddings=False
            )
            
            llm_client = LLMClient(
                primary_provider="openai",
                openai_api_key="test_key"
            )
            
            tool_manager = ToolManager(allow_unsafe=False, allow_restricted=True)
            
            agent_manager = AgentManager()
            await agent_manager.start()
            
            research_agent = ResearchAgent(
                agent_id="test_research",
                memory_manager=memory_manager,
                llm_client=llm_client,
                tool_manager=tool_manager
            )
            
            writer_agent = WriterAgent(
                agent_id="test_writer",
                memory_manager=memory_manager,
                llm_client=llm_client,
                research_agent=research_agent,
                writing_style=WritingStyle()
            )
            
            editor_agent = EditorAgent(
                agent_id="test_editor",
                llm_client=llm_client,
                style_guide=StyleGuide()
            )
            
            tool_agent = ToolAgent(
                agent_id="test_tool",
                tool_manager=tool_manager
            )
            
            # Register agents
            agent_manager.register_agent(research_agent, "research", "research", ["research"])
            agent_manager.register_agent(writer_agent, "writer", "writer", ["writing"])
            agent_manager.register_agent(editor_agent, "editor", "editor", ["editing"])
            agent_manager.register_agent(tool_agent, "tool", "tool", ["tools"])
            
            book_builder = BookBuilder(
                agent_manager=agent_manager,
                memory_manager=memory_manager,
                research_agent=research_agent,
                writer_agent=writer_agent,
                editor_agent=editor_agent,
                tool_agent=tool_agent
            )
            
            yield {
                'memory_manager': memory_manager,
                'llm_client': llm_client,
                'tool_manager': tool_manager,
                'agent_manager': agent_manager,
                'research_agent': research_agent,
                'writer_agent': writer_agent,
                'editor_agent': editor_agent,
                'tool_agent': tool_agent,
                'book_builder': book_builder
            }
    
    @pytest.mark.asyncio
    async def test_document_ingestion_workflow(self, initialized_system, temp_dir):
        """Test complete document ingestion workflow."""
        # Create a sample text file
        sample_file = Path(temp_dir) / "sample.txt"
        sample_file.write_text("""
        This is a sample document for testing the integration.
        It contains multiple paragraphs with various content.
        
        The document should be processed through the complete pipeline.
        This includes ingestion, chunking, embedding, and storage.
        """)
        
        # Ingest document
        ingestor = DocumentIngestor()
        metadata, chunks = await ingestor.ingest_document(sample_file)
        
        # Store in memory
        chunk_ids = await initialized_system['memory_manager'].store_document_chunks(
            metadata, chunks, "test_agent"
        )
        
        # Verify storage
        assert len(chunk_ids) == len(chunks)
        
        # Test retrieval
        results = await initialized_system['memory_manager'].retrieve_relevant_chunks(
            query="sample document testing",
            top_k=5
        )
        
        assert len(results) > 0
        assert all(result.score >= 0.0 for result in results)
    
    @pytest.mark.asyncio
    async def test_research_workflow(self, initialized_system):
        """Test research agent workflow."""
        # Start research
        topic_id = await initialized_system['research_agent'].start_research(
            topic_title="Artificial Intelligence",
            description="Research on AI trends and applications",
            keywords=["AI", "machine learning", "automation"],
            priority=5
        )
        
        assert isinstance(topic_id, str)
        assert len(topic_id) > 0
        
        # Wait a bit for research to complete (in real scenario)
        await asyncio.sleep(0.1)
        
        # Get research results
        results = await initialized_system['research_agent'].get_research_results(topic_id)
        summary = await initialized_system['research_agent'].get_research_summary(topic_id)
        
        # Results might be empty in test environment, but should not error
        assert isinstance(results, list)
        assert summary is None or isinstance(summary, dict)
    
    @pytest.mark.asyncio
    async def test_writing_workflow(self, initialized_system):
        """Test writing agent workflow."""
        # Create chapter outline
        outline_id = await initialized_system['writer_agent'].create_chapter_outline(
            chapter_title="Introduction to AI",
            chapter_order=1,
            research_topics=[],
            word_count_target=1000
        )
        
        assert isinstance(outline_id, str)
        
        # Get outline
        outline = await initialized_system['writer_agent'].get_chapter_outline(outline_id)
        assert outline is not None
        assert outline.title == "Introduction to AI"
        assert outline.order == 1
    
    @pytest.mark.asyncio
    async def test_editing_workflow(self, initialized_system):
        """Test editing agent workflow."""
        content = """
        This is a sample chapter content for testing the editor.
        It contains some text that might need editing and review.
        The editor should analyze this content and provide suggestions.
        """
        
        # Review content
        report_id = await initialized_system['editor_agent'].review_content(
            content=content,
            content_id="test_chapter",
            content_type="chapter"
        )
        
        assert isinstance(report_id, str)
        
        # Get edit report
        report = await initialized_system['editor_agent'].get_edit_report(report_id)
        assert report is not None
        assert report.content_id == "test_chapter"
        assert report.overall_score >= 0.0
        assert report.overall_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_tool_execution_workflow(self, initialized_system):
        """Test tool agent workflow."""
        # Get available tools
        tools = await initialized_system['tool_agent'].get_available_tools()
        assert len(tools) > 0
        
        # Execute a tool (web search)
        request_id = await initialized_system['tool_agent'].execute_tool(
            tool_name="web_search",
            parameters={"query": "artificial intelligence trends 2024"}
        )
        
        assert isinstance(request_id, str)
        
        # Get execution result
        result = await initialized_system['tool_agent'].get_execution_result(request_id)
        assert result is not None
        assert result.tool_name == "web_search"
    
    @pytest.mark.asyncio
    async def test_book_creation_workflow(self, initialized_system):
        """Test book creation workflow."""
        # Create book
        book_id = await initialized_system['book_builder'].create_book(
            title="Test Book",
            author="Test Author",
            description="A test book for integration testing",
            target_audience="general",
            estimated_word_count=10000
        )
        
        assert isinstance(book_id, str)
        
        # Get book status
        status = await initialized_system['book_builder'].get_book_status(book_id)
        assert status["book_id"] == book_id
        assert status["title"] == "Test Book"
        assert status["total_chapters"] == 0  # No chapters yet
    
    @pytest.mark.asyncio
    async def test_agent_manager_workflow(self, initialized_system):
        """Test agent manager workflow."""
        # Submit a task
        task_id = await initialized_system['agent_manager'].submit_task(
            agent_id="research",
            task_type="start_research",
            payload={
                "title": "Test Research",
                "description": "Test research description",
                "keywords": ["test"],
                "priority": 1
            }
        )
        
        assert isinstance(task_id, str)
        
        # Get task status
        task = initialized_system['agent_manager'].get_task_status(task_id)
        assert task is not None
        assert task.task_id == task_id
        assert task.agent_id == "research"
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self, initialized_system, temp_dir):
        """Test memory persistence across restarts."""
        # Add some data to memory
        await initialized_system['memory_manager'].add_agent_notes(
            content="Test persistent content",
            agent_id="test_agent",
            tags=["test", "persistence"]
        )
        
        # Get initial stats
        initial_stats = initialized_system['memory_manager'].get_stats()
        
        # Create new memory manager (simulating restart)
        new_memory_manager = MemoryManager(
            persist_directory=temp_dir,
            use_remote_embeddings=False
        )
        
        # Check that data persists
        new_stats = new_memory_manager.get_stats()
        assert new_stats["total_chunks"] == initial_stats["total_chunks"]
        
        # Test retrieval from persisted data
        results = await new_memory_manager.search_by_tags(["test"], top_k=5)
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, initialized_system):
        """Test error handling across the system."""
        # Test invalid agent ID
        with pytest.raises(ValueError):
            await initialized_system['agent_manager'].submit_task(
                agent_id="nonexistent_agent",
                task_type="test_task",
                payload={}
            )
        
        # Test invalid book ID
        status = await initialized_system['book_builder'].get_book_status("nonexistent_book")
        assert "error" in status
        
        # Test invalid tool execution
        with pytest.raises(ValueError):
            await initialized_system['tool_agent'].execute_tool(
                tool_name="nonexistent_tool",
                parameters={}
            )
    
    @pytest.mark.asyncio
    async def test_cleanup(self, initialized_system):
        """Test system cleanup."""
        # Stop agent manager
        await initialized_system['agent_manager'].stop()
        
        # Cleanup tool agent
        await initialized_system['tool_agent'].cleanup()
        
        # System should be properly cleaned up
        assert True  # If we get here without errors, cleanup worked