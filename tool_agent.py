"""
Tool Agent Module

Executes registered tools under ToolManager supervision.
Handles tool selection, execution, and result processing.

Chosen libraries:
- asyncio: Asynchronous tool execution
- pydantic: Data validation and type safety
- logging: Tool execution logging

Adapted from: ReDel (https://github.com/zhudotexe/redel)
Pattern: Tool delegation and execution with safety controls
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pydantic

logger = logging.getLogger(__name__)


class ToolExecutionRequest(pydantic.BaseModel):
    """Model for tool execution requests."""
    request_id: str
    tool_name: str
    parameters: Dict[str, Any]
    priority: int = 0
    timeout: int = 30
    context: str = ""


class ToolExecutionResult(pydantic.BaseModel):
    """Model for tool execution results."""
    request_id: str
    tool_name: str
    status: str  # success, error, timeout, cancelled
    output: Any
    execution_time: float
    error_message: str = ""
    metadata: Dict[str, Any] = {}


class ToolCapability(pydantic.BaseModel):
    """Model for tool capabilities."""
    tool_name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]] = []


class ToolAgent:
    """
    Agent responsible for executing tools under ToolManager supervision.
    
    Responsibilities:
    - Execute tools based on agent requests
    - Handle tool selection and parameter validation
    - Process tool results and provide feedback
    - Manage tool execution queues and priorities
    - Ensure safe tool execution within policies
    """
    
    def __init__(
        self,
        agent_id: str,
        tool_manager: Any,
        max_concurrent_executions: int = 3
    ):
        """
        Initialize the tool agent.
        
        Args:
            agent_id: Unique agent identifier
            tool_manager: Tool manager for tool execution
            max_concurrent_executions: Maximum concurrent tool executions
        """
        self.agent_id = agent_id
        self.tool_manager = tool_manager
        self.max_concurrent_executions = max_concurrent_executions
        
        # Execution state
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.execution_history: List[ToolExecutionResult] = []
        self.capabilities: Dict[str, ToolCapability] = {}
        
        # Initialize capabilities
        self._load_tool_capabilities()
        
        logger.info(f"Tool agent {agent_id} initialized")
    
    def _load_tool_capabilities(self):
        """Load available tool capabilities from tool manager."""
        try:
            available_tools = self.tool_manager.get_available_tools()
            
            for tool_def in available_tools:
                capability = ToolCapability(
                    tool_name=tool_def.name,
                    description=tool_def.description,
                    category=tool_def.category.value,
                    parameters=tool_def.parameters,
                    examples=self._generate_tool_examples(tool_def)
                )
                self.capabilities[tool_def.name] = capability
            
            logger.info(f"Loaded {len(self.capabilities)} tool capabilities")
            
        except Exception as e:
            logger.error(f"Failed to load tool capabilities: {e}")
    
    def _generate_tool_examples(self, tool_def) -> List[Dict[str, Any]]:
        """Generate example usage for a tool."""
        examples = []
        
        if tool_def.name == "python_script":
            examples.append({
                "description": "Calculate factorial",
                "parameters": {
                    "script": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\nprint(factorial(5))"
                }
            })
        elif tool_def.name == "shell_command":
            examples.append({
                "description": "List files in directory",
                "parameters": {
                    "command": "ls -la"
                }
            })
        elif tool_def.name == "web_search":
            examples.append({
                "description": "Search for information",
                "parameters": {
                    "query": "artificial intelligence trends 2024"
                }
            })
        
        return examples
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        priority: int = 0,
        timeout: int = 30,
        context: str = ""
    ) -> str:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            priority: Execution priority (higher = more important)
            timeout: Timeout in seconds
            context: Context for the execution
            
        Returns:
            Request ID
        """
        request_id = f"tool_{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Check if tool is available
        if tool_name not in self.capabilities:
            raise ValueError(f"Tool {tool_name} not available")
        
        # Validate parameters
        if not self._validate_parameters(tool_name, parameters):
            raise ValueError(f"Invalid parameters for tool {tool_name}")
        
        # Check concurrent execution limit
        if len(self.active_executions) >= self.max_concurrent_executions:
            raise RuntimeError("Maximum concurrent executions reached")
        
        # Create execution request
        request = ToolExecutionRequest(
            request_id=request_id,
            tool_name=tool_name,
            parameters=parameters,
            priority=priority,
            timeout=timeout,
            context=context
        )
        
        # Start execution
        task = asyncio.create_task(self._execute_tool_async(request))
        self.active_executions[request_id] = task
        
        logger.info(f"Started tool execution: {tool_name} (request_id: {request_id})")
        return request_id
    
    async def _execute_tool_async(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Execute tool asynchronously."""
        start_time = datetime.now()
        
        try:
            # Execute tool through tool manager
            tool_request = {
                "tool_name": request.tool_name,
                "args": request.parameters,
                "request_id": request.request_id,
                "agent_id": self.agent_id,
                "timeout": request.timeout
            }
            
            response = await self.tool_manager.execute_tool(tool_request)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = ToolExecutionResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                status=response.status,
                output=response.output,
                execution_time=execution_time,
                error_message=response.error_message,
                metadata={
                    "stdout": response.stdout,
                    "stderr": response.stderr,
                    "hashes": response.hashes,
                    "context": request.context
                }
            )
            
            # Store in history
            self.execution_history.append(result)
            
            logger.info(f"Completed tool execution: {request.tool_name} (status: {response.status})")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = ToolExecutionResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                status="error",
                output=None,
                execution_time=execution_time,
                error_message=str(e),
                metadata={"context": request.context}
            )
            
            self.execution_history.append(result)
            logger.error(f"Tool execution failed: {request.tool_name} - {e}")
            return result
        
        finally:
            # Remove from active executions
            if request.request_id in self.active_executions:
                del self.active_executions[request.request_id]
    
    def _validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters."""
        if tool_name not in self.capabilities:
            return False
        
        capability = self.capabilities[tool_name]
        
        # Check required parameters
        for param_name, param_info in capability.parameters.items():
            if param_info.get("required", False) and param_name not in parameters:
                return False
            
            # Check parameter type if specified
            if param_name in parameters:
                expected_type = param_info.get("type")
                if expected_type and not isinstance(parameters[param_name], expected_type):
                    return False
        
        return True
    
    async def get_execution_result(self, request_id: str) -> Optional[ToolExecutionResult]:
        """Get execution result by request ID."""
        # Check active executions
        if request_id in self.active_executions:
            task = self.active_executions[request_id]
            if task.done():
                try:
                    return await task
                except Exception as e:
                    logger.error(f"Failed to get result for {request_id}: {e}")
                    return None
            else:
                return None  # Still running
        
        # Check history
        for result in self.execution_history:
            if result.request_id == request_id:
                return result
        
        return None
    
    async def cancel_execution(self, request_id: str) -> bool:
        """Cancel a running tool execution."""
        if request_id in self.active_executions:
            task = self.active_executions[request_id]
            task.cancel()
            del self.active_executions[request_id]
            logger.info(f"Cancelled tool execution: {request_id}")
            return True
        
        return False
    
    async def get_available_tools(self) -> List[ToolCapability]:
        """Get list of available tool capabilities."""
        return list(self.capabilities.values())
    
    async def get_tool_capability(self, tool_name: str) -> Optional[ToolCapability]:
        """Get capability information for a specific tool."""
        return self.capabilities.get(tool_name)
    
    async def suggest_tool(
        self,
        description: str,
        context: str = ""
    ) -> List[ToolCapability]:
        """
        Suggest tools based on description and context.
        
        Args:
            description: Description of what needs to be done
            context: Additional context
            
        Returns:
            List of suggested tool capabilities
        """
        suggestions = []
        
        # Simple keyword-based matching
        description_lower = description.lower()
        
        for capability in self.capabilities.values():
            score = 0
            
            # Check tool name
            if any(keyword in capability.tool_name.lower() for keyword in description_lower.split()):
                score += 2
            
            # Check description
            if any(keyword in capability.description.lower() for keyword in description_lower.split()):
                score += 1
            
            # Check category
            if any(keyword in capability.category.lower() for keyword in description_lower.split()):
                score += 1
            
            if score > 0:
                suggestions.append((score, capability))
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x[0], reverse=True)
        return [capability for score, capability in suggestions[:5]]
    
    async def get_execution_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for r in self.execution_history if r.status == "success")
        failed_executions = sum(1 for r in self.execution_history if r.status == "error")
        
        avg_execution_time = 0
        if self.execution_history:
            avg_execution_time = sum(r.execution_time for r in self.execution_history) / len(self.execution_history)
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time,
            "active_executions": len(self.active_executions),
            "available_tools": len(self.capabilities)
        }
    
    async def get_execution_history(
        self,
        limit: int = 100,
        tool_name: Optional[str] = None
    ) -> List[ToolExecutionResult]:
        """Get execution history with optional filtering."""
        history = self.execution_history
        
        if tool_name:
            history = [r for r in history if r.tool_name == tool_name]
        
        return history[-limit:]
    
    async def execute_task(self, task_type: str, payload: Dict[str, Any]) -> Any:
        """Execute a tool agent task."""
        if task_type == "execute_tool":
            return await self.execute_tool(
                tool_name=payload.get("tool_name", ""),
                parameters=payload.get("parameters", {}),
                priority=payload.get("priority", 0),
                timeout=payload.get("timeout", 30),
                context=payload.get("context", "")
            )
        elif task_type == "get_result":
            return await self.get_execution_result(payload.get("request_id"))
        elif task_type == "cancel_execution":
            return await self.cancel_execution(payload.get("request_id"))
        elif task_type == "suggest_tool":
            return await self.suggest_tool(
                description=payload.get("description", ""),
                context=payload.get("context", "")
            )
        elif task_type == "get_stats":
            return await self.get_execution_stats()
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def cleanup(self):
        """Clean up active executions and resources."""
        # Cancel all active executions
        for request_id, task in self.active_executions.items():
            task.cancel()
            logger.info(f"Cancelled active execution: {request_id}")
        
        self.active_executions.clear()
        logger.info("Tool agent cleanup completed")