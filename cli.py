"""
CLI Module

Command-line interface for the non-fiction book-writing system.
Provides full access to all system capabilities through CLI commands.

Chosen libraries:
- Click: Command-line interface framework
- asyncio: Asynchronous operations
- logging: CLI activity logging

Adapted from: Click documentation (https://click.palletsprojects.com/)
Pattern: Nested command structure with comprehensive help
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click

# Import system modules
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLIContext:
    """Context object for CLI commands."""
    
    def __init__(self):
        self.system_initialized = False
        self.memory_manager = None
        self.llm_client = None
        self.tool_manager = None
        self.agent_manager = None
        self.research_agent = None
        self.writer_agent = None
        self.editor_agent = None
        self.tool_agent = None
        self.book_builder = None


pass_context = click.make_pass_decorator(CLIContext, ensure=True)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', help='Configuration file path')
@pass_context
def cli(ctx, verbose, config):
    """Non-Fiction Book-Writing System CLI
    
    A production-capable system for generating non-fiction books using RAG,
    multi-agent orchestration, and MCP-style tooling.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration if provided
    if config and Path(config).exists():
        # TODO: Implement configuration loading
        pass


@cli.command()
@click.option('--openai-key', envvar='LLM_REMOTE_API_KEY', help='OpenAI API key')
@click.option('--ollama-url', envvar='OLLAMA_LOCAL_URL', default='http://localhost:11434', help='Ollama server URL')
@click.option('--embedding-key', envvar='EMBEDDING_API_KEY', help='Embedding API key')
@click.option('--vector-db-path', envvar='VECTOR_DB_PATH', default='./memory_db', help='Vector database path')
@click.option('--allow-unsafe', envvar='TOOL_MANAGER_ALLOW_UNSAFE', is_flag=True, help='Allow unsafe tools')
@pass_context
def init(ctx, openai_key, ollama_url, embedding_key, vector_db_path, allow_unsafe):
    """Initialize the book-writing system."""
    try:
        click.echo("Initializing book-writing system...")
        
        # Initialize memory manager
        ctx.memory_manager = MemoryManager(
            persist_directory=vector_db_path,
            use_remote_embeddings=bool(embedding_key),
            openai_api_key=embedding_key
        )
        
        # Initialize LLM client
        ctx.llm_client = LLMClient(
            primary_provider="openai" if openai_key else "ollama",
            openai_api_key=openai_key,
            ollama_url=ollama_url
        )
        
        # Initialize tool manager
        ctx.tool_manager = ToolManager(
            allow_unsafe=allow_unsafe,
            allow_restricted=True
        )
        
        # Initialize agent manager
        ctx.agent_manager = AgentManager()
        await ctx.agent_manager.start()
        
        # Initialize agents
        ctx.research_agent = ResearchAgent(
            agent_id="research_agent",
            memory_manager=ctx.memory_manager,
            llm_client=ctx.llm_client,
            tool_manager=ctx.tool_manager
        )
        
        ctx.writer_agent = WriterAgent(
            agent_id="writer_agent",
            memory_manager=ctx.memory_manager,
            llm_client=ctx.llm_client,
            research_agent=ctx.research_agent,
            writing_style=WritingStyle()
        )
        
        ctx.editor_agent = EditorAgent(
            agent_id="editor_agent",
            llm_client=ctx.llm_client,
            style_guide=StyleGuide()
        )
        
        ctx.tool_agent = ToolAgent(
            agent_id="tool_agent",
            tool_manager=ctx.tool_manager
        )
        
        # Register agents
        ctx.agent_manager.register_agent(
            ctx.research_agent, "research_agent", "research", 
            ["research", "web_search", "information_gathering"]
        )
        ctx.agent_manager.register_agent(
            ctx.writer_agent, "writer_agent", "writer",
            ["writing", "drafting", "content_generation"]
        )
        ctx.agent_manager.register_agent(
            ctx.editor_agent, "editor_agent", "editor",
            ["editing", "review", "quality_assurance"]
        )
        ctx.agent_manager.register_agent(
            ctx.tool_agent, "tool_agent", "tool",
            ["tool_execution", "automation"]
        )
        
        # Initialize book builder
        ctx.book_builder = BookBuilder(
            agent_manager=ctx.agent_manager,
            memory_manager=ctx.memory_manager,
            research_agent=ctx.research_agent,
            writer_agent=ctx.writer_agent,
            editor_agent=ctx.editor_agent,
            tool_agent=ctx.tool_agent
        )
        
        ctx.system_initialized = True
        
        click.echo("✅ System initialized successfully!")
        click.echo(f"Memory database: {vector_db_path}")
        click.echo(f"LLM provider: {'OpenAI' if openai_key else 'Ollama'}")
        click.echo(f"Unsafe tools: {'Enabled' if allow_unsafe else 'Disabled'}")
        
    except Exception as e:
        click.echo(f"❌ Failed to initialize system: {e}", err=True)
        sys.exit(1)


