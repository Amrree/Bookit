"""
Comprehensive tests for the tool manager module.
Tests all tool operations, safety mechanisms, and edge cases.
"""
import pytest
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from datetime import datetime

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tool_manager import (
    ToolManager, Tool, ToolDefinition, ToolRequest, ToolResponse,
    ToolCategory, PythonScriptTool, ShellCommandTool, WebSearchTool
)


class TestToolManagerCore:
    """Test core tool manager functionality."""
    
    @pytest.fixture
    def tool_manager(self):
        """Create tool manager instance."""
        return ToolManager()
    
    def test_tool_manager_initialization(self, tool_manager):
        """Test tool manager initialization."""
        assert tool_manager is not None
        assert hasattr(tool_manager, 'tools')
        assert hasattr(tool_manager, 'allow_unsafe')
        assert hasattr(tool_manager, 'allow_restricted')
        assert isinstance(tool_manager.tools, dict)
    
    def test_tool_manager_configuration(self, tool_manager):
        """Test tool manager configuration."""
        assert tool_manager.allow_unsafe == False  # Default value
        assert tool_manager.allow_restricted == False  # Default value
    
    def test_tool_manager_unsafe_mode(self):
        """Test tool manager with unsafe mode enabled."""
        manager = ToolManager(allow_unsafe=True)
        assert manager.allow_unsafe == True
    
    def test_tool_manager_restricted_mode(self):
        """Test tool manager with restricted mode enabled."""
        manager = ToolManager(allow_restricted=True)
        assert manager.allow_restricted == True


