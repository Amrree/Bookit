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
        self.book_builder = None
        self.document_ingestor = None


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
@click.pass_context
def cli(ctx, verbose, config):
    """Non-fiction book-writing system CLI."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    ctx.ensure_object(CLIContext)
    
    # Load configuration if provided
    if config and os.path.exists(config):
        # TODO: Implement configuration loading
        pass


@cli.command()
@click.option('--openai-key', help='OpenAI API key')
@click.option('--ollama-url', default='http://localhost:11434', help='Ollama API URL')
@click.option('--memory-dir', default='./memory_db', help='Memory database directory')
@click.option('--output-dir', default='./books', help='Book output directory')
@click.pass_context
def init(ctx, openai_key, ollama_url, memory_dir, output_dir):
    """Initialize the system with configuration."""
    try:
        # Initialize memory manager
        ctx.obj.memory_manager = MemoryManager(
            persist_directory=memory_dir,
            use_remote_embeddings=bool(openai_key),
            openai_api_key=openai_key
        )
        
        # Initialize LLM client
        ctx.obj.llm_client = LLMClient(
            provider="openai" if openai_key else "ollama",
            openai_api_key=openai_key,
            ollama_base_url=ollama_url
        )
        
        # Initialize tool manager
        ctx.obj.tool_manager = ToolManager()
        
        # Initialize document ingestor
        ctx.obj.document_ingestor = DocumentIngestor()
        
        # Initialize book builder
        ctx.obj.book_builder = BookBuilder(output_directory=output_dir)
        
        # Initialize agent manager
        ctx.obj.agent_manager = AgentManager(
            memory_manager=ctx.obj.memory_manager,
            llm_client=ctx.obj.llm_client,
            tool_manager=ctx.obj.tool_manager
        )
        
        ctx.obj.system_initialized = True
        
        click.echo("✅ System initialized successfully!")
        click.echo(f"Memory directory: {memory_dir}")
        click.echo(f"Output directory: {output_dir}")
        click.echo(f"LLM provider: {'OpenAI' if openai_key else 'Ollama'}")
        
    except Exception as e:
        click.echo(f"❌ Failed to initialize system: {e}", err=True)
        sys.exit(1)


@cli.group()
def memory():
    """Memory management commands."""
    pass


@memory.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--source-id', help='Custom source ID')
@click.pass_context
def ingest(ctx, file_path, source_id):
    """Ingest a document into memory."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    async def _ingest():
        try:
            metadata, chunks = await ctx.obj.document_ingestor.ingest_document(
                file_path, source_id
            )
            
            await ctx.obj.memory_manager.store_document_chunks(
                metadata, chunks, agent_id="cli"
            )
            
            click.echo(f"✅ Ingested {len(chunks)} chunks from {metadata.original_filename}")
            
        except Exception as e:
            click.echo(f"❌ Ingestion failed: {e}", err=True)
    
    asyncio.run(_ingest())


@memory.command()
@click.argument('query')
@click.option('--top-k', default=5, help='Number of results to return')
@click.pass_context
def search(ctx, query, top_k):
    """Search memory for relevant content."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    async def _search():
        try:
            results = await ctx.obj.memory_manager.retrieve_relevant_chunks(
                query, top_k=top_k
            )
            
            if not results:
                click.echo("No results found.")
                return
            
            for i, result in enumerate(results, 1):
                click.echo(f"\n--- Result {i} ---")
                click.echo(f"Score: {result.score:.3f}")
                click.echo(f"Source: {result.metadata.get('original_filename', 'Unknown')}")
                click.echo(f"Content: {result.content[:200]}...")
                
        except Exception as e:
            click.echo(f"❌ Search failed: {e}", err=True)
    
    asyncio.run(_search())


@cli.group()
def book():
    """Book management commands."""
    pass


@book.command()
@click.argument('title')
@click.option('--author', required=True, help='Book author')
@click.option('--description', required=True, help='Book description')
@click.option('--audience', required=True, help='Target audience')
@click.option('--word-count', default=50000, help='Estimated word count')
@click.pass_context
def create(ctx, title, author, description, audience, word_count):
    """Create a new book outline."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    async def _create():
        try:
            outline = await ctx.obj.book_builder.create_book_outline(
                title=title,
                author=author,
                description=description,
                target_audience=audience,
                estimated_word_count=word_count
            )
            
            click.echo(f"✅ Created book outline: {outline.title}")
            click.echo(f"Book ID: {outline.book_id}")
            
        except Exception as e:
            click.echo(f"❌ Book creation failed: {e}", err=True)
    
    asyncio.run(_create())