@cli.group()
@pass_context
def ingest(ctx):
    """Document ingestion commands."""
    if not ctx.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        sys.exit(1)


@ingest.command()
@click.argument('file_path', type=click.Path(exists=True))
@pass_context
def document(ctx, file_path):
    """Ingest a single document."""
    try:
        ingestor = DocumentIngestor()
        
        async def ingest_doc():
            metadata, chunks = await ingestor.ingest_document(file_path)
            
            # Store in memory
            chunk_ids = await ctx.memory_manager.store_document_chunks(
                metadata, chunks, "cli_user"
            )
            
            click.echo(f"✅ Ingested document: {metadata.original_filename}")
            click.echo(f"   Chunks: {len(chunks)}")
            click.echo(f"   Word count: {sum(c.word_count for c in chunks)}")
            click.echo(f"   Stored chunk IDs: {len(chunk_ids)}")
        
        asyncio.run(ingest_doc())
        
    except Exception as e:
        click.echo(f"❌ Failed to ingest document: {e}", err=True)
        sys.exit(1)


@ingest.command()
@click.argument('directory_path', type=click.Path(exists=True, file_okay=False))
@pass_context
def directory(ctx, directory_path):
    """Ingest all documents in a directory."""
    try:
        ingestor = DocumentIngestor()
        
        async def ingest_dir():
            results = await ingestor.ingest_directory(directory_path)
            
            total_chunks = 0
            total_words = 0
            
            for metadata, chunks in results:
                chunk_ids = await ctx.memory_manager.store_document_chunks(
                    metadata, chunks, "cli_user"
                )
                total_chunks += len(chunks)
                total_words += sum(c.word_count for c in chunks)
            
            click.echo(f"✅ Ingested {len(results)} documents from {directory_path}")
            click.echo(f"   Total chunks: {total_chunks}")
            click.echo(f"   Total words: {total_words}")
        
        asyncio.run(ingest_dir())
        
    except Exception as e:
        click.echo(f"❌ Failed to ingest directory: {e}", err=True)
        sys.exit(1)


@cli.group()
@pass_context
def research(ctx):
    """Research commands."""
    if not ctx.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        sys.exit(1)


@research.command()
@click.argument('topic')
@click.option('--description', help='Research description')
@click.option('--keywords', help='Comma-separated keywords')
@click.option('--priority', type=int, default=1, help='Research priority (1-10)')
@pass_context
def start(ctx, topic, description, keywords, priority):
    """Start research on a topic."""
    try:
        async def start_research():
            topic_id = await ctx.research_agent.start_research(
                topic_title=topic,
                description=description or f"Research on {topic}",
                keywords=keywords.split(',') if keywords else [],
                priority=priority
            )
            
            click.echo(f"✅ Started research: {topic}")
            click.echo(f"   Topic ID: {topic_id}")
        
        asyncio.run(start_research())
        
    except Exception as e:
        click.echo(f"❌ Failed to start research: {e}", err=True)
        sys.exit(1)


