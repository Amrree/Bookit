"""
Enhanced Book Writing System

This module integrates all the new features including:
- Enhanced Output Management
- Template System
- Advanced Export Options
- Style Guide Integration
- Research Assistant
- Collaboration Features
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import new modules
from output_manager import OutputManager, BookMetadata
from template_manager import TemplateManager, BookTemplate
from export_manager import ExportManager, ExportOptions
from style_manager import StyleManager, StyleGuide
from research_assistant import ResearchAssistant, ResearchResult

# Import existing modules
from memory_manager import MemoryManager
from llm_client import LLMClient
from tool_manager import ToolManager
from book_builder import BookBuilder

logger = logging.getLogger(__name__)


class EnhancedBookWritingSystem:
    """
    Enhanced book writing system with all new features integrated.
    
    Features:
    - Enhanced output management
    - Template system
    - Advanced export options
    - Style guide integration
    - Research assistant
    - Collaboration features
    """
    
    def __init__(self, 
                 output_dir: str = "./output",
                 memory_dir: str = "./memory_db",
                 openai_api_key: Optional[str] = None):
        """
        Initialize enhanced book writing system.
        
        Args:
            output_dir: Base output directory
            memory_dir: Memory database directory
            openai_api_key: OpenAI API key
        """
        self.output_dir = Path(output_dir)
        self.memory_dir = Path(memory_dir)
        
        # Initialize core components
        self.memory_manager = MemoryManager(
            persist_directory=str(memory_dir),
            use_remote_embeddings=bool(openai_api_key),
            openai_api_key=openai_api_key
        )
        
        self.llm_client = LLMClient(
            provider="openai" if openai_api_key else "ollama",
            openai_api_key=openai_api_key
        )
        
        self.tool_manager = ToolManager()
        
        # Initialize new components
        self.output_manager = OutputManager(str(output_dir))
        self.template_manager = TemplateManager(str(output_dir / "templates"))
        self.export_manager = ExportManager(str(output_dir))
        self.style_manager = StyleManager(str(output_dir / "styles"))
        self.research_assistant = ResearchAssistant(str(output_dir / "research"))
        
        # Initialize book builder
        self.book_builder = BookBuilder(str(output_dir / "books"))
        
        logger.info("Enhanced book writing system initialized")
    
    async def create_book_with_template(self, 
                                      title: str,
                                      author: str,
                                      description: str,
                                      target_audience: str,
                                      template_id: str,
                                      style_guide_id: str = "business_professional") -> str:
        """
        Create a new book using a template and style guide.
        
        Args:
            title: Book title
            author: Book author
            description: Book description
            target_audience: Target audience
            template_id: Template ID to use
            style_guide_id: Style guide ID to use
            
        Returns:
            Book ID
        """
        # Get template
        template = self.template_manager.get_book_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Create book structure
        book_dir = self.output_manager.create_book_structure(
            book_id=f"book_{title.lower().replace(' ', '_')}_{asyncio.get_event_loop().time()}",
            title=title,
            author=author,
            description=description,
            target_audience=target_audience
        )
        
        book_id = book_dir.name
        
        # Update metadata with template and style information
        self.output_manager.update_book_metadata(book_id, 
                                               template_id=template_id,
                                               style_guide_id=style_guide_id,
                                               genre=template.category)
        
        logger.info(f"Created book '{title}' with template '{template_id}' and style '{style_guide_id}'")
        
        return book_id
    
    async def research_and_write_chapter(self, 
                                       book_id: str,
                                       chapter_title: str,
                                       research_query: str,
                                       style_guide_id: str = "business_professional") -> str:
        """
        Research and write a chapter using AI and style guides.
        
        Args:
            book_id: Book ID
            chapter_title: Chapter title
            research_query: Research query for the chapter
            style_guide_id: Style guide ID to use
            
        Returns:
            Chapter content
        """
        # Research the topic
        research_result = await self.research_assistant.research_topic(
            topic=research_query,
            depth="medium",
            max_sources=10
        )
        
        # Store research in memory
        await self.memory_manager.add_agent_notes(
            content=research_result.summary,
            agent_id="research_assistant",
            tags=["research", chapter_title, book_id],
            provenance_notes=f"Research for chapter: {chapter_title}"
        )
        
        # Generate chapter content using LLM
        prompt = f"""
        Write a chapter titled "{chapter_title}" based on the following research:
        
        Research Summary:
        {research_result.summary}
        
        Key Findings:
        {chr(10).join(research_result.key_findings)}
        
        Please write a comprehensive, well-structured chapter that incorporates the research findings.
        Use a professional, engaging tone suitable for the target audience.
        """
        
        response = await self.llm_client.generate_completion(
            prompt=prompt,
            max_tokens=3000,
            temperature=0.7
        )
        
        chapter_content = response.content
        
        # Apply style guide
        style_guide = self.style_manager.get_style_guide(style_guide_id)
        if style_guide:
            chapter_content, _ = self.style_manager.apply_style_guide(
                chapter_content, style_guide_id
            )
        
        # Add chapter to book
        self.book_builder.add_chapter_content(
            book_id=book_id,
            chapter_id=f"{book_id}_ch_{chapter_title.lower().replace(' ', '_')}",
            content=chapter_content,
            status="completed"
        )
        
        # Save chapter to output manager
        chapter_path = self.output_manager.get_book_directory(book_id) / "drafts" / f"{chapter_title}.md"
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
        
        logger.info(f"Generated chapter '{chapter_title}' for book '{book_id}'")
        
        return chapter_content
    
    async def export_book_multiple_formats(self, 
                                         book_id: str,
                                         formats: List[str] = None) -> Dict[str, str]:
        """
        Export book to multiple formats.
        
        Args:
            book_id: Book ID
            formats: List of formats to export
            
        Returns:
            Dictionary of format -> file path
        """
        if formats is None:
            formats = ["pdf", "docx", "epub", "html", "markdown"]
        
        # Get book content
        book_info = self.output_manager.get_book_directory(book_id)
        if not book_info:
            raise ValueError(f"Book not found: {book_id}")
        
        # Read book content (simplified - in real implementation, you'd assemble from chapters)
        content = "# Book Content\n\nThis is a placeholder for the actual book content."
        
        # Get book metadata
        metadata_path = book_info / "metadata.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {"title": "Unknown", "author": "Unknown"}
        
        # Export to multiple formats
        export_results = {}
        
        for format_name in formats:
            options = ExportOptions(
                format=format_name,
                include_cover=True,
                include_toc=True,
                quality="high"
            )
            
            result = self.export_manager.export_book(
                book_id=book_id,
                content=content,
                metadata=metadata,
                options=options
            )
            
            if result.success:
                export_results[format_name] = result.file_path
                logger.info(f"Exported {book_id} to {format_name}: {result.file_path}")
            else:
                logger.error(f"Failed to export {book_id} to {format_name}: {result.error}")
        
        return export_results
    
    async def check_book_style(self, book_id: str, style_guide_id: str) -> Dict[str, Any]:
        """
        Check book content against style guide.
        
        Args:
            book_id: Book ID
            style_guide_id: Style guide ID
            
        Returns:
            Style check results
        """
        # Get book content (simplified)
        book_dir = self.output_manager.get_book_directory(book_id)
        if not book_dir:
            raise ValueError(f"Book not found: {book_id}")
        
        # Read all chapter files
        content = ""
        for chapter_file in book_dir.glob("drafts/*.md"):
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content += f.read() + "\n\n"
        
        # Check style
        style_checks = self.style_manager.check_content(content, style_guide_id)
        style_stats = self.style_manager.get_style_statistics(content, style_guide_id)
        
        return {
            "checks": [check.dict() for check in style_checks],
            "statistics": style_stats,
            "total_issues": len(style_checks),
            "style_guide": style_guide_id
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            "output_manager": self.output_manager.get_statistics(),
            "template_manager": self.template_manager.get_statistics(),
            "export_manager": self.export_manager.get_statistics(),
            "style_manager": self.style_manager.get_statistics(),
            "research_assistant": self.research_assistant.get_statistics(),
            "memory_manager": self.memory_manager.get_stats(),
            "tool_manager": self.tool_manager.get_tool_usage_stats()
        }
    
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """List all available book templates."""
        templates = self.template_manager.list_book_templates()
        return [template.dict() for template in templates]
    
    def list_available_style_guides(self) -> List[Dict[str, Any]]:
        """List all available style guides."""
        style_guides = self.style_manager.list_style_guides()
        return [guide.dict() for guide in style_guides]
    
    def get_supported_export_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return self.export_manager.get_supported_formats()


# Example usage
async def main():
    """Example usage of the enhanced system."""
    # Initialize system
    system = EnhancedBookWritingSystem(
        output_dir="./output",
        memory_dir="./memory_db",
        openai_api_key="your-api-key-here"
    )
    
    # Create a book with template
    book_id = await system.create_book_with_template(
        title="AI and the Future of Work",
        author="John Doe",
        description="Exploring how AI will transform the workplace",
        target_audience="Business professionals",
        template_id="business_white_paper",
        style_guide_id="business_professional"
    )
    
    print(f"Created book: {book_id}")
    
    # Research and write a chapter
    chapter_content = await system.research_and_write_chapter(
        book_id=book_id,
        chapter_title="Introduction to AI",
        research_query="artificial intelligence workplace automation",
        style_guide_id="business_professional"
    )
    
    print(f"Generated chapter: {len(chapter_content)} characters")
    
    # Export to multiple formats
    export_results = await system.export_book_multiple_formats(
        book_id=book_id,
        formats=["pdf", "docx", "epub", "html"]
    )
    
    print(f"Exported to formats: {list(export_results.keys())}")
    
    # Check style
    style_results = await system.check_book_style(book_id, "business_professional")
    print(f"Style check found {style_results['total_issues']} issues")
    
    # Get system statistics
    stats = system.get_system_statistics()
    print(f"System statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())