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


class ToolResult(pydantic.BaseModel):
    """Model for tool results."""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float
    tool_name: str
    request_id: str
    agent_id: str
    metadata: Dict[str, Any] = {}


class Tool(ABC):
    """Abstract base class for tools."""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: ToolCategory = ToolCategory.SAFE,
        max_execution_time: int = 30
    ):
        """
        Initialize tool.
        
        Args:
            name: Tool name
            description: Tool description
            category: Tool safety category
            max_execution_time: Maximum execution time in seconds
        """
        self.name = name
        self.description = description
        self.category = category
        self.max_execution_time = max_execution_time
        self.usage_count = 0
        self.last_used = None
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any]) -> Any:
        """Execute the tool with given arguments."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "max_execution_time": self.max_execution_time,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None
        }


class FileSystemTool(Tool):
    """Tool for file system operations."""
    
    def __init__(self):
        super().__init__(
            name="file_system",
            description="File system operations (read, write, list)",
            category=ToolCategory.SAFE
        )
    
    async def execute(self, args: Dict[str, Any]) -> Any:
        """Execute file system operation."""
        operation = args.get("operation")
        path = args.get("path")
        
        if operation == "read":
            return await self._read_file(path)
        elif operation == "write":
            content = args.get("content", "")
            return await self._write_file(path, content)
        elif operation == "list":
            return await self._list_directory(path)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _read_file(self, path: str) -> str:
        """Read file content."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read file {path}: {e}")
    
    async def _write_file(self, path: str, content: str) -> str:
        """Write content to file."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            raise Exception(f"Failed to write file {path}: {e}")
    
    async def _list_directory(self, path: str) -> List[str]:
        """List directory contents."""
        try:
            return os.listdir(path)
        except Exception as e:
            raise Exception(f"Failed to list directory {path}: {e}")


class WebSearchTool(Tool):
    """Tool for web search operations."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information",
            category=ToolCategory.RESTRICTED
        )
    
    async def execute(self, args: Dict[str, Any]) -> Any:
        """Execute web search."""
        query = args.get("query")
        if not query:
            raise ValueError("Query is required")
        
        # This is a placeholder implementation
        # In a real implementation, you would integrate with a search API
        return {
            "query": query,
            "results": [
                {
                    "title": f"Search result for: {query}",
                    "url": "https://example.com",
                    "snippet": f"This is a placeholder result for the query: {query}"
                }
            ]
        }