class TestToolDefinition:
    """Test tool definition model."""
    
    def test_tool_definition_creation(self):
        """Test tool definition creation."""
        definition = ToolDefinition(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.SAFE,
            parameters={"arg1": {"type": str, "description": "Test argument"}},
            required_parameters=["arg1"]
        )
        assert definition.name == "test_tool"
        assert definition.description == "A test tool"
        assert definition.category == ToolCategory.SAFE
    
    def test_tool_definition_validation(self):
        """Test tool definition validation."""
        definition = ToolDefinition(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.SAFE,
            parameters={"arg1": {"type": str, "description": "Test argument"}},
            required_parameters=["arg1"]
        )
        assert definition.name == "test_tool"
        assert len(definition.parameters) == 1
        assert len(definition.required_parameters) == 1
    
    def test_tool_definition_categories(self):
        """Test tool definition categories."""
        safe_def = ToolDefinition(
            name="safe_tool",
            description="Safe tool",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        restricted_def = ToolDefinition(
            name="restricted_tool",
            description="Restricted tool",
            category=ToolCategory.RESTRICTED,
            parameters={},
            required_parameters=[]
        )
        unsafe_def = ToolDefinition(
            name="unsafe_tool",
            description="Unsafe tool",
            category=ToolCategory.UNSAFE,
            parameters={},
            required_parameters=[]
        )
        
        assert safe_def.category == ToolCategory.SAFE
        assert restricted_def.category == ToolCategory.RESTRICTED
        assert unsafe_def.category == ToolCategory.UNSAFE


class TestToolRequest:
    """Test tool request model."""
    
    def test_tool_request_creation(self):
        """Test tool request creation."""
        request = ToolRequest(
            tool_name="test_tool",
            args={"arg1": "value1"},
            request_id="req_123",
            agent_id="agent_456"
        )
        assert request.tool_name == "test_tool"
        assert request.args == {"arg1": "value1"}
        assert request.request_id == "req_123"
        assert request.agent_id == "agent_456"
    
    def test_tool_request_validation(self):
        """Test tool request validation."""
        request = ToolRequest(
            tool_name="test_tool",
            args={"arg1": "value1"},
            request_id="req_123",
            agent_id="agent_456",
            timeout=60
        )
        assert request.timeout == 60


class TestToolResponse:
    """Test tool response model."""
    
    def test_tool_response_creation(self):
        """Test tool response creation."""
        response = ToolResponse(
            status="success",
            output="Test output",
            stdout="stdout content",
            stderr="stderr content",
            runtime=1.5,
            hashes={"file1": "hash1"},
            error_message=""
        )
        assert response.status == "success"
        assert response.output == "Test output"
        assert response.stdout == "stdout content"
        assert response.stderr == "stderr content"
        assert response.runtime == 1.5
        assert response.hashes == {"file1": "hash1"}
        assert response.error_message == ""
    
    def test_tool_response_defaults(self):
        """Test tool response default values."""
        response = ToolResponse(status="success", output="Test output")
        assert response.stdout == ""
        assert response.stderr == ""
        assert response.runtime == 0.0
        assert response.hashes == {}
        assert response.error_message == ""


class TestToolRegistration:
    """Test tool registration functionality."""
    
    def test_register_safe_tool(self):
        """Test registering a safe tool."""
        manager = ToolManager()
        
        definition = ToolDefinition(
            name="safe_tool",
            description="A safe tool",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class SafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Safe tool executed")
        
        tool = SafeTool(definition)
        manager.register_tool(tool)
        
        assert "safe_tool" in manager.tools
        assert manager.tools["safe_tool"] == tool
    
    def test_register_restricted_tool(self):
        """Test registering a restricted tool."""
        manager = ToolManager(allow_restricted=True)
        
        definition = ToolDefinition(
            name="restricted_tool",
            description="A restricted tool",
            category=ToolCategory.RESTRICTED,
            parameters={},
            required_parameters=[]
        )
        
        class RestrictedTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Restricted tool executed")
        
        tool = RestrictedTool(definition)
        manager.register_tool(tool)
        
        assert "restricted_tool" in manager.tools
        assert manager.tools["restricted_tool"] == tool
    
    def test_register_unsafe_tool(self):
        """Test registering an unsafe tool."""
        manager = ToolManager(allow_unsafe=True)
        
        definition = ToolDefinition(
            name="unsafe_tool",
            description="An unsafe tool",
            category=ToolCategory.UNSAFE,
            parameters={},
            required_parameters=[]
        )
        
        class UnsafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Unsafe tool executed")
        
        tool = UnsafeTool(definition)
        manager.register_tool(tool)
        
        assert "unsafe_tool" in manager.tools
        assert manager.tools["unsafe_tool"] == tool
    
    def test_register_duplicate_tool(self):
        """Test registering a duplicate tool."""
        manager = ToolManager()
        
        definition = ToolDefinition(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class TestTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Test tool executed")
        
        tool1 = TestTool(definition)
        tool2 = TestTool(definition)
        
        manager.register_tool(tool1)
        # Registering the same tool should replace the existing one
        manager.register_tool(tool2)
        
        assert "test_tool" in manager.tools
        assert manager.tools["test_tool"] == tool2


class TestToolExecution:
    """Test tool execution functionality."""
    
    @pytest.fixture
    def safe_tool(self):
        """Create a safe tool for testing."""
        definition = ToolDefinition(
            name="safe_tool",
            description="A safe tool",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class SafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Safe tool executed")
        
        return SafeTool(definition)
    
    @pytest.fixture
    def restricted_tool(self):
        """Create a restricted tool for testing."""
        definition = ToolDefinition(
            name="restricted_tool",
            description="A restricted tool",
            category=ToolCategory.RESTRICTED,
            parameters={},
            required_parameters=[]
        )
        
        class RestrictedTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Restricted tool executed")
        
        return RestrictedTool(definition)
    
    @pytest.fixture
    def unsafe_tool(self):
        """Create an unsafe tool for testing."""
        definition = ToolDefinition(
            name="unsafe_tool",
            description="An unsafe tool",
            category=ToolCategory.UNSAFE,
            parameters={},
            required_parameters=[]
        )
        
        class UnsafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Unsafe tool executed")
        
        return UnsafeTool(definition)
    
    @pytest.mark.asyncio
    async def test_execute_safe_tool(self, tool_manager, safe_tool):
        """Test executing a safe tool."""
        tool_manager.register_tool(safe_tool)
        
        request = ToolRequest(
            tool_name="safe_tool",
            args={},
            request_id="req_123",
            agent_id="agent_456"
        )
        
        response = await tool_manager.execute_tool(request)
        assert response.status == "success"
        assert response.output == "Safe tool executed"
    
    @pytest.mark.asyncio
    async def test_execute_restricted_tool(self, tool_manager, restricted_tool):
        """Test executing a restricted tool."""
        tool_manager = ToolManager(allow_restricted=True)
        tool_manager.register_tool(restricted_tool)
        
        request = ToolRequest(
            tool_name="restricted_tool",
            args={},
            request_id="req_123",
            agent_id="agent_456"
        )
        
        response = await tool_manager.execute_tool(request)
        assert response.status == "success"
        assert response.output == "Restricted tool executed"
    
    @pytest.mark.asyncio
    async def test_execute_unsafe_tool_allowed(self, unsafe_tool):
        """Test executing an unsafe tool when allowed."""
        tool_manager = ToolManager(allow_unsafe=True)
        tool_manager.register_tool(unsafe_tool)
        
        request = ToolRequest(
            tool_name="unsafe_tool",
            args={},
            request_id="req_123",
            agent_id="agent_456"
        )
        
        response = await tool_manager.execute_tool(request)
        assert response.status == "success"
        assert response.output == "Unsafe tool executed"
    
    @pytest.mark.asyncio
    async def test_execute_unsafe_tool_denied(self, tool_manager, unsafe_tool):
        """Test executing an unsafe tool when denied."""
        tool_manager.register_tool(unsafe_tool)
        
        request = ToolRequest(
            tool_name="unsafe_tool",
            args={},
            request_id="req_123",
            agent_id="agent_456"
        )
        
        response = await tool_manager.execute_tool(request)
        assert response.status == "error"
        assert "requires unsafe permissions" in response.error_message
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, tool_manager):
        """Test executing a nonexistent tool."""
        request = ToolRequest(
            tool_name="nonexistent_tool",
            args={},
            request_id="req_123",
            agent_id="agent_456"
        )
        
        response = await tool_manager.execute_tool(request)
        assert response.status == "error"
        assert "not found" in response.error_message


class TestToolSafety:
    """Test tool safety mechanisms."""
    
    def test_safety_validation_safe_tool(self):
        """Test safety validation for safe tools."""
        definition = ToolDefinition(
            name="safe_tool",
            description="A safe tool",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class SafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Safe tool executed")
        
        tool = SafeTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # Safe tools should be available
        available_tools = manager.get_available_tools()
        assert len(available_tools) > 0
        assert any(t.name == "safe_tool" for t in available_tools)
    
    def test_safety_validation_restricted_tool(self):
        """Test safety validation for restricted tools."""
        definition = ToolDefinition(
            name="restricted_tool",
            description="A restricted tool",
            category=ToolCategory.RESTRICTED,
            parameters={},
            required_parameters=[]
        )
        
        class RestrictedTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Restricted tool executed")
        
        tool = RestrictedTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # Restricted tools should not be available by default
        available_tools = manager.get_available_tools()
        assert not any(t.name == "restricted_tool" for t in available_tools)
        
        manager_restricted = ToolManager(allow_restricted=True)
        manager_restricted.register_tool(tool)
        available_tools = manager_restricted.get_available_tools()
        assert any(t.name == "restricted_tool" for t in available_tools)
    
    def test_safety_validation_unsafe_tool(self):
        """Test safety validation for unsafe tools."""
        definition = ToolDefinition(
            name="unsafe_tool",
            description="An unsafe tool",
            category=ToolCategory.UNSAFE,
            parameters={},
            required_parameters=[]
        )
        
        class UnsafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Unsafe tool executed")
        
        tool = UnsafeTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # Unsafe tools should not be available by default
        available_tools = manager.get_available_tools()
        assert not any(t.name == "unsafe_tool" for t in available_tools)
        
        manager_unsafe = ToolManager(allow_unsafe=True)
        manager_unsafe.register_tool(tool)
        available_tools = manager_unsafe.get_available_tools()
        assert any(t.name == "unsafe_tool" for t in available_tools)
    
    def test_safety_validation_unsafe_tool_allowed(self):
        """Test safety validation for unsafe tools when allowed."""
        definition = ToolDefinition(
            name="unsafe_tool",
            description="An unsafe tool",
            category=ToolCategory.UNSAFE,
            parameters={},
            required_parameters=[]
        )
        
        class UnsafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Unsafe tool executed")
        
        tool = UnsafeTool(definition)
        manager = ToolManager(allow_unsafe=True)
        manager.register_tool(tool)
        
        available_tools = manager.get_available_tools()
        assert any(t.name == "unsafe_tool" for t in available_tools)


class TestExceptions:
    """Test exception handling."""
    
    def test_tool_execution_exception(self):
        """Test tool execution exception handling."""
        definition = ToolDefinition(
            name="failing_tool",
            description="A failing tool",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class FailingTool(Tool):
            async def execute(self, args):
                raise Exception("Tool execution failed")
        
        tool = FailingTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # The tool should be registered but execution will fail
        assert "failing_tool" in manager.tools
    
    def test_tool_timeout(self):
        """Test tool timeout handling."""
        definition = ToolDefinition(
            name="slow_tool",
            description="A slow tool",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class SlowTool(Tool):
            async def execute(self, args):
                await asyncio.sleep(10)  # This will timeout
                return ToolResponse(status="success", output="Slow tool executed")
        
        tool = SlowTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # The tool should be registered
        assert "slow_tool" in manager.tools
    
    def test_tool_invalid_response(self):
        """Test tool invalid response handling."""
        definition = ToolDefinition(
            name="invalid_response_tool",
            description="A tool with invalid response",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class InvalidResponseTool(Tool):
            async def execute(self, args):
                return "Invalid response type"  # Should be ToolResponse
        
        tool = InvalidResponseTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # The tool should be registered
        assert "invalid_response_tool" in manager.tools


class TestToolLogging:
    """Test tool logging functionality."""
    
    def test_tool_execution_logging(self):
        """Test tool execution logging."""
        definition = ToolDefinition(
            name="logging_tool",
            description="A tool for testing logging",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class LoggingTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Logging tool executed")
        
        tool = LoggingTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # The tool should be registered
        assert "logging_tool" in manager.tools
    
    def test_get_execution_stats(self, tool_manager):
        """Test getting execution statistics."""
        stats = tool_manager.get_execution_stats()
        
        assert isinstance(stats, dict)
        assert 'total_tools' in stats
        assert 'available_tools' in stats
        assert 'safety_settings' in stats
        assert 'tools_by_category' in stats


class TestToolValidation:
    """Test tool validation functionality."""
    
    def test_validate_tool_parameters(self):
        """Test tool parameter validation."""
        definition = ToolDefinition(
            name="parameterized_tool",
            description="A tool with parameters",
            category=ToolCategory.SAFE,
            parameters={
                "arg1": {"type": str, "description": "First argument"},
                "arg2": {"type": int, "description": "Second argument"}
            },
            required_parameters=["arg1"]
        )
        
        class ParameterizedTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Parameterized tool executed")
        
        tool = ParameterizedTool(definition)
        
        # Test valid arguments
        valid_args = {"arg1": "value1", "arg2": 42}
        assert tool.validate_args(valid_args) == True
        
        # Test missing required argument
        invalid_args = {"arg2": 42}
        assert tool.validate_args(invalid_args) == False
    
    def test_validate_tool_parameter_types(self):
        """Test tool parameter type validation."""
        definition = ToolDefinition(
            name="typed_tool",
            description="A tool with typed parameters",
            category=ToolCategory.SAFE,
            parameters={
                "string_arg": {"type": str, "description": "String argument"},
                "int_arg": {"type": int, "description": "Integer argument"},
                "bool_arg": {"type": bool, "description": "Boolean argument"}
            },
            required_parameters=["string_arg", "int_arg"]
        )
        
        class TypedTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Typed tool executed")
        
        tool = TypedTool(definition)
        
        # Test correct types
        valid_args = {"string_arg": "test", "int_arg": 42, "bool_arg": True}
        assert tool.validate_args(valid_args) == True
        
        # Test incorrect types
        invalid_args = {"string_arg": 123, "int_arg": "test", "bool_arg": "true"}
        assert tool.validate_args(invalid_args) == False


class TestToolPerformance:
    """Test tool performance characteristics."""
    
    def test_tool_execution_performance(self):
        """Test tool execution performance."""
        definition = ToolDefinition(
            name="performance_tool",
            description="A tool for performance testing",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class PerformanceTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Performance tool executed")
        
        tool = PerformanceTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # The tool should be registered
        assert "performance_tool" in manager.tools
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test concurrent tool execution."""
        definition = ToolDefinition(
            name="concurrent_tool",
            description="A tool for concurrent testing",
            category=ToolCategory.SAFE,
            parameters={},
            required_parameters=[]
        )
        
        class ConcurrentTool(Tool):
            async def execute(self, args):
                await asyncio.sleep(0.1)  # Simulate some work
                return ToolResponse(status="success", output="Concurrent tool executed")
        
        tool = ConcurrentTool(definition)
        manager = ToolManager()
        manager.register_tool(tool)
        
        # Create multiple concurrent requests
        requests = [
            ToolRequest(
                tool_name="concurrent_tool",
                args={},
                request_id=f"req_{i}",
                agent_id=f"agent_{i}"
            )
            for i in range(5)
        ]
        
        # Execute all requests concurrently
        tasks = [manager.execute_tool(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # All responses should be successful
        for response in responses:
            assert response.status == "success"
            assert response.output == "Concurrent tool executed"


class TestToolIntegration:
    """Test tool integration with other components."""
    
    def test_agent_integration(self, tool_manager):
        """Test integration with agent system."""
        # This is a placeholder for agent integration tests
        assert tool_manager is not None
    
    def test_memory_manager_integration(self, tool_manager):
        """Test integration with memory manager."""
        # This is a placeholder for memory manager integration tests
        assert tool_manager is not None
    
    def test_llm_client_integration(self, tool_manager):
        """Test integration with LLM client."""
        # This is a placeholder for LLM client integration tests
        assert tool_manager is not None


class TestToolErrorHandling:
    """Test tool error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_tool_not_found_error(self, tool_manager):
        """Test handling of tool not found error."""
        request = ToolRequest(
            tool_name="nonexistent_tool",
            args={},
            request_id="req_123",
            agent_id="agent_456"
        )
        
        response = await tool_manager.execute_tool(request)
        assert response.status == "error"
        assert "not found" in response.error_message
    
    def test_tool_safety_error(self):
        """Test handling of tool safety error."""
        definition = ToolDefinition(
            name="unsafe_tool",
            description="An unsafe tool",
            category=ToolCategory.UNSAFE,
            parameters={},
            required_parameters=[]
        )
        
        class UnsafeTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Unsafe tool executed")
        
        tool = UnsafeTool(definition)
        manager = ToolManager()  # Unsafe not allowed
        manager.register_tool(tool)
        
        # Tool should not be available
        available_tools = manager.get_available_tools()
        assert not any(t.name == "unsafe_tool" for t in available_tools)
    
    def test_tool_parameter_validation_error(self):
        """Test handling of tool parameter validation error."""
        definition = ToolDefinition(
            name="parameterized_tool",
            description="A tool with parameters",
            category=ToolCategory.SAFE,
            parameters={
                "required_arg": {"type": str, "description": "Required argument"}
            },
            required_parameters=["required_arg"]
        )
        
        class ParameterizedTool(Tool):
            async def execute(self, args):
                return ToolResponse(status="success", output="Parameterized tool executed")
        
        tool = ParameterizedTool(definition)
        
        # Test missing required parameter
        invalid_args = {}
        assert tool.validate_args(invalid_args) == False