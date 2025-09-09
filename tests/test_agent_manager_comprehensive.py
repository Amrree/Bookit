"""
Comprehensive tests for the agent manager module.
Tests all agent operations, task management, and coordination.
"""
import pytest
import os
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from datetime import datetime

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent_manager import (
    AgentManager, AgentTask, AgentStatus, TaskStatus,
    AgentInfo, WorkflowState
)


class TestAgentManagerCore:
    """Test core agent manager functionality."""
    
    @pytest.fixture
    def agent_manager(self):
        """Create agent manager instance."""
        return AgentManager()
    
    def test_agent_manager_initialization(self, agent_manager):
        """Test agent manager initialization."""
        assert agent_manager is not None
        assert hasattr(agent_manager, 'agents')
        assert hasattr(agent_manager, 'tasks')
        assert hasattr(agent_manager, 'workflows')
        assert isinstance(agent_manager.agents, dict)
        assert isinstance(agent_manager.tasks, dict)
        assert isinstance(agent_manager.workflows, dict)
    
    def test_agent_manager_configuration(self, agent_manager):
        """Test agent manager configuration."""
        assert agent_manager.agents == {}
        assert agent_manager.tasks == {}
        assert agent_manager.workflows == {}
    
    @pytest.mark.asyncio
    async def test_agent_manager_startup(self, agent_manager):
        """Test agent manager startup."""
        await agent_manager.start()
        # Agent manager should be running after start
        assert True  # Basic test that start() doesn't raise an exception
    
    @pytest.mark.asyncio
    async def test_agent_manager_shutdown(self, agent_manager):
        """Test agent manager shutdown."""
        await agent_manager.start()
        await agent_manager.stop()
        # Agent manager should be stopped after stop()
        assert True  # Basic test that stop() doesn't raise an exception


class TestAgentTask:
    """Test agent task model."""
    
    def test_agent_task_creation(self):
        """Test agent task creation."""
        task = AgentTask(
            task_id="task_123",
            agent_id="agent_456",
            task_type="research",
            payload={"query": "test query"},
            priority=1,
            created_at=datetime.now(),
            status=TaskStatus.PENDING
        )
        assert task.task_id == "task_123"
        assert task.agent_id == "agent_456"
        assert task.task_type == "research"
        assert task.payload == {"query": "test query"}
        assert task.priority == 1
        assert task.status == TaskStatus.PENDING
    
    def test_agent_task_validation(self):
        """Test agent task validation."""
        task = AgentTask(
            task_id="task_123",
            agent_id="agent_456",
            task_type="research",
            payload={"query": "test query"},
            priority=1,
            created_at=datetime.now(),
            status=TaskStatus.PENDING
        )
        assert task.task_id == "task_123"
        assert task.agent_id == "agent_456"
        assert task.status == TaskStatus.PENDING
    
    def test_agent_task_status_management(self):
        """Test agent task status management."""
        task = AgentTask(
            task_id="task_123",
            agent_id="agent_456",
            task_type="research",
            payload={"query": "test query"},
            priority=1,
            created_at=datetime.now(),
            status=TaskStatus.PENDING
        )
        
        # Test status changes
        task.status = TaskStatus.IN_PROGRESS
        assert task.status == TaskStatus.IN_PROGRESS
        
        task.status = TaskStatus.COMPLETED
        assert task.status == TaskStatus.COMPLETED


class TestAgentRegistration:
    """Test agent registration functionality."""
    
    @pytest.mark.asyncio
    async def test_register_agent(self, agent_manager):
        """Test registering an agent."""
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        assert "test_agent" in agent_manager.agents
        assert agent_manager.agents["test_agent"]["info"].agent_id == "test_agent"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_agent(self, agent_manager):
        """Test registering a duplicate agent."""
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        # Registering the same agent should replace the existing one
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        assert "test_agent" in agent_manager.agents
        assert agent_manager.agents["test_agent"]["info"].agent_id == "test_agent"
    
    @pytest.mark.asyncio
    async def test_unregister_agent(self, agent_manager):
        """Test unregistering an agent."""
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        agent_manager.unregister_agent("test_agent")
        
        assert "test_agent" not in agent_manager.agents
    
    @pytest.mark.asyncio
    async def test_unregister_nonexistent_agent(self, agent_manager):
        """Test unregistering a nonexistent agent."""
        # This should not raise an exception
        agent_manager.unregister_agent("nonexistent_agent")
        assert True  # Basic test that it doesn't raise an exception


