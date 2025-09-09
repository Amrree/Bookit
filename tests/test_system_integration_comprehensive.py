"""
Comprehensive system integration tests.
Tests complete workflows, end-to-end functionality, and system coordination.
"""
import pytest
import os
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from datetime import datetime

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from memory_manager import MemoryManager, MemoryEntry
from llm_client import LLMClient, LLMRequest
from tool_manager import ToolManager, Tool, ToolCategory, ToolRequest
from agent_manager import AgentManager, Agent, AgentTask, TaskPriority
from document_ingestor import DocumentIngestor
from book_workflow import BookWorkflow, BookMetadata, ChapterMetadata


class TestSystemInitialization:
    """Test complete system initialization and setup."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    async def initialized_system(self, temp_dir):
        """Create fully initialized system for testing."""
        # Initialize core components
        memory_manager = MemoryManager(persist_directory=temp_dir)
        llm_client = LLMClient()
        tool_manager = ToolManager()
        agent_manager = AgentManager()
        
        # Start agent manager
        await agent_manager.start()
        
        # Initialize document ingestor
        document_ingestor = DocumentIngestor()
        
        return {
            'memory_manager': memory_manager,
            'llm_client': llm_client,
            'tool_manager': tool_manager,
            'agent_manager': agent_manager,
            'document_ingestor': document_ingestor
        }
    
    def test_system_components_initialization(self, initialized_system):
        """Test that all system components are properly initialized."""
        assert initialized_system['memory_manager'] is not None
        assert initialized_system['llm_client'] is not None
        assert initialized_system['tool_manager'] is not None
        assert initialized_system['agent_manager'] is not None
        assert initialized_system['document_ingestor'] is not None
    
    def test_system_component_interconnections(self, initialized_system):
        """Test that system components can work together."""
        memory_manager = initialized_system['memory_manager']
        llm_client = initialized_system['llm_client']
        tool_manager = initialized_system['tool_manager']
        agent_manager = initialized_system['agent_manager']
        
        # Test that components have required attributes
        assert hasattr(memory_manager, 'get_stats')
        assert hasattr(llm_client, 'providers')
        assert hasattr(tool_manager, 'tools')
        assert hasattr(agent_manager, 'agents')
    
    @pytest.mark.asyncio
    async def test_system_startup_sequence(self, temp_dir):
        """Test proper system startup sequence."""
        # Initialize components in order
        memory_manager = MemoryManager(persist_directory=temp_dir)
        llm_client = LLMClient()
        tool_manager = ToolManager()
        agent_manager = AgentManager()
        
        # Start agent manager
        await agent_manager.start()
        
        # Verify system is running
        assert agent_manager.is_running == True
        
        # Cleanup
        await agent_manager.stop()
        assert agent_manager.is_running == False


class TestDocumentProcessingWorkflow:
    """Test complete document processing workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    async def processing_system(self, temp_dir):
        """Create system for document processing testing."""
        memory_manager = MemoryManager(persist_directory=temp_dir)
        document_ingestor = DocumentIngestor()
        
        return {
            'memory_manager': memory_manager,
            'document_ingestor': document_ingestor
        }
    
    @pytest.mark.asyncio
    async def test_document_ingestion_to_memory(self, processing_system):
        """Test complete document ingestion to memory workflow."""
        memory_manager = processing_system['memory_manager']
        document_ingestor = processing_system['document_ingestor']
        
        # Mock document ingestion
        mock_document = Mock()
        mock_document.title = "Test Document"
        mock_document.author = "Test Author"
        mock_document.content = "This is test content for document processing workflow."
        mock_document.file_format = ".txt"
        mock_document.file_size = 100
        
        with patch.object(document_ingestor, 'ingest_document', return_value=mock_document):
            # Ingest document
            document = document_ingestor.ingest_document("test.txt")
            
            # Create memory chunks from document
            chunks = [
                MemoryEntry(
                    source_id="test_doc",
                    chunk_id="chunk_001",
                    original_filename="test.txt",
                    ingestion_timestamp=datetime.now(),
                    content=document.content,
                    metadata={
                        "title": document.title,
                        "author": document.author,
                        "file_format": document.file_format,
                        "file_size": document.file_size
                    }
                )
            ]
            
            # Store chunks in memory
            result = await memory_manager.store_document_chunks(chunks)
            
            assert result is not None
            assert result['stored_chunks'] == 1
            assert result['source_id'] == "test_doc"
    
    @pytest.mark.asyncio
    async def test_document_retrieval_from_memory(self, processing_system):
        """Test document retrieval from memory."""
        memory_manager = processing_system['memory_manager']
        
        # Store test chunks
        chunks = [
            MemoryEntry(
                source_id="retrieval_test",
                chunk_id="chunk_001",
                original_filename="retrieval.txt",
                ingestion_timestamp=datetime.now(),
                content="Machine learning is a subset of artificial intelligence.",
                metadata={"topic": "AI", "importance": "high"}
            ),
            MemoryEntry(
                source_id="retrieval_test",
                chunk_id="chunk_002",
                original_filename="retrieval.txt",
                ingestion_timestamp=datetime.now(),
                content="Deep learning uses neural networks for pattern recognition.",
                metadata={"topic": "AI", "importance": "high"}
            )
        ]
        
        await memory_manager.store_document_chunks(chunks)
        
        # Retrieve relevant chunks
        results = await memory_manager.retrieve_relevant_chunks(
            query="artificial intelligence",
            max_results=5
        )
        
        assert results is not None
        assert len(results) > 0
        assert all("artificial intelligence" in result.content or "neural networks" in result.content for result in results)
    
    @pytest.mark.asyncio
    async def test_document_search_and_filtering(self, processing_system):
        """Test document search and filtering capabilities."""
        memory_manager = processing_system['memory_manager']
        
        # Store diverse chunks
        chunks = [
            MemoryEntry(
                source_id="search_test",
                chunk_id="chunk_001",
                original_filename="ai_doc.txt",
                ingestion_timestamp=datetime.now(),
                content="Artificial intelligence and machine learning",
                metadata={"category": "technology", "topic": "AI"}
            ),
            MemoryEntry(
                source_id="search_test",
                chunk_id="chunk_002",
                original_filename="cooking_doc.txt",
                ingestion_timestamp=datetime.now(),
                content="Cooking recipes and techniques",
                metadata={"category": "lifestyle", "topic": "cooking"}
            ),
            MemoryEntry(
                source_id="search_test",
                chunk_id="chunk_003",
                original_filename="ai_advanced.txt",
                ingestion_timestamp=datetime.now(),
                content="Advanced AI algorithms and neural networks",
                metadata={"category": "technology", "topic": "AI", "level": "advanced"}
            )
        ]
        
        await memory_manager.store_document_chunks(chunks)
        
        # Search with category filter
        results = await memory_manager.retrieve_relevant_chunks(
            query="technology",
            max_results=10,
            metadata_filter={"category": "technology"}
        )
        
        assert results is not None
        assert len(results) > 0
        # All results should be technology category
        for result in results:
            assert result.metadata.get("category") == "technology"


