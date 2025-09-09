"""
Simple system integration tests.
Tests basic system functionality without complex async operations.
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
from datetime import datetime

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSystemImports:
    """Test system module imports and basic functionality."""
    
    def test_core_module_imports(self):
        """Test that all core modules can be imported."""
        try:
            from memory_manager import MemoryManager, MemoryEntry
            from llm_client import LLMClient, LLMRequest
            from tool_manager import ToolManager, Tool, ToolCategory, ToolRequest
            from agent_manager import AgentManager, AgentTask
            from document_ingestor import DocumentIngestor
            from book_workflow import BookWorkflow, BookMetadata, ChapterMetadata
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")
    
    def test_module_classes_exist(self):
        """Test that module classes exist and are callable."""
        from memory_manager import MemoryManager, MemoryEntry
        from llm_client import LLMClient, LLMRequest
        from tool_manager import ToolManager, Tool, ToolCategory, ToolRequest
        from agent_manager import AgentManager, AgentTask
        from document_ingestor import DocumentIngestor
        from book_workflow import BookWorkflow, BookMetadata, ChapterMetadata
        
        # Test that classes exist
        classes = [MemoryManager, MemoryEntry, LLMClient, LLMRequest, 
                  ToolManager, Tool, ToolCategory, ToolRequest, AgentManager, 
                  AgentTask, DocumentIngestor, BookWorkflow, BookMetadata, ChapterMetadata]
        
        for cls in classes:
            assert cls is not None
            assert isinstance(cls, type)


class TestSystemInitialization:
    """Test system component initialization."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_memory_manager_initialization(self, temp_dir):
        """Test memory manager initialization."""
        from memory_manager import MemoryManager
        
        memory_manager = MemoryManager(persist_directory=temp_dir)
        assert memory_manager is not None
        assert hasattr(memory_manager, 'collection')
        assert hasattr(memory_manager, 'embedder')
    
    def test_llm_client_initialization(self):
        """Test LLM client initialization."""
        from llm_client import LLMClient
        
        llm_client = LLMClient()
        assert llm_client is not None
        assert hasattr(llm_client, 'providers')
        assert hasattr(llm_client, 'primary_provider')
    
    def test_tool_manager_initialization(self):
        """Test tool manager initialization."""
        from tool_manager import ToolManager
        
        tool_manager = ToolManager()
        assert tool_manager is not None
        assert hasattr(tool_manager, 'tools')
        assert hasattr(tool_manager, 'allow_unsafe')
    
    def test_agent_manager_initialization(self):
        """Test agent manager initialization."""
        from agent_manager import AgentManager
        
        agent_manager = AgentManager()
        assert agent_manager is not None
        assert hasattr(agent_manager, 'agents')
        assert hasattr(agent_manager, 'tasks')
    
    def test_document_ingestor_initialization(self):
        """Test document ingestor initialization."""
        from document_ingestor import DocumentIngestor
        
        document_ingestor = DocumentIngestor()
        assert document_ingestor is not None
        assert hasattr(document_ingestor, 'supported_formats')
    
    def test_book_workflow_initialization(self):
        """Test book workflow initialization."""
        from book_workflow import BookWorkflow
        from memory_manager import MemoryManager
        from llm_client import LLMClient
        from tool_manager import ToolManager
        from agent_manager import AgentManager
        
        # Create mock dependencies
        memory_manager = Mock(spec=MemoryManager)
        llm_client = Mock(spec=LLMClient)
        tool_manager = Mock(spec=ToolManager)
        research_agent = Mock()
        writer_agent = Mock()
        editor_agent = Mock()
        tool_agent = Mock()
        
        book_workflow = BookWorkflow(
            memory_manager=memory_manager,
            llm_client=llm_client,
            tool_manager=tool_manager,
            research_agent=research_agent,
            writer_agent=writer_agent,
            editor_agent=editor_agent,
            tool_agent=tool_agent
        )
        assert book_workflow is not None
        assert hasattr(book_workflow, 'memory_manager')