@research.command()
@click.argument('topic_id')
@pass_context
def status(ctx, topic_id):
    """Get research status and results."""
    try:
        async def get_status():
            # Get research summary
            summary = await ctx.research_agent.get_research_summary(topic_id)
            if summary:
                click.echo(f"Research Summary: {summary.title}")
                click.echo(f"Overview: {summary.overview}")
                click.echo(f"Key Findings: {len(summary.key_findings)}")
                for finding in summary.key_findings[:5]:
                    click.echo(f"  - {finding}")
            else:
                click.echo("Research not found or still in progress")
        
        asyncio.run(get_status())
        
    except Exception as e:
        click.echo(f"❌ Failed to get research status: {e}", err=True)
        sys.exit(1)


@cli.group()
@pass_context
def book(ctx):
    """Book management commands."""
    if not ctx.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        sys.exit(1)


@book.command()
@click.argument('title')
@click.option('--author', required=True, help='Author name')
@click.option('--description', required=True, help='Book description')
@click.option('--audience', default='general', help='Target audience')
@click.option('--word-count', type=int, default=50000, help='Estimated word count')
@pass_context
def create(ctx, title, author, description, audience, word_count):
    """Create a new book project."""
    try:
        async def create_book():
            book_id = await ctx.book_builder.create_book(
                title=title,
                author=author,
                description=description,
                target_audience=audience,
                estimated_word_count=word_count
            )
            
            click.echo(f"✅ Created book: {title}")
            click.echo(f"   Book ID: {book_id}")
            click.echo(f"   Author: {author}")
            click.echo(f"   Target audience: {audience}")
            click.echo(f"   Estimated words: {word_count:,}")
        
        asyncio.run(create_book())
        
    except Exception as e:
        click.echo(f"❌ Failed to create book: {e}", err=True)
        sys.exit(1)


@book.command()
@click.argument('book_id')
@click.option('--chapters', type=int, default=10, help='Number of chapters')
@click.option('--topics', help='Comma-separated research topics')
@pass_context
def outline(ctx, book_id, chapters, topics):
    """Generate book outline."""
    try:
        async def generate_outline():
            research_topics = topics.split(',') if topics else []
            outline_id = await ctx.book_builder.generate_book_outline(
                book_id=book_id,
                chapter_count=chapters,
                research_topics=research_topics
            )
            
            click.echo(f"✅ Generated outline for book {book_id}")
            click.echo(f"   Outline ID: {outline_id}")
            click.echo(f"   Chapters: {chapters}")
        
        asyncio.run(generate_outline())
        
    except Exception as e:
        click.echo(f"❌ Failed to generate outline: {e}", err=True)
        sys.exit(1)


@book.command()
@click.argument('book_id')
@click.option('--chapters', help='Comma-separated chapter numbers to build')
@pass_context
def build(ctx, book_id, chapters):
    """Build a book (generate all chapters)."""
    try:
        async def build_book():
            chapters_to_build = None
            if chapters:
                chapters_to_build = [int(c.strip()) for c in chapters.split(',')]
            
            build_id = await ctx.book_builder.build_book(
                book_id=book_id,
                chapters_to_build=chapters_to_build
            )
            
            click.echo(f"✅ Started book build: {book_id}")
            click.echo(f"   Build ID: {build_id}")
            click.echo("   Use 'book status' to check progress")
        
        asyncio.run(build_book())
        
    except Exception as e:
        click.echo(f"❌ Failed to start book build: {e}", err=True)
        sys.exit(1)


@book.command()
@click.argument('book_id')
@pass_context
def status(ctx, book_id):
    """Get book build status."""
    try:
        async def get_status():
            status = await ctx.book_builder.get_book_status(book_id)
            
            if "error" in status:
                click.echo(f"❌ {status['error']}")
                return
            
            click.echo(f"Book: {status['title']}")
            click.echo(f"Chapters: {status['completed_chapters']}/{status['total_chapters']} completed")
            click.echo(f"In progress: {status['in_progress_chapters']}")
            click.echo(f"Failed: {status['failed_chapters']}")
            click.echo("")
            
            for chapter in status['chapters']:
                status_icon = {
                    'final': '✅',
                    'in_progress': '🔄',
                    'draft': '📝',
                    'planned': '⏳',
                    'failed': '❌'
                }.get(chapter['status'], '❓')
                
                click.echo(f"  {status_icon} {chapter['order']}. {chapter['title']} ({chapter['word_count']}/{chapter['target_word_count']} words)")
        
        asyncio.run(get_status())
        
    except Exception as e:
        click.echo(f"❌ Failed to get book status: {e}", err=True)
        sys.exit(1)


