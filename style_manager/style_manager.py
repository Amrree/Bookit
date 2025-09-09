"""
Style Manager Module

Provides comprehensive style guide management and consistency checking
for book generation with grammar, tone, and formatting validation.

Features:
- Style guide management
- Grammar and tone checking
- Consistency validation
- Brand voice maintenance
- Automated style application
- Custom style rules
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

import pydantic

logger = logging.getLogger(__name__)


class StyleRule(pydantic.BaseModel):
    """Individual style rule."""
    rule_id: str
    name: str
    description: str
    pattern: str
    replacement: str
    category: str  # grammar, tone, formatting, consistency
    severity: str  # error, warning, suggestion
    enabled: bool = True
    examples: List[Dict[str, str]] = []  # [{"incorrect": "...", "correct": "..."}]


class StyleGuide(pydantic.BaseModel):
    """Complete style guide."""
    guide_id: str
    name: str
    description: str
    category: str
    rules: List[StyleRule]
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class StyleCheck(pydantic.BaseModel):
    """Result of style checking."""
    rule_id: str
    rule_name: str
    severity: str
    message: str
    position: int
    length: int
    suggested_fix: str
    context: str


class StyleManager:
    """
    Manages style guides and consistency checking.
    
    Features:
    - Style guide management
    - Grammar and tone checking
    - Consistency validation
    - Brand voice maintenance
    - Automated style application
    """
    
    def __init__(self, styles_dir: str = "./output/styles"):
        """
        Initialize style manager.
        
        Args:
            styles_dir: Directory for storing style guides
        """
        self.styles_dir = Path(styles_dir)
        self.styles_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize with default style guides
        self._create_default_style_guides()
        
        logger.info(f"Style manager initialized with directory: {self.styles_dir}")
    
    def _create_default_style_guides(self):
        """Create default style guides."""
        self._create_academic_style_guide()
        self._create_business_style_guide()
        self._create_conversational_style_guide()
        self._create_technical_style_guide()
    
    def _create_academic_style_guide(self):
        """Create academic style guide."""
        rules = [
            StyleRule(
                rule_id="academic_no_contractions",
                name="No Contractions",
                description="Avoid contractions in academic writing",
                pattern=r"\b(?:don't|won't|can't|isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't|doesn't|didn't|wouldn't|couldn't|shouldn't|mustn't)\b",
                replacement="do not, will not, cannot, is not, are not, was not, were not, has not, have not, had not, does not, did not, would not, could not, should not, must not",
                category="tone",
                severity="warning",
                examples=[
                    {"incorrect": "don't", "correct": "do not"},
                    {"incorrect": "won't", "correct": "will not"}
                ]
            ),
            StyleRule(
                rule_id="academic_passive_voice",
                name="Prefer Active Voice",
                description="Use active voice instead of passive voice",
                pattern=r"\b(?:is|are|was|were|be|been|being)\s+\w+ed\b",
                replacement="[Consider active voice]",
                category="tone",
                severity="suggestion",
                examples=[
                    {"incorrect": "The study was conducted by researchers", "correct": "Researchers conducted the study"}
                ]
            ),
            StyleRule(
                rule_id="academic_first_person",
                name="Avoid First Person",
                description="Avoid first person pronouns in academic writing",
                pattern=r"\b(?:I|we|my|our|me|us)\b",
                replacement="[Consider third person]",
                category="tone",
                severity="warning",
                examples=[
                    {"incorrect": "I believe", "correct": "The evidence suggests"}
                ]
            ),
            StyleRule(
                rule_id="academic_citations",
                name="Proper Citations",
                description="Ensure proper citation format",
                pattern=r"\([^)]*\)",
                replacement="[Check citation format]",
                category="formatting",
                severity="error",
                examples=[
                    {"incorrect": "(Smith, 2020)", "correct": "(Smith, 2020, p. 15)"}
                ]
            )
        ]
        
        guide = StyleGuide(
            guide_id="academic_apa",
            name="Academic APA Style",
            description="APA style guide for academic writing",
            category="academic",
            rules=rules,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._save_style_guide(guide)
    
    def _create_business_style_guide(self):
        """Create business style guide."""
        rules = [
            StyleRule(
                rule_id="business_clear_language",
                name="Clear and Concise Language",
                description="Use clear, concise language in business writing",
                pattern=r"\b(?:utilize|facilitate|implement|leverage|optimize|enhance)\b",
                replacement="use, help, do, use, improve, improve",
                category="tone",
                severity="suggestion",
                examples=[
                    {"incorrect": "utilize", "correct": "use"},
                    {"incorrect": "facilitate", "correct": "help"}
                ]
            ),
            StyleRule(
                rule_id="business_positive_tone",
                name="Positive Tone",
                description="Use positive language in business writing",
                pattern=r"\b(?:can't|cannot|won't|will not|don't|do not)\b",
                replacement="[Consider positive phrasing]",
                category="tone",
                severity="suggestion",
                examples=[
                    {"incorrect": "We can't do that", "correct": "We can explore alternatives"}
                ]
            ),
            StyleRule(
                rule_id="business_bullet_points",
                name="Consistent Bullet Points",
                description="Use consistent bullet point formatting",
                pattern=r"^[\s]*[•·▪▫]\s",
                replacement="• ",
                category="formatting",
                severity="warning",
                examples=[
                    {"incorrect": "· Item", "correct": "• Item"}
                ]
            ),
            StyleRule(
                rule_id="business_numbers",
                name="Number Formatting",
                description="Use consistent number formatting",
                pattern=r"\b(\d{1,3})(\d{3})\b",
                replacement=r"\1,\2",
                category="formatting",
                severity="warning",
                examples=[
                    {"incorrect": "1000", "correct": "1,000"}
                ]
            )
        ]
        
        guide = StyleGuide(
            guide_id="business_professional",
            name="Business Professional Style",
            description="Professional business writing style guide",
            category="business",
            rules=rules,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._save_style_guide(guide)
    
    def _create_conversational_style_guide(self):
        """Create conversational style guide."""
        rules = [
            StyleRule(
                rule_id="conversational_contractions",
                name="Use Contractions",
                description="Use contractions for conversational tone",
                pattern=r"\b(?:do not|will not|cannot|is not|are not|was not|were not|has not|have not|had not|does not|did not|would not|could not|should not|must not)\b",
                replacement="don't, won't, can't, isn't, aren't, wasn't, weren't, hasn't, haven't, hadn't, doesn't, didn't, wouldn't, couldn't, shouldn't, mustn't",
                category="tone",
                severity="suggestion",
                examples=[
                    {"incorrect": "do not", "correct": "don't"},
                    {"incorrect": "will not", "correct": "won't"}
                ]
            ),
            StyleRule(
                rule_id="conversational_questions",
                name="Use Questions",
                description="Use questions to engage readers",
                pattern=r"\.(?!\s*$)",
                replacement="?",
                category="tone",
                severity="suggestion",
                examples=[
                    {"incorrect": "This is important.", "correct": "Why is this important?"}
                ]
            ),
            StyleRule(
                rule_id="conversational_short_sentences",
                name="Short Sentences",
                description="Use short, clear sentences",
                pattern=r"[^.!?]{50,}[.!?]",
                replacement="[Consider breaking into shorter sentences]",
                category="tone",
                severity="suggestion",
                examples=[
                    {"incorrect": "This is a very long sentence that goes on and on and should be broken up.", "correct": "This is a long sentence. It should be broken up."}
                ]
            )
        ]
        
        guide = StyleGuide(
            guide_id="conversational",
            name="Conversational Style",
            description="Friendly, conversational writing style guide",
            category="creative",
            rules=rules,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._save_style_guide(guide)
    
    def _create_technical_style_guide(self):
        """Create technical style guide."""
        rules = [
            StyleRule(
                rule_id="technical_precise_language",
                name="Precise Technical Language",
                description="Use precise technical terminology",
                pattern=r"\b(?:thing|stuff|thingy|gizmo)\b",
                replacement="[Use specific technical term]",
                category="tone",
                severity="error",
                examples=[
                    {"incorrect": "thing", "correct": "component, module, function, etc."}
                ]
            ),
            StyleRule(
                rule_id="technical_code_formatting",
                name="Code Formatting",
                description="Format code properly",
                pattern=r"`[^`]+`",
                replacement="[Check code formatting]",
                category="formatting",
                severity="warning",
                examples=[
                    {"incorrect": "`code`", "correct": "```code```"}
                ]
            ),
            StyleRule(
                rule_id="technical_acronyms",
                name="Define Acronyms",
                description="Define acronyms on first use",
                pattern=r"\b[A-Z]{2,}\b",
                replacement="[Define acronym]",
                category="consistency",
                severity="warning",
                examples=[
                    {"incorrect": "API", "correct": "API (Application Programming Interface)"}
                ]
            )
        ]
        
        guide = StyleGuide(
            guide_id="technical_precise",
            name="Technical Precise Style",
            description="Precise technical writing style guide",
            category="technical",
            rules=rules,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._save_style_guide(guide)
    
    def create_style_guide(self, guide_data: Dict[str, Any]) -> bool:
        """Create a new style guide."""
        try:
            guide = StyleGuide(
                guide_id=guide_data["guide_id"],
                name=guide_data["name"],
                description=guide_data["description"],
                category=guide_data["category"],
                rules=[StyleRule(**rule) for rule in guide_data.get("rules", [])],
                metadata=guide_data.get("metadata", {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            return self._save_style_guide(guide)
            
        except Exception as e:
            logger.error(f"Failed to create style guide: {e}")
            return False
    
    def get_style_guide(self, guide_id: str) -> Optional[StyleGuide]:
        """Get a style guide by ID."""
        guide_path = self.styles_dir / f"{guide_id}.json"
        
        if not guide_path.exists():
            return None
        
        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                guide_data = json.load(f)
            
            return StyleGuide(**guide_data)
            
        except Exception as e:
            logger.error(f"Failed to load style guide {guide_id}: {e}")
            return None
    
    def list_style_guides(self, category: Optional[str] = None) -> List[StyleGuide]:
        """List all style guides, optionally filtered by category."""
        guides = []
        
        for guide_file in self.styles_dir.glob("*.json"):
            try:
                with open(guide_file, 'r', encoding='utf-8') as f:
                    guide_data = json.load(f)
                
                guide = StyleGuide(**guide_data)
                
                if category is None or guide.category == category:
                    guides.append(guide)
                    
            except Exception as e:
                logger.warning(f"Failed to load style guide {guide_file.name}: {e}")
        
        return guides
    
    def check_content(self, content: str, guide_id: str) -> List[StyleCheck]:
        """
        Check content against a style guide.
        
        Args:
            content: Content to check
            guide_id: Style guide ID
            
        Returns:
            List of style check results
        """
        guide = self.get_style_guide(guide_id)
        if not guide:
            return []
        
        checks = []
        
        for rule in guide.rules:
            if not rule.enabled:
                continue
            
            try:
                matches = list(re.finditer(rule.pattern, content, re.IGNORECASE))
                
                for match in matches:
                    check = StyleCheck(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=rule.description,
                        position=match.start(),
                        length=match.end() - match.start(),
                        suggested_fix=rule.replacement,
                        context=content[max(0, match.start()-50):match.end()+50]
                    )
                    checks.append(check)
                    
            except re.error as e:
                logger.warning(f"Invalid regex pattern in rule {rule.rule_id}: {e}")
                continue
        
        return checks
    
    def apply_style_guide(self, content: str, guide_id: str) -> Tuple[str, List[StyleCheck]]:
        """
        Apply style guide to content.
        
        Args:
            content: Content to apply style to
            guide_id: Style guide ID
            
        Returns:
            Tuple of (modified_content, applied_changes)
        """
        guide = self.get_style_guide(guide_id)
        if not guide:
            return content, []
        
        modified_content = content
        applied_changes = []
        
        for rule in guide.rules:
            if not rule.enabled:
                continue
            
            try:
                # Apply simple replacements
                if not rule.replacement.startswith('['):
                    new_content = re.sub(rule.pattern, rule.replacement, modified_content, flags=re.IGNORECASE)
                    if new_content != modified_content:
                        modified_content = new_content
                        applied_changes.append(StyleCheck(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            severity="applied",
                            message=f"Applied: {rule.description}",
                            position=0,
                            length=0,
                            suggested_fix="",
                            context=""
                        ))
                        
            except re.error as e:
                logger.warning(f"Invalid regex pattern in rule {rule.rule_id}: {e}")
                continue
        
        return modified_content, applied_changes
    
    def get_style_statistics(self, content: str, guide_id: str) -> Dict[str, Any]:
        """Get style statistics for content."""
        checks = self.check_content(content, guide_id)
        
        stats = {
            "total_issues": len(checks),
            "errors": len([c for c in checks if c.severity == "error"]),
            "warnings": len([c for c in checks if c.severity == "warning"]),
            "suggestions": len([c for c in checks if c.severity == "suggestion"]),
            "word_count": len(content.split()),
            "character_count": len(content),
            "sentence_count": len(re.findall(r'[.!?]+', content)),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "issues_by_category": {}
        }
        
        # Group issues by category
        for check in checks:
            guide = self.get_style_guide(guide_id)
            if guide:
                rule = next((r for r in guide.rules if r.rule_id == check.rule_id), None)
                if rule:
                    category = rule.category
                    if category not in stats["issues_by_category"]:
                        stats["issues_by_category"][category] = 0
                    stats["issues_by_category"][category] += 1
        
        return stats
    
    def _save_style_guide(self, guide: StyleGuide) -> bool:
        """Save style guide to file."""
        try:
            guide_path = self.styles_dir / f"{guide.guide_id}.json"
            with open(guide_path, 'w', encoding='utf-8') as f:
                json.dump(guide.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Failed to save style guide: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get style manager statistics."""
        return {
            "total_style_guides": len(list(self.styles_dir.glob("*.json"))),
            "styles_directory": str(self.styles_dir)
        }