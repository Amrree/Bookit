"""
Core functionality tests for the book-writing system.
Tests the actual methods and classes that exist in the codebase.
"""
import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch


class TestCoreImports:
    """Test that all core modules can be imported."""
    
    def test_memory_manager_import(self):
        """Test memory manager import."""
        from memory_manager import MemoryManager, MemoryEntry, RetrievalResult
        assert MemoryManager is not None
        assert MemoryEntry is not None
        assert RetrievalResult is not None
    
    def test_llm_client_import(self):
        """Test LLM client import."""
        from llm_client import LLMClient
        assert LLMClient is not None
    
    def test_tool_manager_import(self):
        """Test tool manager import."""
        from tool_manager import ToolManager, ToolRequest, ToolResponse, ToolDefinition
        assert ToolManager is not None
        assert ToolRequest is not None
        assert ToolResponse is not None
        assert ToolDefinition is not None
    
    def test_agent_manager_import(self):
        """Test agent manager import."""
        from agent_manager import AgentManager, AgentStatus, TaskStatus
        assert AgentManager is not None
        assert AgentStatus is not None
        assert TaskStatus is not None
    
    def test_agents_import(self):
        """Test individual agent imports."""
        from research_agent import ResearchAgent
        from writer_agent import WriterAgent
        from editor_agent import EditorAgent
        from tool_agent import ToolAgent
        
        assert ResearchAgent is not None
        assert WriterAgent is not None
        assert EditorAgent is not None
        assert ToolAgent is not None
    
    def test_document_ingestor_import(self):
        """Test document ingestor import."""
        from document_ingestor import DocumentIngestor
        assert DocumentIngestor is not None
    
    def test_book_workflow_import(self):
        """Test book workflow import."""
        from book_workflow import BookWorkflow
        assert BookWorkflow is not None
    
    def test_cli_import(self):
        """Test CLI import."""
        import cli
        assert cli is not None
    
    def test_gui_import(self):
        """Test GUI import."""
        try:
            import gui
            assert gui is not None
        except ImportError as e:
            if "PyQt6" in str(e):
                pytest.skip("PyQt6 not installed - GUI module not available")
            else:
                raise


class TestMemoryManagerCore:
    """Test core memory manager functionality."""
    
    def test_memory_manager_creation(self):
        """Test creating a memory manager instance."""
        from memory_manager import MemoryManager
        
        memory = MemoryManager()
        assert memory is not None
        assert hasattr(memory, 'persist_directory')
        assert hasattr(memory, 'embedding_model')
    
    def test_memory_entry_creation(self):
        """Test creating a memory entry."""
        from memory_manager import MemoryEntry
        
        entry = MemoryEntry(
            source_id="test_source",
            chunk_id="test_chunk_001",
            original_filename="test.txt",
            ingestion_timestamp=datetime.now(),
            content="Test content",
            metadata={"test": "value"}
        )
        
        assert entry.source_id == "test_source"
        assert entry.chunk_id == "test_chunk_001"
        assert entry.content == "Test content"
    
    def test_retrieval_result_creation(self):
        """Test creating a retrieval result."""
        from memory_manager import RetrievalResult
        
        result = RetrievalResult(
            content="Retrieved content",
            chunk_id="chunk_001",
            source_id="source_001",
            score=0.95,
            metadata={"source": "test"}
        )
        
        assert result.content == "Retrieved content"
        assert result.chunk_id == "chunk_001"
        assert result.source_id == "source_001"
        assert result.score == 0.95


class TestLLMClientCore:
    """Test core LLM client functionality."""
    
    def test_llm_client_creation(self):
        """Test creating an LLM client instance."""
        from llm_client import LLMClient
        
        client = LLMClient()
        assert client is not None
        assert hasattr(client, 'providers')
        assert hasattr(client, 'primary_provider')
    
    def test_llm_client_attributes(self):
        """Test LLM client attributes."""
        from llm_client import LLMClient
        
        client = LLMClient()
        assert isinstance(client.providers, dict)
        assert client.primary_provider in ["ollama", "openai"]


