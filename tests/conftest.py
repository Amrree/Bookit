"""
Pytest configuration and shared fixtures for the book-writing system tests.
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import json
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_manager import MemoryManager
from llm_client import LLMClient
from tool_manager import ToolManager
from agent_manager import AgentManager
from research_agent import ResearchAgent
from writer_agent import WriterAgent
from editor_agent import EditorAgent
from tool_agent import ToolAgent
from book_builder import BookBuilder
from document_ingestor import DocumentIngestor
from book_workflow import BookWorkflow
from full_book_generator import FullBookGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
async def memory_manager(temp_dir):
    """Create a MemoryManager instance for testing."""
    memory = MemoryManager()
    await memory.initialize()
    yield memory
    await memory.close()


@pytest.fixture
async def llm_client():
    """Create an LLMClient instance for testing."""
    client = LLMClient()
    yield client


@pytest.fixture
async def tool_manager():
    """Create a ToolManager instance for testing."""
    manager = ToolManager()
    await manager.initialize()
    yield manager
    await manager.close()


@pytest.fixture
async def agent_manager(memory_manager, llm_client, tool_manager):
    """Create an AgentManager instance for testing."""
    manager = AgentManager(
        memory_manager=memory_manager,
        llm_client=llm_client,
        tool_manager=tool_manager
    )
    await manager.start()
    yield manager
    await manager.stop()


@pytest.fixture
async def research_agent(agent_manager):
    """Create a ResearchAgent instance for testing."""
    return agent_manager.research_agent


@pytest.fixture
async def writer_agent(agent_manager):
    """Create a WriterAgent instance for testing."""
    return agent_manager.writer_agent


@pytest.fixture
async def editor_agent(agent_manager):
    """Create an EditorAgent instance for testing."""
    return agent_manager.editor_agent


@pytest.fixture
async def tool_agent(agent_manager):
    """Create a ToolAgent instance for testing."""
    return agent_manager.tool_agent


@pytest.fixture
async def book_builder(memory_manager, llm_client):
    """Create a BookBuilder instance for testing."""
    builder = BookBuilder(memory_manager=memory_manager, llm_client=llm_client)
    yield builder


@pytest.fixture
async def document_ingestor(memory_manager):
    """Create a DocumentIngestor instance for testing."""
    ingestor = DocumentIngestor(memory_manager=memory_manager)
    yield ingestor


@pytest.fixture
async def book_workflow(agent_manager, book_builder):
    """Create a BookWorkflow instance for testing."""
    workflow = BookWorkflow(
        agent_manager=agent_manager,
        book_builder=book_builder,
        llm_client=agent_manager.llm_client
    )
    yield workflow


@pytest.fixture
async def full_book_generator(agent_manager, book_builder):
    """Create a FullBookGenerator instance for testing."""
    generator = FullBookGenerator(
        agent_manager=agent_manager,
        book_builder=book_builder,
        llm_client=agent_manager.llm_client
    )
    yield generator


@pytest.fixture
def sample_documents(temp_dir):
    """Create sample documents for testing."""
    docs = {}
    
    # Sample PDF content (simulated)
    pdf_content = """
    # Introduction to Machine Learning
    
    Machine learning is a subset of artificial intelligence that focuses on algorithms
    that can learn from data. This document covers the fundamentals of ML including
    supervised learning, unsupervised learning, and reinforcement learning.
    
    ## Supervised Learning
    
    Supervised learning uses labeled training data to learn a mapping from inputs
    to outputs. Common algorithms include linear regression, decision trees, and
    neural networks.
    
    ## Unsupervised Learning
    
    Unsupervised learning finds patterns in data without labeled examples.
    Clustering and dimensionality reduction are common techniques.
    """
    
    # Sample Markdown content
    markdown_content = """
    # The Future of Artificial Intelligence
    
    Artificial intelligence is rapidly evolving and will shape our future in
    profound ways. This article explores the current state of AI and its
    potential impact on society.
    
    ## Current Applications
    
    AI is already being used in healthcare, finance, transportation, and
    many other industries. The technology is becoming more accessible
    and powerful every day.
    
    ## Ethical Considerations
    
    As AI becomes more powerful, we must consider the ethical implications
    of its use. Issues include bias, privacy, and the potential for misuse.
    """
    
    # Sample TXT content
    txt_content = """
    Data Science Fundamentals
    
    Data science combines statistics, programming, and domain expertise to
    extract insights from data. It involves data collection, cleaning,
    analysis, and visualization.
    
    Key Skills:
    - Programming (Python, R)
    - Statistics and Mathematics
    - Machine Learning
    - Data Visualization
    - Domain Knowledge
    
    Tools and Technologies:
    - Python libraries (pandas, numpy, scikit-learn)
    - R programming language
    - SQL databases
    - Cloud platforms (AWS, GCP, Azure)
    """
    
    # Create sample files
    pdf_file = temp_dir / "sample_ml.pdf"
    markdown_file = temp_dir / "sample_ai.md"
    txt_file = temp_dir / "sample_ds.txt"
    
    # Write content to files
    pdf_file.write_text(pdf_content)
    markdown_file.write_text(markdown_content)
    txt_file.write_text(txt_content)
    
    docs = {
        "pdf": pdf_file,
        "markdown": markdown_file,
        "txt": txt_file
    }
    
    return docs


@pytest.fixture
def test_book_metadata():
    """Sample book metadata for testing."""
    return {
        "title": "Test Book: A Comprehensive Guide",
        "theme": "Technology and Society",
        "author": "Test Author",
        "word_count_target": 10000,
        "chapters_count": 5,
        "build_id": "test_book_001"
    }


@pytest.fixture
def mock_llm_responses():
    """Mock LLM responses for testing."""
    return {
        "research_summary": "This is a comprehensive research summary covering the main topics and key findings.",
        "chapter_content": "This is a detailed chapter covering the specified topic with proper structure and flow.",
        "editing_suggestions": "Here are some suggestions to improve clarity and flow in the text.",
        "outline": {
            "introduction": "Introduction to the topic",
            "chapters": [
                {"title": "Chapter 1", "key_points": ["Point 1", "Point 2"]},
                {"title": "Chapter 2", "key_points": ["Point 3", "Point 4"]}
            ],
            "conclusion": "Conclusion and future directions"
        }
    }


@pytest.fixture
def performance_metrics():
    """Performance metrics tracking for tests."""
    return {
        "embedding_time": [],
        "retrieval_time": [],
        "llm_response_time": [],
        "memory_operations": [],
        "agent_coordination_time": []
    }


@pytest.fixture
def test_results_logger():
    """Logger for test results and analysis."""
    class TestResultsLogger:
        def __init__(self):
            self.results = []
            self.failures = []
            self.warnings = []
            self.performance_metrics = {}
        
        def log_test_result(self, test_name: str, status: str, details: Dict[str, Any]):
            self.results.append({
                "test_name": test_name,
                "status": status,
                "details": details,
                "timestamp": asyncio.get_event_loop().time()
            })
        
        def log_failure(self, test_name: str, error: str, context: Dict[str, Any]):
            self.failures.append({
                "test_name": test_name,
                "error": error,
                "context": context,
                "timestamp": asyncio.get_event_loop().time()
            })
        
        def log_warning(self, test_name: str, warning: str, context: Dict[str, Any]):
            self.warnings.append({
                "test_name": test_name,
                "warning": warning,
                "context": context,
                "timestamp": asyncio.get_event_loop().time()
            })
        
        def get_summary(self):
            return {
                "total_tests": len(self.results),
                "passed": len([r for r in self.results if r["status"] == "passed"]),
                "failed": len(self.failures),
                "warnings": len(self.warnings),
                "results": self.results,
                "failures": self.failures,
                "warnings": self.warnings
            }
    
    return TestResultsLogger()