@book.command()
@click.argument('book_id')
@click.argument('chapter_title')
@click.option('--description', help='Chapter description')
@click.option('--word-count', default=3000, help='Estimated word count')
@click.pass_context
def add_chapter(ctx, book_id, chapter_title, description, word_count):
    """Add a chapter to book outline."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    async def _add_chapter():
        try:
            success = await ctx.obj.book_builder.add_chapter_to_outline(
                book_id=book_id,
                chapter_title=chapter_title,
                chapter_description=description or "",
                estimated_word_count=word_count
            )
            
            if success:
                click.echo(f"✅ Added chapter: {chapter_title}")
            else:
                click.echo("❌ Failed to add chapter", err=True)
                
        except Exception as e:
            click.echo(f"❌ Chapter addition failed: {e}", err=True)
    
    asyncio.run(_add_chapter())


@book.command()
@click.argument('book_id')
@click.option('--format', 'export_format', type=click.Choice(['md', 'docx', 'pdf']), 
              default='md', help='Export format')
@click.option('--output', help='Output file path')
@click.pass_context
def export(ctx, book_id, export_format, output):
    """Export book to specified format."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    async def _export():
        try:
            if export_format == 'md':
                output_path = await ctx.obj.book_builder.export_to_markdown(
                    book_id, output
                )
            elif export_format == 'docx':
                output_path = await ctx.obj.book_builder.export_to_docx(
                    book_id, output
                )
            elif export_format == 'pdf':
                output_path = await ctx.obj.book_builder.export_to_pdf(
                    book_id, output
                )
            
            click.echo(f"✅ Exported book to {export_format.upper()}: {output_path}")
            
        except Exception as e:
            click.echo(f"❌ Export failed: {e}", err=True)
    
    asyncio.run(_export())


@cli.group()
def agent():
    """Agent management commands."""
    pass


@agent.command()
@click.argument('agent_type', type=click.Choice(['research', 'writer', 'editor', 'tool']))
@click.argument('task')
@click.option('--context', help='Additional context')
@click.pass_context
def run(ctx, agent_type, task, context):
    """Run a specific agent with a task."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    async def _run_agent():
        try:
            if agent_type == 'research':
                agent = ResearchAgent(
                    memory_manager=ctx.obj.memory_manager,
                    llm_client=ctx.obj.llm_client
                )
                result = await agent.research_topic(task, context or "")
                
            elif agent_type == 'writer':
                agent = WriterAgent(
                    memory_manager=ctx.obj.memory_manager,
                    llm_client=ctx.obj.llm_client
                )
                result = await agent.write_content(task, context or "")
                
            elif agent_type == 'editor':
                agent = EditorAgent(
                    memory_manager=ctx.obj.memory_manager,
                    llm_client=ctx.obj.llm_client
                )
                result = await agent.edit_content(task, context or "")
                
            elif agent_type == 'tool':
                agent = ToolAgent(
                    tool_manager=ctx.obj.tool_manager,
                    llm_client=ctx.obj.llm_client
                )
                result = await agent.execute_tool(task, context or "")
            
            click.echo(f"✅ Agent {agent_type} completed task")
            click.echo(f"Result: {result}")
            
        except Exception as e:
            click.echo(f"❌ Agent execution failed: {e}", err=True)
    
    asyncio.run(_run_agent())


@cli.command()
@click.argument('book_id')
@click.option('--chapter-id', help='Specific chapter to generate')
@click.option('--style', type=click.Choice(['academic', 'journalistic', 'conversational']), 
              default='academic', help='Writing style')
@click.pass_context
def generate(ctx, book_id, chapter_id, style):
    """Generate book content using agents."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    async def _generate():
        try:
            # Start book manuscript
            manuscript = await ctx.obj.book_builder.start_book_manuscript(book_id)
            
            # Initialize agents
            research_agent = ResearchAgent(
                memory_manager=ctx.obj.memory_manager,
                llm_client=ctx.obj.llm_client
            )
            
            writer_agent = WriterAgent(
                memory_manager=ctx.obj.memory_manager,
                llm_client=ctx.obj.llm_client
            )
            
            editor_agent = EditorAgent(
                memory_manager=ctx.obj.memory_manager,
                llm_client=ctx.obj.llm_client
            )
            
            # Generate content for each chapter
            for chapter in manuscript.chapters:
                if chapter_id and chapter.chapter_id != chapter_id:
                    continue
                
                click.echo(f"Generating content for: {chapter.title}")
                
                # Research phase
                research_result = await research_agent.research_topic(
                    chapter.title, manuscript.description
                )
                
                # Writing phase
                writing_style = WritingStyle(style)
                content = await writer_agent.write_content(
                    f"Write a chapter about: {chapter.title}",
                    research_result,
                    writing_style
                )
                
                # Editing phase
                edited_content = await editor_agent.edit_content(
                    content, f"Edit this chapter: {chapter.title}"
                )
                
                # Add to manuscript
                await ctx.obj.book_builder.add_chapter_content(
                    book_id, chapter.chapter_id, edited_content
                )
                
                click.echo(f"✅ Completed: {chapter.title}")
            
            click.echo("✅ Book generation completed!")
            
        except Exception as e:
            click.echo(f"❌ Generation failed: {e}", err=True)
    
    asyncio.run(_generate())


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status."""
    if not ctx.obj.system_initialized:
        click.echo("❌ System not initialized. Run 'init' first.", err=True)
        return
    
    # Get system stats
    memory_stats = ctx.obj.memory_manager.get_stats()
    tool_stats = ctx.obj.tool_manager.get_tool_usage_stats()
    books = ctx.obj.book_builder.list_books()
    
    click.echo("📊 System Status")
    click.echo(f"Memory chunks: {memory_stats.get('total_chunks', 0)}")
    click.echo(f"Registered tools: {len(tool_stats)}")
    click.echo(f"Active books: {len(books)}")
    
    if books:
        click.echo("\n📚 Books:")
        for book in books:
            if book:
                click.echo(f"  - {book['title']} ({book['total_word_count']} words)")


def main():
    """Main CLI entry point."""
    cli()


if __name__ == '__main__':
    main()