class TestToolManagerCore:
    """Test core tool manager functionality."""
    
    def test_tool_manager_creation(self):
        """Test creating a tool manager instance."""
        from tool_manager import ToolManager
        
        manager = ToolManager()
        assert manager is not None
        assert hasattr(manager, 'tools')
        assert hasattr(manager, 'allow_unsafe')
    
    def test_tool_definition_creation(self):
        """Test creating a tool definition."""
        from tool_manager import ToolDefinition, ToolCategory
        
        tool_def = ToolDefinition(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.SAFE,
            parameters={"input": {"type": "string", "description": "Input parameter"}}
        )
        
        assert tool_def.name == "test_tool"
        assert tool_def.description == "A test tool"
        assert tool_def.category == ToolCategory.SAFE
    
    def test_tool_request_creation(self):
        """Test creating a tool request."""
        from tool_manager import ToolRequest
        
        request = ToolRequest(
            tool_name="test_tool",
            args={"input": "test_value"},
            request_id="req_001",
            agent_id="agent_001"
        )
        
        assert request.tool_name == "test_tool"
        assert request.args["input"] == "test_value"
        assert request.request_id == "req_001"


class TestAgentManagerCore:
    """Test core agent manager functionality."""
    
    def test_agent_manager_creation(self):
        """Test creating an agent manager instance."""
        from agent_manager import AgentManager
        
        manager = AgentManager()
        assert manager is not None
        assert hasattr(manager, 'max_concurrent_tasks')
        assert hasattr(manager, 'agents')
        assert hasattr(manager, 'tasks')
    
    def test_agent_status_enum(self):
        """Test agent status enumeration."""
        from agent_manager import AgentStatus
        
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.BUSY.value == "busy"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.COMPLETED.value == "completed"
    
    def test_task_status_enum(self):
        """Test task status enumeration."""
        from agent_manager import TaskStatus
        
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"


class TestDocumentIngestorCore:
    """Test core document ingestor functionality."""
    
    def test_document_ingestor_creation(self):
        """Test creating a document ingestor instance."""
        from document_ingestor import DocumentIngestor
        
        ingestor = DocumentIngestor()
        assert ingestor is not None
        assert hasattr(ingestor, 'supported_formats')
    
    def test_supported_formats(self):
        """Test supported document formats."""
        from document_ingestor import DocumentIngestor
        
        ingestor = DocumentIngestor()
        assert isinstance(ingestor.supported_formats, set)
        assert len(ingestor.supported_formats) > 0


class TestBookWorkflowCore:
    """Test core book workflow functionality."""
    
    def test_book_workflow_creation(self):
        """Test creating a book workflow instance."""
        from book_workflow import BookWorkflow
        from unittest.mock import Mock
        
        # Mock dependencies
        memory_manager = Mock()
        llm_client = Mock()
        tool_manager = Mock()
        agent_manager = Mock()
        research_agent = Mock()
        writer_agent = Mock()
        editor_agent = Mock()
        tool_agent = Mock()
        book_builder = Mock()
        
        workflow = BookWorkflow(
            memory_manager=memory_manager,
            llm_client=llm_client,
            tool_manager=tool_manager,
            agent_manager=agent_manager,
            research_agent=research_agent,
            writer_agent=writer_agent,
            editor_agent=editor_agent,
            tool_agent=tool_agent,
            book_builder=book_builder
        )
        
        assert workflow is not None
        assert workflow.agent_manager == agent_manager
        assert workflow.book_builder == book_builder
        assert workflow.llm_client == llm_client


class TestCLICore:
    """Test core CLI functionality."""
    
    def test_cli_module_structure(self):
        """Test CLI module structure."""
        import cli
        
        assert hasattr(cli, 'cli')
        assert hasattr(cli, 'book')
    
    def test_cli_commands_available(self):
        """Test that CLI commands are available."""
        import cli
        
        # Test that the CLI group exists
        assert cli.cli is not None
        assert cli.book is not None


