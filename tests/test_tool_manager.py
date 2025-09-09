"""
Unit tests for the ToolManager module.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from tool_manager import ToolManager, Tool, ToolRequest, ToolResponse, ToolDefinition


class TestToolManager:
    """Test cases for ToolManager functionality."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, tool_manager):
        """Test tool manager initialization."""
        assert tool_manager is not None
        assert tool_manager.tools is not None
        assert tool_manager.tool_registry is not None
    
    @pytest.mark.asyncio
    async def test_register_tool(self, tool_manager):
        """Test tool registration."""
        tool_def = ToolDefinition(
            name="test_tool",
            description="A test tool for unit testing",
            parameters={
                "param1": {"type": "string", "description": "Test parameter 1"},
                "param2": {"type": "integer", "description": "Test parameter 2"}
            }
        )
        
        result = await tool_manager.register_tool(tool_def)
        assert result is True
        
        # Verify tool is registered
        registered_tool = tool_manager.get_tool("test_tool")
        assert registered_tool is not None
        assert registered_tool.name == "test_tool"
    
    @pytest.mark.asyncio
    async def test_execute_tool(self, tool_manager):
        """Test tool execution."""
        # Create a tool definition
        tool_def = ToolDefinition(
            name="execute_test_tool",
            description="Tool for testing execution",
            parameters={
                "input": {"type": "string", "description": "Input parameter"}
            }
        )
        
        await tool_manager.register_tool(tool_def)
        
        # Execute the tool
        tool_request = ToolRequest(
            tool_name="execute_test_tool",
            args={"input": "test_input"},
            request_id="test_request_001",
            agent_id="test_agent"
        )
        
        result = await tool_manager.execute_tool(tool_request)
        assert result is not None
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_validation(self, tool_manager):
        """Test tool execution with parameter validation."""
        # Create a tool with required parameters
        tool = Tool(
            name="validation_test_tool",
            description="Tool for testing parameter validation",
            parameters={
                "required_param": {"type": "string", "required": True, "description": "Required parameter"},
                "optional_param": {"type": "integer", "required": False, "description": "Optional parameter"}
            },
            function=Mock(return_value="validation_result")
        )
        
        await tool_manager.register_tool(tool)
        
        # Test with valid parameters
        tool_call = ToolRequest(
            tool_name="validation_test_tool",
            parameters={"required_param": "test_value"}
        )
        
        result = await tool_manager.execute_tool(tool_call)
        assert result.success is True
        
        # Test with missing required parameter
        tool_call = ToolRequest(
            tool_name="validation_test_tool",
            parameters={"optional_param": 123}
        )
        
        result = await tool_manager.execute_tool(tool_call)
        assert result.success is False
        assert "required_param" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_error_handling(self, tool_manager):
        """Test tool execution error handling."""
        # Create a tool that raises an exception
        def error_function():
            raise Exception("Test error")
        
        tool = Tool(
            name="error_test_tool",
            description="Tool for testing error handling",
            parameters={},
            function=error_function
        )
        
        await tool_manager.register_tool(tool)
        
        # Execute the tool
        tool_call = ToolRequest(
            tool_name="error_test_tool",
            parameters={}
        )
        
        result = await tool_manager.execute_tool(tool_call)
        assert result.success is False
        assert "Test error" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_timeout(self, tool_manager):
        """Test tool execution with timeout."""
        # Create a tool that takes a long time
        async def slow_function():
            await asyncio.sleep(2)
            return "slow_result"
        
        tool = Tool(
            name="slow_test_tool",
            description="Tool for testing timeout",
            parameters={},
            function=slow_function
        )
        
        await tool_manager.register_tool(tool)
        
        # Execute with short timeout
        tool_call = ToolRequest(
            tool_name="slow_test_tool",
            parameters={}
        )
        
        result = await tool_manager.execute_tool(tool_call, timeout=1)
        assert result.success is False
        assert "timeout" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_execute_tool_with_safety_checks(self, tool_manager):
        """Test tool execution with safety checks."""
        # Create a potentially unsafe tool
        tool = Tool(
            name="unsafe_test_tool",
            description="Tool for testing safety checks",
            parameters={
                "command": {"type": "string", "description": "Command to execute"}
            },
            function=Mock(return_value="unsafe_result"),
            safety_level="unsafe"
        )
        
        await tool_manager.register_tool(tool)
        
        # Test execution with safety checks enabled
        tool_call = ToolRequest(
            tool_name="unsafe_test_tool",
            parameters={"command": "rm -rf /"}
        )
        
        result = await tool_manager.execute_tool(tool_call, safety_checks=True)
        assert result.success is False
        assert "safety" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_list_tools(self, tool_manager):
        """Test listing available tools."""
        # Register multiple tools
        tools = [
            Tool(
                name="tool1",
                description="First tool",
                parameters={},
                function=Mock()
            ),
            Tool(
                name="tool2",
                description="Second tool",
                parameters={},
                function=Mock()
            )
        ]
        
        for tool in tools:
            await tool_manager.register_tool(tool)
        
        # List tools
        tool_list = tool_manager.list_tools()
        assert len(tool_list) >= 2
        assert any(tool.name == "tool1" for tool in tool_list)
        assert any(tool.name == "tool2" for tool in tool_list)
    
    @pytest.mark.asyncio
    async def test_tool_metadata(self, tool_manager):
        """Test tool metadata and descriptions."""
        tool = Tool(
            name="metadata_test_tool",
            description="Tool for testing metadata",
            parameters={
                "param1": {"type": "string", "description": "Parameter 1"},
                "param2": {"type": "integer", "description": "Parameter 2"}
            },
            function=Mock(),
            version="1.0.0",
            author="Test Author"
        )
        
        await tool_manager.register_tool(tool)
        
        # Get tool metadata
        metadata = tool_manager.get_tool_metadata("metadata_test_tool")
        assert metadata is not None
        assert metadata["name"] == "metadata_test_tool"
        assert metadata["description"] == "Tool for testing metadata"
        assert metadata["version"] == "1.0.0"
        assert metadata["author"] == "Test Author"
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self, tool_manager):
        """Test concurrent tool execution."""
        # Create a tool that can be executed concurrently
        tool = Tool(
            name="concurrent_test_tool",
            description="Tool for testing concurrency",
            parameters={
                "delay": {"type": "integer", "description": "Delay in seconds"}
            },
            function=Mock(return_value="concurrent_result")
        )
        
        await tool_manager.register_tool(tool)
        
        # Execute multiple tools concurrently
        tool_calls = [
            ToolRequest(
                tool_name="concurrent_test_tool",
                parameters={"delay": 0.1}
            )
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*[
            tool_manager.execute_tool(tool_call)
            for tool_call in tool_calls
        ])
        
        assert len(results) == 5
        assert all(result.success for result in results)
    
    @pytest.mark.asyncio
    async def test_tool_registry_persistence(self, tool_manager):
        """Test tool registry persistence."""
        # Register a tool
        tool = Tool(
            name="persistence_test_tool",
            description="Tool for testing persistence",
            parameters={},
            function=Mock()
        )
        
        await tool_manager.register_tool(tool)
        
        # Save registry
        await tool_manager.save_registry()
        
        # Create new tool manager and load registry
        new_tool_manager = ToolManager()
        await new_tool_manager.initialize()
        await new_tool_manager.load_registry()
        
        # Verify tool is loaded
        loaded_tool = new_tool_manager.get_tool("persistence_test_tool")
        assert loaded_tool is not None
        assert loaded_tool.name == "persistence_test_tool"
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, tool_manager, performance_metrics):
        """Test performance metrics collection."""
        import time
        
        # Create a tool for performance testing
        tool = Tool(
            name="perf_test_tool",
            description="Tool for performance testing",
            parameters={},
            function=Mock(return_value="perf_result")
        )
        
        await tool_manager.register_tool(tool)
        
        # Test execution performance
        start_time = time.time()
        tool_call = ToolRequest(
            tool_name="perf_test_tool",
            parameters={}
        )
        result = await tool_manager.execute_tool(tool_call)
        end_time = time.time()
        
        execution_time = end_time - start_time
        performance_metrics["tool_execution_time"] = execution_time
        
        assert execution_time > 0
        assert result.success is True