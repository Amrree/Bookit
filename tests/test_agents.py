"""
Unit tests for all agent modules.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from research_agent import ResearchAgent
from writer_agent import WriterAgent
from editor_agent import EditorAgent
from tool_agent import ToolAgent


class TestResearchAgent:
    """Test cases for ResearchAgent functionality."""
    
    @pytest.mark.asyncio
    async def test_start_research(self, research_agent):
        """Test starting a research task."""
        topic_id = await research_agent.start_research(
            topic_title="Machine Learning",
            description="Research on machine learning algorithms",
            keywords=["AI", "ML", "algorithms"],
            priority=1
        )
        
        assert topic_id is not None
        assert isinstance(topic_id, str)
    
    @pytest.mark.asyncio
    async def test_get_research_results(self, research_agent):
        """Test getting research results."""
        # Start research
        topic_id = await research_agent.start_research(
            topic_title="Test Topic",
            description="Test research",
            keywords=["test"],
            priority=1
        )
        
        # Get results
        results = await research_agent.get_research_results(topic_id)
        assert results is not None
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_research_summary(self, research_agent):
        """Test getting research summary."""
        # Start research
        topic_id = await research_agent.start_research(
            topic_title="Test Topic",
            description="Test research",
            keywords=["test"],
            priority=1
        )
        
        # Get summary
        summary = await research_agent.get_research_summary(topic_id)
        assert summary is not None
    
    @pytest.mark.asyncio
    async def test_research_with_context(self, research_agent):
        """Test research with additional context."""
        topic_id = await research_agent.start_research(
            topic_title="Contextual Research",
            description="Research with context",
            keywords=["context", "research"],
            priority=1,
            context="Additional context for research"
        )
        
        assert topic_id is not None
        
        # Get results with context
        results = await research_agent.get_research_results(topic_id)
        assert results is not None
    
    @pytest.mark.asyncio
    async def test_research_priority_handling(self, research_agent):
        """Test research priority handling."""
        # Start multiple research tasks with different priorities
        high_priority = await research_agent.start_research(
            topic_title="High Priority",
            description="High priority research",
            keywords=["high"],
            priority=3
        )
        
        low_priority = await research_agent.start_research(
            topic_title="Low Priority",
            description="Low priority research",
            keywords=["low"],
            priority=1
        )
        
        assert high_priority is not None
        assert low_priority is not None
        assert high_priority != low_priority


class TestWriterAgent:
    """Test cases for WriterAgent functionality."""
    
    @pytest.mark.asyncio
    async def test_write_chapter(self, writer_agent):
        """Test writing a chapter."""
        chapter_content = await writer_agent.write_chapter(
            title="Test Chapter",
            outline="Test chapter outline",
            context="Test context",
            references=["ref1", "ref2"],
            word_count_target=1000
        )
        
        assert chapter_content is not None
        assert isinstance(chapter_content, str)
        assert len(chapter_content) > 0
    
    @pytest.mark.asyncio
    async def test_write_with_style_guidelines(self, writer_agent):
        """Test writing with style guidelines."""
        style_guidelines = {
            "tone": "professional",
            "voice": "third_person",
            "format": "academic"
        }
        
        chapter_content = await writer_agent.write_chapter(
            title="Styled Chapter",
            outline="Test outline",
            context="Test context",
            references=[],
            word_count_target=500,
            style_guidelines=style_guidelines
        )
        
        assert chapter_content is not None
        assert len(chapter_content) > 0
    
    @pytest.mark.asyncio
    async def test_write_with_continuity(self, writer_agent):
        """Test writing with continuity from previous chapters."""
        previous_chapters = [
            "Chapter 1: Introduction to the topic",
            "Chapter 2: Background and context"
        ]
        
        chapter_content = await writer_agent.write_chapter(
            title="Chapter 3: Main Content",
            outline="Test outline",
            context="Test context",
            references=[],
            word_count_target=800,
            previous_chapters=previous_chapters
        )
        
        assert chapter_content is not None
        assert len(chapter_content) > 0
    
    @pytest.mark.asyncio
    async def test_write_with_citations(self, writer_agent):
        """Test writing with proper citations."""
        references = [
            {"id": "ref1", "title": "Reference 1", "author": "Author 1"},
            {"id": "ref2", "title": "Reference 2", "author": "Author 2"}
        ]
        
        chapter_content = await writer_agent.write_chapter(
            title="Cited Chapter",
            outline="Test outline",
            context="Test context",
            references=references,
            word_count_target=600
        )
        
        assert chapter_content is not None
        assert len(chapter_content) > 0


class TestEditorAgent:
    """Test cases for EditorAgent functionality."""
    
    @pytest.mark.asyncio
    async def test_edit_chapter(self, editor_agent):
        """Test editing a chapter."""
        original_content = "This is the original chapter content that needs editing."
        
        edited_content = await editor_agent.edit_chapter(
            content=original_content,
            title="Test Chapter",
            context="Test context",
            requirements=["improve clarity", "fix grammar"]
        )
        
        assert edited_content is not None
        assert isinstance(edited_content, str)
        assert len(edited_content) > 0
    
    @pytest.mark.asyncio
    async def test_edit_with_specific_focus(self, editor_agent):
        """Test editing with specific focus areas."""
        original_content = "This chapter needs improvement in several areas."
        
        edited_content = await editor_agent.edit_chapter(
            content=original_content,
            title="Focused Edit Chapter",
            context="Test context",
            requirements=["improve flow", "enhance readability"],
            focus_areas=["introduction", "conclusion"]
        )
        
        assert edited_content is not None
        assert len(edited_content) > 0
    
    @pytest.mark.asyncio
    async def test_edit_with_style_consistency(self, editor_agent):
        """Test editing for style consistency."""
        original_content = "This chapter has inconsistent style and tone."
        
        style_guidelines = {
            "tone": "professional",
            "voice": "third_person",
            "format": "academic"
        }
        
        edited_content = await editor_agent.edit_chapter(
            content=original_content,
            title="Style Consistency Chapter",
            context="Test context",
            requirements=["maintain style consistency"],
            style_guidelines=style_guidelines
        )
        
        assert edited_content is not None
        assert len(edited_content) > 0
    
    @pytest.mark.asyncio
    async def test_edit_with_word_count_target(self, editor_agent):
        """Test editing with word count target."""
        original_content = "This is a very short chapter that needs to be expanded."
        
        edited_content = await editor_agent.edit_chapter(
            content=original_content,
            title="Word Count Chapter",
            context="Test context",
            requirements=["expand content"],
            word_count_target=1000
        )
        
        assert edited_content is not None
        assert len(edited_content) > len(original_content)
    
    @pytest.mark.asyncio
    async def test_edit_with_quality_checks(self, editor_agent):
        """Test editing with quality checks."""
        original_content = "This chapter has some issues that need to be fixed."
        
        quality_checks = [
            "grammar_check",
            "clarity_check",
            "coherence_check",
            "citation_check"
        ]
        
        edited_content = await editor_agent.edit_chapter(
            content=original_content,
            title="Quality Check Chapter",
            context="Test context",
            requirements=["improve quality"],
            quality_checks=quality_checks
        )
        
        assert edited_content is not None
        assert len(edited_content) > 0


class TestToolAgent:
    """Test cases for ToolAgent functionality."""
    
    @pytest.mark.asyncio
    async def test_execute_tool_call(self, tool_agent):
        """Test executing a tool call."""
        tool_call = {
            "tool_name": "test_tool",
            "parameters": {"input": "test_input"}
        }
        
        result = await tool_agent.execute_tool_call(tool_call)
        assert result is not None
        assert "success" in result
        assert "result" in result
    
    @pytest.mark.asyncio
    async def test_execute_multiple_tool_calls(self, tool_agent):
        """Test executing multiple tool calls."""
        tool_calls = [
            {"tool_name": "tool1", "parameters": {"input": "input1"}},
            {"tool_name": "tool2", "parameters": {"input": "input2"}}
        ]
        
        results = await tool_agent.execute_tool_calls(tool_calls)
        assert results is not None
        assert isinstance(results, list)
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_execute_tool_call_with_error_handling(self, tool_agent):
        """Test tool call execution with error handling."""
        tool_call = {
            "tool_name": "nonexistent_tool",
            "parameters": {"input": "test_input"}
        }
        
        result = await tool_agent.execute_tool_call(tool_call)
        assert result is not None
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_call_with_validation(self, tool_agent):
        """Test tool call execution with parameter validation."""
        tool_call = {
            "tool_name": "test_tool",
            "parameters": {"invalid_param": "invalid_value"}
        }
        
        result = await tool_agent.execute_tool_call(tool_call)
        assert result is not None
        # Should handle validation errors gracefully
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_call_with_timeout(self, tool_agent):
        """Test tool call execution with timeout."""
        tool_call = {
            "tool_name": "slow_tool",
            "parameters": {"delay": 2}
        }
        
        result = await tool_agent.execute_tool_call(tool_call, timeout=1)
        assert result is not None
        assert result["success"] is False
        assert "timeout" in result.get("error", "").lower()
    
    @pytest.mark.asyncio
    async def test_execute_tool_call_with_safety_checks(self, tool_agent):
        """Test tool call execution with safety checks."""
        tool_call = {
            "tool_name": "unsafe_tool",
            "parameters": {"command": "rm -rf /"}
        }
        
        result = await tool_agent.execute_tool_call(tool_call, safety_checks=True)
        assert result is not None
        assert result["success"] is False
        assert "safety" in result.get("error", "").lower()
    
    @pytest.mark.asyncio
    async def test_get_available_tools(self, tool_agent):
        """Test getting available tools."""
        tools = await tool_agent.get_available_tools()
        assert tools is not None
        assert isinstance(tools, list)
    
    @pytest.mark.asyncio
    async def test_get_tool_metadata(self, tool_agent):
        """Test getting tool metadata."""
        metadata = await tool_agent.get_tool_metadata("test_tool")
        assert metadata is not None
        assert "name" in metadata
        assert "description" in metadata