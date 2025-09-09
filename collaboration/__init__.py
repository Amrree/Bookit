"""
Collaboration module.

This module provides real-time collaboration features including
multi-user editing, comments, version control, and user management.
"""

from .collaboration_manager import CollaborationManager, User, Comment, Change, CollaborationSession

__all__ = ["CollaborationManager", "User", "Comment", "Change", "CollaborationSession"]