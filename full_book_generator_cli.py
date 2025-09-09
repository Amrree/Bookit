#!/usr/bin/env python3
"""
CLI interface for the full_book_generator module.

This script provides a command-line interface for generating complete books
using the LibriScribe integration and multi-agent coordination.
"""

import asyncio
import argparse
import logging
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


async def generate_full_book(
    title: str,
    theme: str,
    target_word_count: int = 50000,
    chapters_count: int = 12,
    author: str = "AI Book Writer",
    genre: str = "Non-Fiction",
    language: str = "English",
    reference_documents: list = None
):
    """Generate a complete book using the full book generator."""
    
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
        from full_book_generator import SystemIntegration
        
        logger.info("Initializing system components...")
        
        # Initialize system components
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
        
        logger.info(f"Starting book generation: '{title}'")
        
        # Generate the book
        result = await system_integration.generate_full_book(
            title=title,
            theme=theme,
            target_word_count=target_word_count,
            chapters_count=chapters_count,
            author=author,
            genre=genre,
            language=language,
            reference_documents=reference_documents or []
        )
        
        if result["success"]:
            book_metadata = result["book_metadata"]
            logger.info(f"✓ Book generated successfully!")
            logger.info(f"  Title: {book_metadata['title']}")
            logger.info(f"  Author: {book_metadata['author']}")
            logger.info(f"  Word Count: {book_metadata['word_count']:,}")
            logger.info(f"  Chapters: {book_metadata['chapter_count']}")
            logger.info(f"  Output Directory: {result['output_directory']}")
            logger.info(f"  Formats Available: {', '.join(result['formats_available'])}")
            logger.info(f"  Build Log: {result['build_log_path']}")
            
            return True
        else:
            logger.error(f"✗ Book generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error during book generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            await agent_manager.stop()
            await system_integration.cleanup_resources()
        except:
            pass


async def test_integration():
    """Test the integration components."""
    
    try:
        logger.info("Testing full book generator integration...")
        
        # Import test components
        from full_book_generator import SystemIntegration
        from memory_manager import MemoryManager
        from llm_client import LLMClient
        from tool_manager import ToolManager
        from agent_manager import AgentManager
        from research_agent import ResearchAgent
        from writer_agent import WriterAgent
        from editor_agent import EditorAgent
        from tool_agent import ToolAgent
        from book_builder import BookBuilder
        
        # Initialize system components
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
        status = system_integration.get_integration_status()
        logger.info(f"Integration status: {status}")
        
        # Test available commands
        commands = system_integration.get_available_commands()
        logger.info(f"Available commands: {len(commands)}")
        
        logger.info("✓ Integration test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            await agent_manager.stop()
            await system_integration.cleanup_resources()
        except:
            pass


def main():
    """Main CLI function."""
    
    parser = argparse.ArgumentParser(
        description="Full Book Generator CLI - Generate complete books using LibriScribe integration"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a complete book')
    generate_parser.add_argument('--title', required=True, help='Book title')
    generate_parser.add_argument('--theme', required=True, help='Book theme/topic')
    generate_parser.add_argument('--target-word-count', type=int, default=50000, help='Target word count (default: 50000)')
    generate_parser.add_argument('--chapters-count', type=int, default=12, help='Number of chapters (default: 12)')
    generate_parser.add_argument('--author', default='AI Book Writer', help='Author name (default: AI Book Writer)')
    generate_parser.add_argument('--genre', default='Non-Fiction', help='Book genre (default: Non-Fiction)')
    generate_parser.add_argument('--language', default='English', help='Book language (default: English)')
    generate_parser.add_argument('--reference-documents', nargs='*', help='Reference document paths')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test the integration')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == 'generate':
        # Ensure minimum word count
        target_word_count = max(args.target_word_count, 50000)
        
        logger.info("Starting book generation...")
        logger.info(f"  Title: {args.title}")
        logger.info(f"  Theme: {args.theme}")
        logger.info(f"  Target Word Count: {target_word_count:,}")
        logger.info(f"  Chapters: {args.chapters_count}")
        logger.info(f"  Author: {args.author}")
        logger.info(f"  Genre: {args.genre}")
        logger.info(f"  Language: {args.language}")
        if args.reference_documents:
            logger.info(f"  Reference Documents: {len(args.reference_documents)}")
        
        success = asyncio.run(generate_full_book(
            title=args.title,
            theme=args.theme,
            target_word_count=target_word_count,
            chapters_count=args.chapters_count,
            author=args.author,
            genre=args.genre,
            language=args.language,
            reference_documents=args.reference_documents
        ))
        
        sys.exit(0 if success else 1)
        
    elif args.command == 'test':
        logger.info("Testing integration...")
        success = asyncio.run(test_integration())
        sys.exit(0 if success else 1)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()