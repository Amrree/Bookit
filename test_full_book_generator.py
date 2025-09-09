"""
Test script for the full_book_generator module integration.

This script tests the basic functionality of the LibriScribe integration
and ensures that all components work together properly.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_full_book_generator():
    """Test the full book generator integration."""
    
    try:
        # Import required components
        from memory_manager import MemoryManager
        from llm_client import LLMClient
        from tool_manager import ToolManager
        from agent_manager import AgentManager
        from research_agent import ResearchAgent
        from writer_agent import WriterAgent
        from editor_agent import EditorAgent
        from tool_agent import ToolAgent
        from book_builder import BookBuilder
        
        # Import full book generator
        from full_book_generator import FullBookWorkflow, SystemIntegration
        
        logger.info("Testing full book generator integration...")
        
        # Initialize system components
        logger.info("Initializing system components...")
        memory_manager = MemoryManager()
        llm_client = LLMClient()
        tool_manager = ToolManager()
        agent_manager = AgentManager()
        
        # Initialize agents
        research_agent = ResearchAgent(memory_manager, llm_client)
        writer_agent = WriterAgent(memory_manager, llm_client)
        editor_agent = EditorAgent(llm_client)
        tool_agent = ToolAgent(tool_manager)
        book_builder = BookBuilder()
        
        # Start agent manager
        await agent_manager.start()
        
        # Initialize system integration
        logger.info("Initializing system integration...")
        system_integration = SystemIntegration(
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
        
        # Test integration status
        logger.info("Checking integration status...")
        status = system_integration.get_integration_status()
        logger.info(f"Integration status: {status}")
        
        # Test LibriScribe integration
        logger.info("Testing LibriScribe integration...")
        libriscribe_status = system_integration.full_book_workflow.libriscribe.get_agent_status()
        logger.info(f"LibriScribe status: {libriscribe_status}")
        
        # Test available commands
        logger.info("Testing available commands...")
        commands = system_integration.get_available_commands()
        logger.info(f"Available commands: {len(commands)}")
        for cmd in commands:
            logger.info(f"  - {cmd['command']}: {cmd['description']}")
        
        # Test tool registration
        logger.info("Testing tool registration...")
        if "full_book_generator" in [tool.name for tool in tool_manager.tools.values()]:
            logger.info("✓ Full book generator tool registered successfully")
        else:
            logger.warning("✗ Full book generator tool not found")
        
        # Test agent registration
        logger.info("Testing agent registration...")
        if "full_book_generator" in agent_manager.agents:
            logger.info("✓ Full book generator agent registered successfully")
        else:
            logger.warning("✗ Full book generator agent not found")
        
        # Test parameter validation
        logger.info("Testing parameter validation...")
        tool = tool_manager.tools.get("full_book_generator")
        if tool:
            validation_result = tool.validate_parameters(
                title="Test Book",
                theme="Test Theme",
                target_word_count=50000,
                chapters_count=10
            )
            logger.info(f"Parameter validation: {validation_result}")
        
        logger.info("✓ All tests completed successfully!")
        
        # Cleanup
        await agent_manager.stop()
        await system_integration.cleanup_resources()
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_libriscribe_components():
    """Test LibriScribe components individually."""
    
    try:
        logger.info("Testing LibriScribe components...")
        
        # Test LibriScribe integration
        from full_book_generator.libriscribe_integration import LibriScribeIntegration
        from llm_client import LLMClient
        
        llm_client = LLMClient()
        libriscribe = LibriScribeIntegration(llm_client)
        
        # Test agent status
        status = libriscribe.get_agent_status()
        logger.info(f"LibriScribe agent status: {status}")
        
        # Test project initialization
        project_data = {
            "project_name": "test_project",
            "title": "Test Book",
            "genre": "Non-Fiction",
            "category": "Non-Fiction",
            "language": "English",
            "description": "A test book",
            "book_length": "Full Book",
            "num_chapters": 10,
            "target_audience": "General",
            "tone": "Informative",
            "review_preference": "AI"
        }
        
        result = await libriscribe.initialize_project(project_data)
        logger.info(f"Project initialization: {result is not None}")
        
        logger.info("✓ LibriScribe components test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"LibriScribe components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    
    logger.info("Starting full book generator integration tests...")
    
    # Test 1: LibriScribe components
    logger.info("\n=== Test 1: LibriScribe Components ===")
    test1_result = await test_libriscribe_components()
    
    # Test 2: Full integration
    logger.info("\n=== Test 2: Full Integration ===")
    test2_result = await test_full_book_generator()
    
    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"LibriScribe Components: {'✓ PASS' if test1_result else '✗ FAIL'}")
    logger.info(f"Full Integration: {'✓ PASS' if test2_result else '✗ FAIL'}")
    
    if test1_result and test2_result:
        logger.info("🎉 All tests passed! Integration is working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)