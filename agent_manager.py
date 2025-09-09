"""
Agent Manager Module

Manages task routing, concurrency, lifecycle, and audit logs for agents.
Coordinates research, writer, editor, and tool agents.

Chosen libraries:
- asyncio: Asynchronous agent orchestration
- pydantic: Data validation and type safety
- logging: Comprehensive audit logging

Adapted from: LangGraph (https://github.com/langchain-ai/langgraph)
Pattern: Graph-based orchestration with state management
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import pydantic

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    COMPLETED = "completed"


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTask(pydantic.BaseModel):
    """Model for agent tasks."""
    task_id: str
    agent_id: str
    task_type: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    dependencies: List[str] = []
    priority: int = 0


class AgentInfo(pydantic.BaseModel):
    """Model for agent information."""
    agent_id: str
    agent_type: str
    status: AgentStatus
    current_task: Optional[str] = None
    capabilities: List[str] = []
    created_at: datetime
    last_activity: Optional[datetime] = None


class WorkflowState(pydantic.BaseModel):
    """Model for workflow state."""
    workflow_id: str
    current_step: str
    completed_steps: List[str] = []
    pending_steps: List[str] = []
    state_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class AgentManager:
    """
    Manages agent orchestration and task coordination.
    
    Responsibilities:
    - Coordinate multiple agents (research, writer, editor, tool)
    - Manage task routing and lifecycle
    - Handle agent communication and delegation
    - Maintain audit logs and state management
    - Support both synchronous and asynchronous workflows
    """
    
    def __init__(self, max_concurrent_tasks: int = 5):
        """
        Initialize the agent manager.
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.agents: Dict[str, Any] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.workflows: Dict[str, WorkflowState] = {}
        self.task_queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        # Start task processor
        self._task_processor = None
        self._shutdown = False
        
        logger.info("Agent manager initialized")
    
    async def start(self):
        """Start the agent manager and task processor."""
        if self._task_processor is None:
            self._task_processor = asyncio.create_task(self._process_tasks())
            logger.info("Agent manager started")
    
    async def stop(self):
        """Stop the agent manager and clean up resources."""
        self._shutdown = True
        
        # Cancel all running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        # Wait for task processor to finish
        if self._task_processor:
            self._task_processor.cancel()
            try:
                await self._task_processor
            except asyncio.CancelledError:
                pass
        
        logger.info("Agent manager stopped")
    
    def register_agent(self, agent: Any, agent_id: str, agent_type: str, capabilities: List[str]):
        """
        Register an agent with the manager.
        
        Args:
            agent: Agent instance
            agent_id: Unique agent identifier
            agent_type: Type of agent (research, writer, editor, tool)
            capabilities: List of agent capabilities
        """
        agent_info = AgentInfo(
            agent_id=agent_id,
            agent_type=agent_type,
            status=AgentStatus.IDLE,
            capabilities=capabilities,
            created_at=datetime.now()
        )
        
        self.agents[agent_id] = {
            "instance": agent,
            "info": agent_info
        }
        
        self._log_audit("agent_registered", {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "capabilities": capabilities
        })
        
        logger.info(f"Registered agent: {agent_id} ({agent_type})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._log_audit("agent_unregistered", {"agent_id": agent_id})
            logger.info(f"Unregistered agent: {agent_id}")
    
    async def submit_task(
        self,
        agent_id: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = 0,
        dependencies: List[str] = None
    ) -> str:
        """
        Submit a task to an agent.
        
        Args:
            agent_id: Target agent ID
            task_type: Type of task
            payload: Task payload
            priority: Task priority (higher = more important)
            dependencies: List of task IDs this task depends on
            
        Returns:
            Task ID
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        task_id = f"task_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        task = AgentTask(
            task_id=task_id,
            agent_id=agent_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            dependencies=dependencies or [],
            created_at=datetime.now()
        )
        
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        
        self._log_audit("task_submitted", {
            "task_id": task_id,
            "agent_id": agent_id,
            "task_type": task_type,
            "priority": priority
        })
        
        logger.info(f"Submitted task {task_id} to agent {agent_id}")
        return task_id
    
    async def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            
            # Cancel running task if exists
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                del self.running_tasks[task_id]
            
            self._log_audit("task_cancelled", {"task_id": task_id})
            logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    async def create_workflow(
        self,
        workflow_id: str,
        steps: List[Dict[str, Any]],
        initial_data: Dict[str, Any] = None
    ) -> str:
        """
        Create a new workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            steps: List of workflow steps
            initial_data: Initial workflow data
            
        Returns:
            Workflow ID
        """
        workflow = WorkflowState(
            workflow_id=workflow_id,
            current_step=steps[0]["step_id"] if steps else "",
            pending_steps=[step["step_id"] for step in steps],
            state_data=initial_data or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.workflows[workflow_id] = workflow
        
        self._log_audit("workflow_created", {
            "workflow_id": workflow_id,
            "steps": len(steps)
        })
        
        logger.info(f"Created workflow: {workflow_id}")
        return workflow_id
    
    async def execute_workflow_step(
        self,
        workflow_id: str,
        step_id: str,
        agent_id: str,
        task_type: str,
        payload: Dict[str, Any]
    ) -> str:
        """
        Execute a workflow step.
        
        Args:
            workflow_id: Workflow ID
            step_id: Step ID
            agent_id: Agent to execute the step
            task_type: Type of task
            payload: Task payload
            
        Returns:
            Task ID
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        
        if step_id not in workflow.pending_steps:
            raise ValueError(f"Step {step_id} not in pending steps")
        
        # Submit task
        task_id = await self.submit_task(agent_id, task_type, payload)
        
        # Update workflow state
        workflow.current_step = step_id
        workflow.pending_steps.remove(step_id)
        workflow.completed_steps.append(step_id)
        workflow.updated_at = datetime.now()
        
        self._log_audit("workflow_step_executed", {
            "workflow_id": workflow_id,
            "step_id": step_id,
            "task_id": task_id
        })
        
        return task_id
    
    async def _process_tasks(self):
        """Process tasks from the queue."""
        while not self._shutdown:
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Check if we can run more tasks
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    # Put task back and wait
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.1)
                    continue
                
                # Check dependencies
                if not await self._check_dependencies(task):
                    # Put task back and wait
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.1)
                    continue
                
                # Start task execution
                asyncio.create_task(self._execute_task(task))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
    
    async def _check_dependencies(self, task: AgentTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _execute_task(self, task: AgentTask):
        """Execute a task."""
        task_id = task.task_id
        agent_id = task.agent_id
        
        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            # Update agent status
            if agent_id in self.agents:
                self.agents[agent_id]["info"].status = AgentStatus.BUSY
                self.agents[agent_id]["info"].current_task = task_id
                self.agents[agent_id]["info"].last_activity = datetime.now()
            
            # Store running task
            self.running_tasks[task_id] = asyncio.current_task()
            
            # Get agent instance
            agent = self.agents[agent_id]["instance"]
            
            # Execute task based on type
            if hasattr(agent, 'execute_task'):
                result = await agent.execute_task(task.task_type, task.payload)
            else:
                # Fallback to generic execution
                result = await self._generic_task_execution(agent, task)
            
            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            self._log_audit("task_completed", {
                "task_id": task_id,
                "agent_id": agent_id,
                "runtime": (task.completed_at - task.started_at).total_seconds()
            })
            
        except Exception as e:
            # Update task with error
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)
            
            self._log_audit("task_failed", {
                "task_id": task_id,
                "agent_id": agent_id,
                "error": str(e)
            })
            
            logger.error(f"Task {task_id} failed: {e}")
        
        finally:
            # Clean up
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            # Update agent status
            if agent_id in self.agents:
                self.agents[agent_id]["info"].status = AgentStatus.IDLE
                self.agents[agent_id]["info"].current_task = None
                self.agents[agent_id]["info"].last_activity = datetime.now()
    
    async def _generic_task_execution(self, agent: Any, task: AgentTask) -> Any:
        """Generic task execution fallback."""
        # Try common method names
        method_names = ['process', 'handle', 'execute', 'run']
        
        for method_name in method_names:
            if hasattr(agent, method_name):
                method = getattr(agent, method_name)
                if callable(method):
                    return await method(task.payload)
        
        raise NotImplementedError(f"Agent {task.agent_id} does not support task execution")
    
    def _log_audit(self, event_type: str, data: Dict[str, Any]):
        """Log audit event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.audit_log.append(log_entry)
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent status."""
        if agent_id in self.agents:
            return self.agents[agent_id]["info"]
        return None
    
    def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get task status."""
        return self.tasks.get(task_id)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow status."""
        return self.workflows.get(workflow_id)
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent manager statistics."""
        return {
            "total_agents": len(self.agents),
            "total_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "total_workflows": len(self.workflows),
            "task_queue_size": self.task_queue.qsize(),
            "agents_by_status": {
                status.value: sum(1 for agent in self.agents.values() 
                                if agent["info"].status == status)
                for status in AgentStatus
            },
            "tasks_by_status": {
                status.value: sum(1 for task in self.tasks.values() 
                                if task.status == status)
                for status in TaskStatus
            }
        }