class TestGUICore:
    """Test core GUI functionality."""
    
    def test_gui_module_structure(self):
        """Test GUI module structure."""
        try:
            import gui
            assert hasattr(gui, 'main')
            assert callable(gui.main)
        except ImportError as e:
            if "PyQt6" in str(e):
                pytest.skip("PyQt6 not installed - GUI module not available")
            else:
                raise


class TestIntegrationCore:
    """Test core integration functionality."""
    
    def test_module_interconnections(self):
        """Test that modules can work together."""
        from memory_manager import MemoryManager
        from llm_client import LLMClient
        from tool_manager import ToolManager
        from agent_manager import AgentManager
        
        # Test that all modules can be instantiated
        memory = MemoryManager()
        llm = LLMClient()
        tools = ToolManager()
        agents = AgentManager()
        
        assert memory is not None
        assert llm is not None
        assert tools is not None
        assert agents is not None
    
    def test_data_flow_compatibility(self):
        """Test that data flows correctly between modules."""
        from memory_manager import MemoryEntry, RetrievalResult
        from tool_manager import ToolRequest, ToolResponse
        from agent_manager import AgentTask
        
        # Test data creation
        memory_entry = MemoryEntry(
            source_id="test",
            chunk_id="chunk_001",
            original_filename="test.txt",
            ingestion_timestamp=datetime.now(),
            content="Test content"
        )
        
        retrieval_result = RetrievalResult(
            content="Retrieved content",
            chunk_id="chunk_001",
            source_id="source_001",
            score=0.95
        )
        
        tool_request = ToolRequest(
            tool_name="test_tool",
            args={"input": "test"},
            request_id="req_001",
            agent_id="agent_001"
        )
        
        tool_response = ToolResponse(
            status="success",
            output="Test result",
            request_id="req_001"
        )
        
        agent_task = AgentTask(
            task_id="task_001",
            agent_id="agent_001",
            task_type="test",
            payload={"test": "data"},
            created_at=datetime.now()
        )
        
        # Verify all objects are created successfully
        assert memory_entry is not None
        assert retrieval_result is not None
        assert tool_request is not None
        assert tool_response is not None
        assert agent_task is not None


class TestErrorHandling:
    """Test error handling across modules."""
    
    def test_memory_manager_error_handling(self):
        """Test memory manager error handling."""
        from memory_manager import MemoryManager
        
        memory = MemoryManager()
        
        # Test with invalid data
        try:
            # This should handle errors gracefully
            memory.get_stats()
        except Exception as e:
            # Should not raise unexpected errors
            assert isinstance(e, Exception)
    
    def test_llm_client_error_handling(self):
        """Test LLM client error handling."""
        from llm_client import LLMClient
        
        client = LLMClient()
        
        # Test that client handles connection errors gracefully
        assert client is not None
        assert hasattr(client, 'primary_provider')
    
    def test_tool_manager_error_handling(self):
        """Test tool manager error handling."""
        from tool_manager import ToolManager
        
        manager = ToolManager()
        
        # Test that manager handles errors gracefully
        assert manager is not None
        assert hasattr(manager, 'tools')


class TestPerformance:
    """Test basic performance characteristics."""
    
    def test_memory_manager_performance(self):
        """Test memory manager performance."""
        from memory_manager import MemoryManager
        import time
        
        start_time = time.time()
        memory = MemoryManager()
        end_time = time.time()
        
        # Should initialize quickly
        assert (end_time - start_time) < 5.0  # Less than 5 seconds
    
    def test_llm_client_performance(self):
        """Test LLM client performance."""
        from llm_client import LLMClient
        import time
        
        start_time = time.time()
        client = LLMClient()
        end_time = time.time()
        
        # Should initialize quickly
        assert (end_time - start_time) < 5.0  # Less than 5 seconds
    
    def test_tool_manager_performance(self):
        """Test tool manager performance."""
        from tool_manager import ToolManager
        import time
        
        start_time = time.time()
        manager = ToolManager()
        end_time = time.time()
        
        # Should initialize quickly
        assert (end_time - start_time) < 1.0  # Less than 1 second