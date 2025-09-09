"""
Template Manager Module

Provides comprehensive template management for book generation,
including pre-built templates, custom template creation, and style guides.

Features:
- Pre-built book templates (Academic, Business, Creative, Technical)
- Chapter structure templates
- Style guide integration
- Custom template creation
- Template marketplace
- Template validation and testing
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

import pydantic

logger = logging.getLogger(__name__)


class ChapterTemplate(pydantic.BaseModel):
    """Template for individual chapters."""
    template_id: str
    name: str
    description: str
    category: str
    structure: List[Dict[str, Any]]
    word_count_target: int
    style_guidelines: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class BookTemplate(pydantic.BaseModel):
    """Template for complete books."""
    template_id: str
    name: str
    description: str
    category: str
    target_audience: str
    estimated_word_count: int
    chapter_templates: List[ChapterTemplate]
    style_guide: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class StyleTemplate(pydantic.BaseModel):
    """Style guide template."""
    style_id: str
    name: str
    description: str
    category: str
    rules: Dict[str, Any]
    examples: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class TemplateManager:
    """
    Manages templates for book generation.
    
    Features:
    - Pre-built template library
    - Custom template creation
    - Template validation
    - Style guide integration
    - Template marketplace
    """
    
    def __init__(self, templates_dir: str = "./output/templates"):
        """
        Initialize template manager.
        
        Args:
            templates_dir: Directory for storing templates
        """
        self.templates_dir = Path(templates_dir)
        self.book_templates_dir = self.templates_dir / "book_templates"
        self.chapter_templates_dir = self.templates_dir / "chapter_templates"
        self.style_templates_dir = self.templates_dir / "style_templates"
        
        # Create directories
        self._create_directories()
        
        # Initialize with default templates
        self._create_default_templates()
        
        logger.info(f"Template manager initialized with directory: {self.templates_dir}")
    
    def _create_directories(self):
        """Create template directories."""
        directories = [
            self.templates_dir,
            self.book_templates_dir,
            self.chapter_templates_dir,
            self.style_templates_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _create_default_templates(self):
        """Create default templates."""
        self._create_default_book_templates()
        self._create_default_chapter_templates()
        self._create_default_style_templates()
    
    def _create_default_book_templates(self):
        """Create default book templates."""
        templates = [
            {
                "template_id": "academic_research_paper",
                "name": "Academic Research Paper",
                "description": "Template for academic research papers with proper structure and citations",
                "category": "academic",
                "target_audience": "Researchers, academics, students",
                "estimated_word_count": 8000,
                "style_guide": "academic_apa",
                "chapters": [
                    "abstract", "introduction", "literature_review", "methodology",
                    "results", "discussion", "conclusion", "references"
                ]
            },
            {
                "template_id": "business_white_paper",
                "name": "Business White Paper",
                "description": "Professional white paper template for business analysis and recommendations",
                "category": "business",
                "target_audience": "Business professionals, executives",
                "estimated_word_count": 5000,
                "style_guide": "business_professional",
                "chapters": [
                    "executive_summary", "problem_statement", "solution_overview",
                    "market_analysis", "implementation_plan", "conclusion"
                ]
            },
            {
                "template_id": "self_help_guide",
                "name": "Self-Help Guide",
                "description": "Template for self-help and personal development books",
                "category": "creative",
                "target_audience": "General readers seeking personal growth",
                "estimated_word_count": 40000,
                "style_guide": "conversational",
                "chapters": [
                    "introduction", "foundation_principles", "practical_steps",
                    "case_studies", "action_plans", "conclusion"
                ]
            },
            {
                "template_id": "technical_documentation",
                "name": "Technical Documentation",
                "description": "Comprehensive technical documentation template",
                "category": "technical",
                "target_audience": "Developers, technical users",
                "estimated_word_count": 15000,
                "style_guide": "technical_precise",
                "chapters": [
                    "overview", "installation", "configuration", "api_reference",
                    "examples", "troubleshooting", "appendix"
                ]
            },
            {
                "template_id": "memoir_biography",
                "name": "Memoir/Biography",
                "description": "Template for personal memoirs and biographies",
                "category": "creative",
                "target_audience": "General readers interested in personal stories",
                "estimated_word_count": 60000,
                "style_guide": "narrative_personal",
                "chapters": [
                    "early_life", "formative_years", "key_events", "challenges",
                    "achievements", "reflections", "legacy"
                ]
            }
        ]
        
        for template_data in templates:
            self._save_book_template(template_data)
    
    def _create_default_chapter_templates(self):
        """Create default chapter templates."""
        templates = [
            {
                "template_id": "introduction",
                "name": "Introduction Chapter",
                "description": "Standard introduction chapter template",
                "category": "general",
                "structure": [
                    {"section": "hook", "description": "Engaging opening", "word_count": 200},
                    {"section": "background", "description": "Context and background", "word_count": 400},
                    {"section": "problem_statement", "description": "Problem being addressed", "word_count": 300},
                    {"section": "solution_preview", "description": "Brief solution overview", "word_count": 200},
                    {"section": "chapter_outline", "description": "What readers will learn", "word_count": 100}
                ],
                "word_count_target": 1200
            },
            {
                "template_id": "conclusion",
                "name": "Conclusion Chapter",
                "description": "Standard conclusion chapter template",
                "category": "general",
                "structure": [
                    {"section": "summary", "description": "Key points summary", "word_count": 300},
                    {"section": "key_takeaways", "description": "Main takeaways", "word_count": 400},
                    {"section": "call_to_action", "description": "Next steps for readers", "word_count": 200},
                    {"section": "final_thoughts", "description": "Closing thoughts", "word_count": 100}
                ],
                "word_count_target": 1000
            },
            {
                "template_id": "case_study",
                "name": "Case Study Chapter",
                "description": "Template for case study chapters",
                "category": "business",
                "structure": [
                    {"section": "case_overview", "description": "Case background", "word_count": 300},
                    {"section": "challenge", "description": "Problem faced", "word_count": 400},
                    {"section": "solution", "description": "Solution implemented", "word_count": 500},
                    {"section": "results", "description": "Outcomes and results", "word_count": 400},
                    {"section": "lessons_learned", "description": "Key insights", "word_count": 200}
                ],
                "word_count_target": 1800
            }
        ]
        
        for template_data in templates:
            self._save_chapter_template(template_data)
    
    def _create_default_style_templates(self):
        """Create default style templates."""
        templates = [
            {
                "style_id": "academic_apa",
                "name": "Academic APA Style",
                "description": "APA style guide for academic writing",
                "category": "academic",
                "rules": {
                    "font": "Times New Roman, 12pt",
                    "spacing": "double",
                    "margins": "1 inch all sides",
                    "citations": "author-date format",
                    "tone": "formal, objective",
                    "voice": "third person",
                    "paragraph_spacing": "no extra space between paragraphs"
                }
            },
            {
                "style_id": "business_professional",
                "name": "Business Professional",
                "description": "Professional business writing style",
                "category": "business",
                "rules": {
                    "font": "Arial, 11pt",
                    "spacing": "1.15",
                    "margins": "1 inch all sides",
                    "tone": "professional, confident",
                    "voice": "second person (you)",
                    "paragraph_spacing": "space between paragraphs",
                    "headings": "bold, title case"
                }
            },
            {
                "style_id": "conversational",
                "name": "Conversational",
                "description": "Friendly, conversational writing style",
                "category": "creative",
                "rules": {
                    "font": "Georgia, 12pt",
                    "spacing": "1.5",
                    "margins": "1 inch all sides",
                    "tone": "friendly, approachable",
                    "voice": "first person (I, we)",
                    "paragraph_spacing": "space between paragraphs",
                    "contractions": "allowed"
                }
            },
            {
                "style_id": "technical_precise",
                "name": "Technical Precise",
                "description": "Precise technical writing style",
                "category": "technical",
                "rules": {
                    "font": "Consolas, 11pt",
                    "spacing": "single",
                    "margins": "1 inch all sides",
                    "tone": "precise, clear",
                    "voice": "third person",
                    "paragraph_spacing": "no extra space",
                    "code_blocks": "monospace font"
                }
            }
        ]
        
        for template_data in templates:
            self._save_style_template(template_data)
    
    def create_book_template(self, template_data: Dict[str, Any]) -> bool:
        """Create a new book template."""
        try:
            template = BookTemplate(
                template_id=template_data["template_id"],
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                target_audience=template_data["target_audience"],
                estimated_word_count=template_data["estimated_word_count"],
                chapter_templates=template_data.get("chapter_templates", []),
                style_guide=template_data["style_guide"],
                metadata=template_data.get("metadata", {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return self._save_book_template(template.dict())
            
        except Exception as e:
            logger.error(f"Failed to create book template: {e}")
            return False
    
    def get_book_template(self, template_id: str) -> Optional[BookTemplate]:
        """Get a book template by ID."""
        template_path = self.book_templates_dir / f"{template_id}.json"
        
        if not template_path.exists():
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return BookTemplate(**template_data)
            
        except Exception as e:
            logger.error(f"Failed to load book template {template_id}: {e}")
            return None
    
    def list_book_templates(self, category: Optional[str] = None) -> List[BookTemplate]:
        """List all book templates, optionally filtered by category."""
        templates = []
        
        for template_file in self.book_templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                template = BookTemplate(**template_data)
                
                if category is None or template.category == category:
                    templates.append(template)
                    
            except Exception as e:
                logger.warning(f"Failed to load template {template_file.name}: {e}")
        
        return templates
    
    def create_chapter_template(self, template_data: Dict[str, Any]) -> bool:
        """Create a new chapter template."""
        try:
            template = ChapterTemplate(
                template_id=template_data["template_id"],
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                structure=template_data["structure"],
                word_count_target=template_data["word_count_target"],
                style_guidelines=template_data.get("style_guidelines", {}),
                metadata=template_data.get("metadata", {})
            )
            
            return self._save_chapter_template(template.dict())
            
        except Exception as e:
            logger.error(f"Failed to create chapter template: {e}")
            return False
    
    def get_chapter_template(self, template_id: str) -> Optional[ChapterTemplate]:
        """Get a chapter template by ID."""
        template_path = self.chapter_templates_dir / f"{template_id}.json"
        
        if not template_path.exists():
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return ChapterTemplate(**template_data)
            
        except Exception as e:
            logger.error(f"Failed to load chapter template {template_id}: {e}")
            return None
    
    def create_style_template(self, template_data: Dict[str, Any]) -> bool:
        """Create a new style template."""
        try:
            template = StyleTemplate(
                style_id=template_data["style_id"],
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                rules=template_data["rules"],
                examples=template_data.get("examples", {}),
                metadata=template_data.get("metadata", {})
            )
            
            return self._save_style_template(template.dict())
            
        except Exception as e:
            logger.error(f"Failed to create style template: {e}")
            return False
    
    def get_style_template(self, style_id: str) -> Optional[StyleTemplate]:
        """Get a style template by ID."""
        template_path = self.style_templates_dir / f"{style_id}.json"
        
        if not template_path.exists():
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return StyleTemplate(**template_data)
            
        except Exception as e:
            logger.error(f"Failed to load style template {style_id}: {e}")
            return None
    
    def _save_book_template(self, template_data: Dict[str, Any]) -> bool:
        """Save book template to file."""
        try:
            template_path = self.book_templates_dir / f"{template_data['template_id']}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save book template: {e}")
            return False
    
    def _save_chapter_template(self, template_data: Dict[str, Any]) -> bool:
        """Save chapter template to file."""
        try:
            template_path = self.chapter_templates_dir / f"{template_data['template_id']}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save chapter template: {e}")
            return False
    
    def _save_style_template(self, template_data: Dict[str, Any]) -> bool:
        """Save style template to file."""
        try:
            template_path = self.style_templates_dir / f"{template_data['style_id']}.json"
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save style template: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get template manager statistics."""
        return {
            "total_book_templates": len(list(self.book_templates_dir.glob("*.json"))),
            "total_chapter_templates": len(list(self.chapter_templates_dir.glob("*.json"))),
            "total_style_templates": len(list(self.style_templates_dir.glob("*.json"))),
            "templates_directory": str(self.templates_dir)
        }