@book.command()
@click.argument('book_id')
@click.option('--format', type=click.Choice(['markdown', 'docx', 'pdf']), default='markdown', help='Export format')
@click.option('--no-bibliography', is_flag=True, help='Exclude bibliography')
@pass_context
def export(ctx, book_id, format, no_bibliography):
    """Export book to file."""
    try:
        async def export_book():
            output_path = await ctx.book_builder.export_book(
                book_id=book_id,
                format=format,
                include_bibliography=not no_bibliography
            )
            
            click.echo(f"✅ Exported book to {format.upper()}")
            click.echo(f"   Output: {output_path}")
        
        asyncio.run(export_book())
        
    except Exception as e:
        click.echo(f"❌ Failed to export book: {e}", err=True)
        sys.exit(1)


@cli.group()
@pass_context
def tools(ctx):
    """Tool management commands."""
    if not ctx.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        sys.exit(1)


@tools.command()
@pass_context
def list(ctx):
    """List available tools."""
    try:
        async def list_tools():
            tools = await ctx.tool_agent.get_available_tools()
            
            click.echo("Available Tools:")
            click.echo("")
            
            for tool in tools:
                click.echo(f"  {tool.tool_name}")
                click.echo(f"    Category: {tool.category}")
                click.echo(f"    Description: {tool.description}")
                click.echo("")
        
        asyncio.run(list_tools())
        
    except Exception as e:
        click.echo(f"❌ Failed to list tools: {e}", err=True)
        sys.exit(1)


@tools.command()
@click.argument('tool_name')
@click.argument('parameters', nargs=-1)
@pass_context
def execute(ctx, tool_name, parameters):
    """Execute a tool."""
    try:
        async def execute_tool():
            # Parse parameters (simple key=value format)
            params = {}
            for param in parameters:
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
                else:
                    params['query'] = param  # Default parameter for search tools
            
            request_id = await ctx.tool_agent.execute_tool(
                tool_name=tool_name,
                parameters=params
            )
            
            click.echo(f"✅ Started tool execution: {tool_name}")
            click.echo(f"   Request ID: {request_id}")
            
            # Wait for completion and show result
            result = await ctx.tool_agent.get_execution_result(request_id)
            if result:
                click.echo(f"   Status: {result.status}")
                if result.output:
                    click.echo(f"   Output: {result.output}")
                if result.error_message:
                    click.echo(f"   Error: {result.error_message}")
        
        asyncio.run(execute_tool())
        
    except Exception as e:
        click.echo(f"❌ Failed to execute tool: {e}", err=True)
        sys.exit(1)


@cli.command()
@pass_context
def status(ctx):
    """Show system status."""
    if not ctx.system_initialized:
        click.echo("❌ System not initialized")
        return
    
    try:
        # Get memory stats
        memory_stats = ctx.memory_manager.get_stats()
        
        # Get agent stats
        agent_stats = ctx.agent_manager.get_stats()
        
        # Get tool stats
        tool_stats = ctx.tool_manager.get_execution_stats()
        
        click.echo("System Status:")
        click.echo(f"  Memory: {memory_stats['total_chunks']} chunks")
        click.echo(f"  Agents: {agent_stats['total_agents']} registered")
        click.echo(f"  Tasks: {agent_stats['running_tasks']} running, {agent_stats['total_tasks']} total")
        click.echo(f"  Tools: {tool_stats['available_tools']} available")
        
    except Exception as e:
        click.echo(f"❌ Failed to get system status: {e}", err=True)


@cli.command()
@pass_context
def cleanup(ctx):
    """Clean up system resources."""
    try:
        async def cleanup_system():
            if ctx.agent_manager:
                await ctx.agent_manager.stop()
            if ctx.tool_agent:
                await ctx.tool_agent.cleanup()
            
            click.echo("✅ System cleanup completed")
        
        asyncio.run(cleanup_system())
        
    except Exception as e:
        click.echo(f"❌ Failed to cleanup system: {e}", err=True)


if __name__ == '__main__':
    cli()