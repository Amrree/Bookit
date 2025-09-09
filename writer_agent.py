"""
Writer Agent Module

Handles RAG-driven drafting and chapter generation.
Uses research results and memory to create book content.

Chosen libraries:
- asyncio: Asynchronous writing operations
- pydantic: Data validation and type safety
- logging: Writing activity logging

Adapted from: exp-pj-m-multi-agent-system (https://github.com/krik8235/exp-pj-m-multi-agent-system)
Pattern: RAG-driven content generation with structured output
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pydantic

logger = logging.getLogger(__name__)


class ChapterOutline(pydantic.BaseModel):
    """Model for chapter outlines."""
    chapter_id: str
    title: str
    order: int
    sections: List[Dict[str, str]] = []  # [{"title": "Section Title", "content": "Brief description"}]
    key_points: List[str] = []
    research_topics: List[str] = []
    word_count_target: int = 2000
    created_at: datetime


class ChapterDraft(pydantic.BaseModel):
    """Model for chapter drafts."""
    draft_id: str
    chapter_id: str
    title: str
    content: str
    word_count: int
    sections: List[Dict[str, str]] = []
    citations: List[Dict[str, str]] = []  # [{"text": "cited text", "source": "source info", "chunk_id": "id"}]
    research_sources: List[Dict[str, str]] = []
    status: str = "draft"  # draft, review, final
    created_at: datetime
    updated_at: datetime


class WritingStyle(pydantic.BaseModel):
    """Model for writing style preferences."""
    tone: str = "professional"  # professional, academic, conversational, technical
    audience: str = "general"  # general, academic, technical, beginner, expert
    formality: str = "medium"  # low, medium, high
    voice: str = "third_person"  # first_person, second_person, third_person
    length_preference: str = "medium"  # short, medium, long


class WriterAgent:
    """
    RAG-driven writing agent for book content generation.
    
    Responsibilities:
    - Generate chapter outlines based on research
    - Create detailed chapter drafts using RAG
    - Incorporate research findings and citations
    - Maintain consistent writing style and voice
    - Structure content for non-fiction books
    """
    
    def __init__(
        self,
        agent_id: str,
        memory_manager: Any,
        llm_client: Any,
        research_agent: Any,
        writing_style: WritingStyle = None
    ):
        """
        Initialize the writer agent.
        
        Args:
            agent_id: Unique agent identifier
            memory_manager: Memory manager for RAG operations
            llm_client: LLM client for text generation
            research_agent: Research agent for gathering information
            writing_style: Writing style preferences
        """
        self.agent_id = agent_id
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.research_agent = research_agent
        self.writing_style = writing_style or WritingStyle()
        
        # Writing state
        self.chapter_outlines: Dict[str, ChapterOutline] = {}
        self.chapter_drafts: Dict[str, ChapterDraft] = {}
        self.current_project: Optional[str] = None
        
        logger.info(f"Writer agent {agent_id} initialized")
    
    async def create_chapter_outline(
        self,
        chapter_title: str,
        chapter_order: int,
        research_topics: List[str] = None,
        word_count_target: int = 2000
    ) -> str:
        """
        Create a chapter outline based on research.
        
        Args:
            chapter_title: Title of the chapter
            chapter_order: Order of the chapter in the book
            research_topics: List of research topic IDs to use
            word_count_target: Target word count for the chapter
            
        Returns:
            Chapter ID
        """
        chapter_id = f"chapter_{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Gather research information
        research_content = ""
        if research_topics:
            for topic_id in research_topics:
                summary = await self.research_agent.get_research_summary(topic_id)
                if summary:
                    research_content += f"\n\nTopic: {summary.title}\n{summary.overview}\n"
                    research_content += f"Key Findings: {'; '.join(summary.key_findings)}\n"
        
        # Generate outline using LLM
        outline_prompt = f"""
        Create a detailed chapter outline for a non-fiction book chapter titled: "{chapter_title}"
        
        Writing Style:
        - Tone: {self.writing_style.tone}
        - Audience: {self.writing_style.audience}
        - Formality: {self.writing_style.formality}
        - Voice: {self.writing_style.voice}
        
        Target word count: {word_count_target} words
        Chapter order: {chapter_order}
        
        Research Context:
        {research_content}
        
        Please provide:
        1. A brief chapter overview (2-3 sentences)
        2. 4-6 main sections with titles and brief descriptions
        3. Key points to cover in each section
        4. Suggested research topics for deeper investigation
        
        Format as a structured outline with clear sections and subsections.
        """
        
        try:
            response = await self.llm_client.generate(
                prompt=outline_prompt,
                max_tokens=1000,
                temperature=0.4
            )
            
            # Parse the response to extract sections
            sections = await self._parse_outline_sections(response.content)
            key_points = await self._extract_key_points(response.content)
            
            outline = ChapterOutline(
                chapter_id=chapter_id,
                title=chapter_title,
                order=chapter_order,
                sections=sections,
                key_points=key_points,
                research_topics=research_topics or [],
                word_count_target=word_count_target,
                created_at=datetime.now()
            )
            
            self.chapter_outlines[chapter_id] = outline
            
            logger.info(f"Created chapter outline: {chapter_title}")
            return chapter_id
            
        except Exception as e:
            logger.error(f"Failed to create chapter outline: {e}")
            raise
    
    async def write_chapter_draft(
        self,
        chapter_id: str,
        section_focus: Optional[str] = None
    ) -> str:
        """
        Write a chapter draft using RAG.
        
        Args:
            chapter_id: ID of the chapter to write
            section_focus: Specific section to focus on (optional)
            
        Returns:
            Draft ID
        """
        outline = self.chapter_outlines.get(chapter_id)
        if not outline:
            raise ValueError(f"Chapter outline {chapter_id} not found")
        
        draft_id = f"draft_{chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Gather research content using RAG
            research_content = await self._gather_research_content(outline)
            
            # Generate chapter content
            if section_focus:
                content = await self._write_section(outline, section_focus, research_content)
            else:
                content = await self._write_full_chapter(outline, research_content)
            
            # Extract citations and sources
            citations = await self._extract_citations(content, research_content)
            research_sources = await self._extract_research_sources(outline)
            
            # Create draft
            draft = ChapterDraft(
                draft_id=draft_id,
                chapter_id=chapter_id,
                title=outline.title,
                content=content,
                word_count=len(content.split()),
                sections=outline.sections,
                citations=citations,
                research_sources=research_sources,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.chapter_drafts[draft_id] = draft
            
            # Store in memory for future reference
            await self.memory_manager.add_agent_notes(
                content=content,
                agent_id=self.agent_id,
                tags=[outline.title, "chapter_draft"],
                provenance_notes=f"Chapter draft for: {outline.title}"
            )
            
            logger.info(f"Created chapter draft: {outline.title} ({draft.word_count} words)")
            return draft_id
            
        except Exception as e:
            logger.error(f"Failed to write chapter draft: {e}")
            raise
    
    async def _gather_research_content(self, outline: ChapterOutline) -> str:
        """Gather research content using RAG."""
        research_parts = []
        
        # Search memory for relevant content
        query = f"{outline.title} {' '.join(outline.key_points)}"
        
        try:
            context, retrieval_results = await self.memory_manager.get_context_for_generation(
                query=query,
                max_tokens=3000
            )
            research_parts.append(context)
        except Exception as e:
            logger.warning(f"Failed to retrieve from memory: {e}")
        
        # Get research summaries
        for topic_id in outline.research_topics:
            try:
                summary = await self.research_agent.get_research_summary(topic_id)
                if summary:
                    research_parts.append(f"Research: {summary.title}\n{summary.overview}")
                    research_parts.append(f"Key Findings: {'; '.join(summary.key_findings)}")
            except Exception as e:
                logger.warning(f"Failed to get research summary {topic_id}: {e}")
        
        return "\n\n".join(research_parts)
    
    async def _write_full_chapter(
        self,
        outline: ChapterOutline,
        research_content: str
    ) -> str:
        """Write a full chapter using the outline and research."""
        prompt = f"""
        Write a complete non-fiction book chapter based on the following outline and research.
        
        Chapter Title: {outline.title}
        Target Word Count: {outline.word_count_target}
        
        Writing Style:
        - Tone: {self.writing_style.tone}
        - Audience: {self.writing_style.audience}
        - Formality: {self.writing_style.formality}
        - Voice: {self.writing_style.voice}
        
        Chapter Outline:
        {self._format_outline(outline)}
        
        Research Content:
        {research_content}
        
        Requirements:
        1. Write a compelling introduction that hooks the reader
        2. Follow the outline structure with clear section headings
        3. Include specific examples and evidence from research
        4. Use proper citations in the format [Source: filename] or [Source: URL]
        5. Write a strong conclusion that summarizes key points
        6. Maintain consistent tone and voice throughout
        7. Aim for approximately {outline.word_count_target} words
        
        Write the complete chapter now:
        """
        
        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=4000,
            temperature=0.6
        )
        
        return response.content
    
    async def _write_section(
        self,
        outline: ChapterOutline,
        section_title: str,
        research_content: str
    ) -> str:
        """Write a specific section of a chapter."""
        # Find the section in the outline
        section_info = None
        for section in outline.sections:
            if section["title"].lower() == section_title.lower():
                section_info = section
                break
        
        if not section_info:
            raise ValueError(f"Section '{section_title}' not found in outline")
        
        prompt = f"""
        Write a detailed section for a non-fiction book chapter.
        
        Chapter Title: {outline.title}
        Section Title: {section_title}
        Section Description: {section_info.get('content', '')}
        
        Writing Style:
        - Tone: {self.writing_style.tone}
        - Audience: {self.writing_style.audience}
        - Formality: {self.writing_style.formality}
        - Voice: {self.writing_style.voice}
        
        Research Content:
        {research_content}
        
        Requirements:
        1. Write a comprehensive section that covers the topic thoroughly
        2. Include specific examples and evidence from research
        3. Use proper citations in the format [Source: filename] or [Source: URL]
        4. Maintain consistent tone and voice
        5. Aim for 500-800 words
        
        Write the section now:
        """
        
        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.6
        )
        
        return response.content
    
    async def _parse_outline_sections(self, outline_text: str) -> List[Dict[str, str]]:
        """Parse outline text to extract sections."""
        sections = []
        lines = outline_text.split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            if (line.startswith('#') or 
                line.startswith('##') or 
                line.startswith('**') or
                line[0].isupper() and ':' in line):
                
                if current_section:
                    sections.append(current_section)
                
                # Extract section title
                title = line.replace('#', '').replace('*', '').strip()
                if ':' in title:
                    title = title.split(':')[0].strip()
                
                current_section = {"title": title, "content": ""}
            elif current_section and line:
                # Add content to current section
                current_section["content"] += line + " "
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    async def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text."""
        try:
            prompt = f"Extract 5-7 key points from this text:\n\n{text}"
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            points = []
            for line in response.content.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    points.append(line[1:].strip())
                elif line and line[0].isdigit():
                    points.append(line)
            
            return points[:7]  # Limit to 7 points
        except Exception as e:
            logger.warning(f"Failed to extract key points: {e}")
            return []
    
    async def _extract_citations(self, content: str, research_content: str) -> List[Dict[str, str]]:
        """Extract citations from content."""
        citations = []
        
        # Look for citation patterns in content
        import re
        citation_patterns = [
            r'\[Source: ([^\]]+)\]',
            r'\[([^\]]+)\]',
            r'\(Source: ([^)]+)\)'
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                citations.append({
                    "text": match,
                    "source": match,
                    "chunk_id": ""
                })
        
        return citations
    
    async def _extract_research_sources(self, outline: ChapterOutline) -> List[Dict[str, str]]:
        """Extract research sources from outline."""
        sources = []
        
        for topic_id in outline.research_topics:
            try:
                results = await self.research_agent.get_research_results(topic_id)
                for result in results[:5]:  # Limit to top 5 results
                    sources.append({
                        "title": result.source_title,
                        "url": result.source_url or "",
                        "type": result.source_type,
                        "relevance": result.relevance_score
                    })
            except Exception as e:
                logger.warning(f"Failed to get research sources for topic {topic_id}: {e}")
        
        return sources
    
    def _format_outline(self, outline: ChapterOutline) -> str:
        """Format outline for use in prompts."""
        formatted = f"Chapter: {outline.title}\n\n"
        
        for i, section in enumerate(outline.sections, 1):
            formatted += f"{i}. {section['title']}\n"
            if section.get('content'):
                formatted += f"   {section['content']}\n"
        
        if outline.key_points:
            formatted += f"\nKey Points:\n"
            for point in outline.key_points:
                formatted += f"- {point}\n"
        
        return formatted
    
    async def revise_chapter(
        self,
        draft_id: str,
        revision_notes: str
    ) -> str:
        """
        Revise a chapter draft based on feedback.
        
        Args:
            draft_id: ID of the draft to revise
            revision_notes: Notes on what to revise
            
        Returns:
            New draft ID
        """
        draft = self.chapter_drafts.get(draft_id)
        if not draft:
            raise ValueError(f"Draft {draft_id} not found")
        
        new_draft_id = f"draft_{draft.chapter_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            prompt = f"""
            Revise the following chapter draft based on the revision notes.
            
            Chapter Title: {draft.title}
            Current Word Count: {draft.word_count}
            
            Revision Notes:
            {revision_notes}
            
            Current Draft:
            {draft.content}
            
            Writing Style:
            - Tone: {self.writing_style.tone}
            - Audience: {self.writing_style.audience}
            - Formality: {self.writing_style.formality}
            - Voice: {self.writing_style.voice}
            
            Please revise the chapter according to the notes while maintaining the writing style and improving the content quality.
            """
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.5
            )
            
            # Create revised draft
            revised_draft = ChapterDraft(
                draft_id=new_draft_id,
                chapter_id=draft.chapter_id,
                title=draft.title,
                content=response.content,
                word_count=len(response.content.split()),
                sections=draft.sections,
                citations=draft.citations,
                research_sources=draft.research_sources,
                status="draft",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.chapter_drafts[new_draft_id] = revised_draft
            
            logger.info(f"Revised chapter draft: {draft.title}")
            return new_draft_id
            
        except Exception as e:
            logger.error(f"Failed to revise chapter draft: {e}")
            raise
    
    async def get_chapter_outline(self, chapter_id: str) -> Optional[ChapterOutline]:
        """Get chapter outline by ID."""
        return self.chapter_outlines.get(chapter_id)
    
    async def get_chapter_draft(self, draft_id: str) -> Optional[ChapterDraft]:
        """Get chapter draft by ID."""
        return self.chapter_drafts.get(draft_id)
    
    async def get_all_drafts(self) -> List[ChapterDraft]:
        """Get all chapter drafts."""
        return list(self.chapter_drafts.values())
    
    async def execute_task(self, task_type: str, payload: Dict[str, Any]) -> Any:
        """Execute a writing task."""
        if task_type == "create_outline":
            return await self.create_chapter_outline(
                chapter_title=payload.get("title", ""),
                chapter_order=payload.get("order", 1),
                research_topics=payload.get("research_topics", []),
                word_count_target=payload.get("word_count", 2000)
            )
        elif task_type == "write_draft":
            return await self.write_chapter_draft(
                chapter_id=payload.get("chapter_id"),
                section_focus=payload.get("section_focus")
            )
        elif task_type == "revise_draft":
            return await self.revise_chapter(
                draft_id=payload.get("draft_id"),
                revision_notes=payload.get("revision_notes", "")
            )
        elif task_type == "get_draft":
            return await self.get_chapter_draft(payload.get("draft_id"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")