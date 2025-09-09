"""
Collaboration Manager Module

Provides real-time collaboration features including multi-user editing,
comments, version control, change tracking, and user management.

Features:
- Multi-user editing
- Real-time synchronization
- Comment system
- Change tracking and history
- User permissions and roles
- Conflict resolution
- Notification system
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
import logging

import pydantic

logger = logging.getLogger(__name__)


class User(pydantic.BaseModel):
    """User model for collaboration."""
    user_id: str
    username: str
    email: str
    role: str = "editor"  # admin, editor, viewer, commenter
    permissions: List[str] = ["read", "write"]
    last_active: datetime
    avatar_url: Optional[str] = None
    metadata: Dict[str, Any] = {}


class Comment(pydantic.BaseModel):
    """Comment model for collaborative editing."""
    comment_id: str
    book_id: str
    chapter_id: str
    user_id: str
    content: str
    position: int  # Character position in text
    length: int    # Length of selected text
    created_at: datetime
    updated_at: datetime
    resolved: bool = False
    replies: List[str] = []  # Comment IDs of replies
    parent_id: Optional[str] = None


class Change(pydantic.BaseModel):
    """Change model for tracking edits."""
    change_id: str
    book_id: str
    chapter_id: str
    user_id: str
    change_type: str  # insert, delete, replace, format
    position: int
    old_text: str
    new_text: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class CollaborationSession(pydantic.BaseModel):
    """Active collaboration session."""
    session_id: str
    book_id: str
    chapter_id: str
    active_users: List[str] = []  # User IDs
    created_at: datetime
    last_activity: datetime
    status: str = "active"  # active, paused, ended


class CollaborationManager:
    """
    Manages real-time collaboration features.
    
    Features:
    - Multi-user editing
    - Real-time synchronization
    - Comment system
    - Change tracking
    - User management
    - Conflict resolution
    """
    
    def __init__(self, collaboration_dir: str = "./output/collaboration"):
        """
        Initialize collaboration manager.
        
        Args:
            collaboration_dir: Directory for collaboration data
        """
        self.collaboration_dir = Path(collaboration_dir)
        self.users_dir = self.collaboration_dir / "users"
        self.comments_dir = self.collaboration_dir / "comments"
        self.changes_dir = self.collaboration_dir / "changes"
        self.sessions_dir = self.collaboration_dir / "sessions"
        
        # Create directories
        for directory in [self.collaboration_dir, self.users_dir, self.comments_dir, 
                         self.changes_dir, self.sessions_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Active sessions
        self.active_sessions: Dict[str, CollaborationSession] = {}
        
        # User connections (WebSocket connections would be stored here)
        self.user_connections: Dict[str, Any] = {}
        
        logger.info(f"Collaboration manager initialized with directory: {self.collaboration_dir}")
    
    def create_user(self, username: str, email: str, role: str = "editor") -> User:
        """
        Create a new user.
        
        Args:
            username: Username
            email: Email address
            role: User role (admin, editor, viewer, commenter)
            
        Returns:
            Created user
        """
        user_id = str(uuid.uuid4())
        
        # Set permissions based on role
        permissions = {
            "admin": ["read", "write", "delete", "manage_users", "manage_permissions"],
            "editor": ["read", "write", "comment"],
            "viewer": ["read", "comment"],
            "commenter": ["read", "comment"]
        }.get(role, ["read"])
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            last_active=datetime.now()
        )
        
        # Save user
        self._save_user(user)
        
        logger.info(f"Created user: {username} ({role})")
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        user_path = self.users_dir / f"{user_id}.json"
        
        if not user_path.exists():
            return None
        
        try:
            with open(user_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            return User(**user_data)
            
        except Exception as e:
            logger.error(f"Failed to load user {user_id}: {e}")
            return None
    
    def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp."""
        user = self.get_user(user_id)
        if user:
            user.last_active = datetime.now()
            self._save_user(user)
    
    def create_comment(self, book_id: str, chapter_id: str, user_id: str, 
                      content: str, position: int, length: int = 0) -> Comment:
        """
        Create a new comment.
        
        Args:
            book_id: Book ID
            chapter_id: Chapter ID
            user_id: User ID
            content: Comment content
            position: Character position
            length: Length of selected text
            
        Returns:
            Created comment
        """
        comment_id = str(uuid.uuid4())
        
        comment = Comment(
            comment_id=comment_id,
            book_id=book_id,
            chapter_id=chapter_id,
            user_id=user_id,
            content=content,
            position=position,
            length=length,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save comment
        self._save_comment(comment)
        
        # Notify other users
        self._notify_comment_created(comment)
        
        logger.info(f"Created comment by user {user_id} on {book_id}/{chapter_id}")
        
        return comment
    
    def get_comments(self, book_id: str, chapter_id: str) -> List[Comment]:
        """Get all comments for a book chapter."""
        comments = []
        
        for comment_file in self.comments_dir.glob("*.json"):
            try:
                with open(comment_file, 'r', encoding='utf-8') as f:
                    comment_data = json.load(f)
                
                comment = Comment(**comment_data)
                
                if comment.book_id == book_id and comment.chapter_id == chapter_id:
                    comments.append(comment)
                    
            except Exception as e:
                logger.warning(f"Failed to load comment {comment_file.name}: {e}")
        
        # Sort by position
        comments.sort(key=lambda c: c.position)
        
        return comments
    
    def resolve_comment(self, comment_id: str, user_id: str) -> bool:
        """Resolve a comment."""
        comment = self._get_comment_by_id(comment_id)
        if not comment:
            return False
        
        comment.resolved = True
        comment.updated_at = datetime.now()
        
        self._save_comment(comment)
        
        # Notify other users
        self._notify_comment_resolved(comment)
        
        logger.info(f"Resolved comment {comment_id} by user {user_id}")
        
        return True
    
    def create_change(self, book_id: str, chapter_id: str, user_id: str,
                     change_type: str, position: int, old_text: str, new_text: str) -> Change:
        """
        Create a change record.
        
        Args:
            book_id: Book ID
            chapter_id: Chapter ID
            user_id: User ID
            change_type: Type of change
            position: Position in text
            old_text: Original text
            new_text: New text
            
        Returns:
            Created change
        """
        change_id = str(uuid.uuid4())
        
        change = Change(
            change_id=change_id,
            book_id=book_id,
            chapter_id=chapter_id,
            user_id=user_id,
            change_type=change_type,
            position=position,
            old_text=old_text,
            new_text=new_text,
            timestamp=datetime.now()
        )
        
        # Save change
        self._save_change(change)
        
        # Notify other users
        self._notify_change_created(change)
        
        logger.info(f"Created change by user {user_id} on {book_id}/{chapter_id}")
        
        return change
    
    def get_changes(self, book_id: str, chapter_id: str, since: Optional[datetime] = None) -> List[Change]:
        """Get changes for a book chapter."""
        changes = []
        
        for change_file in self.changes_dir.glob("*.json"):
            try:
                with open(change_file, 'r', encoding='utf-8') as f:
                    change_data = json.load(f)
                
                change = Change(**change_data)
                
                if (change.book_id == book_id and 
                    change.chapter_id == chapter_id and
                    (since is None or change.timestamp >= since)):
                    changes.append(change)
                    
            except Exception as e:
                logger.warning(f"Failed to load change {change_file.name}: {e}")
        
        # Sort by timestamp
        changes.sort(key=lambda c: c.timestamp)
        
        return changes
    
    def start_collaboration_session(self, book_id: str, chapter_id: str, user_id: str) -> CollaborationSession:
        """
        Start a new collaboration session.
        
        Args:
            book_id: Book ID
            chapter_id: Chapter ID
            user_id: User ID
            
        Returns:
            Collaboration session
        """
        session_id = str(uuid.uuid4())
        
        session = CollaborationSession(
            session_id=session_id,
            book_id=book_id,
            chapter_id=chapter_id,
            active_users=[user_id],
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        # Save session
        self._save_session(session)
        
        # Add to active sessions
        self.active_sessions[session_id] = session
        
        # Update user activity
        self.update_user_activity(user_id)
        
        logger.info(f"Started collaboration session {session_id} for {book_id}/{chapter_id}")
        
        return session
    
    def join_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """
        Join an existing collaboration session.
        
        Args:
            session_id: Session ID
            user_id: User ID
            
        Returns:
            True if successful
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        if user_id not in session.active_users:
            session.active_users.append(user_id)
            session.last_activity = datetime.now()
            
            # Save updated session
            self._save_session(session)
            
            # Notify other users
            self._notify_user_joined(session, user_id)
            
            logger.info(f"User {user_id} joined session {session_id}")
        
        # Update user activity
        self.update_user_activity(user_id)
        
        return True
    
    def leave_collaboration_session(self, session_id: str, user_id: str) -> bool:
        """
        Leave a collaboration session.
        
        Args:
            session_id: Session ID
            user_id: User ID
            
        Returns:
            True if successful
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        if user_id in session.active_users:
            session.active_users.remove(user_id)
            session.last_activity = datetime.now()
            
            # If no users left, end session
            if not session.active_users:
                session.status = "ended"
                del self.active_sessions[session_id]
            else:
                # Save updated session
                self._save_session(session)
            
            # Notify other users
            self._notify_user_left(session, user_id)
            
            logger.info(f"User {user_id} left session {session_id}")
        
        return True
    
    def get_active_sessions(self, book_id: str) -> List[CollaborationSession]:
        """Get active sessions for a book."""
        sessions = []
        
        for session in self.active_sessions.values():
            if session.book_id == book_id and session.status == "active":
                sessions.append(session)
        
        return sessions
    
    def get_collaboration_statistics(self, book_id: str) -> Dict[str, Any]:
        """Get collaboration statistics for a book."""
        # Count comments
        comment_count = 0
        resolved_comments = 0
        
        for comment_file in self.comments_dir.glob("*.json"):
            try:
                with open(comment_file, 'r', encoding='utf-8') as f:
                    comment_data = json.load(f)
                
                comment = Comment(**comment_data)
                
                if comment.book_id == book_id:
                    comment_count += 1
                    if comment.resolved:
                        resolved_comments += 1
                        
            except Exception as e:
                logger.warning(f"Failed to load comment {comment_file.name}: {e}")
        
        # Count changes
        change_count = 0
        
        for change_file in self.changes_dir.glob("*.json"):
            try:
                with open(change_file, 'r', encoding='utf-8') as f:
                    change_data = json.load(f)
                
                change = Change(**change_data)
                
                if change.book_id == book_id:
                    change_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to load change {change_file.name}: {e}")
        
        # Count active sessions
        active_sessions = len([s for s in self.active_sessions.values() 
                              if s.book_id == book_id and s.status == "active"])
        
        return {
            "book_id": book_id,
            "total_comments": comment_count,
            "resolved_comments": resolved_comments,
            "unresolved_comments": comment_count - resolved_comments,
            "total_changes": change_count,
            "active_sessions": active_sessions,
            "collaboration_score": self._calculate_collaboration_score(book_id)
        }
    
    def _calculate_collaboration_score(self, book_id: str) -> float:
        """Calculate collaboration score for a book."""
        stats = self.get_collaboration_statistics(book_id)
        
        # Simple scoring algorithm
        score = 0.0
        
        # Comments contribute to score
        if stats["total_comments"] > 0:
            score += min(stats["total_comments"] * 0.1, 2.0)
        
        # Resolved comments contribute more
        if stats["resolved_comments"] > 0:
            score += min(stats["resolved_comments"] * 0.2, 2.0)
        
        # Changes contribute to score
        if stats["total_changes"] > 0:
            score += min(stats["total_changes"] * 0.05, 1.0)
        
        # Active sessions contribute to score
        if stats["active_sessions"] > 0:
            score += min(stats["active_sessions"] * 0.5, 2.0)
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _save_user(self, user: User):
        """Save user to file."""
        user_path = self.users_dir / f"{user.user_id}.json"
        
        with open(user_path, 'w', encoding='utf-8') as f:
            json.dump(user.dict(), f, indent=2, default=str)
    
    def _save_comment(self, comment: Comment):
        """Save comment to file."""
        comment_path = self.comments_dir / f"{comment.comment_id}.json"
        
        with open(comment_path, 'w', encoding='utf-8') as f:
            json.dump(comment.dict(), f, indent=2, default=str)
    
    def _save_change(self, change: Change):
        """Save change to file."""
        change_path = self.changes_dir / f"{change.change_id}.json"
        
        with open(change_path, 'w', encoding='utf-8') as f:
            json.dump(change.dict(), f, indent=2, default=str)
    
    def _save_session(self, session: CollaborationSession):
        """Save session to file."""
        session_path = self.sessions_dir / f"{session.session_id}.json"
        
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session.dict(), f, indent=2, default=str)
    
    def _get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID."""
        comment_path = self.comments_dir / f"{comment_id}.json"
        
        if not comment_path.exists():
            return None
        
        try:
            with open(comment_path, 'r', encoding='utf-8') as f:
                comment_data = json.load(f)
            
            return Comment(**comment_data)
            
        except Exception as e:
            logger.error(f"Failed to load comment {comment_id}: {e}")
            return None
    
    def _notify_comment_created(self, comment: Comment):
        """Notify users about new comment."""
        # In a real implementation, this would send WebSocket messages
        logger.info(f"Notifying users about new comment: {comment.comment_id}")
    
    def _notify_comment_resolved(self, comment: Comment):
        """Notify users about resolved comment."""
        # In a real implementation, this would send WebSocket messages
        logger.info(f"Notifying users about resolved comment: {comment.comment_id}")
    
    def _notify_change_created(self, change: Change):
        """Notify users about new change."""
        # In a real implementation, this would send WebSocket messages
        logger.info(f"Notifying users about new change: {change.change_id}")
    
    def _notify_user_joined(self, session: CollaborationSession, user_id: str):
        """Notify users about user joining session."""
        # In a real implementation, this would send WebSocket messages
        logger.info(f"Notifying users about user {user_id} joining session {session.session_id}")
    
    def _notify_user_left(self, session: CollaborationSession, user_id: str):
        """Notify users about user leaving session."""
        # In a real implementation, this would send WebSocket messages
        logger.info(f"Notifying users about user {user_id} leaving session {session.session_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get collaboration manager statistics."""
        return {
            "total_users": len(list(self.users_dir.glob("*.json"))),
            "total_comments": len(list(self.comments_dir.glob("*.json"))),
            "total_changes": len(list(self.changes_dir.glob("*.json"))),
            "total_sessions": len(list(self.sessions_dir.glob("*.json"))),
            "active_sessions": len(self.active_sessions),
            "collaboration_directory": str(self.collaboration_dir)
        }