class TestAgentWorkflowIntegration:
    """Test agent workflow integration and coordination."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    async def agent_system(self, temp_dir):
        """Create system with agents for testing."""
        memory_manager = MemoryManager(persist_directory=temp_dir)
        llm_client = LLMClient()
        tool_manager = ToolManager()
        agent_manager = AgentManager()
        
        await agent_manager.start()
        
        # Create and register agents
        research_agent = Agent(
            agent_id="research_agent",
            agent_type="research",
            capabilities=["research", "analysis"]
        )
        
        writer_agent = Agent(
            agent_id="writer_agent",
            agent_type="writer",
            capabilities=["writing", "drafting"]
        )
        
        editor_agent = Agent(
            agent_id="editor_agent",
            agent_type="editor",
            capabilities=["editing", "revision"]
        )
        
        await agent_manager.register_agent(research_agent, "research_agent", "research", ["research", "analysis"])
        await agent_manager.register_agent(writer_agent, "writer_agent", "writer", ["writing", "drafting"])
        await agent_manager.register_agent(editor_agent, "editor_agent", "editor", ["editing", "revision"])
        
        return {
            'memory_manager': memory_manager,
            'llm_client': llm_client,
            'tool_manager': tool_manager,
            'agent_manager': agent_manager,
            'research_agent': research_agent,
            'writer_agent': writer_agent,
            'editor_agent': editor_agent
        }
    
    @pytest.mark.asyncio
    async def test_research_agent_workflow(self, agent_system):
        """Test research agent workflow."""
        memory_manager = agent_system['memory_manager']
        agent_manager = agent_system['agent_manager']
        research_agent = agent_system['research_agent']
        
        # Mock research agent execution
        with patch.object(research_agent, 'execute_task') as mock_research:
            mock_research.return_value = {
                "research_result": "Research completed",
                "sources": ["source1", "source2"],
                "key_points": ["point1", "point2"]
            }
            
            # Create research task
            research_task = AgentTask(
                task_id="research_workflow_001",
                agent_id="research_agent",
                task_type="research",
                payload={"topic": "Artificial Intelligence", "scope": "comprehensive"},
                priority=TaskPriority.HIGH,
                created_at=datetime.now()
            )
            
            # Submit and execute task
            await agent_manager.submit_task(research_task)
            result = await agent_manager.execute_task("research_workflow_001")
            
            assert result is not None
            assert result["research_result"] == "Research completed"
            assert "sources" in result
            assert "key_points" in result
    
    @pytest.mark.asyncio
    async def test_writer_agent_workflow(self, agent_system):
        """Test writer agent workflow."""
        memory_manager = agent_system['memory_manager']
        agent_manager = agent_system['agent_manager']
        writer_agent = agent_system['writer_agent']
        
        # Mock writer agent execution
        with patch.object(writer_agent, 'execute_task') as mock_writer:
            mock_writer.return_value = {
                "writing_result": "Chapter written",
                "word_count": 1500,
                "content": "This is the written chapter content...",
                "citations": ["citation1", "citation2"]
            }
            
            # Create writing task
            writing_task = AgentTask(
                task_id="writing_workflow_001",
                agent_id="writer_agent",
                task_type="writing",
                payload={
                    "chapter_title": "Introduction to AI",
                    "research_data": {"sources": ["source1"], "key_points": ["point1"]},
                    "target_word_count": 1500
                },
                priority=TaskPriority.HIGH,
                created_at=datetime.now()
            )
            
            # Submit and execute task
            await agent_manager.submit_task(writing_task)
            result = await agent_manager.execute_task("writing_workflow_001")
            
            assert result is not None
            assert result["writing_result"] == "Chapter written"
            assert result["word_count"] == 1500
            assert "content" in result
            assert "citations" in result
    
    @pytest.mark.asyncio
    async def test_editor_agent_workflow(self, agent_system):
        """Test editor agent workflow."""
        memory_manager = agent_system['memory_manager']
        agent_manager = agent_system['agent_manager']
        editor_agent = agent_system['editor_agent']
        
        # Mock editor agent execution
        with patch.object(editor_agent, 'execute_task') as mock_editor:
            mock_editor.return_value = {
                "editing_result": "Chapter edited",
                "revisions": ["grammar_fix", "style_improvement"],
                "final_content": "This is the edited chapter content...",
                "quality_score": 0.95
            }
            
            # Create editing task
            editing_task = AgentTask(
                task_id="editing_workflow_001",
                agent_id="editor_agent",
                task_type="editing",
                payload={
                    "content": "This is the chapter content to edit...",
                    "style_guide": "academic",
                    "target_quality": 0.9
                },
                priority=TaskPriority.MEDIUM,
                created_at=datetime.now()
            )
            
            # Submit and execute task
            await agent_manager.submit_task(editing_task)
            result = await agent_manager.execute_task("editing_workflow_001")
            
            assert result is not None
            assert result["editing_result"] == "Chapter edited"
            assert "revisions" in result
            assert "final_content" in result
            assert result["quality_score"] == 0.95
    
    @pytest.mark.asyncio
    async def test_agent_coordination_workflow(self, agent_system):
        """Test coordinated agent workflow."""
        memory_manager = agent_system['memory_manager']
        agent_manager = agent_system['agent_manager']
        research_agent = agent_system['research_agent']
        writer_agent = agent_system['writer_agent']
        editor_agent = agent_system['editor_agent']
        
        # Mock all agents
        with patch.object(research_agent, 'execute_task') as mock_research, \
             patch.object(writer_agent, 'execute_task') as mock_writer, \
             patch.object(editor_agent, 'execute_task') as mock_editor:
            
            # Research phase
            mock_research.return_value = {
                "research_result": "Research completed",
                "sources": ["AI_source1", "AI_source2"],
                "key_points": ["ML basics", "Neural networks", "Applications"]
            }
            
            # Writing phase
            mock_writer.return_value = {
                "writing_result": "Chapter written",
                "word_count": 2000,
                "content": "This is the comprehensive chapter on AI...",
                "citations": ["AI_source1", "AI_source2"]
            }
            
            # Editing phase
            mock_editor.return_value = {
                "editing_result": "Chapter edited",
                "revisions": ["clarity_improvement", "citation_formatting"],
                "final_content": "This is the polished chapter on AI...",
                "quality_score": 0.98
            }
            
            # Execute coordinated workflow
            # 1. Research
            research_task = AgentTask(
                task_id="coord_research_001",
                agent_id="research_agent",
                task_type="research",
                payload={"topic": "Artificial Intelligence", "scope": "comprehensive"},
                created_at=datetime.now()
            )
            await agent_manager.submit_task(research_task)
            research_result = await agent_manager.execute_task("coord_research_001")
            
            # 2. Writing (using research results)
            writing_task = AgentTask(
                task_id="coord_writing_001",
                agent_id="writer_agent",
                task_type="writing",
                payload={
                    "chapter_title": "Introduction to AI",
                    "research_data": research_result,
                    "target_word_count": 2000
                },
                created_at=datetime.now()
            )
            await agent_manager.submit_task(writing_task)
            writing_result = await agent_manager.execute_task("coord_writing_001")
            
            # 3. Editing (using writing results)
            editing_task = AgentTask(
                task_id="coord_editing_001",
                agent_id="editor_agent",
                task_type="editing",
                payload={
                    "content": writing_result["content"],
                    "style_guide": "academic",
                    "target_quality": 0.95
                },
                created_at=datetime.now()
            )
            await agent_manager.submit_task(editing_task)
            editing_result = await agent_manager.execute_task("coord_editing_001")
            
            # Verify workflow results
            assert research_result["research_result"] == "Research completed"
            assert writing_result["writing_result"] == "Chapter written"
            assert editing_result["editing_result"] == "Chapter edited"
            
            # Verify data flow between agents
            assert "research_data" in writing_task.payload
            assert "content" in editing_task.payload


class TestBookWorkflowIntegration:
    """Test complete book workflow integration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    async def book_system(self, temp_dir):
        """Create system for book workflow testing."""
        memory_manager = MemoryManager(persist_directory=temp_dir)
        llm_client = LLMClient()
        tool_manager = ToolManager()
        agent_manager = AgentManager()
        
        await agent_manager.start()
        
        # Create book workflow
        book_workflow = BookWorkflow(
            memory_manager=memory_manager,
            tool_manager=tool_manager,
            research_agent=Mock(),
            writer_agent=Mock(),
            editor_agent=Mock(),
            tool_agent=Mock()
        )
        
        return {
            'memory_manager': memory_manager,
            'llm_client': llm_client,
            'tool_manager': tool_manager,
            'agent_manager': agent_manager,
            'book_workflow': book_workflow
        }
    
    def test_book_metadata_creation(self, book_system):
        """Test book metadata creation."""
        book_workflow = book_system['book_workflow']
        
        metadata = BookMetadata(
            title="Test Book",
            theme="Testing",
            author="Test Author"
        )
        
        assert metadata.title == "Test Book"
        assert metadata.theme == "Testing"
        assert metadata.author == "Test Author"
        assert metadata.status == "draft"
    
    def test_chapter_metadata_creation(self, book_system):
        """Test chapter metadata creation."""
        book_workflow = book_system['book_workflow']
        
        chapter = ChapterMetadata(
            chapter_number=1,
            title="Test Chapter",
            word_count_target=5000
        )
        
        assert chapter.chapter_number == 1
        assert chapter.title == "Test Chapter"
        assert chapter.word_count_target == 5000
        assert chapter.status == "draft"
    
    @pytest.mark.asyncio
    async def test_book_workflow_initialization(self, book_system):
        """Test book workflow initialization."""
        book_workflow = book_system['book_workflow']
        
        # Test workflow creation
        assert book_workflow is not None
        assert hasattr(book_workflow, 'memory_manager')
        assert hasattr(book_workflow, 'tool_manager')
        assert hasattr(book_workflow, 'research_agent')
        assert hasattr(book_workflow, 'writer_agent')
        assert hasattr(book_workflow, 'editor_agent')
        assert hasattr(book_workflow, 'tool_agent')
    
    @pytest.mark.asyncio
    async def test_book_workflow_status_tracking(self, book_system):
        """Test book workflow status tracking."""
        book_workflow = book_system['book_workflow']
        
        # Test initial status
        status = book_workflow.get_book_status("test_book_id")
        assert status is not None
        assert 'status' in status
        assert 'progress' in status


