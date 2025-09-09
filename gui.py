"""
Mac-Native GUI Module

Clean, Zed-inspired graphical user interface for the non-fiction book-writing system.
Uses PyQt6 for native Mac integration and modern UI design.

Chosen libraries:
- PyQt6: Native Mac GUI framework with modern design capabilities
- asyncio: Asynchronous operations
- logging: GUI activity logging

Adapted from: Zed editor design principles
Pattern: Clean, minimal interface with powerful functionality
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTabWidget, QTextEdit, QListWidget, QTreeWidget, 
    QTreeWidgetItem, QPushButton, QLabel, QLineEdit, QTextBrowser,
    QProgressBar, QStatusBar, QMenuBar, QMenu, QAction,
    QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QSpinBox, QComboBox, QCheckBox, QGroupBox, QScrollArea,
    QFrame, QSizePolicy, QGridLayout, QStackedWidget
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QRect, QPoint
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QAction,
    QKeySequence, QTextCursor, QTextCharFormat, QSyntaxHighlighter
)

# Import system modules
from document_ingestor import DocumentIngestor
from memory_manager import MemoryManager
from llm_client import LLMClient
from tool_manager import ToolManager
from agent_manager import AgentManager
from research_agent import ResearchAgent
from writer_agent import WriterAgent, WritingStyle
from editor_agent import EditorAgent, StyleGuide
from tool_agent import ToolAgent
from book_builder import BookBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemWorker(QThread):
    """Background worker for system operations."""
    
    operation_completed = pyqtSignal(str, object)
    operation_failed = pyqtSignal(str, str)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = asyncio.run(self.operation(*self.args, **self.kwargs))
            self.operation_completed.emit("success", result)
        except Exception as e:
            self.operation_failed.emit("error", str(e))


class ConfigurationDialog(QDialog):
    """Configuration dialog with Zed-inspired design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Configuration")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.apply_zed_style()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # API Configuration Group
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()
        
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setPlaceholderText("Enter OpenAI API key")
        
        self.ollama_url = QLineEdit()
        self.ollama_url.setText("http://localhost:11434")
        self.ollama_url.setPlaceholderText("Ollama server URL")
        
        self.embedding_key = QLineEdit()
        self.embedding_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.embedding_key.setPlaceholderText("Optional: Embedding API key")
        
        api_layout.addRow("OpenAI API Key:", self.openai_key)
        api_layout.addRow("Ollama URL:", self.ollama_url)
        api_layout.addRow("Embedding API Key:", self.embedding_key)
        api_group.setLayout(api_layout)
        
        # System Configuration Group
        system_group = QGroupBox("System Configuration")
        system_layout = QFormLayout()
        
        self.vector_db_path = QLineEdit()
        self.vector_db_path.setText("./memory_db")
        self.vector_db_path.setPlaceholderText("Vector database path")
        
        self.allow_unsafe = QCheckBox()
        self.allow_unsafe.setText("Allow unsafe tools")
        
        system_layout.addRow("Vector DB Path:", self.vector_db_path)
        system_layout.addRow("", self.allow_unsafe)
        system_group.setLayout(system_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(api_group)
        layout.addWidget(system_group)
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def apply_zed_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 5px;
                color: #d4d4d4;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QCheckBox {
                color: #d4d4d4;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8a;
            }
        """)


class MainWindow(QMainWindow):
    """Main application window with Zed-inspired design."""
    
    def __init__(self):
        super().__init__()
        self.system_initialized = False
        self.system_components = {}
        self.setup_ui()
        self.apply_zed_style()
        self.setup_connections()
        
        # Initialize with configuration dialog
        self.show_configuration_dialog()
    
    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("Non-Fiction Book Writer")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left sidebar
        self.setup_sidebar(splitter)
        
        # Main content area
        self.setup_main_content(splitter)
        
        # Set splitter proportions
        splitter.setSizes([300, 1100])
        
        # Status bar
        self.setup_status_bar()
        
        # Menu bar
        self.setup_menu_bar()
    
    def setup_sidebar(self, parent):
        """Setup the left sidebar."""
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        
        # System status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Not Initialized")
        self.status_label.setStyleSheet("color: #f48771; font-weight: bold;")
        
        self.memory_chunks_label = QLabel("Memory: 0 chunks")
        self.agents_label = QLabel("Agents: 0 active")
        self.tools_label = QLabel("Tools: 0 available")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.memory_chunks_label)
        status_layout.addWidget(self.agents_label)
        status_layout.addWidget(self.tools_label)
        status_group.setLayout(status_layout)
        
        # Navigation
        nav_group = QGroupBox("Navigation")
        nav_layout = QVBoxLayout()
        
        self.nav_buttons = {
            'documents': QPushButton("📄 Documents"),
            'research': QPushButton("🔍 Research"),
            'books': QPushButton("📚 Books"),
            'tools': QPushButton("🔧 Tools"),
            'settings': QPushButton("⚙️ Settings")
        }
        
        for button in self.nav_buttons.values():
            button.setCheckable(True)
            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    background-color: transparent;
                    color: #d4d4d4;
                }
                QPushButton:hover {
                    background-color: #2d2d30;
                }
                QPushButton:checked {
                    background-color: #0e639c;
                    color: white;
                }
            """)
            nav_layout.addWidget(button)
        
        nav_group.setLayout(nav_layout)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        
        self.new_book_btn = QPushButton("New Book")
        self.import_doc_btn = QPushButton("Import Document")
        self.start_research_btn = QPushButton("Start Research")
        
        for btn in [self.new_book_btn, self.import_doc_btn, self.start_research_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0e639c;
                    border: none;
                    border-radius: 3px;
                    padding: 8px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QPushButton:disabled {
                    background-color: #3c3c3c;
                    color: #666666;
                }
            """)
            actions_layout.addWidget(btn)
        
        actions_group.setLayout(actions_layout)
        
        sidebar_layout.addWidget(status_group)
        sidebar_layout.addWidget(nav_group)
        sidebar_layout.addWidget(actions_group)
        sidebar_layout.addStretch()
        
        parent.addWidget(sidebar)
    
    def setup_main_content(self, parent):
        """Setup the main content area."""
        self.content_stack = QStackedWidget()
        parent.addWidget(self.content_stack)
        
        # Documents page
        self.setup_documents_page()
        
        # Research page
        self.setup_research_page()
        
        # Books page
        self.setup_books_page()
        
        # Tools page
        self.setup_tools_page()
        
        # Settings page
        self.setup_settings_page()
    
    def setup_documents_page(self):
        """Setup the documents management page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Documents")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #d4d4d4;")
        header.addWidget(title)
        header.addStretch()
        
        import_btn = QPushButton("Import Document")
        import_btn.clicked.connect(self.import_document)
        header.addWidget(import_btn)
        
        layout.addLayout(header)
        
        # Document list
        self.documents_list = QTreeWidget()
        self.documents_list.setHeaderLabels(["Name", "Type", "Chunks", "Size"])
        self.documents_list.setStyleSheet("""
            QTreeWidget {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3c3c3c;
            }
            QTreeWidget::item:selected {
                background-color: #0e639c;
            }
        """)
        
        layout.addWidget(self.documents_list)
        
        self.content_stack.addWidget(page)
    
    def setup_research_page(self):
        """Setup the research management page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Research")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #d4d4d4;")
        header.addWidget(title)
        header.addStretch()
        
        new_research_btn = QPushButton("New Research")
        new_research_btn.clicked.connect(self.new_research)
        header.addWidget(new_research_btn)
        
        layout.addLayout(header)
        
        # Research topics list
        self.research_list = QListWidget()
        self.research_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3c3c3c;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
            }
        """)
        
        layout.addWidget(self.research_list)
        
        self.content_stack.addWidget(page)
    
    def setup_books_page(self):
        """Setup the books management page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Books")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #d4d4d4;")
        header.addWidget(title)
        header.addStretch()
        
        new_book_btn = QPushButton("New Book")
        new_book_btn.clicked.connect(self.new_book)
        header.addWidget(new_book_btn)
        
        layout.addLayout(header)
        
        # Books list
        self.books_list = QTreeWidget()
        self.books_list.setHeaderLabels(["Title", "Author", "Status", "Chapters", "Progress"])
        self.books_list.setStyleSheet("""
            QTreeWidget {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3c3c3c;
            }
            QTreeWidget::item:selected {
                background-color: #0e639c;
            }
        """)
        
        layout.addWidget(self.books_list)
        
        self.content_stack.addWidget(page)
    
    def setup_tools_page(self):
        """Setup the tools management page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Tools")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #d4d4d4;")
        header.addWidget(title)
        header.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_tools)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Tools list
        self.tools_list = QListWidget()
        self.tools_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3c3c3c;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
            }
        """)
        
        layout.addWidget(self.tools_list)
        
        self.content_stack.addWidget(page)
    
    def setup_settings_page(self):
        """Setup the settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #d4d4d4;")
        header.addWidget(title)
        header.addStretch()
        
        config_btn = QPushButton("Configure System")
        config_btn.clicked.connect(self.show_configuration_dialog)
        header.addWidget(config_btn)
        
        layout.addLayout(header)
        
        # Settings content
        settings_group = QGroupBox("System Configuration")
        settings_layout = QFormLayout()
        
        self.current_config = QTextEdit()
        self.current_config.setReadOnly(True)
        self.current_config.setMaximumHeight(200)
        
        settings_layout.addRow("Current Configuration:", self.current_config)
        settings_group.setLayout(settings_layout)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        self.content_stack.addWidget(page)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def setup_menu_bar(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        import_action = QAction("Import Document", self)
        import_action.triggered.connect(self.import_document)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Quit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_configuration_dialog)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        for name, button in self.nav_buttons.items():
            action = QAction(name.title(), self)
            action.triggered.connect(lambda checked, n=name: self.switch_page(n))
            view_menu.addAction(action)
    
    def apply_zed_style(self):
        """Apply Zed-inspired styling to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #d4d4d4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8a;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #666666;
            }
            QLineEdit {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 5px;
                color: #d4d4d4;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QTextEdit {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QListWidget {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3c3c3c;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
            }
            QTreeWidget {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                color: #d4d4d4;
            }
            QTreeWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3c3c3c;
            }
            QTreeWidget::item:selected {
                background-color: #0e639c;
            }
            QStatusBar {
                background-color: #2d2d30;
                border-top: 1px solid #3c3c3c;
                color: #d4d4d4;
            }
            QMenuBar {
                background-color: #2d2d30;
                border-bottom: 1px solid #3c3c3c;
                color: #d4d4d4;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #0e639c;
            }
            QMenu {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                color: #d4d4d4;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #0e639c;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Navigation buttons
        for name, button in self.nav_buttons.items():
            button.clicked.connect(lambda checked, n=name: self.switch_page(n))
        
        # Quick action buttons
        self.new_book_btn.clicked.connect(self.new_book)
        self.import_doc_btn.clicked.connect(self.import_document)
        self.start_research_btn.clicked.connect(self.new_research)
    
    def show_configuration_dialog(self):
        """Show the configuration dialog."""
        dialog = ConfigurationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.initialize_system(
                openai_key=dialog.openai_key.text(),
                ollama_url=dialog.ollama_url.text(),
                embedding_key=dialog.embedding_key.text(),
                vector_db_path=dialog.vector_db_path.text(),
                allow_unsafe=dialog.allow_unsafe.isChecked()
            )
    
    def initialize_system(self, **config):
        """Initialize the system with given configuration."""
        self.status_bar.showMessage("Initializing system...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start initialization in background thread
        self.worker = SystemWorker(self._async_initialize_system, config)
        self.worker.operation_completed.connect(self.on_system_initialized)
        self.worker.operation_failed.connect(self.on_system_initialization_failed)
        self.worker.start()
    
    async def _async_initialize_system(self, config):
        """Async system initialization."""
        try:
            # Initialize components
            memory_manager = MemoryManager(
                persist_directory=config.get('vector_db_path', './memory_db'),
                use_remote_embeddings=bool(config.get('embedding_key')),
                openai_api_key=config.get('embedding_key')
            )
            
            llm_client = LLMClient(
                primary_provider="openai" if config.get('openai_key') else "ollama",
                openai_api_key=config.get('openai_key'),
                ollama_url=config.get('ollama_url', 'http://localhost:11434')
            )
            
            tool_manager = ToolManager(
                allow_unsafe=config.get('allow_unsafe', False),
                allow_restricted=True
            )
            
            agent_manager = AgentManager()
            await agent_manager.start()
            
            # Initialize agents
            research_agent = ResearchAgent(
                agent_id="research_agent",
                memory_manager=memory_manager,
                llm_client=llm_client,
                tool_manager=tool_manager
            )
            
            writer_agent = WriterAgent(
                agent_id="writer_agent",
                memory_manager=memory_manager,
                llm_client=llm_client,
                research_agent=research_agent,
                writing_style=WritingStyle()
            )
            
            editor_agent = EditorAgent(
                agent_id="editor_agent",
                llm_client=llm_client,
                style_guide=StyleGuide()
            )
            
            tool_agent = ToolAgent(
                agent_id="tool_agent",
                tool_manager=tool_manager
            )
            
            # Register agents
            agent_manager.register_agent(research_agent, "research_agent", "research", ["research"])
            agent_manager.register_agent(writer_agent, "writer_agent", "writer", ["writing"])
            agent_manager.register_agent(editor_agent, "editor_agent", "editor", ["editing"])
            agent_manager.register_agent(tool_agent, "tool_agent", "tool", ["tools"])
            
            book_builder = BookBuilder(
                agent_manager=agent_manager,
                memory_manager=memory_manager,
                research_agent=research_agent,
                writer_agent=writer_agent,
                editor_agent=editor_agent,
                tool_agent=tool_agent
            )
            
            return {
                'memory_manager': memory_manager,
                'llm_client': llm_client,
                'tool_manager': tool_manager,
                'agent_manager': agent_manager,
                'research_agent': research_agent,
                'writer_agent': writer_agent,
                'editor_agent': editor_agent,
                'tool_agent': tool_agent,
                'book_builder': book_builder
            }
            
        except Exception as e:
            raise Exception(f"System initialization failed: {e}")
    
    def on_system_initialized(self, status, result):
        """Handle successful system initialization."""
        self.system_components = result
        self.system_initialized = True
        
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("System initialized successfully")
        
        # Update UI
        self.status_label.setText("Initialized")
        self.status_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        
        # Enable buttons
        for btn in [self.new_book_btn, self.import_doc_btn, self.start_research_btn]:
            btn.setEnabled(True)
        
        # Update status
        self.update_system_status()
    
    def on_system_initialization_failed(self, status, error):
        """Handle failed system initialization."""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"System initialization failed: {error}")
        
        QMessageBox.critical(self, "Initialization Error", f"Failed to initialize system:\n{error}")
    
    def update_system_status(self):
        """Update the system status display."""
        if not self.system_initialized:
            return
        
        try:
            # Update memory stats
            memory_stats = self.system_components['memory_manager'].get_stats()
            self.memory_chunks_label.setText(f"Memory: {memory_stats['total_chunks']} chunks")
            
            # Update agent stats
            agent_stats = self.system_components['agent_manager'].get_stats()
            self.agents_label.setText(f"Agents: {agent_stats['total_agents']} active")
            
            # Update tool stats
            tool_stats = self.system_components['tool_manager'].get_execution_stats()
            self.tools_label.setText(f"Tools: {tool_stats['available_tools']} available")
            
        except Exception as e:
            logger.error(f"Failed to update system status: {e}")
    
    def switch_page(self, page_name):
        """Switch to the specified page."""
        page_map = {
            'documents': 0,
            'research': 1,
            'books': 2,
            'tools': 3,
            'settings': 4
        }
        
        if page_name in page_map:
            self.content_stack.setCurrentIndex(page_map[page_name])
            
            # Update button states
            for name, button in self.nav_buttons.items():
                button.setChecked(name == page_name)
    
    def import_document(self):
        """Import a document."""
        if not self.system_initialized:
            QMessageBox.warning(self, "Not Initialized", "Please initialize the system first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Document",
            "",
            "All Supported (*.pdf *.docx *.epub *.txt *.md);;PDF (*.pdf);;Word (*.docx);;EPUB (*.epub);;Text (*.txt);;Markdown (*.md)"
        )
        
        if file_path:
            self.status_bar.showMessage("Importing document...")
            # TODO: Implement document import
            QMessageBox.information(self, "Import", f"Document imported: {Path(file_path).name}")
    
    def new_research(self):
        """Start new research."""
        if not self.system_initialized:
            QMessageBox.warning(self, "Not Initialized", "Please initialize the system first.")
            return
        
        # TODO: Implement research dialog
        QMessageBox.information(self, "New Research", "Research functionality will be implemented here.")
    
    def new_book(self):
        """Create new book."""
        if not self.system_initialized:
            QMessageBox.warning(self, "Not Initialized", "Please initialize the system first.")
            return
        
        # TODO: Implement book creation dialog
        QMessageBox.information(self, "New Book", "Book creation functionality will be implemented here.")
    
    def refresh_tools(self):
        """Refresh the tools list."""
        if not self.system_initialized:
            return
        
        # TODO: Implement tools refresh
        pass


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Non-Fiction Book Writer")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()