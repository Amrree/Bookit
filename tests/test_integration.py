"""
Integration tests for the book-writing system.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch


class TestRAGPipeline:
    """Test cases for the complete RAG pipeline."""
    
    @pytest.mark.asyncio
    async def test_document_to_llm_pipeline(self, document_ingestor, memory_manager, llm_client, sample_documents):
        """Test complete pipeline from document ingestion to LLM response."""
        # Ingest document
        pdf_file = sample_documents["pdf"]
        ingest_result = await document_ingestor.ingest_document(pdf_file)
        assert ingest_result["success"] is True
        assert ingest_result["chunks_created"] > 0
        
        # Search for relevant chunks
        search_results = await memory_manager.search_chunks("machine learning algorithms", limit=3)
        assert len(search_results) > 0
        
        # Prepare context for LLM
        context = "\n".join([chunk.content for chunk in search_results])
        references = [chunk.chunk_id for chunk in search_results]
        
        # Generate response using LLM
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = Mock(
                content="Machine learning algorithms are computational methods that enable systems to learn from data...",
                tokens_used=50,
                model="test-model"
            )
            
            response = await llm_client.generate(
                prompt="Explain machine learning algorithms",
                context=context,
                references=references,
                max_tokens=200
            )
            
            assert response is not None
            assert response.content is not None
            assert "machine learning" in response.content.lower()
    
    @pytest.mark.asyncio
    async def test_multi_document_rag_pipeline(self, document_ingestor, memory_manager, llm_client, sample_documents):
        """Test RAG pipeline with multiple documents."""
        # Ingest multiple documents
        files = list(sample_documents.values())
        ingest_results = await document_ingestor.ingest_documents(files)
        
        assert all(result["success"] for result in ingest_results)
        total_chunks = sum(result["chunks_created"] for result in ingest_results)
        assert total_chunks > 0
        
        # Search across all documents
        search_results = await memory_manager.search_chunks("artificial intelligence", limit=5)
        assert len(search_results) > 0
        
        # Generate comprehensive response
        context = "\n".join([chunk.content for chunk in search_results])
        references = [chunk.chunk_id for chunk in search_results]
        
        with patch.object(llm_client, '_call_ollama') as mock_ollama:
            mock_ollama.return_value = Mock(
                content="Artificial intelligence encompasses machine learning, deep learning, and other computational approaches...",
                tokens_used=75,
                model="test-model"
            )
            
            response = await llm_client.generate(
                prompt="Provide a comprehensive overview of artificial intelligence",
                context=context,
                references=references,
                max_tokens=300
            )
            
            assert response is not None
            assert response.content is not None
            assert len(response.content) > 100


class TestAgentCoordination:
    """Test cases for agent coordination and workflows."""
    
    @pytest.mark.asyncio
    async def test_research_to_writer_workflow(self, research_agent, writer_agent, memory_manager):
        """Test workflow from research to writing."""
        # Start research
        topic_id = await research_agent.start_research(
            topic_title="Test Research Topic",
            description="Research for testing workflow",
            keywords=["test", "workflow"],
            priority=1
        )
        
        # Get research results
        research_results = await research_agent.get_research_results(topic_id)
        research_summary = await research_agent.get_research_summary(topic_id)
        
        # Use research for writing
        chapter_content = await writer_agent.write_chapter(
            title="Test Chapter",
            outline="Chapter based on research",
            context=research_summary.summary if research_summary else "Research context",
            references=[r.chunk_id for r in research_results if r.chunk_id],
            word_count_target=800
        )
        
        assert chapter_content is not None
        assert len(chapter_content) > 0
    
    @pytest.mark.asyncio
    async def test_writer_to_editor_workflow(self, writer_agent, editor_agent):
        """Test workflow from writing to editing."""
        # Write initial chapter
        original_content = await writer_agent.write_chapter(
            title="Test Chapter",
            outline="Test outline",
            context="Test context",
            references=[],
            word_count_target=500
        )
        
        # Edit the chapter
        edited_content = await editor_agent.edit_chapter(
            content=original_content,
            title="Test Chapter",
            context="Test context",
            requirements=["improve clarity", "enhance flow"]
        )
        
        assert edited_content is not None
        assert len(edited_content) > 0
        assert edited_content != original_content
    
    @pytest.mark.asyncio
    async def test_full_agent_workflow(self, research_agent, writer_agent, editor_agent, memory_manager):
        """Test complete agent workflow from research to final editing."""
        # Research phase
        topic_id = await research_agent.start_research(
            topic_title="Complete Workflow Test",
            description="Testing complete agent workflow",
            keywords=["workflow", "test"],
            priority=1
        )
        
        research_results = await research_agent.get_research_results(topic_id)
        research_summary = await research_agent.get_research_summary(topic_id)
        
        # Writing phase
        chapter_content = await writer_agent.write_chapter(
            title="Workflow Test Chapter",
            outline="Chapter outline based on research",
            context=research_summary.summary if research_summary else "Research context",
            references=[r.chunk_id for r in research_results if r.chunk_id],
            word_count_target=1000
        )
        
        # Editing phase
        final_content = await editor_agent.edit_chapter(
            content=chapter_content,
            title="Workflow Test Chapter",
            context="Complete workflow context",
            requirements=["final polish", "quality check"]
        )
        
        assert final_content is not None
        assert len(final_content) > 0
        assert final_content != chapter_content


class TestBookWorkflow:
    """Test cases for the complete book workflow."""
    
    @pytest.mark.asyncio
    async def test_book_workflow_initialization(self, book_workflow, test_book_metadata):
        """Test book workflow initialization."""
        assert book_workflow is not None
        assert book_workflow.agent_manager is not None
        assert book_workflow.book_builder is not None
        assert book_workflow.llm_client is not None
    
    @pytest.mark.asyncio
    async def test_book_workflow_with_mock_llm(self, book_workflow, test_book_metadata):
        """Test book workflow with mock LLM responses."""
        with patch.object(book_workflow.llm_client, 'generate') as mock_generate:
            # Mock LLM responses for different stages
            mock_responses = [
                Mock(content='{"introduction": {"title": "Test Introduction", "key_points": ["Point 1", "Point 2"]}, "chapters": [{"chapter_number": 1, "title": "Test Chapter 1", "key_points": ["Point 3", "Point 4"]}], "conclusion": {"title": "Test Conclusion", "key_points": ["Point 5", "Point 6"]}, "word_count_target": 2000}'),
                Mock(content="Test introduction content"),
                Mock(content="Test chapter 1 content"),
                Mock(content="Test conclusion content"),
                Mock(content="Test global revision content")
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
                            chapters_count=test_book_metadata["chapters_count"]
                        )
                        
                        assert result is not None
                        assert "book_metadata" in result
                        assert result["book_metadata"]["title"] == test_book_metadata["title"]


class TestMemoryIntegration:
    """Test cases for memory integration across components."""
    
    @pytest.mark.asyncio
    async def test_memory_persistence_across_agents(self, memory_manager, research_agent, writer_agent):
        """Test memory persistence across different agents."""
        # Store some data in memory
        from memory_manager import MemoryChunk
        chunk = MemoryChunk(
            content="Test memory content for persistence",
            metadata={"source": "test", "type": "persistence"},
            chunk_id="persistence_test_001"
        )
        await memory_manager.store_chunk(chunk)
        
        # Verify data is accessible
        retrieved = await memory_manager.get_chunk("persistence_test_001")
        assert retrieved is not None
        assert retrieved.content == chunk.content
        
        # Test that agents can access the same memory
        search_results = await memory_manager.search_chunks("persistence", limit=1)
        assert len(search_results) > 0
        assert search_results[0].content == chunk.content
    
    @pytest.mark.asyncio
    async def test_memory_tagging_and_retrieval(self, memory_manager):
        """Test memory tagging and retrieval functionality."""
        from memory_manager import MemoryChunk, MemoryTag
        
        # Create tags
        tag1 = MemoryTag(name="AI", description="Artificial Intelligence")
        tag2 = MemoryTag(name="ML", description="Machine Learning")
        
        await memory_manager.create_tag(tag1)
        await memory_manager.create_tag(tag2)
        
        # Store chunks with tags
        chunk1 = MemoryChunk(
            content="AI content",
            metadata={"tags": ["AI"], "type": "concept"},
            chunk_id="tagged_chunk_001"
        )
        chunk2 = MemoryChunk(
            content="ML content",
            metadata={"tags": ["ML"], "type": "concept"},
            chunk_id="tagged_chunk_002"
        )
        
        await memory_manager.store_chunk(chunk1)
        await memory_manager.store_chunk(chunk2)
        
        # Test tag-based retrieval
        ai_chunks = await memory_manager.search_chunks(
            "intelligence",
            metadata_filter={"tags": "AI"},
            limit=5
        )
        assert len(ai_chunks) > 0
        
        ml_chunks = await memory_manager.search_chunks(
            "learning",
            metadata_filter={"tags": "ML"},
            limit=5
        )
        assert len(ml_chunks) > 0


class TestToolIntegration:
    """Test cases for tool integration across the system."""
    
    @pytest.mark.asyncio
    async def test_tool_registry_integration(self, tool_manager, tool_agent):
        """Test tool registry integration with tool agent."""
        # Register a tool
        from tool_manager import Tool
        tool = Tool(
            name="integration_test_tool",
            description="Tool for integration testing",
            parameters={
                "input": {"type": "string", "description": "Input parameter"}
            },
            function=Mock(return_value="integration_result")
        )
        
        await tool_manager.register_tool(tool)
        
        # Test tool execution through tool agent
        tool_call = {
            "tool_name": "integration_test_tool",
            "parameters": {"input": "test_input"}
        }
        
        result = await tool_agent.execute_tool_call(tool_call)
        assert result is not None
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_tool_safety_integration(self, tool_manager, tool_agent):
        """Test tool safety integration across components."""
        # Register a potentially unsafe tool
        from tool_manager import Tool
        unsafe_tool = Tool(
            name="unsafe_integration_tool",
            description="Unsafe tool for testing",
            parameters={
                "command": {"type": "string", "description": "Command to execute"}
            },
            function=Mock(return_value="unsafe_result"),
            safety_level="unsafe"
        )
        
        await tool_manager.register_tool(unsafe_tool)
        
        # Test safety enforcement
        tool_call = {
            "tool_name": "unsafe_integration_tool",
            "parameters": {"command": "rm -rf /"}
        }
        
        result = await tool_agent.execute_tool_call(tool_call, safety_checks=True)
        assert result is not None
        assert result["success"] is False
        assert "safety" in result.get("error", "").lower()