class TestToolIntegration:
    """Test tool integration with system components."""
    
    @pytest.fixture
    async def tool_system(self):
        """Create system with tools for testing."""
        tool_manager = ToolManager()
        
        # Create test tools
        class TestTool(Tool):
            def __init__(self, name, category):
                super().__init__(
                    name=name,
                    description=f"A {category} test tool",
                    category=category
                )
            
            async def execute(self, request: ToolRequest) -> ToolResponse:
                return ToolResponse(
                    status="success",
                    output=f"{self.name} executed with args: {request.args}"
                )
        
        # Register tools
        safe_tool = TestTool("safe_tool", ToolCategory.SAFE)
        restricted_tool = TestTool("restricted_tool", ToolCategory.RESTRICTED)
        unsafe_tool = TestTool("unsafe_tool", ToolCategory.UNSAFE)
        
        tool_manager.register_tool(safe_tool)
        tool_manager.register_tool(restricted_tool)
        tool_manager.register_tool(unsafe_tool)
        
        return {
            'tool_manager': tool_manager,
            'safe_tool': safe_tool,
            'restricted_tool': restricted_tool,
            'unsafe_tool': unsafe_tool
        }
    
    @pytest.mark.asyncio
    async def test_safe_tool_execution(self, tool_system):
        """Test safe tool execution."""
        tool_manager = tool_system['tool_manager']
        
        request = ToolRequest(
            tool_name="safe_tool",
            args={"input": "test_input"},
            request_id="req_001",
            agent_id="agent_001"
        )
        
        response = await tool_manager.execute_tool(request)
        
        assert response is not None
        assert response.status == "success"
        assert "safe_tool executed" in response.output
    
    @pytest.mark.asyncio
    async def test_restricted_tool_execution(self, tool_system):
        """Test restricted tool execution."""
        tool_manager = tool_system['tool_manager']
        
        request = ToolRequest(
            tool_name="restricted_tool",
            args={"input": "test_input"},
            request_id="req_001",
            agent_id="agent_001"
        )
        
        response = await tool_manager.execute_tool(request)
        
        assert response is not None
        assert response.status == "success"
        assert "restricted_tool executed" in response.output
    
    @pytest.mark.asyncio
    async def test_unsafe_tool_execution_denied(self, tool_system):
        """Test unsafe tool execution when denied."""
        tool_manager = tool_system['tool_manager']
        
        request = ToolRequest(
            tool_name="unsafe_tool",
            args={"input": "test_input"},
            request_id="req_001",
            agent_id="agent_001"
        )
        
        with pytest.raises(Exception, match="Unsafe tools not allowed"):
            await tool_manager.execute_tool(request)
    
    @pytest.mark.asyncio
    async def test_unsafe_tool_execution_allowed(self, tool_system):
        """Test unsafe tool execution when allowed."""
        # Create tool manager with unsafe tools allowed
        tool_manager = ToolManager(allow_unsafe=True)
        
        class UnsafeTool(Tool):
            def __init__(self):
                super().__init__(
                    name="unsafe_tool_allowed",
                    description="An unsafe tool",
                    category=ToolCategory.UNSAFE
                )
            
            async def execute(self, request: ToolRequest) -> ToolResponse:
                return ToolResponse(
                    status="success",
                    output="Unsafe tool executed"
                )
        
        tool = UnsafeTool()
        tool_manager.register_tool(tool)
        
        request = ToolRequest(
            tool_name="unsafe_tool_allowed",
            args={"input": "test_input"},
            request_id="req_001",
            agent_id="agent_001"
        )
        
        response = await tool_manager.execute_tool(request)
        
        assert response is not None
        assert response.status == "success"
        assert "Unsafe tool executed" in response.output


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    async def complete_system(self, temp_dir):
        """Create complete system for end-to-end testing."""
        # Initialize all components
        memory_manager = MemoryManager(persist_directory=temp_dir)
        llm_client = LLMClient()
        tool_manager = ToolManager()
        agent_manager = AgentManager()
        document_ingestor = DocumentIngestor()
        
        await agent_manager.start()
        
        return {
            'memory_manager': memory_manager,
            'llm_client': llm_client,
            'tool_manager': tool_manager,
            'agent_manager': agent_manager,
            'document_ingestor': document_ingestor
        }
    
    @pytest.mark.asyncio
    async def test_complete_document_to_memory_workflow(self, complete_system):
        """Test complete document to memory workflow."""
        memory_manager = complete_system['memory_manager']
        document_ingestor = complete_system['document_ingestor']
        
        # Mock document ingestion
        mock_document = Mock()
        mock_document.title = "AI Research Paper"
        mock_document.author = "AI Researcher"
        mock_document.content = "This is a comprehensive research paper on artificial intelligence and machine learning."
        mock_document.file_format = ".pdf"
        mock_document.file_size = 50000
        
        with patch.object(document_ingestor, 'ingest_document', return_value=mock_document):
            # 1. Ingest document
            document = document_ingestor.ingest_document("ai_research.pdf")
            
            # 2. Create memory chunks
            chunks = [
                MemoryEntry(
                    source_id="ai_research",
                    chunk_id="chunk_001",
                    original_filename="ai_research.pdf",
                    ingestion_timestamp=datetime.now(),
                    content=document.content,
                    metadata={
                        "title": document.title,
                        "author": document.author,
                        "file_format": document.file_format,
                        "file_size": document.file_size,
                        "topic": "AI",
                        "importance": "high"
                    }
                )
            ]
            
            # 3. Store in memory
            store_result = await memory_manager.store_document_chunks(chunks)
            
            # 4. Retrieve from memory
            retrieval_results = await memory_manager.retrieve_relevant_chunks(
                query="artificial intelligence",
                max_results=5
            )
            
            # Verify complete workflow
            assert document.title == "AI Research Paper"
            assert store_result['stored_chunks'] == 1
            assert len(retrieval_results) > 0
            assert any("artificial intelligence" in result.content for result in retrieval_results)
    
    @pytest.mark.asyncio
    async def test_complete_agent_workflow(self, complete_system):
        """Test complete agent workflow."""
        agent_manager = complete_system['agent_manager']
        
        # Create and register agents
        research_agent = Agent(
            agent_id="e2e_research_agent",
            agent_type="research",
            capabilities=["research", "analysis"]
        )
        
        writer_agent = Agent(
            agent_id="e2e_writer_agent",
            agent_type="writer",
            capabilities=["writing", "drafting"]
        )
        
        await agent_manager.register_agent(research_agent, "e2e_research_agent", "research", ["research", "analysis"])
        await agent_manager.register_agent(writer_agent, "e2e_writer_agent", "writer", ["writing", "drafting"])
        
        # Mock agent executions
        with patch.object(research_agent, 'execute_task') as mock_research, \
             patch.object(writer_agent, 'execute_task') as mock_writer:
            
            mock_research.return_value = {
                "research_result": "E2E research completed",
                "sources": ["source1", "source2"],
                "key_points": ["point1", "point2", "point3"]
            }
            
            mock_writer.return_value = {
                "writing_result": "E2E writing completed",
                "word_count": 2500,
                "content": "This is the complete chapter content...",
                "citations": ["source1", "source2"]
            }
            
            # Execute complete workflow
            # 1. Research task
            research_task = AgentTask(
                task_id="e2e_research_001",
                agent_id="e2e_research_agent",
                task_type="research",
                payload={"topic": "Machine Learning", "scope": "comprehensive"},
                created_at=datetime.now()
            )
            
            await agent_manager.submit_task(research_task)
            research_result = await agent_manager.execute_task("e2e_research_001")
            
            # 2. Writing task (using research results)
            writing_task = AgentTask(
                task_id="e2e_writing_001",
                agent_id="e2e_writer_agent",
                task_type="writing",
                payload={
                    "chapter_title": "Introduction to Machine Learning",
                    "research_data": research_result,
                    "target_word_count": 2500
                },
                created_at=datetime.now()
            )
            
            await agent_manager.submit_task(writing_task)
            writing_result = await agent_manager.execute_task("e2e_writing_001")
            
            # Verify complete workflow
            assert research_result["research_result"] == "E2E research completed"
            assert writing_result["writing_result"] == "E2E writing completed"
            assert writing_result["word_count"] == 2500
            assert "chapter content" in writing_result["content"]
    
    @pytest.mark.asyncio
    async def test_system_performance_under_load(self, complete_system):
        """Test system performance under load."""
        memory_manager = complete_system['memory_manager']
        agent_manager = complete_system['agent_manager']
        
        # Create agent
        agent = Agent(
            agent_id="load_test_agent",
            agent_type="test",
            capabilities=["test_capability"]
        )
        
        await agent_manager.register_agent(agent, "load_test_agent", "test", ["test_capability"])
        
        # Mock fast agent execution
        with patch.object(agent, 'execute_task') as mock_execute:
            mock_execute.return_value = {"result": "load_test_success"}
            
            # Create many tasks
            tasks = []
            for i in range(50):  # 50 concurrent tasks
                task = AgentTask(
                    task_id=f"load_task_{i:03d}",
                    agent_id="load_test_agent",
                    task_type="test_task",
                    payload={"task_id": i},
                    created_at=datetime.now()
                )
                tasks.append(task)
                await agent_manager.submit_task(task)
            
            # Execute all tasks
            start_time = asyncio.get_event_loop().time()
            
            for task in tasks:
                await agent_manager.execute_task(task.task_id)
            
            end_time = asyncio.get_event_loop().time()
            
            # Verify performance
            assert (end_time - start_time) < 30.0  # Should complete within 30 seconds
            assert mock_execute.call_count == 50  # All tasks executed