class TestTaskManagement:
    """Test task management functionality."""
    
    @pytest.mark.asyncio
    async def test_submit_task(self, agent_manager):
        """Test submitting a task."""
        # First register an agent
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        # Submit a task
        task_id = await agent_manager.submit_task("test_agent", "research", {"query": "test query"})
        
        assert task_id is not None
        assert task_id in agent_manager.tasks
    
    @pytest.mark.asyncio
    async def test_submit_task_to_nonexistent_agent(self, agent_manager):
        """Test submitting a task to a nonexistent agent."""
        # This should raise an exception
        with pytest.raises(ValueError, match="Agent nonexistent_agent not found"):
            await agent_manager.submit_task("nonexistent_agent", "research", {"query": "test query"})
    
    @pytest.mark.asyncio
    async def test_get_task(self, agent_manager):
        """Test getting a task."""
        # First register an agent and submit a task
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        task_id = await agent_manager.submit_task("test_agent", "research", {"query": "test query"})
        
        # Get the task
        task = agent_manager.tasks.get(task_id)
        assert task is not None
        assert task.task_id == task_id
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, agent_manager):
        """Test getting a nonexistent task."""
        task = agent_manager.tasks.get("nonexistent_task")
        assert task is None
    
    @pytest.mark.asyncio
    async def test_cancel_task(self, agent_manager):
        """Test canceling a task."""
        # First register an agent and submit a task
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        task_id = await agent_manager.submit_task("test_agent", "research", {"query": "test query"})
        
        # Cancel the task
        await agent_manager.cancel_task(task_id)
        
        # The task should be marked as cancelled
        task = agent_manager.tasks.get(task_id)
        assert task is not None
        assert task.status == TaskStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self, agent_manager):
        """Test canceling a nonexistent task."""
        # This should not raise an exception
        await agent_manager.cancel_task("nonexistent_task")
        assert True  # Basic test that it doesn't raise an exception


class TestAgentMonitoring:
    """Test agent monitoring functionality."""
    
    def test_get_agent_stats(self, agent_manager):
        """Test getting agent statistics."""
        stats = agent_manager.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_agents' in stats
        assert 'total_tasks' in stats
        assert 'running_tasks' in stats
        assert 'total_workflows' in stats
        assert 'task_queue_size' in stats
        assert 'agents_by_status' in stats
        assert 'tasks_by_status' in stats
    
    @pytest.mark.asyncio
    async def test_agent_status_monitoring(self, agent_manager):
        """Test agent status monitoring."""
        # Register an agent
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        # Check agent status
        agent = agent_manager.agents.get("test_agent")
        assert agent is not None
        assert agent["info"].status == AgentStatus.IDLE
    
    @pytest.mark.asyncio
    async def test_task_status_monitoring(self, agent_manager):
        """Test task status monitoring."""
        # Register an agent and submit a task
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        task_id = await agent_manager.submit_task("test_agent", "research", {"query": "test query"})
        
        # Check task status
        task = agent_manager.tasks.get(task_id)
        assert task is not None
        assert task.status == TaskStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_agent_performance_monitoring(self, agent_manager):
        """Test agent performance monitoring."""
        # Register an agent
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        # Get performance stats
        stats = agent_manager.get_stats()
        assert isinstance(stats, dict)
        assert 'total_agents' in stats


class TestPerformance:
    """Test performance characteristics."""
    
    def test_agent_manager_performance(self, agent_manager):
        """Test agent manager performance."""
        # Basic performance test
        start_time = datetime.now()
        
        # Perform some operations
        stats = agent_manager.get_stats()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        assert duration < 1.0  # Should complete quickly
        assert isinstance(stats, dict)
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, agent_manager):
        """Test concurrent agent operations."""
        # Register multiple agents concurrently
        tasks = []
        for i in range(5):
            agent_info = AgentInfo(
                agent_id=f"agent_{i}",
                agent_type="research",
                capabilities=["research", "analysis"],
                status=AgentStatus.IDLE,
                created_at=datetime.now()
            )
            agent_manager.register_agent(agent_info, f"agent_{i}", "research", ["research", "analysis"])
        
        # All agents registered synchronously
        
        # Check that all agents were registered
        assert len(agent_manager.agents) == 5
    
    @pytest.mark.asyncio
    async def test_large_scale_task_processing(self, agent_manager):
        """Test large scale task processing."""
        # Register an agent
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        # Submit multiple tasks
        task_ids = []
        for i in range(10):
            task_id = await agent_manager.submit_task("test_agent", "research", {"query": f"test query {i}"})
            task_ids.append(task_id)
        
        # Check that all tasks were submitted
        assert len(task_ids) == 10
        assert all(task_id is not None for task_id in task_ids)


class TestIntegration:
    """Test integration with other components."""
    
    @pytest.mark.asyncio
    async def test_memory_manager_integration(self, agent_manager):
        """Test integration with memory manager."""
        from memory_manager import MemoryManager
        
        memory_manager = MemoryManager()
        
        # Register an agent
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        # Basic integration test
        assert agent_manager is not None
        assert memory_manager is not None
    
    @pytest.mark.asyncio
    async def test_llm_client_integration(self, agent_manager):
        """Test integration with LLM client."""
        from llm_client import LLMClient
        
        llm_client = LLMClient()
        
        # Register an agent
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        # Basic integration test
        assert agent_manager is not None
        assert llm_client is not None
    
    @pytest.mark.asyncio
    async def test_tool_manager_integration(self, agent_manager):
        """Test integration with tool manager."""
        from tool_manager import ToolManager
        
        tool_manager = ToolManager()
        
        # Register an agent
        agent_info = AgentInfo(
            agent_id="test_agent",
            agent_type="research",
            capabilities=["research", "analysis"],
            status=AgentStatus.IDLE,
            created_at=datetime.now()
        )
        agent_manager.register_agent(agent_info, "test_agent", "research", ["research", "analysis"])
        
        # Basic integration test
        assert agent_manager is not None
        assert tool_manager is not None