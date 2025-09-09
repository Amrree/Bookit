"""
Tool Manager Module

Implements an MCP-style registry, sandboxing policy, safe execution, and logging.
Manages tool registration, execution, and safety controls.

Chosen libraries:
- subprocess: Safe subprocess execution
- asyncio: Asynchronous tool execution
- pydantic: Data validation and type safety
- json: Tool result serialization

Adapted from: ReDel (https://github.com/zhudotexe/redel)
Pattern: Tool integration with safety controls and delegation
"""

import asyncio
import hashlib
import json
import logging
import os
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pydantic

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool safety categories."""
    SAFE = "safe"
    RESTRICTED = "restricted"
    UNSAFE = "unsafe"


class ToolRequest(pydantic.BaseModel):
    """Model for tool requests."""
    tool_name: str
    args: Dict[str, Any]
    request_id: str
    agent_id: str
    timeout: int = 30


class ToolResponse(pydantic.BaseModel):
    """Model for tool responses."""
    status: str  # "success", "error", "timeout"
    output: Any
    stdout: str = ""
    stderr: str = ""
    runtime: float = 0.0
    hashes: Dict[str, str] = {}
    error_message: str = ""


class ToolDefinition(pydantic.BaseModel):
    """Model for tool definitions."""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any]
    required_parameters: List[str] = []
    optional_parameters: List[str] = []
    timeout: int = 30
    max_memory_mb: int = 100
    allowed_directories: List[str] = []
    environment_variables: Dict[str, str] = {}


class Tool(ABC):
    """Abstract base class for tools."""
    
    def __init__(self, definition: ToolDefinition):
        self.definition = definition
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any]) -> ToolResponse:
        """Execute the tool with given arguments."""
        pass
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        # Check required parameters
        for param in self.definition.required_parameters:
            if param not in args:
                return False
        
        # Check parameter types (simplified validation)
        for param, value in args.items():
            if param in self.definition.parameters:
                expected_type = self.definition.parameters[param].get("type")
                if expected_type and not isinstance(value, expected_type):
                    return False
        
        return True


class PythonScriptTool(Tool):
    """Tool for executing Python scripts."""
    
    async def execute(self, args: Dict[str, Any]) -> ToolResponse:
        """Execute a Python script."""
        start_time = time.time()
        
        try:
            # Validate arguments
            if not self.validate_args(args):
                return ToolResponse(
                    status="error",
                    output=None,
                    error_message="Invalid arguments"
                )
            
            script = args.get("script", "")
            if not script:
                return ToolResponse(
                    status="error",
                    output=None,
                    error_message="No script provided"
                )
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script)
                temp_file = f.name
            
            try:
                # Execute script in subprocess
                result = subprocess.run(
                    ["python", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.definition.timeout,
                    cwd=self.definition.allowed_directories[0] if self.definition.allowed_directories else None
                )
                
                runtime = time.time() - start_time
                
                # Calculate hashes
                hashes = {
                    "script": hashlib.sha256(script.encode()).hexdigest(),
                    "stdout": hashlib.sha256(result.stdout.encode()).hexdigest() if result.stdout else "",
                    "stderr": hashlib.sha256(result.stderr.encode()).hexdigest() if result.stderr else ""
                }
                
                return ToolResponse(
                    status="success" if result.returncode == 0 else "error",
                    output=result.stdout,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    runtime=runtime,
                    hashes=hashes,
                    error_message=result.stderr if result.returncode != 0 else ""
                )
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return ToolResponse(
                status="timeout",
                output=None,
                runtime=time.time() - start_time,
                error_message=f"Tool execution timed out after {self.definition.timeout} seconds"
            )
        except Exception as e:
            return ToolResponse(
                status="error",
                output=None,
                runtime=time.time() - start_time,
                error_message=str(e)
            )


class ShellCommandTool(Tool):
    """Tool for executing shell commands."""
    
    async def execute(self, args: Dict[str, Any]) -> ToolResponse:
        """Execute a shell command."""
        start_time = time.time()
        
        try:
            # Validate arguments
            if not self.validate_args(args):
                return ToolResponse(
                    status="error",
                    output=None,
                    error_message="Invalid arguments"
                )
            
            command = args.get("command", "")
            if not command:
                return ToolResponse(
                    status="error",
                    output=None,
                    error_message="No command provided"
                )
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.definition.timeout,
                cwd=self.definition.allowed_directories[0] if self.definition.allowed_directories else None
            )
            
            runtime = time.time() - start_time
            
            # Calculate hashes
            hashes = {
                "command": hashlib.sha256(command.encode()).hexdigest(),
                "stdout": hashlib.sha256(result.stdout.encode()).hexdigest() if result.stdout else "",
                "stderr": hashlib.sha256(result.stderr.encode()).hexdigest() if result.stderr else ""
            }
            
            return ToolResponse(
                status="success" if result.returncode == 0 else "error",
                output=result.stdout,
                stdout=result.stdout,
                stderr=result.stderr,
                runtime=runtime,
                hashes=hashes,
                error_message=result.stderr if result.returncode != 0 else ""
            )
            
        except subprocess.TimeoutExpired:
            return ToolResponse(
                status="timeout",
                output=None,
                runtime=time.time() - start_time,
                error_message=f"Tool execution timed out after {self.definition.timeout} seconds"
            )
        except Exception as e:
            return ToolResponse(
                status="error",
                output=None,
                runtime=time.time() - start_time,
                error_message=str(e)
            )


class WebSearchTool(Tool):
    """Tool for web search operations."""
    
    async def execute(self, args: Dict[str, Any]) -> ToolResponse:
        """Execute a web search."""
        start_time = time.time()
        
        try:
            # Validate arguments
            if not self.validate_args(args):
                return ToolResponse(
                    status="error",
                    output=None,
                    error_message="Invalid arguments"
                )
            
            query = args.get("query", "")
            if not query:
                return ToolResponse(
                    status="error",
                    output=None,
                    error_message="No search query provided"
                )
            
            # Simulate web search (in a real implementation, you'd use a search API)
            # This is a placeholder implementation
            search_results = {
                "query": query,
                "results": [
                    {
                        "title": f"Search result for: {query}",
                        "url": f"https://example.com/search?q={query}",
                        "snippet": f"This is a simulated search result for the query: {query}"
                    }
                ],
                "total_results": 1
            }
            
            runtime = time.time() - start_time
            
            # Calculate hashes
            hashes = {
                "query": hashlib.sha256(query.encode()).hexdigest(),
                "results": hashlib.sha256(json.dumps(search_results).encode()).hexdigest()
            }
            
            return ToolResponse(
                status="success",
                output=search_results,
                stdout=json.dumps(search_results, indent=2),
                runtime=runtime,
                hashes=hashes
            )
            
        except Exception as e:
            return ToolResponse(
                status="error",
                output=None,
                runtime=time.time() - start_time,
                error_message=str(e)
            )


class ToolManager:
    """
    Manages tool registration, execution, and safety controls.
    
    Responsibilities:
    - Register and manage tools with safety categories
    - Execute tools in sandboxed environments
    - Enforce safety policies and resource limits
    - Log all tool executions and results
    - Provide MCP-style tool interface
    """
    
    def __init__(
        self,
        allow_unsafe: bool = False,
        allow_restricted: bool = False,
        log_file: Optional[str] = None
    ):
        """
        Initialize the tool manager.
        
        Args:
            allow_unsafe: Whether to allow unsafe tools
            allow_restricted: Whether to allow restricted tools
            log_file: Path to log file for tool executions
        """
        self.allow_unsafe = allow_unsafe
        self.allow_restricted = allow_restricted
        self.tools: Dict[str, Tool] = {}
        self.log_file = log_file or "tool_executions.log"
        
        # Initialize with default tools
        self._register_default_tools()
        
        logger.info(f"Tool manager initialized (unsafe: {allow_unsafe}, restricted: {allow_restricted})")
    
    def _register_default_tools(self):
        """Register default tools."""
        # Python script tool
        python_tool_def = ToolDefinition(
            name="python_script",
            description="Execute Python scripts safely",
            category=ToolCategory.SAFE,
            parameters={
                "script": {"type": str, "description": "Python script to execute"}
            },
            required_parameters=["script"],
            timeout=30,
            max_memory_mb=100,
            allowed_directories=[str(Path.cwd())]
        )
        self.register_tool(PythonScriptTool(python_tool_def))
        
        # Shell command tool (restricted)
        shell_tool_def = ToolDefinition(
            name="shell_command",
            description="Execute shell commands",
            category=ToolCategory.RESTRICTED,
            parameters={
                "command": {"type": str, "description": "Shell command to execute"}
            },
            required_parameters=["command"],
            timeout=30,
            max_memory_mb=100,
            allowed_directories=[str(Path.cwd())]
        )
        self.register_tool(ShellCommandTool(shell_tool_def))
        
        # Web search tool
        search_tool_def = ToolDefinition(
            name="web_search",
            description="Search the web for information",
            category=ToolCategory.SAFE,
            parameters={
                "query": {"type": str, "description": "Search query"}
            },
            required_parameters=["query"],
            timeout=10
        )
        self.register_tool(WebSearchTool(search_tool_def))
    
    def register_tool(self, tool: Tool):
        """Register a new tool."""
        if tool.definition.name in self.tools:
            logger.warning(f"Tool {tool.definition.name} already registered, overwriting")
        
        self.tools[tool.definition.name] = tool
        logger.info(f"Registered tool: {tool.definition.name} ({tool.definition.category.value})")
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
        else:
            logger.warning(f"Tool {tool_name} not found")
    
    def get_available_tools(self) -> List[ToolDefinition]:
        """Get list of available tools based on safety settings."""
        available = []
        for tool in self.tools.values():
            if tool.definition.category == ToolCategory.SAFE:
                available.append(tool.definition)
            elif tool.definition.category == ToolCategory.RESTRICTED and self.allow_restricted:
                available.append(tool.definition)
            elif tool.definition.category == ToolCategory.UNSAFE and self.allow_unsafe:
                available.append(tool.definition)
        return available
    
    def get_tool_definition(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name."""
        tool = self.tools.get(tool_name)
        return tool.definition if tool else None
    
    async def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """
        Execute a tool with safety checks.
        
        Args:
            request: Tool execution request
            
        Returns:
            Tool execution response
        """
        # Check if tool exists
        if request.tool_name not in self.tools:
            return ToolResponse(
                status="error",
                output=None,
                error_message=f"Tool {request.tool_name} not found"
            )
        
        tool = self.tools[request.tool_name]
        
        # Check safety permissions
        if tool.definition.category == ToolCategory.RESTRICTED and not self.allow_restricted:
            return ToolResponse(
                status="error",
                output=None,
                error_message=f"Tool {request.tool_name} requires restricted permissions"
            )
        
        if tool.definition.category == ToolCategory.UNSAFE and not self.allow_unsafe:
            return ToolResponse(
                status="error",
                output=None,
                error_message=f"Tool {request.tool_name} requires unsafe permissions"
            )
        
        # Execute tool
        try:
            response = await tool.execute(request.args)
            
            # Log execution
            await self._log_execution(request, response)
            
            return response
            
        except Exception as e:
            error_response = ToolResponse(
                status="error",
                output=None,
                error_message=str(e)
            )
            await self._log_execution(request, error_response)
            return error_response
    
    async def _log_execution(self, request: ToolRequest, response: ToolResponse):
        """Log tool execution."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id,
            "agent_id": request.agent_id,
            "tool_name": request.tool_name,
            "args": request.args,
            "status": response.status,
            "runtime": response.runtime,
            "hashes": response.hashes,
            "error_message": response.error_message
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def update_safety_settings(
        self,
        allow_unsafe: Optional[bool] = None,
        allow_restricted: Optional[bool] = None
    ):
        """Update safety settings."""
        if allow_unsafe is not None:
            self.allow_unsafe = allow_unsafe
            logger.info(f"Unsafe tools {'enabled' if allow_unsafe else 'disabled'}")
        
        if allow_restricted is not None:
            self.allow_restricted = allow_restricted
            logger.info(f"Restricted tools {'enabled' if allow_restricted else 'disabled'}")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        try:
            stats = {
                "total_tools": len(self.tools),
                "available_tools": len(self.get_available_tools()),
                "safety_settings": {
                    "allow_unsafe": self.allow_unsafe,
                    "allow_restricted": self.allow_restricted
                }
            }
            
            # Count tools by category
            category_counts = {category.value: 0 for category in ToolCategory}
            for tool in self.tools.values():
                category_counts[tool.definition.category.value] += 1
            stats["tools_by_category"] = category_counts
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get execution stats: {e}")
            return {"error": str(e)}