"""
Output Manager module.

This module provides comprehensive output management for generated books,
including folder structure, metadata, version control, and asset management.
"""

from .output_manager import OutputManager, BookMetadata, VersionHistory, BuildLog

__all__ = ["OutputManager", "BookMetadata", "VersionHistory", "BuildLog"]