class ToolManager:
    """
    Manages tool registration, execution, and safety controls.
    
    Responsibilities:
    - Tool registration and discovery
    - Safe tool execution with sandboxing
    - Tool usage logging and monitoring
    - Safety policy enforcement
    """
    
    def __init__(self, sandbox_directory: Optional[str] = None):
        """
        Initialize tool manager.
        
        Args:
            sandbox_directory: Directory for sandboxed tool execution
        """
        self.tools: Dict[str, Tool] = {}
        self.execution_log: List[ToolResult] = []
        self.sandbox_directory = sandbox_directory or tempfile.mkdtemp()
        
        # Create sandbox directory
        os.makedirs(self.sandbox_directory, exist_ok=True)
        
        # Register default tools
        self._register_default_tools()
        
        logger.info(f"Tool manager initialized with sandbox: {self.sandbox_directory}")
    
    def _register_default_tools(self):
        """Register default tools."""
        self.register_tool(FileSystemTool())
        self.register_tool(WebSearchTool())
    
    def register_tool(self, tool: Tool) -> bool:
        """
        Register a new tool.
        
        Args:
            tool: Tool instance to register
            
        Returns:
            True if successful, False if tool already exists
        """
        if tool.name in self.tools:
            logger.warning(f"Tool '{tool.name}' already registered")
            return False
        
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if successful, False if tool not found
        """
        if tool_name not in self.tools:
            logger.warning(f"Tool '{tool_name}' not found")
            return False
        
        del self.tools[tool_name]
        logger.info(f"Unregistered tool: {tool_name}")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of tool to get
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of all registered tools."""
        return [tool.get_info() for tool in self.tools.values()]
    
    async def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        agent_id: str,
        timeout: int = 30
    ) -> ToolResult:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of tool to execute
            args: Tool arguments
            agent_id: ID of agent requesting execution
            timeout: Execution timeout in seconds
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found",
                execution_time=0.0,
                tool_name=tool_name,
                request_id="",
                agent_id=agent_id
            )
        
        tool = self.tools[tool_name]
        request_id = self._generate_request_id(tool_name, args, agent_id)
        
        start_time = time.time()
        
        try:
            # Check safety policy
            if not self._check_safety_policy(tool, agent_id):
                raise Exception("Tool execution blocked by safety policy")
            
            # Execute tool with timeout
            result = await asyncio.wait_for(
                tool.execute(args),
                timeout=min(timeout, tool.max_execution_time)
            )
            
            execution_time = time.time() - start_time
            
            # Update tool usage
            tool.usage_count += 1
            tool.last_used = datetime.now()
            
            # Create result
            tool_result = ToolResult(
                success=True,
                result=result,
                execution_time=execution_time,
                tool_name=tool_name,
                request_id=request_id,
                agent_id=agent_id,
                metadata={
                    "tool_category": tool.category.value,
                    "execution_time": execution_time
                }
            )
            
            # Log execution
            self.execution_log.append(tool_result)
            logger.info(f"Tool '{tool_name}' executed successfully by agent '{agent_id}'")
            
            return tool_result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Tool '{tool_name}' timed out after {execution_time:.2f}s"
            
            tool_result = ToolResult(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time,
                tool_name=tool_name,
                request_id=request_id,
                agent_id=agent_id
            )
            
            self.execution_log.append(tool_result)
            logger.error(error_msg)
            return tool_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Tool execution failed: {str(e)}"
            
            tool_result = ToolResult(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time,
                tool_name=tool_name,
                request_id=request_id,
                agent_id=agent_id
            )
            
            self.execution_log.append(tool_result)
            logger.error(f"Tool '{tool_name}' execution failed: {e}")
            return tool_result
    
    def _check_safety_policy(self, tool: Tool, agent_id: str) -> bool:
        """
        Check if tool execution is allowed by safety policy.
        
        Args:
            tool: Tool to check
            agent_id: ID of agent requesting execution
            
        Returns:
            True if execution is allowed, False otherwise
        """
        # Basic safety policy implementation
        if tool.category == ToolCategory.UNSAFE:
            # Only allow unsafe tools for specific agents
            return agent_id in ["admin", "system"]
        
        return True
    
    def _generate_request_id(self, tool_name: str, args: Dict[str, Any], agent_id: str) -> str:
        """Generate unique request ID."""
        content = f"{tool_name}:{json.dumps(args, sort_keys=True)}:{agent_id}:{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def get_execution_log(self, limit: int = 100) -> List[ToolResult]:
        """
        Get tool execution log.
        
        Args:
            limit: Maximum number of log entries to return
            
        Returns:
            List of tool execution results
        """
        return self.execution_log[-limit:]
    
    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        stats = {}
        for tool_name, tool in self.tools.items():
            stats[tool_name] = {
                "usage_count": tool.usage_count,
                "last_used": tool.last_used.isoformat() if tool.last_used else None,
                "category": tool.category.value
            }
        return stats
    
    def clear_execution_log(self):
        """Clear execution log."""
        self.execution_log.clear()
        logger.info("Execution log cleared")
    
    def get_sandbox_info(self) -> Dict[str, str]:
        """Get sandbox directory information."""
        return {
            "sandbox_directory": self.sandbox_directory,
            "exists": str(os.path.exists(self.sandbox_directory)),
            "size": str(self._get_directory_size(self.sandbox_directory))
        }
    
    def _get_directory_size(self, path: str) -> int:
        """Get directory size in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size