class TestSystemIntegration:
    """Test system component integration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_memory_manager_with_documents(self, temp_dir):
        """Test memory manager with document storage."""
        from memory_manager import MemoryManager, MemoryEntry
        from document_ingestor import DocumentIngestor, DocumentMetadata, DocumentChunk
        
        memory_manager = MemoryManager(persist_directory=temp_dir)
        document_ingestor = DocumentIngestor()
        
        # Create sample document metadata
        metadata = DocumentMetadata(
            source_id="test_doc",
            original_filename="test.txt",
            file_type="txt",
            file_size=100,
            page_count=1,
            ingestion_timestamp=datetime.now(),
            title="Test Document",
            author="Test Author",
            language="en",
            tags=["test"]
        )
        
        # Create sample chunks
        chunks = [
            DocumentChunk(
                chunk_id="chunk_1",
                content="This is a test document chunk.",
                page_number=1,
                chunk_index=0,
                metadata={"test": "value"}
            )
        ]
        
        # Store document chunks
        memory_manager.store_document_chunks(metadata, chunks)
        
        # Verify storage
        stats = memory_manager.get_stats()
        assert stats['total_chunks'] > 0
    
    def test_llm_client_with_memory_manager(self, temp_dir):
        """Test LLM client integration with memory manager."""
        from memory_manager import MemoryManager
        from llm_client import LLMClient, LLMRequest
        
        memory_manager = MemoryManager(persist_directory=temp_dir)
        llm_client = LLMClient()
        
        # Test that they can work together
        assert memory_manager is not None
        assert llm_client is not None
        
        # Test LLM request creation
        request = LLMRequest(
            prompt="Test prompt",
            max_tokens=100
        )
        assert request.prompt == "Test prompt"
        assert request.max_tokens == 100
    
    def test_tool_manager_with_agent_manager(self):
        """Test tool manager integration with agent manager."""
        from tool_manager import ToolManager, ToolDefinition, ToolCategory
        from agent_manager import AgentManager
        
        tool_manager = ToolManager()
        agent_manager = AgentManager()
        
        # Test that they can work together
        assert tool_manager is not None
        assert agent_manager is not None
        
        # Test tool definition
        tool_def = ToolDefinition(
            name="test_tool",
            description="Test tool",
            category=ToolCategory.SAFE,
            parameters={}
        )
        assert tool_def.name == "test_tool"
        assert tool_def.category == ToolCategory.SAFE
    
    def test_document_ingestor_with_memory_manager(self, temp_dir):
        """Test document ingestor integration with memory manager."""
        from document_ingestor import DocumentIngestor
        from memory_manager import MemoryManager
        
        document_ingestor = DocumentIngestor()
        memory_manager = MemoryManager(persist_directory=temp_dir)
        
        # Test that they can work together
        assert document_ingestor is not None
        assert memory_manager is not None
        
        # Test supported formats
        assert isinstance(document_ingestor.supported_formats, set)
        assert len(document_ingestor.supported_formats) > 0


class TestSystemDataFlow:
    """Test data flow between system components."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_document_to_memory_flow(self, temp_dir):
        """Test document ingestion to memory storage flow."""
        from memory_manager import MemoryManager, MemoryEntry
        from document_ingestor import DocumentIngestor, DocumentMetadata, DocumentChunk
        
        memory_manager = MemoryManager(persist_directory=temp_dir)
        document_ingestor = DocumentIngestor()
        
        # Create test document
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("This is a test document for ingestion.")
        
        # Ingest document
        result = document_ingestor.ingest_document(str(test_file))
        assert result is not None
        assert result.metadata is not None
        assert len(result.chunks) > 0
        
        # Store in memory
        memory_manager.store_document_chunks(result.metadata, result.chunks)
        
        # Verify storage
        stats = memory_manager.get_stats()
        assert stats['total_chunks'] > 0
    
    def test_memory_to_llm_flow(self, temp_dir):
        """Test memory retrieval to LLM context flow."""
        from memory_manager import MemoryManager, MemoryEntry
        from llm_client import LLMClient
        
        memory_manager = MemoryManager(persist_directory=temp_dir)
        llm_client = LLMClient()
        
        # Add some test data to memory
        memory_entry = MemoryEntry(
            content="Test content for retrieval",
            chunk_id="test_chunk",
            source_id="test_source",
            original_filename="test.txt",
            ingestion_timestamp=datetime.now(),
            tags=["test"]
        )
        
        # Store in memory (simplified)
        memory_manager.collection.add(
            ids=["test_chunk"],
            documents=["Test content for retrieval"],
            metadatas=[{"chunk_id": "test_chunk", "source_id": "test_source"}],
            embeddings=[[0.1] * 384]  # Mock embedding
        )
        
        # Retrieve context
        context, sources = memory_manager.get_context_for_generation("test query")
        assert context is not None
        assert sources is not None
    
    def test_agent_task_flow(self):
        """Test agent task creation and management flow."""
        from agent_manager import AgentManager, AgentTask, TaskStatus
        from datetime import datetime
        
        agent_manager = AgentManager()
        
        # Create a task
        task = AgentTask(
            task_id="test_task",
            agent_id="test_agent",
            task_type="research",
            payload={"query": "test query"},
            priority=1,
            created_at=datetime.now()
        )
        
        # Add to agent manager
        agent_manager.tasks["test_task"] = task
        
        # Verify task exists
        assert "test_task" in agent_manager.tasks
        assert agent_manager.tasks["test_task"].status == TaskStatus.PENDING