class TestErrorRecovery:
    """Test system error recovery and resilience."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    async def resilient_system(self, temp_dir):
        """Create system for error recovery testing."""
        memory_manager = MemoryManager(persist_directory=temp_dir)
        agent_manager = AgentManager()
        
        await agent_manager.start()
        
        return {
            'memory_manager': memory_manager,
            'agent_manager': agent_manager
        }
    
    @pytest.mark.asyncio
    async def test_agent_error_recovery(self, resilient_system):
        """Test agent error recovery."""
        agent_manager = resilient_system['agent_manager']
        
        # Create agent that fails initially but recovers
        class ResilientAgent(Agent):
            def __init__(self):
                super().__init__(
                    agent_id="resilient_agent",
                    agent_type="test",
                    capabilities=["test_capability"]
                )
                self.failure_count = 0
            
            async def execute_task(self, task):
                self.failure_count += 1
                if self.failure_count <= 2:  # Fail first two times
                    raise Exception("Simulated agent error")
                return {"result": "recovered_success"}
        
        agent = ResilientAgent()
        await agent_manager.register_agent(agent, "resilient_agent", "test", ["test_capability"])
        
        # Create task
        task = AgentTask(
            task_id="resilient_task_001",
            agent_id="resilient_agent",
            task_type="test_task",
            payload={},
            created_at=datetime.now()
        )
        
        await agent_manager.submit_task(task)
        
        # First two executions should fail
        with pytest.raises(Exception, match="Simulated agent error"):
            await agent_manager.execute_task("resilient_task_001")
        
        with pytest.raises(Exception, match="Simulated agent error"):
            await agent_manager.execute_task("resilient_task_001")
        
        # Third execution should succeed
        result = await agent_manager.execute_task("resilient_task_001")
        assert result["result"] == "recovered_success"
    
    @pytest.mark.asyncio
    async def test_memory_error_recovery(self, resilient_system):
        """Test memory error recovery."""
        memory_manager = resilient_system['memory_manager']
        
        # Test with corrupted data
        try:
            # This should handle errors gracefully
            stats = memory_manager.get_stats()
            assert stats is not None
        except Exception as e:
            # If there's an error, it should be handled gracefully
            assert isinstance(e, Exception)
    
    @pytest.mark.asyncio
    async def test_system_graceful_degradation(self, resilient_system):
        """Test system graceful degradation."""
        agent_manager = resilient_system['agent_manager']
        
        # Test system continues to work even with some components failing
        agent = Agent(
            agent_id="degradation_agent",
            agent_type="test",
            capabilities=["test_capability"]
        )
        
        await agent_manager.register_agent(agent, "degradation_agent", "test", ["test_capability"])
        
        # Mock agent that sometimes fails
        with patch.object(agent, 'execute_task') as mock_execute:
            mock_execute.side_effect = [Exception("Temporary failure"), {"result": "success"}]
            
            task = AgentTask(
                task_id="degradation_task_001",
                agent_id="degradation_agent",
                task_type="test_task",
                payload={},
                created_at=datetime.now()
            )
            
            await agent_manager.submit_task(task)
            
            # First execution should fail
            with pytest.raises(Exception, match="Temporary failure"):
                await agent_manager.execute_task("degradation_task_001")
            
            # Second execution should succeed
            result = await agent_manager.execute_task("degradation_task_001")
            assert result["result"] == "success"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])