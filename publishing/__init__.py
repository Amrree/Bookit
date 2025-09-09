"""
Publishing module.

This module provides publishing integration for various platforms
including Amazon KDP, Google Books, and other publishing channels.
"""

from .publishing_manager import PublishingManager, PublishingPlatform, BookMetadata, PublishingResult

__all__ = ["PublishingManager", "PublishingPlatform", "BookMetadata", "PublishingResult"]