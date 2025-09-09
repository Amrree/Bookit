"""
Retro Writer - Professional Mac Book Writing Application
A complete reimagining of the book writing system with retro writer aesthetics.

Theme: Vintage Typewriter / Retro Writer
Framework: PyQt6 with native Mac integration
Design: Professional Mac app with retro styling
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QTextEdit, QListWidget, QTreeWidget,
    QTreeWidgetItem, QPushButton, QLabel, QLineEdit, QTextBrowser,
    QProgressBar, QStatusBar, QMenuBar, QMenu, QFileDialog, 
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QSpinBox, QComboBox, QCheckBox, QGroupBox, QScrollArea,
    QFrame, QGridLayout, QSizePolicy, QStackedWidget, QListWidgetItem,
    QSlider, QDial, QLCDNumber, QCalendarWidget, QDateEdit,
    QTimeEdit, QDateTimeEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QTreeView, QListView,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPixmapItem
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QDate, QTime, QDateTime,
    QAbstractItemModel, QModelIndex, QVariant, QObject
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QAction, QPainter,
    QPen, QBrush, QLinearGradient, QRadialGradient, QConicalGradient,
    QFontMetrics, QTextCharFormat, QTextCursor, QTextDocument,
    QSyntaxHighlighter, QTextBlockFormat, QTextListFormat,
    QMovie, QImage, QTransform, QPolygon, QPolygonF
)

# Import our system modules
from memory_manager import MemoryManager
from llm_client import LLMClient
from tool_manager import ToolManager
from agent_manager import AgentManager
from document_ingestor import DocumentIngestor
from book_workflow import BookWorkflow, BookMetadata
from research_agent import ResearchAgent
from writer_agent import WriterAgent
from editor_agent import EditorAgent
from tool_agent import ToolAgent
from book_builder import BookBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RetroWriterTheme:
    """Retro writer theme configuration."""
    
    # Color palette inspired by vintage typewriters and sepia tones
    COLORS = {
        'background': QColor(250, 248, 240),      # Cream/off-white
        'paper': QColor(255, 253, 245),           # Slightly yellowed paper
        'text': QColor(45, 45, 45),               # Dark charcoal
        'accent': QColor(139, 69, 19),            # Saddle brown
        'secondary': QColor(160, 82, 45),         # Sienna
        'highlight': QColor(222, 184, 135),       # Burlywood
        'border': QColor(210, 180, 140),          # Tan
        'shadow': QColor(200, 200, 200),          # Light gray
        'success': QColor(34, 139, 34),           # Forest green
        'warning': QColor(255, 165, 0),           # Orange
        'error': QColor(220, 20, 60),             # Crimson
        'selection': QColor(255, 248, 220),       # Light cream
        'button': QColor(245, 245, 220),          # Beige
        'button_hover': QColor(255, 239, 213),    # Papaya whip
        'button_pressed': QColor(238, 203, 173),  # Peach puff
    }
    
    # Typography inspired by typewriter fonts
    FONTS = {
        'heading': QFont('Courier New', 16, QFont.Weight.Bold),
        'subheading': QFont('Courier New', 14, QFont.Weight.Bold),
        'body': QFont('Courier New', 12),
        'monospace': QFont('Courier New', 11),
        'small': QFont('Courier New', 10),
        'large': QFont('Courier New', 18),
    }
    
    # Styling constants
    BORDER_RADIUS = 8
    BORDER_WIDTH = 2
    SHADOW_OFFSET = 3
    ANIMATION_DURATION = 200


class RetroWriterApp(QApplication):
    """Main application class with retro writer theme."""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Retro Writer")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Book Writing Systems")
        
        # Apply retro writer theme
        self.apply_theme()
        
        # Initialize system components
        self.system_components = {}
        self.initialize_system()
    
    def apply_theme(self):
        """Apply retro writer theme to the application."""
        palette = QPalette()
        theme = RetroWriterTheme()
        
        # Set color palette
        palette.setColor(QPalette.ColorRole.Window, theme.COLORS['background'])
        palette.setColor(QPalette.ColorRole.WindowText, theme.COLORS['text'])
        palette.setColor(QPalette.ColorRole.Base, theme.COLORS['paper'])
        palette.setColor(QPalette.ColorRole.AlternateBase, theme.COLORS['selection'])
        palette.setColor(QPalette.ColorRole.ToolTipBase, theme.COLORS['paper'])
        palette.setColor(QPalette.ColorRole.ToolTipText, theme.COLORS['text'])
        palette.setColor(QPalette.ColorRole.Text, theme.COLORS['text'])
        palette.setColor(QPalette.ColorRole.Button, theme.COLORS['button'])
        palette.setColor(QPalette.ColorRole.ButtonText, theme.COLORS['text'])
        palette.setColor(QPalette.ColorRole.BrightText, theme.COLORS['error'])
        palette.setColor(QPalette.ColorRole.Link, theme.COLORS['accent'])
        palette.setColor(QPalette.ColorRole.Highlight, theme.COLORS['highlight'])
        palette.setColor(QPalette.ColorRole.HighlightedText, theme.COLORS['text'])
        
        self.setPalette(palette)
        
        # Set application font
        self.setFont(theme.FONTS['body'])
    
    def initialize_system(self):
        """Initialize all system components."""
        try:
            # Initialize core components
            self.system_components['memory_manager'] = MemoryManager()
            self.system_components['llm_client'] = LLMClient()
            self.system_components['tool_manager'] = ToolManager()
            self.system_components['agent_manager'] = AgentManager()
            self.system_components['document_ingestor'] = DocumentIngestor()
            
            # Initialize agents
            self.system_components['research_agent'] = ResearchAgent(
                memory_manager=self.system_components['memory_manager'],
                llm_client=self.system_components['llm_client'],
                tool_manager=self.system_components['tool_manager']
            )
            
            self.system_components['writer_agent'] = WriterAgent(
                memory_manager=self.system_components['memory_manager'],
                llm_client=self.system_components['llm_client']
            )
            
            self.system_components['editor_agent'] = EditorAgent(
                memory_manager=self.system_components['memory_manager'],
                llm_client=self.system_components['llm_client']
            )
            
            self.system_components['tool_agent'] = ToolAgent(
                tool_manager=self.system_components['tool_manager']
            )
            
            # Initialize book workflow
            self.system_components['book_workflow'] = BookWorkflow(
                memory_manager=self.system_components['memory_manager'],
                llm_client=self.system_components['llm_client'],
                tool_manager=self.system_components['tool_manager'],
                research_agent=self.system_components['research_agent'],
                writer_agent=self.system_components['writer_agent'],
                editor_agent=self.system_components['editor_agent'],
                tool_agent=self.system_components['tool_agent']
            )
            
            logger.info("System components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize system components: {e}")
            QMessageBox.critical(None, "Initialization Error", 
                               f"Failed to initialize system components:\n{e}")


class RetroWriterMainWindow(QMainWindow):
    """Main window with retro writer design and complete functionality."""
    
    def __init__(self, app: RetroWriterApp):
        super().__init__()
        self.app = app
        self.current_book = None
        self.workflow_running = False
        
        # Initialize UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Apply retro styling
        self.apply_retro_styling()
        
        # Set window properties
        self.setWindowTitle("Retro Writer - Professional Book Writing Studio")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Center window
        self.center_window()
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left sidebar (Navigation & Tools)
        self.setup_left_sidebar(main_splitter)
        
        # Center area (Main content)
        self.setup_center_area(main_splitter)
        
        # Right sidebar (Status & Info)
        self.setup_right_sidebar(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([300, 1000, 300])
    
    def setup_left_sidebar(self, parent):
        """Setup left sidebar with navigation and tools."""
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #faf8f0;
                border: 2px solid #d2b48c;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("📚 Retro Writer Studio")
        title.setFont(RetroWriterTheme.FONTS['heading'])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #8b4513; font-weight: bold;")
        layout.addWidget(title)
        
        # Navigation tabs
        self.nav_tabs = QTabWidget()
        self.nav_tabs.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(self.nav_tabs)
        
        # Workspace tab
        self.setup_workspace_tab()
        
        # Research tab
        self.setup_research_tab()
        
        # Writing tab
        self.setup_writing_tab()
        
        # Tools tab
        self.setup_tools_tab()
        
        # Settings tab
        self.setup_settings_tab()
        
        parent.addWidget(sidebar)
    
    def setup_center_area(self, parent):
        """Setup center area with main content."""
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(10)
        center_layout.setContentsMargins(15, 15, 15, 15)
        
        # Main content stack
        self.content_stack = QStackedWidget()
        center_layout.addWidget(self.content_stack)
        
        # Setup different content pages
        self.setup_dashboard_page()
        self.setup_book_editor_page()
        self.setup_research_page()
        self.setup_writing_page()
        self.setup_tools_page()
        self.setup_settings_page()
        
        parent.addWidget(center_widget)
    
    def setup_right_sidebar(self, parent):
        """Setup right sidebar with status and information."""
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #faf8f0;
                border: 2px solid #d2b48c;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("📊 Status & Info")
        title.setFont(RetroWriterTheme.FONTS['subheading'])
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #8b4513; font-weight: bold;")
        layout.addWidget(title)
        
        # Status information
        self.setup_status_info(layout)
        
        # Progress tracking
        self.setup_progress_tracking(layout)
        
        # Recent activity
        self.setup_recent_activity(layout)
        
        parent.addWidget(sidebar)
    
    def setup_menu_bar(self):
        """Setup menu bar with retro styling."""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f5f5dc;
                border-bottom: 2px solid #d2b48c;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px;
            }
            QMenuBar::item:selected {
                background-color: #ffe4b5;
            }
            QMenuBar::item:pressed {
                background-color: #eecda3;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        file_menu.addAction("New Book", self.new_book)
        file_menu.addAction("Open Book", self.open_book)
        file_menu.addAction("Save Book", self.save_book)
        file_menu.addSeparator()
        file_menu.addAction("Import Documents", self.import_documents)
        file_menu.addAction("Export Book", self.export_book)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("✏️ Edit")
        edit_menu.addAction("Undo", self.undo_action)
        edit_menu.addAction("Redo", self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction("Find & Replace", self.find_replace)
        edit_menu.addAction("Preferences", self.show_preferences)
        
        # Research menu
        research_menu = menubar.addMenu("🔍 Research")
        research_menu.addAction("Start Research", self.start_research)
        research_menu.addAction("View Sources", self.view_sources)
        research_menu.addAction("Manage Memory", self.manage_memory)
        
        # Writing menu
        writing_menu = menubar.addMenu("✍️ Writing")
        writing_menu.addAction("Generate Chapter", self.generate_chapter)
        writing_menu.addAction("Edit Chapter", self.edit_chapter)
        writing_menu.addAction("Review Style", self.review_style)
        
        # Tools menu
        tools_menu = menubar.addMenu("🛠️ Tools")
        tools_menu.addAction("Agent Status", self.show_agent_status)
        tools_menu.addAction("System Monitor", self.show_system_monitor)
        tools_menu.addAction("Test Tools", self.test_tools)
        
        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        help_menu.addAction("User Guide", self.show_user_guide)
        help_menu.addAction("About", self.show_about)
    
    def setup_status_bar(self):
        """Setup status bar with retro styling."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f5f5dc;
                border-top: 2px solid #d2b48c;
                padding: 5px;
            }
        """)
        
        # Status labels
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8b4513; font-weight: bold;")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #d2b48c;
                border-radius: 5px;
                text-align: center;
                background-color: #faf8f0;
            }
            QProgressBar::chunk {
                background-color: #8b4513;
                border-radius: 3px;
            }
        """)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Word count
        self.word_count_label = QLabel("Words: 0")
        self.word_count_label.setStyleSheet("color: #8b4513;")
        self.status_bar.addPermanentWidget(self.word_count_label)
    
    def apply_retro_styling(self):
        """Apply retro styling to all components."""
        # Set window styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #faf8f0;
            }
            QWidget {
                font-family: 'Courier New';
                color: #2d2d2d;
            }
            QPushButton {
                background-color: #f5f5dc;
                border: 2px solid #d2b48c;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
                color: #8b4513;
            }
            QPushButton:hover {
                background-color: #ffe4b5;
                border-color: #8b4513;
            }
            QPushButton:pressed {
                background-color: #eecda3;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #999999;
                border-color: #cccccc;
            }
            QTextEdit, QTextBrowser {
                background-color: #fffdf5;
                border: 2px solid #d2b48c;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 12px;
                line-height: 1.4;
            }
            QLineEdit {
                background-color: #fffdf5;
                border: 2px solid #d2b48c;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Courier New';
            }
            QLineEdit:focus {
                border-color: #8b4513;
            }
            QListWidget, QTreeWidget {
                background-color: #fffdf5;
                border: 2px solid #d2b48c;
                border-radius: 6px;
                padding: 5px;
                font-family: 'Courier New';
            }
            QListWidget::item, QTreeWidget::item {
                padding: 5px;
                border-radius: 3px;
                margin: 1px;
            }
            QListWidget::item:selected, QTreeWidget::item:selected {
                background-color: #ffe4b5;
                color: #8b4513;
            }
            QTabWidget::pane {
                border: 2px solid #d2b48c;
                border-radius: 6px;
                background-color: #faf8f0;
            }
            QTabBar::tab {
                background-color: #f5f5dc;
                border: 2px solid #d2b48c;
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 8px 15px;
                margin-right: 2px;
                color: #8b4513;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #ffe4b5;
                border-color: #8b4513;
            }
            QTabBar::tab:hover {
                background-color: #ffe4b5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d2b48c;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: #8b4513;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QScrollBar:vertical {
                background-color: #f5f5dc;
                width: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #d2b48c;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #8b4513;
            }
        """)
    
    def center_window(self):
        """Center the window on screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def setup_connections(self):
        """Setup signal connections."""
        # Navigation tab connections
        self.nav_tabs.currentChanged.connect(self.on_nav_tab_changed)
    
    # Import workspace and content components
    from retro_writer_workspace import WorkspaceTab, ResearchTab, WritingTab, ToolsTab, SettingsTab
    from retro_writer_content import DashboardPage, BookEditorPage, ResearchPage, WritingPage, ToolsPage, SettingsPage
    
    def setup_workspace_tab(self):
        """Setup workspace navigation tab."""
        workspace_tab = WorkspaceTab(self)
        self.nav_tabs.addTab(workspace_tab, "📚 Workspace")
    
    def setup_research_tab(self):
        """Setup research navigation tab."""
        research_tab = ResearchTab(self)
        self.nav_tabs.addTab(research_tab, "🔍 Research")
    
    def setup_writing_tab(self):
        """Setup writing navigation tab."""
        writing_tab = WritingTab(self)
        self.nav_tabs.addTab(writing_tab, "✍️ Writing")
    
    def setup_tools_tab(self):
        """Setup tools navigation tab."""
        tools_tab = ToolsTab(self)
        self.nav_tabs.addTab(tools_tab, "🛠️ Tools")
    
    def setup_settings_tab(self):
        """Setup settings navigation tab."""
        settings_tab = SettingsTab(self)
        self.nav_tabs.addTab(settings_tab, "⚙️ Settings")
    
    def setup_dashboard_page(self):
        """Setup dashboard content page."""
        dashboard_page = DashboardPage(self)
        self.content_stack.addWidget(dashboard_page)
    
    def setup_book_editor_page(self):
        """Setup book editor content page."""
        book_editor_page = BookEditorPage(self)
        self.content_stack.addWidget(book_editor_page)
    
    def setup_research_page(self):
        """Setup research content page."""
        research_page = ResearchPage(self)
        self.content_stack.addWidget(research_page)
    
    def setup_writing_page(self):
        """Setup writing content page."""
        writing_page = WritingPage(self)
        self.content_stack.addWidget(writing_page)
    
    def setup_tools_page(self):
        """Setup tools content page."""
        tools_page = ToolsPage(self)
        self.content_stack.addWidget(tools_page)
    
    def setup_settings_page(self):
        """Setup settings content page."""
        settings_page = SettingsPage(self)
        self.content_stack.addWidget(settings_page)
    
    def setup_status_info(self, layout):
        """Setup status information panel."""
        status_group = QGroupBox("📊 System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.memory_status_label = QLabel("Memory: Ready")
        self.llm_status_label = QLabel("LLM: Ready")
        self.agents_status_label = QLabel("Agents: Ready")
        
        status_layout.addWidget(self.memory_status_label)
        status_layout.addWidget(self.llm_status_label)
        status_layout.addWidget(self.agents_status_label)
        
        layout.addWidget(status_group)
    
    def setup_progress_tracking(self, layout):
        """Setup progress tracking panel."""
        progress_group = QGroupBox("📈 Progress Tracking")
        progress_layout = QVBoxLayout(progress_group)
        
        self.book_progress_bar = QProgressBar()
        self.book_progress_bar.setVisible(False)
        progress_layout.addWidget(QLabel("Book Progress:"))
        progress_layout.addWidget(self.book_progress_bar)
        
        self.chapter_progress_bar = QProgressBar()
        self.chapter_progress_bar.setVisible(False)
        progress_layout.addWidget(QLabel("Chapter Progress:"))
        progress_layout.addWidget(self.chapter_progress_bar)
        
        self.research_progress_bar = QProgressBar()
        self.research_progress_bar.setVisible(False)
        progress_layout.addWidget(QLabel("Research Progress:"))
        progress_layout.addWidget(self.research_progress_bar)
        
        layout.addWidget(progress_group)
    
    def setup_recent_activity(self, layout):
        """Setup recent activity panel."""
        activity_group = QGroupBox("📝 Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        self.activity_list.setMaximumHeight(200)
        activity_layout.addWidget(self.activity_list)
        
        # Add some sample activities
        self.activity_list.addItem("📝 Generated Chapter 1")
        self.activity_list.addItem("🔍 Completed research on AI")
        self.activity_list.addItem("📄 Imported 3 documents")
        self.activity_list.addItem("✏️ Edited Chapter 2")
        
        layout.addWidget(activity_group)
    
    # Event handlers
    def on_nav_tab_changed(self, index):
        """Handle navigation tab change."""
        self.content_stack.setCurrentIndex(index)
    
    # Menu action handlers
    def new_book(self):
        """Create a new book."""
        title, ok = QInputDialog.getText(self, "New Book", "Enter book title:")
        if ok and title:
            theme, ok = QInputDialog.getText(self, "New Book", "Enter book theme/topic:")
            if ok and theme:
                author, ok = QInputDialog.getText(self, "New Book", "Enter author name:", text="AI Book Writer")
                if ok:
                    # Create new book metadata
                    self.current_book = BookMetadata(title, theme, author)
                    
                    # Update UI
                    self.status_label.setText(f"Created new book: {title}")
                    self.update_book_info()
                    
                    # Add to recent projects
                    if hasattr(self, 'activity_list'):
                        self.activity_list.insertItem(0, f"📝 Created book: {title}")
    
    def open_book(self):
        """Open an existing book."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Book", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    book_data = json.load(f)
                
                # Load book metadata
                self.current_book = BookMetadata(
                    book_data.get('title', 'Untitled'),
                    book_data.get('theme', ''),
                    book_data.get('author', 'AI Book Writer')
                )
                
                # Update UI
                self.status_label.setText(f"Opened book: {self.current_book.title}")
                self.update_book_info()
                
                # Add to recent projects
                if hasattr(self, 'activity_list'):
                    self.activity_list.insertItem(0, f"📂 Opened book: {self.current_book.title}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open book: {e}")
    
    def save_book(self):
        """Save the current book."""
        if not self.current_book:
            QMessageBox.warning(self, "No Book", "No book is currently open.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Book", f"{self.current_book.title}.json", 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                book_data = {
                    'title': self.current_book.title,
                    'theme': self.current_book.theme,
                    'author': self.current_book.author,
                    'created_at': datetime.now().isoformat(),
                    'chapters': []  # Would include actual chapter data
                }
                
                with open(file_path, 'w') as f:
                    json.dump(book_data, f, indent=2)
                
                self.status_label.setText(f"Saved book: {self.current_book.title}")
                
                # Add to recent projects
                if hasattr(self, 'activity_list'):
                    self.activity_list.insertItem(0, f"💾 Saved book: {self.current_book.title}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save book: {e}")
    
    def import_documents(self):
        """Import documents for research."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Import Documents", "", 
            "All Supported (*.pdf *.txt *.md *.docx *.epub);;PDF Files (*.pdf);;Text Files (*.txt);;Markdown Files (*.md);;Word Documents (*.docx);;EPUB Files (*.epub);;All Files (*)"
        )
        
        if file_paths:
            self.status_label.setText(f"Importing {len(file_paths)} documents...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(file_paths))
            
            try:
                document_ingestor = self.app.system_components['document_ingestor']
                memory_manager = self.app.system_components['memory_manager']
                
                for i, file_path in enumerate(file_paths):
                    # Ingest document
                    result = document_ingestor.ingest_document(file_path)
                    
                    # Store in memory
                    memory_manager.store_document_chunks(result.metadata, result.chunks)
                    
                    # Update progress
                    self.progress_bar.setValue(i + 1)
                    QApplication.processEvents()
                
                self.progress_bar.setVisible(False)
                self.status_label.setText(f"Imported {len(file_paths)} documents successfully")
                
                # Add to recent projects
                if hasattr(self, 'activity_list'):
                    self.activity_list.insertItem(0, f"📄 Imported {len(file_paths)} documents")
                    
            except Exception as e:
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Import Error", f"Failed to import documents: {e}")
    
    def export_book(self):
        """Export the book in various formats."""
        if not self.current_book:
            QMessageBox.warning(self, "No Book", "No book is currently open.")
            return
        
        # Show export options dialog
        dialog = ExportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            format_type = dialog.get_selected_format()
            self.export_book_format(format_type)
    
    def export_book_format(self, format_type):
        """Export book in specific format."""
        if not self.current_book:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export Book as {format_type.upper()}", 
            f"{self.current_book.title}.{format_type}", 
            f"{format_type.upper()} Files (*.{format_type});;All Files (*)"
        )
        
        if file_path:
            try:
                self.status_label.setText(f"Exporting book as {format_type}...")
                
                # This would use the book builder to export
                book_builder = BookBuilder()
                # book_builder.export_book(self.current_book, file_path, format_type)
                
                self.status_label.setText(f"Exported book as {format_type}")
                
                # Add to recent projects
                if hasattr(self, 'activity_list'):
                    self.activity_list.insertItem(0, f"📤 Exported book as {format_type}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export book: {e}")
    
    def start_research(self):
        """Start research process."""
        if not self.current_book:
            QMessageBox.warning(self, "No Book", "Please create or open a book first.")
            return
        
        # Start research in background
        self.start_research_async()
    
    def start_research_async(self):
        """Start research process asynchronously."""
        self.status_label.setText("Starting research...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # This would start the research agent
        research_agent = self.app.system_components['research_agent']
        # research_agent.start_research(self.current_book.theme)
        
        # Simulate progress
        self.simulate_progress("Research", 100)
    
    def generate_chapter(self):
        """Generate a new chapter."""
        if not self.current_book:
            QMessageBox.warning(self, "No Book", "Please create or open a book first.")
            return
        
        chapter_title, ok = QInputDialog.getText(self, "Generate Chapter", "Enter chapter title:")
        if ok and chapter_title:
            self.generate_chapter_async(chapter_title)
    
    def generate_chapter_async(self, chapter_title):
        """Generate chapter asynchronously."""
        self.status_label.setText(f"Generating chapter: {chapter_title}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # This would start the writer agent
        writer_agent = self.app.system_components['writer_agent']
        # writer_agent.generate_chapter(chapter_title, self.current_book.theme)
        
        # Simulate progress
        self.simulate_progress("Writing", 100)
    
    def simulate_progress(self, task_name, duration):
        """Simulate progress for a task."""
        for i in range(duration):
            self.progress_bar.setValue(i)
            QApplication.processEvents()
            QThread.msleep(20)  # 20ms delay
        
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Completed {task_name}")
        
        # Add to recent projects
        if hasattr(self, 'activity_list'):
            self.activity_list.insertItem(0, f"✅ Completed {task_name}")
    
    def update_book_info(self):
        """Update book information display."""
        if self.current_book:
            # Update current book label in workspace tab
            for i in range(self.nav_tabs.count()):
                tab = self.nav_tabs.widget(i)
                if hasattr(tab, 'current_book_label'):
                    tab.current_book_label.setText(f"📚 {self.current_book.title}")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Retro Writer</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Professional Book Writing Studio</b></p>
        <p>Create comprehensive, well-researched non-fiction books with AI assistance.</p>
        <p><b>Features:</b></p>
        <ul>
        <li>AI-powered research and writing</li>
        <li>Multi-agent coordination</li>
        <li>Memory management and RAG</li>
        <li>Multiple export formats</li>
        <li>Professional retro writer theme</li>
        </ul>
        <p><b>Built with:</b> Python, PyQt6, ChromaDB, OpenAI, Ollama</p>
        """
        
        QMessageBox.about(self, "About Retro Writer", about_text)
    
    # Additional helper methods
    def add_chapter(self, title):
        """Add a chapter to the current book."""
        if self.current_book:
            # This would add to the book's chapter list
            pass
    
    def delete_chapter(self, title):
        """Delete a chapter from the current book."""
        if self.current_book:
            # This would remove from the book's chapter list
            pass
    
    def load_chapter(self, title):
        """Load a chapter for editing."""
        # This would load chapter content into the editor
        pass
    
    def open_project(self, project_name):
        """Open a recent project."""
        # This would open the project
        pass


class ExportDialog(QDialog):
    """Dialog for selecting export format."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Book")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        
        # Format selection
        layout.addWidget(QLabel("Select export format:"))
        
        self.format_group = QButtonGroup()
        
        self.markdown_radio = QRadioButton("Markdown (.md)")
        self.markdown_radio.setChecked(True)
        self.format_group.addButton(self.markdown_radio, 0)
        layout.addWidget(self.markdown_radio)
        
        self.docx_radio = QRadioButton("Word Document (.docx)")
        self.format_group.addButton(self.docx_radio, 1)
        layout.addWidget(self.docx_radio)
        
        self.pdf_radio = QRadioButton("PDF (.pdf)")
        self.format_group.addButton(self.pdf_radio, 2)
        layout.addWidget(self.pdf_radio)
        
        self.html_radio = QRadioButton("HTML (.html)")
        self.format_group.addButton(self.html_radio, 3)
        layout.addWidget(self.html_radio)
        
        self.epub_radio = QRadioButton("EPUB (.epub)")
        self.format_group.addButton(self.epub_radio, 4)
        layout.addWidget(self.epub_radio)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_selected_format(self):
        """Get the selected export format."""
        formats = ["markdown", "docx", "pdf", "html", "epub"]
        return formats[self.format_group.checkedId()]


def main():
    """Main application entry point."""
    app = RetroWriterApp(sys.argv)
    
    # Create main window
    window = RetroWriterMainWindow(app)
    window.show()
    
    # Start event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())