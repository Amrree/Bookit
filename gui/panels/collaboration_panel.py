"""
Collaboration Panel

A specialized panel for real-time collaboration features including
multi-user editing, comments, change tracking, and user management.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from collaboration.collaboration_manager import CollaborationManager, User, Comment, Change

logger = logging.getLogger(__name__)


class CollaborationPanel(ctk.CTkFrame):
    """
    Collaboration panel with real-time collaboration features.
    
    Features:
    - Multi-user editing
    - Real-time comments and discussions
    - Change tracking and history
    - User management and permissions
    - Session management
    - Conflict resolution
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize collaboration manager
        self.collaboration_manager = CollaborationManager()
        
        # Collaboration state
        self.current_user = None
        self.current_session = None
        self.active_users = []
        self.comments = []
        self.changes = []
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the collaboration panel UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="Collaboration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Real-time collaboration with comments and change tracking",
            font=ctk.CTkFont(size=14),
            text_color=("#666666", "#cccccc")
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Main content area
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - User management and session
        self._create_user_panel(content_frame)
        
        # Right panel - Comments and changes
        self._create_activity_panel(content_frame)
    
    def _create_user_panel(self, parent):
        """Create the user management panel."""
        user_frame = ctk.CTkFrame(parent)
        user_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # User section
        user_section = ctk.CTkFrame(user_frame)
        user_section.pack(fill="x", padx=20, pady=20)
        
        user_title = ctk.CTkLabel(
            user_section,
            text="User Management",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        user_title.pack(anchor="w", pady=(0, 15))
        
        # Current user info
        self.current_user_frame = ctk.CTkFrame(user_section)
        self.current_user_frame.pack(fill="x", pady=(0, 15))
        
        self.user_info_label = ctk.CTkLabel(
            self.current_user_frame,
            text="Not logged in",
            font=ctk.CTkFont(size=14),
            text_color=("#666666", "#cccccc")
        )
        self.user_info_label.pack(padx=15, pady=10)
        
        # Login/Register buttons
        auth_buttons_frame = ctk.CTkFrame(user_section, fg_color="transparent")
        auth_buttons_frame.pack(fill="x", pady=(0, 15))
        
        self.login_btn = ctk.CTkButton(
            auth_buttons_frame,
            text="Login",
            command=self._show_login_dialog,
            width=100,
            height=35
        )
        self.login_btn.pack(side="left", padx=(0, 10))
        
        self.register_btn = ctk.CTkButton(
            auth_buttons_frame,
            text="Register",
            command=self._show_register_dialog,
            width=100,
            height=35
        )
        self.register_btn.pack(side="left")
        
        # Session management
        session_section = ctk.CTkFrame(user_frame)
        session_section.pack(fill="both", expand=True, padx=20, pady=20)
        
        session_title = ctk.CTkLabel(
            session_section,
            text="Session Management",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        session_title.pack(anchor="w", pady=(0, 15))
        
        # Session info
        self.session_info_label = ctk.CTkLabel(
            session_section,
            text="No active session",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#cccccc")
        )
        self.session_info_label.pack(anchor="w", pady=(0, 10))
        
        # Session actions
        session_actions = ctk.CTkFrame(session_section, fg_color="transparent")
        session_actions.pack(fill="x", pady=(0, 15))
        
        self.start_session_btn = ctk.CTkButton(
            session_actions,
            text="Start Session",
            command=self._start_session,
            width=120,
            height=35
        )
        self.start_session_btn.pack(side="left", padx=(0, 10))
        
        self.join_session_btn = ctk.CTkButton(
            session_actions,
            text="Join Session",
            command=self._show_join_session_dialog,
            width=120,
            height=35
        )
        self.join_session_btn.pack(side="left")
        
        # Active users
        users_section = ctk.CTkFrame(session_section)
        users_section.pack(fill="both", expand=True)
        
        users_title = ctk.CTkLabel(
            users_section,
            text="Active Users",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        users_title.pack(anchor="w", padx=15, pady=10)
        
        # Users listbox
        self.users_listbox = tk.Listbox(
            users_section,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#1a1a1a",
            selectbackground="#007bff",
            selectforeground="#ffffff"
        )
        self.users_listbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def _create_activity_panel(self, parent):
        """Create the activity panel for comments and changes."""
        activity_frame = ctk.CTkFrame(parent)
        activity_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Activity tabs
        self.activity_notebook = ctk.CTkTabview(activity_frame)
        self.activity_notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Comments tab
        self._create_comments_tab()
        
        # Changes tab
        self._create_changes_tab()
        
        # Statistics tab
        self._create_statistics_tab()
    
    def _create_comments_tab(self):
        """Create the comments tab."""
        self.comments_tab = self.activity_notebook.add("Comments")
        
        # Comments header
        comments_header = ctk.CTkFrame(self.comments_tab, fg_color="transparent")
        comments_header.pack(fill="x", pady=(0, 15))
        
        comments_title = ctk.CTkLabel(
            comments_header,
            text="Comments & Discussions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        comments_title.pack(anchor="w")
        
        # Add comment section
        add_comment_frame = ctk.CTkFrame(self.comments_tab)
        add_comment_frame.pack(fill="x", pady=(0, 15))
        
        # Comment input
        self.comment_entry = ctk.CTkTextbox(
            add_comment_frame,
            height=80,
            font=ctk.CTkFont(size=12),
            placeholder_text="Add a comment..."
        )
        self.comment_entry.pack(fill="x", padx=15, pady=10)
        
        # Comment actions
        comment_actions = ctk.CTkFrame(add_comment_frame, fg_color="transparent")
        comment_actions.pack(fill="x", padx=15, pady=(0, 15))
        
        self.add_comment_btn = ctk.CTkButton(
            comment_actions,
            text="Add Comment",
            command=self._add_comment,
            width=120,
            height=30
        )
        self.add_comment_btn.pack(side="left")
        
        # Comments display
        self.comments_display = ctk.CTkScrollableFrame(
            self.comments_tab,
            width=500,
            height=300
        )
        self.comments_display.pack(fill="both", expand=True)
    
    def _create_changes_tab(self):
        """Create the changes tab."""
        self.changes_tab = self.activity_notebook.add("Changes")
        
        # Changes header
        changes_header = ctk.CTkFrame(self.changes_tab, fg_color="transparent")
        changes_header.pack(fill="x", pady=(0, 15))
        
        changes_title = ctk.CTkLabel(
            changes_header,
            text="Change History",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        changes_title.pack(anchor="w")
        
        # Changes display
        self.changes_display = ctk.CTkScrollableFrame(
            self.changes_tab,
            width=500,
            height=400
        )
        self.changes_display.pack(fill="both", expand=True)
    
    def _create_statistics_tab(self):
        """Create the statistics tab."""
        self.stats_tab = self.activity_notebook.add("Statistics")
        
        # Statistics content
        stats_content = ctk.CTkFrame(self.stats_tab)
        stats_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        stats_title = ctk.CTkLabel(
            stats_content,
            text="Collaboration Statistics",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        stats_title.pack(anchor="w", pady=(0, 20))
        
        # Statistics widgets
        self.stats_widgets = {}
        
        # Total comments
        comments_frame = ctk.CTkFrame(stats_content)
        comments_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            comments_frame,
            text="Total Comments:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=15, pady=10)
        
        self.stats_widgets["comments"] = ctk.CTkLabel(
            comments_frame,
            text="0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stats_widgets["comments"].pack(side="right", padx=15, pady=10)
        
        # Total changes
        changes_frame = ctk.CTkFrame(stats_content)
        changes_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            changes_frame,
            text="Total Changes:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=15, pady=10)
        
        self.stats_widgets["changes"] = ctk.CTkLabel(
            changes_frame,
            text="0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stats_widgets["changes"].pack(side="right", padx=15, pady=10)
        
        # Active users
        users_frame = ctk.CTkFrame(stats_content)
        users_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            users_frame,
            text="Active Users:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=15, pady=10)
        
        self.stats_widgets["users"] = ctk.CTkLabel(
            users_frame,
            text="0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stats_widgets["users"].pack(side="right", padx=15, pady=10)
        
        # Collaboration score
        score_frame = ctk.CTkFrame(stats_content)
        score_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            score_frame,
            text="Collaboration Score:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=15, pady=10)
        
        self.stats_widgets["score"] = ctk.CTkLabel(
            score_frame,
            text="0.0",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.stats_widgets["score"].pack(side="right", padx=15, pady=10)
    
    def _show_login_dialog(self):
        """Show login dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Login")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Login form
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Username
        ctk.CTkLabel(
            form_frame,
            text="Username:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(20, 5))
        
        username_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        username_entry.pack(fill="x", pady=(0, 15))
        
        # Password
        ctk.CTkLabel(
            form_frame,
            text="Password:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        password_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=35,
            font=ctk.CTkFont(size=12),
            show="*"
        )
        password_entry.pack(fill="x", pady=(0, 20))
        
        # Login button
        def login():
            username = username_entry.get()
            password = password_entry.get()
            
            if username and password:
                # Create user (simplified)
                user = self.collaboration_manager.create_user(username, f"{username}@example.com", "editor")
                self.current_user = user
                self._update_user_info()
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please enter username and password")
        
        ctk.CTkButton(
            form_frame,
            text="Login",
            command=login,
            width=100,
            height=35
        ).pack(pady=10)
    
    def _show_register_dialog(self):
        """Show registration dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Register")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # Registration form
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Username
        ctk.CTkLabel(
            form_frame,
            text="Username:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(20, 5))
        
        username_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        username_entry.pack(fill="x", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(
            form_frame,
            text="Email:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        email_entry = ctk.CTkEntry(
            form_frame,
            width=300,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        email_entry.pack(fill="x", pady=(0, 15))
        
        # Role
        ctk.CTkLabel(
            form_frame,
            text="Role:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 5))
        
        role_combo = ctk.CTkComboBox(
            form_frame,
            values=["editor", "viewer", "commenter"],
            width=300,
            height=35
        )
        role_combo.pack(fill="x", pady=(0, 20))
        
        # Register button
        def register():
            username = username_entry.get()
            email = email_entry.get()
            role = role_combo.get()
            
            if username and email and role:
                user = self.collaboration_manager.create_user(username, email, role)
                self.current_user = user
                self._update_user_info()
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please fill in all fields")
        
        ctk.CTkButton(
            form_frame,
            text="Register",
            command=register,
            width=100,
            height=35
        ).pack(pady=10)
    
    def _show_join_session_dialog(self):
        """Show join session dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Join Session")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Join form
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Session ID
        ctk.CTkLabel(
            form_frame,
            text="Session ID:",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(20, 5))
        
        session_id_entry = ctk.CTkEntry(
            form_frame,
            width=250,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        session_id_entry.pack(fill="x", pady=(0, 20))
        
        # Join button
        def join():
            session_id = session_id_entry.get()
            if session_id:
                success = self.collaboration_manager.join_collaboration_session(session_id, self.current_user.user_id)
                if success:
                    self.current_session = session_id
                    self._update_session_info()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to join session")
            else:
                messagebox.showwarning("Warning", "Please enter session ID")
        
        ctk.CTkButton(
            form_frame,
            text="Join",
            command=join,
            width=100,
            height=35
        ).pack(pady=10)
    
    def _start_session(self):
        """Start a new collaboration session."""
        if not self.current_user:
            messagebox.showwarning("Warning", "Please login first")
            return
        
        session = self.collaboration_manager.start_collaboration_session("book_1", "chapter_1", self.current_user.user_id)
        self.current_session = session.session_id
        self._update_session_info()
        messagebox.showinfo("Success", f"Session started: {session.session_id}")
    
    def _add_comment(self):
        """Add a new comment."""
        if not self.current_user:
            messagebox.showwarning("Warning", "Please login first")
            return
        
        comment_text = self.comment_entry.get("1.0", "end-1c").strip()
        if not comment_text:
            messagebox.showwarning("Warning", "Please enter a comment")
            return
        
        # Create comment
        comment = self.collaboration_manager.create_comment(
            "book_1", "chapter_1", self.current_user.user_id,
            comment_text, 0, 0
        )
        
        # Add to display
        self._display_comment(comment)
        
        # Clear input
        self.comment_entry.delete("1.0", "end")
        
        # Update statistics
        self._update_statistics()
    
    def _display_comment(self, comment: Comment):
        """Display a comment in the comments display."""
        comment_frame = ctk.CTkFrame(
            self.comments_display,
            fg_color=("#f8f9fa", "#2b2b2b"),
            corner_radius=8
        )
        comment_frame.pack(fill="x", pady=5, padx=5)
        
        # Comment content
        content_frame = ctk.CTkFrame(comment_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # User and timestamp
        user_label = ctk.CTkLabel(
            content_frame,
            text=f"{comment.user_id} • {comment.created_at.strftime('%H:%M')}",
            font=ctk.CTkFont(size=11),
            text_color=("#666666", "#cccccc")
        )
        user_label.pack(anchor="w", pady=(0, 5))
        
        # Comment text
        comment_label = ctk.CTkLabel(
            content_frame,
            text=comment.content,
            font=ctk.CTkFont(size=12),
            anchor="w",
            wraplength=450
        )
        comment_label.pack(fill="x")
    
    def _update_user_info(self):
        """Update user information display."""
        if self.current_user:
            self.user_info_label.configure(
                text=f"Logged in as: {self.current_user.username} ({self.current_user.role})"
            )
        else:
            self.user_info_label.configure(text="Not logged in")
    
    def _update_session_info(self):
        """Update session information display."""
        if self.current_session:
            self.session_info_label.configure(
                text=f"Active session: {self.current_session}"
            )
        else:
            self.session_info_label.configure(text="No active session")
    
    def _update_statistics(self):
        """Update collaboration statistics."""
        if self.current_session:
            stats = self.collaboration_manager.get_collaboration_statistics("book_1")
            
            self.stats_widgets["comments"].configure(text=str(stats["total_comments"]))
            self.stats_widgets["changes"].configure(text=str(stats["total_changes"]))
            self.stats_widgets["users"].configure(text=str(stats["active_sessions"]))
            self.stats_widgets["score"].configure(text=f"{stats['collaboration_score']:.1f}")