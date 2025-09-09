"""
Modern Main GUI Application

The main entry point for the modern Mac-style GUI application
that integrates all system modules and panels.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.panels.document_processor_panel import DocumentProcessorPanel
from gui.panels.research_panel import ResearchPanel
from gui.panels.collaboration_panel import CollaborationPanel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode("light")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class ModernBookWriterApp:
    """
    Modern Mac-style book writing application with integrated panels.
    
    Features:
    - Professional interface design
    - Modular panel architecture
    - Real-time collaboration
    - Advanced document processing
    - Research integration
    - Export capabilities
    """
    
    def __init__(self):
        """Initialize the modern book writer application."""
        self.root = ctk.CTk()
        self.root.title("BookWriter Pro")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        
        # Configure window
        self.root.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        
        # Create UI components
        self._create_ui()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        logger.info("Modern BookWriter App initialized")
    
    def _create_ui(self):
        """Create the main UI components."""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create top toolbar
        self._create_toolbar()
        
        # Create main content area
        self._create_main_content()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_toolbar(self):
        """Create the top toolbar."""
        self.toolbar = ctk.CTkFrame(
            self.main_container, 
            height=70, 
            fg_color=("#ffffff", "#2b2b2b"),
            corner_radius=12
        )
        self.toolbar.pack(fill="x", pady=(0, 15))
        self.toolbar.pack_propagate(False)
        
        # Left side - App title and main actions
        left_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=20, pady=15)
        
        # App title with icon
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(0, 30))
        
        # App icon (placeholder)
        icon_label = ctk.CTkLabel(
            title_frame,
            text="📚",
            font=ctk.CTkFont(size=28)
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        self.title_label = ctk.CTkLabel(
            title_frame,
            text="BookWriter Pro",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        self.title_label.pack(side="left")
        
        # Main action buttons
        actions_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        actions_frame.pack(side="left")
        
        self.new_book_btn = ctk.CTkButton(
            actions_frame,
            text="New Book",
            command=self._new_book,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#007bff",
            hover_color="#0056b3"
        )
        self.new_book_btn.pack(side="left", padx=(0, 10))
        
        self.open_book_btn = ctk.CTkButton(
            actions_frame,
            text="Open Book",
            command=self._open_book,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.open_book_btn.pack(side="left", padx=(0, 10))
        
        self.save_book_btn = ctk.CTkButton(
            actions_frame,
            text="Save",
            command=self._save_book,
            width=100,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.save_book_btn.pack(side="left", padx=(0, 20))
        
        # Right side - User actions and settings
        right_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=15)
        
        # Panel buttons
        panel_buttons = [
            ("Document Processing", self._show_document_processor),
            ("Research Assistant", self._show_research_panel),
            ("Collaboration", self._show_collaboration_panel),
            ("Settings", self._show_settings)
        ]
        
        for text, command in panel_buttons:
            btn = ctk.CTkButton(
                right_frame,
                text=text,
                command=command,
                width=140,
                height=40,
                font=ctk.CTkFont(size=13)
            )
            btn.pack(side="right", padx=(10, 0))
    
    def _create_main_content(self):
        """Create the main content area."""
        # Create main content container
        self.content_container = ctk.CTkFrame(
            self.main_container,
            fg_color=("#ffffff", "#2b2b2b"),
            corner_radius=12
        )
        self.content_container.pack(fill="both", expand=True)
        
        # Create sidebar and main workspace
        self._create_sidebar()
        self._create_workspace()
    
    def _create_sidebar(self):
        """Create the left sidebar."""
        self.sidebar = ctk.CTkFrame(
            self.content_container,
            width=280,
            fg_color=("#f8f9fa", "#1e1e1e"),
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 1))
        self.sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_header.pack(fill="x", padx=20, pady=20)
        
        self.sidebar_title = ctk.CTkLabel(
            sidebar_header,
            text="Project",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        self.sidebar_title.pack(anchor="w")
        
        # Project info
        self.project_info = ctk.CTkLabel(
            sidebar_header,
            text="No project loaded",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#cccccc")
        )
        self.project_info.pack(anchor="w", pady=(5, 0))
        
        # Navigation buttons
        self._create_navigation()
        
        # Quick actions
        self._create_quick_actions()
        
        # Recent files
        self._create_recent_files()
    
    def _create_navigation(self):
        """Create navigation buttons."""
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=25)
        
        # Navigation buttons
        nav_buttons = [
            ("📝 Editor", self._show_editor, "#007bff"),
            ("📚 Chapters", self._show_chapters, "#28a745"),
            ("🔍 Research", self._show_research, "#ffc107"),
            ("📊 Analytics", self._show_analytics, "#17a2b8"),
            ("⚙️ Settings", self._show_settings, "#6c757d")
        ]
        
        self.nav_buttons = {}
        for text, command, color in nav_buttons:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                width=240,
                height=45,
                font=ctk.CTkFont(size=14),
                anchor="w",
                fg_color=("transparent", "transparent"),
                hover_color=("#e9ecef", "#3a3a3a"),
                text_color=(color, color)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[text] = btn
    
    def _create_quick_actions(self):
        """Create quick actions section."""
        actions_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=20)
        
        # Section title
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        actions_title.pack(anchor="w", pady=(0, 15))
        
        # Quick action buttons
        quick_actions = [
            ("Import Document", self._import_document),
            ("Process with OCR", self._process_with_ocr),
            ("Extract Tables", self._extract_tables),
            ("Search Research", self._search_research)
        ]
        
        for text, command in quick_actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                command=command,
                width=240,
                height=35,
                font=ctk.CTkFont(size=12),
                fg_color=("transparent", "transparent"),
                hover_color=("#e9ecef", "#3a3a3a")
            )
            btn.pack(fill="x", pady=2)
    
    def _create_recent_files(self):
        """Create recent files section."""
        recent_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        recent_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Section title
        recent_title = ctk.CTkLabel(
            recent_frame,
            text="Recent Files",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        recent_title.pack(anchor="w", pady=(0, 15))
        
        # Recent files list
        self.recent_files_listbox = tk.Listbox(
            recent_frame,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#1a1a1a",
            selectbackground="#007bff",
            selectforeground="#ffffff"
        )
        self.recent_files_listbox.pack(fill="both", expand=True)
        
        # Add some sample recent files
        sample_files = [
            "My Book Project.bwp",
            "Research Notes.txt",
            "Chapter 1 Draft.md",
            "Bibliography.docx"
        ]
        
        for file in sample_files:
            self.recent_files_listbox.insert(tk.END, file)
    
    def _create_workspace(self):
        """Create the main workspace area."""
        self.workspace = ctk.CTkFrame(
            self.content_container,
            fg_color=("transparent", "transparent")
        )
        self.workspace.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # Create tabbed interface
        self._create_tabbed_interface()
    
    def _create_tabbed_interface(self):
        """Create tabbed interface for different views."""
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(
            self.workspace,
            width=1000,
            height=700,
            fg_color=("#ffffff", "#2b2b2b"),
            corner_radius=8
        )
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create tabs
        self._create_editor_tab()
        self._create_chapters_tab()
        self._create_research_tab()
        self._create_analytics_tab()
        self._create_document_processor_tab()
        self._create_collaboration_tab()
    
    def _create_editor_tab(self):
        """Create the main editor tab."""
        self.editor_tab = self.notebook.add("Editor")
        
        # Editor toolbar
        editor_toolbar = ctk.CTkFrame(self.editor_tab, fg_color="transparent")
        editor_toolbar.pack(fill="x", padx=15, pady=(15, 10))
        
        # Formatting buttons
        format_buttons = [
            ("Bold", self._format_bold, "#007bff"),
            ("Italic", self._format_italic, "#28a745"),
            ("Heading", self._format_heading, "#ffc107"),
            ("List", self._format_list, "#17a2b8")
        ]
        
        for text, command, color in format_buttons:
            btn = ctk.CTkButton(
                editor_toolbar,
                text=text,
                command=command,
                width=80,
                height=35,
                font=ctk.CTkFont(size=12),
                fg_color=color,
                hover_color=self._darken_color(color)
            )
            btn.pack(side="left", padx=(0, 8))
        
        # Main text editor
        self.text_editor = ctk.CTkTextbox(
            self.editor_tab,
            width=1000,
            height=600,
            font=ctk.CTkFont(size=14),
            fg_color=("#ffffff", "#1e1e1e"),
            text_color=("#1a1a1a", "#ffffff"),
            corner_radius=8
        )
        self.text_editor.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def _create_chapters_tab(self):
        """Create the chapters management tab."""
        self.chapters_tab = self.notebook.add("Chapters")
        
        # Chapters header
        chapters_header = ctk.CTkFrame(self.chapters_tab, fg_color="transparent")
        chapters_header.pack(fill="x", padx=15, pady=15)
        
        chapters_title = ctk.CTkLabel(
            chapters_header,
            text="Chapter Management",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        chapters_title.pack(anchor="w")
        
        # Chapters list
        chapters_frame = ctk.CTkFrame(self.chapters_tab)
        chapters_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Chapters listbox
        self.chapters_listbox = tk.Listbox(
            chapters_frame,
            font=("Arial", 12),
            bg="#ffffff",
            fg="#1a1a1a",
            selectbackground="#007bff",
            selectforeground="#ffffff"
        )
        self.chapters_listbox.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Chapter actions
        chapter_actions = ctk.CTkFrame(self.chapters_tab, fg_color="transparent")
        chapter_actions.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            chapter_actions,
            text="Add Chapter",
            command=self._add_chapter,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            chapter_actions,
            text="Delete Chapter",
            command=self._delete_chapter,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="left", padx=(0, 10))
    
    def _create_research_tab(self):
        """Create the research assistant tab."""
        self.research_tab = self.notebook.add("Research")
        
        # Initialize research panel
        self.research_panel = ResearchPanel(self.research_tab)
        self.research_panel.pack(fill="both", expand=True)
    
    def _create_analytics_tab(self):
        """Create the analytics tab."""
        self.analytics_tab = self.notebook.add("Analytics")
        
        # Analytics content
        analytics_frame = ctk.CTkFrame(self.analytics_tab)
        analytics_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Analytics widgets
        ctk.CTkLabel(
            analytics_frame,
            text="Writing Analytics",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=30)
        
        # Word count
        self.word_count_label = ctk.CTkLabel(
            analytics_frame,
            text="Word Count: 0",
            font=ctk.CTkFont(size=18)
        )
        self.word_count_label.pack(pady=15)
        
        # Progress tracking
        self.progress_label = ctk.CTkLabel(
            analytics_frame,
            text="Progress: 0%",
            font=ctk.CTkFont(size=18)
        )
        self.progress_label.pack(pady=15)
    
    def _create_document_processor_tab(self):
        """Create the document processor tab."""
        self.document_processor_tab = self.notebook.add("Document Processing")
        
        # Initialize document processor panel
        self.document_processor_panel = DocumentProcessorPanel(self.document_processor_tab)
        self.document_processor_panel.pack(fill="both", expand=True)
    
    def _create_collaboration_tab(self):
        """Create the collaboration tab."""
        self.collaboration_tab = self.notebook.add("Collaboration")
        
        # Initialize collaboration panel
        self.collaboration_panel = CollaborationPanel(self.collaboration_tab)
        self.collaboration_panel.pack(fill="both", expand=True)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ctk.CTkFrame(
            self.main_container,
            height=35,
            fg_color=("#f8f9fa", "#1e1e1e"),
            corner_radius=8
        )
        self.status_bar.pack(fill="x", pady=(15, 0))
        self.status_bar.pack_propagate(False)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#cccccc")
        )
        self.status_label.pack(side="left", padx=20, pady=8)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.status_bar,
            width=200,
            height=20
        )
        self.progress_bar.pack(side="right", padx=20, pady=8)
        self.progress_bar.set(0)
    
    def _setup_event_handlers(self):
        """Setup event handlers."""
        # Text editor events
        self.text_editor.bind("<KeyRelease>", self._on_text_change)
        
        # Window events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _darken_color(self, color):
        """Darken a color for hover effects."""
        # Simple color darkening (in a real app, you'd use proper color manipulation)
        color_map = {
            "#007bff": "#0056b3",
            "#28a745": "#1e7e34",
            "#ffc107": "#e0a800",
            "#17a2b8": "#138496"
        }
        return color_map.get(color, color)
    
    # Event handlers
    def _on_text_change(self, event):
        """Handle text change in editor."""
        # Update word count
        text = self.text_editor.get("1.0", "end-1c")
        word_count = len(text.split())
        self.word_count_label.configure(text=f"Word Count: {word_count}")
    
    def _on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    # Action methods
    def _new_book(self):
        """Create a new book project."""
        self.text_editor.delete("1.0", "end")
        self.project_info.configure(text="New Book Project")
        self.status_label.configure(text="New book created")
    
    def _open_book(self):
        """Open an existing book project."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Open Book Project",
            filetypes=[("BookWriter Files", "*.bwp"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", content)
                self.project_info.configure(text=f"Project: {Path(file_path).name}")
                self.status_label.configure(text="Book opened successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open book: {e}")
    
    def _save_book(self):
        """Save the current book project."""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Save Book Project",
            defaultextension=".bwp",
            filetypes=[("BookWriter Files", "*.bwp"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                content = self.text_editor.get("1.0", "end-1c")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.configure(text="Book saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save book: {e}")
    
    def _import_document(self):
        """Import a document for processing."""
        self.notebook.set("Document Processing")
    
    def _process_with_ocr(self):
        """Process document with OCR."""
        self.notebook.set("Document Processing")
    
    def _extract_tables(self):
        """Extract tables from document."""
        self.notebook.set("Document Processing")
    
    def _search_research(self):
        """Search research."""
        self.notebook.set("Research")
    
    # Navigation methods
    def _show_editor(self):
        """Show the editor tab."""
        self.notebook.set("Editor")
    
    def _show_chapters(self):
        """Show the chapters tab."""
        self.notebook.set("Chapters")
    
    def _show_research(self):
        """Show the research tab."""
        self.notebook.set("Research")
    
    def _show_analytics(self):
        """Show the analytics tab."""
        self.notebook.set("Analytics")
    
    def _show_document_processor(self):
        """Show the document processor tab."""
        self.notebook.set("Document Processing")
    
    def _show_collaboration_panel(self):
        """Show the collaboration tab."""
        self.notebook.set("Collaboration")
    
    def _show_settings(self):
        """Show the settings tab."""
        messagebox.showinfo("Settings", "Settings panel coming soon!")
    
    # Formatting methods
    def _format_bold(self):
        """Format selected text as bold."""
        # Implementation for bold formatting
        pass
    
    def _format_italic(self):
        """Format selected text as italic."""
        # Implementation for italic formatting
        pass
    
    def _format_heading(self):
        """Format selected text as heading."""
        # Implementation for heading formatting
        pass
    
    def _format_list(self):
        """Format selected text as list."""
        # Implementation for list formatting
        pass
    
    # Chapter management methods
    def _add_chapter(self):
        """Add a new chapter."""
        from tkinter import simpledialog
        chapter_name = simpledialog.askstring("Add Chapter", "Enter chapter name:")
        if chapter_name:
            self.chapters_listbox.insert(tk.END, chapter_name)
            self.status_label.configure(text=f"Added chapter: {chapter_name}")
    
    def _delete_chapter(self):
        """Delete selected chapter."""
        selection = self.chapters_listbox.curselection()
        if selection:
            chapter_name = self.chapters_listbox.get(selection[0])
            self.chapters_listbox.delete(selection[0])
            self.status_label.configure(text=f"Deleted chapter: {chapter_name}")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point for the modern GUI application."""
    try:
        app = ModernBookWriterApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Application Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()