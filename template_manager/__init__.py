"""
Template Manager module.

This module provides template management for book generation,
including pre-built templates, custom template creation, and style guides.
"""

from .template_manager import TemplateManager, BookTemplate, ChapterTemplate, StyleTemplate

__all__ = ["TemplateManager", "BookTemplate", "ChapterTemplate", "StyleTemplate"]