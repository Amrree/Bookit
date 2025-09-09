"""
Test Book Workflow

Test script to demonstrate the complete book production workflow.
This creates a sample book to verify all components work together.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append('.')

from document_ingestor import DocumentIngestor
from memory_manager import MemoryManager
from llm_client import LLMClient
from tool_manager import ToolManager
from agent_manager import AgentManager
from research_agent import ResearchAgent
from writer_agent import WriterAgent, WritingStyle
from editor_agent import EditorAgent, StyleGuide
from tool_agent import ToolAgent
from book_builder import BookBuilder
from book_workflow import BookWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_book_workflow():
    """Test the complete book workflow with a sample book."""
    
    print("🚀 Starting Book Workflow Test")
    print("=" * 50)
    
    try:
        # Initialize system components
        print("📋 Initializing system components...")
        
        memory_manager = MemoryManager(
            persist_directory="./test_memory_db",
            use_remote_embeddings=False  # Use local embeddings for testing
        )
        
        llm_client = LLMClient(
            primary_provider="ollama",  # Use Ollama for testing
            ollama_url="http://localhost:11434"
        )
        
        tool_manager = ToolManager(
            allow_unsafe=False,
            allow_restricted=True
        )
        
        agent_manager = AgentManager()
        await agent_manager.start()
        
        # Initialize agents
        research_agent = ResearchAgent(
            agent_id="research_agent",
            memory_manager=memory_manager,
            llm_client=llm_client,
            tool_manager=tool_manager
        )
        
        writer_agent = WriterAgent(
            agent_id="writer_agent",
            memory_manager=memory_manager,
            llm_client=llm_client,
            research_agent=research_agent,
            writing_style=WritingStyle()
        )
        
        editor_agent = EditorAgent(
            agent_id="editor_agent",
            llm_client=llm_client,
            style_guide=StyleGuide()
        )
        
        tool_agent = ToolAgent(
            agent_id="tool_agent",
            tool_manager=tool_manager
        )
        
        book_builder = BookBuilder(
            agent_manager=agent_manager,
            memory_manager=memory_manager,
            research_agent=research_agent,
            writer_agent=writer_agent,
            editor_agent=editor_agent,
            tool_agent=tool_agent
        )
        
        # Initialize book workflow
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
        
        print("✅ System components initialized")
        
        # Create sample reference document
        print("\n📄 Creating sample reference document...")
        sample_doc_path = "test_reference.txt"
        with open(sample_doc_path, 'w') as f:
            f.write("""
# Artificial Intelligence and Machine Learning

## Introduction to AI
Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. The field has evolved significantly since its inception in the 1950s.

## Machine Learning Fundamentals
Machine Learning is a subset of AI that focuses on algorithms that can learn from data. There are three main types:
1. Supervised Learning
2. Unsupervised Learning  
3. Reinforcement Learning

## Deep Learning
Deep Learning uses neural networks with multiple layers to process data. It has revolutionized fields like computer vision and natural language processing.

## Applications
AI and ML are being applied across numerous industries:
- Healthcare: Medical diagnosis and drug discovery
- Finance: Fraud detection and algorithmic trading
- Transportation: Autonomous vehicles
- Technology: Search engines and recommendation systems

## Future Implications
The future of AI holds both promise and challenges. As systems become more capable, questions about ethics, safety, and societal impact become increasingly important.
            """)
        
        print(f"✅ Sample reference document created: {sample_doc_path}")
        
        # Start book production
        print("\n🚀 Starting book production...")
        print("Title: The Future of Artificial Intelligence")
        print("Theme: AI and Machine Learning")
        print("Target: 10,000 words in 5 chapters")
        print("References: 1 document")
        
        book_metadata = await workflow.start_book_production(
            title="The Future of Artificial Intelligence",
            theme="AI and Machine Learning",
            reference_documents=[sample_doc_path],
            target_word_count=10000,  # Smaller target for testing
            chapters_count=5,
            author="AI Book Writer"
        )
        
        # Display results
        print("\n✅ Book production completed!")
        print("=" * 50)
        print(f"📖 Title: {book_metadata.title}")
        print(f"👤 Author: {book_metadata.author}")
        print(f"📝 Word count: {book_metadata.word_count:,}")
        print(f"📚 Chapters: {len(book_metadata.chapters)}")
        print(f"🔗 References: {len(book_metadata.bibliography)}")
        print(f"🆔 Build ID: {book_metadata.build_id}")
        print(f"📁 Output: output/{book_metadata.build_id}/")
        
        # Show chapter breakdown
        print("\n📋 Chapter Breakdown:")
        for chapter in book_metadata.chapters:
            status_icon = "✅" if chapter.status == "completed" else "⏳"
            print(f"  {status_icon} Chapter {chapter.chapter_number}: {chapter.title} ({chapter.actual_word_count:,} words)")
        
        # Check output files
        output_dir = Path(f"output/{book_metadata.build_id}")
        if output_dir.exists():
            print(f"\n📁 Output Files:")
            for file_path in output_dir.iterdir():
                if file_path.is_file():
                    file_size = file_path.stat().st_size
                    print(f"  📄 {file_path.name} ({file_size:,} bytes)")
        
        # Cleanup
        print("\n🧹 Cleaning up test files...")
        if os.path.exists(sample_doc_path):
            os.remove(sample_doc_path)
        
        # Clean up memory database
        import shutil
        if os.path.exists("./test_memory_db"):
            shutil.rmtree("./test_memory_db")
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Test failed with exception")
        raise


async def test_workflow_components():
    """Test individual workflow components."""
    
    print("\n🔧 Testing Workflow Components")
    print("=" * 30)
    
    try:
        # Test memory manager
        print("Testing MemoryManager...")
        memory_manager = MemoryManager(persist_directory="./test_memory")
        
        # Add test memory
        await memory_manager.add_memory(
            content="Test content for workflow testing",
            metadata={"type": "test", "source": "workflow_test"}
        )
        
        stats = memory_manager.get_stats()
        print(f"  ✅ MemoryManager: {stats['total_chunks']} chunks")
        
        # Test LLM client
        print("Testing LLMClient...")
        llm_client = LLMClient(primary_provider="ollama")
        
        # Test simple completion
        try:
            result = await llm_client.generate_completion(
                prompt="What is artificial intelligence?",
                max_tokens=50
            )
            print(f"  ✅ LLMClient: Generated {len(result.get('content', ''))} characters")
        except Exception as e:
            print(f"  ⚠️  LLMClient: {e} (Ollama may not be running)")
        
        # Test tool manager
        print("Testing ToolManager...")
        tool_manager = ToolManager()
        tool_stats = tool_manager.get_execution_stats()
        print(f"  ✅ ToolManager: {tool_stats['available_tools']} tools available")
        
        # Cleanup
        import shutil
        if os.path.exists("./test_memory"):
            shutil.rmtree("./test_memory")
        
        print("✅ Component tests completed")
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        logger.exception("Component test failed")


if __name__ == "__main__":
    print("🧪 Book Workflow Test Suite")
    print("=" * 50)
    
    # Run component tests first
    asyncio.run(test_workflow_components())
    
    # Ask user if they want to run full workflow test
    print("\n" + "=" * 50)
    response = input("Run full book workflow test? This will create a complete book. (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        print("\n🚀 Starting full workflow test...")
        asyncio.run(test_book_workflow())
    else:
        print("Skipping full workflow test.")
    
    print("\n✅ Test suite completed!")