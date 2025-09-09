"""
Editor Agent Module

Conducts revision and consistency passes on generated content.
Ensures quality, coherence, and adherence to style guidelines.

Chosen libraries:
- asyncio: Asynchronous editing operations
- pydantic: Data validation and type safety
- logging: Editing activity logging

Adapted from: AutoGen (https://github.com/microsoft/autogen)
Pattern: Human-AI collaboration with structured feedback
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pydantic

logger = logging.getLogger(__name__)


class EditSuggestion(pydantic.BaseModel):
    """Model for edit suggestions."""
    suggestion_id: str
    type: str  # grammar, style, clarity, structure, fact_check, citation
    severity: str  # low, medium, high, critical
    original_text: str
    suggested_text: str
    explanation: str
    position: int  # Character position in text
    confidence: float  # 0.0 to 1.0


class EditReport(pydantic.BaseModel):
    """Model for edit reports."""
    report_id: str
    content_id: str
    content_type: str  # chapter, section, paragraph
    overall_score: float  # 0.0 to 1.0
    suggestions: List[EditSuggestion] = []
    summary: str
    word_count: int
    readability_score: float
    consistency_score: float
    created_at: datetime


class StyleGuide(pydantic.BaseModel):
    """Model for style guidelines."""
    tone: str = "professional"
    formality: str = "medium"
    voice: str = "third_person"
    sentence_length: str = "medium"  # short, medium, long
    paragraph_length: str = "medium"
    citation_style: str = "apa"  # apa, mla, chicago, custom
    forbidden_words: List[str] = []
    preferred_words: Dict[str, str] = {}  # {"avoid": "prefer"}
    grammar_rules: List[str] = []


class EditorAgent:
    """
    Content editing agent for quality assurance and revision.
    
    Responsibilities:
    - Review and edit generated content
    - Ensure consistency and quality
    - Check grammar, style, and clarity
    - Verify citations and facts
    - Provide structured feedback and suggestions
    """
    
    def __init__(
        self,
        agent_id: str,
        llm_client: Any,
        style_guide: StyleGuide = None
    ):
        """
        Initialize the editor agent.
        
        Args:
            agent_id: Unique agent identifier
            llm_client: LLM client for text analysis and generation
            style_guide: Style guidelines to follow
        """
        self.agent_id = agent_id
        self.llm_client = llm_client
        self.style_guide = style_guide or StyleGuide()
        
        # Editing state
        self.edit_reports: Dict[str, EditReport] = {}
        self.editing_history: List[Dict[str, Any]] = []
        
        logger.info(f"Editor agent {agent_id} initialized")
    
    async def review_content(
        self,
        content: str,
        content_id: str,
        content_type: str = "chapter",
        context: str = ""
    ) -> str:
        """
        Review content and generate edit report.
        
        Args:
            content: Content to review
            content_id: Unique identifier for the content
            content_type: Type of content (chapter, section, paragraph)
            context: Additional context for the review
            
        Returns:
            Report ID
        """
        report_id = f"report_{content_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Analyze content for various issues
            suggestions = []
            
            # Grammar and style check
            grammar_suggestions = await self._check_grammar_and_style(content)
            suggestions.extend(grammar_suggestions)
            
            # Clarity and readability check
            clarity_suggestions = await self._check_clarity(content)
            suggestions.extend(clarity_suggestions)
            
            # Structure and organization check
            structure_suggestions = await self._check_structure(content)
            suggestions.extend(structure_suggestions)
            
            # Citation and fact check
            citation_suggestions = await self._check_citations(content)
            suggestions.extend(citation_suggestions)
            
            # Calculate scores
            overall_score = await self._calculate_overall_score(content, suggestions)
            readability_score = await self._calculate_readability_score(content)
            consistency_score = await self._calculate_consistency_score(content)
            
            # Generate summary
            summary = await self._generate_edit_summary(content, suggestions, overall_score)
            
            # Create edit report
            report = EditReport(
                report_id=report_id,
                content_id=content_id,
                content_type=content_type,
                overall_score=overall_score,
                suggestions=suggestions,
                summary=summary,
                word_count=len(content.split()),
                readability_score=readability_score,
                consistency_score=consistency_score,
                created_at=datetime.now()
            )
            
            self.edit_reports[report_id] = report
            
            # Log editing activity
            self.editing_history.append({
                "timestamp": datetime.now(),
                "action": "review",
                "content_id": content_id,
                "suggestions_count": len(suggestions),
                "overall_score": overall_score
            })
            
            logger.info(f"Created edit report for {content_id}: {len(suggestions)} suggestions")
            return report_id
            
        except Exception as e:
            logger.error(f"Failed to review content {content_id}: {e}")
            raise
    
    async def _check_grammar_and_style(self, content: str) -> List[EditSuggestion]:
        """Check grammar and style issues."""
        suggestions = []
        
        try:
            prompt = f"""
            Review the following text for grammar and style issues. Focus on:
            1. Grammar errors (subject-verb agreement, tense consistency, etc.)
            2. Style consistency (tone: {self.style_guide.tone}, formality: {self.style_guide.formality})
            3. Word choice and clarity
            4. Sentence structure and flow
            
            Style Guidelines:
            - Tone: {self.style_guide.tone}
            - Formality: {self.style_guide.formality}
            - Voice: {self.style_guide.voice}
            - Forbidden words: {', '.join(self.style_guide.forbidden_words)}
            - Preferred words: {self.style_guide.preferred_words}
            
            Text to review:
            {content[:2000]}  # Limit for prompt size
            
            Provide specific suggestions with:
            - Type of issue (grammar, style, word_choice)
            - Severity (low, medium, high, critical)
            - Original text
            - Suggested improvement
            - Brief explanation
            - Character position (approximate)
            """
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse suggestions from response
            suggestions = await self._parse_edit_suggestions(response.content, "grammar_style")
            
        except Exception as e:
            logger.warning(f"Failed to check grammar and style: {e}")
        
        return suggestions
    
    async def _check_clarity(self, content: str) -> List[EditSuggestion]:
        """Check clarity and readability issues."""
        suggestions = []
        
        try:
            prompt = f"""
            Review the following text for clarity and readability issues. Focus on:
            1. Unclear sentences or phrases
            2. Complex sentence structures that could be simplified
            3. Ambiguous references or pronouns
            4. Technical jargon that needs explanation
            5. Logical flow and transitions
            
            Text to review:
            {content[:2000]}
            
            Provide specific suggestions with:
            - Type of issue (clarity, readability, jargon, flow)
            - Severity (low, medium, high, critical)
            - Original text
            - Suggested improvement
            - Brief explanation
            - Character position (approximate)
            """
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            suggestions = await self._parse_edit_suggestions(response.content, "clarity")
            
        except Exception as e:
            logger.warning(f"Failed to check clarity: {e}")
        
        return suggestions
    
    async def _check_structure(self, content: str) -> List[EditSuggestion]:
        """Check structure and organization issues."""
        suggestions = []
        
        try:
            prompt = f"""
            Review the following text for structure and organization issues. Focus on:
            1. Logical flow and paragraph organization
            2. Missing or weak transitions
            3. Inconsistent heading structure
            4. Repetitive content or ideas
            5. Missing introductions or conclusions
            
            Text to review:
            {content[:2000]}
            
            Provide specific suggestions with:
            - Type of issue (structure, organization, flow, repetition)
            - Severity (low, medium, high, critical)
            - Original text
            - Suggested improvement
            - Brief explanation
            - Character position (approximate)
            """
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            suggestions = await self._parse_edit_suggestions(response.content, "structure")
            
        except Exception as e:
            logger.warning(f"Failed to check structure: {e}")
        
        return suggestions
    
    async def _check_citations(self, content: str) -> List[EditSuggestion]:
        """Check citation and fact-checking issues."""
        suggestions = []
        
        try:
            prompt = f"""
            Review the following text for citation and fact-checking issues. Focus on:
            1. Missing citations for claims
            2. Inconsistent citation format
            3. Unclear or weak evidence
            4. Potential factual errors
            5. Missing source information
            
            Citation Style: {self.style_guide.citation_style}
            
            Text to review:
            {content[:2000]}
            
            Provide specific suggestions with:
            - Type of issue (citation, fact_check, evidence)
            - Severity (low, medium, high, critical)
            - Original text
            - Suggested improvement
            - Brief explanation
            - Character position (approximate)
            """
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            suggestions = await self._parse_edit_suggestions(response.content, "citation")
            
        except Exception as e:
            logger.warning(f"Failed to check citations: {e}")
        
        return suggestions
    
    async def _parse_edit_suggestions(self, response_text: str, suggestion_type: str) -> List[EditSuggestion]:
        """Parse edit suggestions from LLM response."""
        suggestions = []
        
        try:
            lines = response_text.split('\n')
            current_suggestion = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for suggestion patterns
                if line.startswith('**') and line.endswith('**'):
                    # Save previous suggestion
                    if current_suggestion:
                        suggestion = EditSuggestion(
                            suggestion_id=f"{suggestion_type}_{len(suggestions)}",
                            type=suggestion_type,
                            severity=current_suggestion.get('severity', 'medium'),
                            original_text=current_suggestion.get('original', ''),
                            suggested_text=current_suggestion.get('suggested', ''),
                            explanation=current_suggestion.get('explanation', ''),
                            position=current_suggestion.get('position', 0),
                            confidence=0.8  # Default confidence
                        )
                        suggestions.append(suggestion)
                    
                    # Start new suggestion
                    current_suggestion = {'type': suggestion_type}
                
                elif ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key in ['severity', 'original', 'suggested', 'explanation', 'position']:
                        current_suggestion[key] = value
            
            # Add last suggestion
            if current_suggestion:
                suggestion = EditSuggestion(
                    suggestion_id=f"{suggestion_type}_{len(suggestions)}",
                    type=suggestion_type,
                    severity=current_suggestion.get('severity', 'medium'),
                    original_text=current_suggestion.get('original', ''),
                    suggested_text=current_suggestion.get('suggested', ''),
                    explanation=current_suggestion.get('explanation', ''),
                    position=current_suggestion.get('position', 0),
                    confidence=0.8
                )
                suggestions.append(suggestion)
        
        except Exception as e:
            logger.warning(f"Failed to parse edit suggestions: {e}")
        
        return suggestions
    
    async def _calculate_overall_score(self, content: str, suggestions: List[EditSuggestion]) -> float:
        """Calculate overall quality score."""
        if not suggestions:
            return 1.0
        
        # Weight suggestions by severity
        severity_weights = {
            'low': 0.1,
            'medium': 0.3,
            'high': 0.6,
            'critical': 1.0
        }
        
        total_weight = sum(severity_weights.get(s.severity, 0.3) for s in suggestions)
        max_possible_weight = len(suggestions) * 1.0
        
        if max_possible_weight == 0:
            return 1.0
        
        score = 1.0 - (total_weight / max_possible_weight)
        return max(0.0, min(1.0, score))
    
    async def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score."""
        try:
            # Simple readability calculation based on sentence length and word complexity
            sentences = content.split('.')
            words = content.split()
            
            if not sentences or not words:
                return 0.5
            
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Simple scoring (higher is more readable)
            sentence_score = max(0, 1.0 - (avg_sentence_length - 15) / 20)
            word_score = max(0, 1.0 - (avg_word_length - 4) / 4)
            
            return (sentence_score + word_score) / 2
            
        except Exception as e:
            logger.warning(f"Failed to calculate readability score: {e}")
            return 0.5
    
    async def _calculate_consistency_score(self, content: str) -> float:
        """Calculate consistency score."""
        try:
            # Check for consistency in style, tone, and terminology
            prompt = f"""
            Rate the consistency of this text on a scale of 0-1. Consider:
            1. Consistent tone and voice throughout
            2. Consistent terminology and definitions
            3. Consistent formatting and structure
            4. Consistent citation style
            
            Text:
            {content[:1000]}
            
            Provide only a number between 0 and 1.
            """
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=10,
                temperature=0.1
            )
            
            # Extract number from response
            import re
            numbers = re.findall(r'0\.\d+|1\.0|0|1', response.content)
            if numbers:
                return float(numbers[0])
            
        except Exception as e:
            logger.warning(f"Failed to calculate consistency score: {e}")
        
        return 0.7  # Default score
    
    async def _generate_edit_summary(
        self,
        content: str,
        suggestions: List[EditSuggestion],
        overall_score: float
    ) -> str:
        """Generate a summary of the edit report."""
        try:
            prompt = f"""
            Generate a brief summary of the editing review for this content.
            
            Content length: {len(content.split())} words
            Overall score: {overall_score:.2f}/1.0
            Number of suggestions: {len(suggestions)}
            
            Suggestion breakdown:
            {self._summarize_suggestions(suggestions)}
            
            Provide a concise summary highlighting:
            1. Overall quality assessment
            2. Main areas for improvement
            3. Key strengths
            4. Priority recommendations
            """
            
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.4
            )
            
            return response.content
            
        except Exception as e:
            logger.warning(f"Failed to generate edit summary: {e}")
            return f"Edit review completed. Overall score: {overall_score:.2f}. {len(suggestions)} suggestions provided."
    
    def _summarize_suggestions(self, suggestions: List[EditSuggestion]) -> str:
        """Summarize suggestions by type and severity."""
        summary = {}
        
        for suggestion in suggestions:
            key = f"{suggestion.type}_{suggestion.severity}"
            summary[key] = summary.get(key, 0) + 1
        
        return "; ".join([f"{k}: {v}" for k, v in summary.items()])
    
    async def apply_edits(
        self,
        content: str,
        suggestions: List[EditSuggestion],
        apply_all: bool = False
    ) -> str:
        """
        Apply edit suggestions to content.
        
        Args:
            content: Original content
            suggestions: List of edit suggestions
            apply_all: Whether to apply all suggestions or only high/critical ones
            
        Returns:
            Edited content
        """
        if not suggestions:
            return content
        
        # Filter suggestions based on severity
        if not apply_all:
            suggestions = [s for s in suggestions if s.severity in ['high', 'critical']]
        
        # Sort suggestions by position (reverse order to avoid position shifts)
        suggestions.sort(key=lambda x: x.position, reverse=True)
        
        edited_content = content
        
        for suggestion in suggestions:
            try:
                # Apply the suggestion
                if suggestion.original_text in edited_content:
                    edited_content = edited_content.replace(
                        suggestion.original_text,
                        suggestion.suggested_text,
                        1
                    )
            except Exception as e:
                logger.warning(f"Failed to apply suggestion {suggestion.suggestion_id}: {e}")
        
        return edited_content
    
    async def get_edit_report(self, report_id: str) -> Optional[EditReport]:
        """Get edit report by ID."""
        return self.edit_reports.get(report_id)
    
    async def get_editing_history(self) -> List[Dict[str, Any]]:
        """Get editing history."""
        return self.editing_history
    
    async def execute_task(self, task_type: str, payload: Dict[str, Any]) -> Any:
        """Execute an editing task."""
        if task_type == "review_content":
            return await self.review_content(
                content=payload.get("content", ""),
                content_id=payload.get("content_id", ""),
                content_type=payload.get("content_type", "chapter"),
                context=payload.get("context", "")
            )
        elif task_type == "apply_edits":
            return await self.apply_edits(
                content=payload.get("content", ""),
                suggestions=payload.get("suggestions", []),
                apply_all=payload.get("apply_all", False)
            )
        elif task_type == "get_report":
            return await self.get_edit_report(payload.get("report_id"))
        else:
            raise ValueError(f"Unknown task type: {task_type}")