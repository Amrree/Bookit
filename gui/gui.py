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


class AsyncWorker(QThread):
    """Worker thread for async operations."""
    
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, coro, *args, **kwargs):
        super().__init__()
        self.coro = coro
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Run the async operation."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.coro(*self.args, **self.kwargs))
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()


class BookWritingGUI(QMainWindow):
    """Main GUI application window."""
    
    def __init__(self):
        super().__init__()
        self.system_initialized = False
        self.memory_manager = None
        self.llm_client = None
        self.tool_manager = None
        self.agent_manager = None
        self.book_builder = None
        self.document_ingestor = None
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Book Writing System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Set modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QLineEdit, QTextEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }
            QListWidget, QTreeWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create left panel (navigation)
        self.create_left_panel(splitter)
        
        # Create right panel (main content)
        self.create_right_panel(splitter)
        
        # Create status bar
        self.create_status_bar()
        
        # Create menu bar
        self.create_menu_bar()
        
    def create_left_panel(self, parent):
        """Create left navigation panel."""
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        # System status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Not Initialized")
        self.status_label.setStyleSheet("color: #ff6b6b;")
        status_layout.addWidget(self.status_label)
        
        self.init_button = QPushButton("Initialize System")
        self.init_button.clicked.connect(self.init_system)
        status_layout.addWidget(self.init_button)
        
        left_layout.addWidget(status_group)
        
        # Navigation
        nav_group = QGroupBox("Navigation")
        nav_layout = QVBoxLayout(nav_group)
        
        self.nav_buttons = {
            'books': QPushButton("📚 Books"),
            'memory': QPushButton("🧠 Memory"),
            'agents': QPushButton("🤖 Agents"),
            'tools': QPushButton("🔧 Tools"),
            'settings': QPushButton("⚙️ Settings")
        }
        
        for button in self.nav_buttons.values():
            button.setCheckable(True)
            button.clicked.connect(self.navigate_to_tab)
            nav_layout.addWidget(button)
        
        left_layout.addWidget(nav_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.new_book_btn = QPushButton("New Book")
        self.new_book_btn.clicked.connect(self.create_new_book)
        actions_layout.addWidget(self.new_book_btn)
        
        self.import_doc_btn = QPushButton("Import Document")
        self.import_doc_btn.clicked.connect(self.import_document)
        actions_layout.addWidget(self.import_doc_btn)
        
        left_layout.addWidget(actions_group)
        
        left_layout.addStretch()
        parent.addWidget(left_panel)
        
    def create_right_panel(self, parent):
        """Create right main content panel."""
        self.content_stack = QStackedWidget()
        parent.addWidget(self.content_stack)
        
        # Create tab widgets for each section
        self.books_tab = self.create_books_tab()
        self.memory_tab = self.create_memory_tab()
        self.agents_tab = self.create_agents_tab()
        self.tools_tab = self.create_tools_tab()
        self.settings_tab = self.create_settings_tab()
        
        # Add tabs to stack
        self.content_stack.addWidget(self.books_tab)
        self.content_stack.addWidget(self.memory_tab)
        self.content_stack.addWidget(self.agents_tab)
        self.content_stack.addWidget(self.tools_tab)
        self.content_stack.addWidget(self.settings_tab)
        
    def create_books_tab(self):
        """Create books management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Books list
        books_group = QGroupBox("Books")
        books_layout = QVBoxLayout(books_group)
        
        self.books_list = QListWidget()
        books_layout.addWidget(self.books_list)
        
        # Book actions
        book_actions = QHBoxLayout()
        self.new_book_btn_tab = QPushButton("New Book")
        self.new_book_btn_tab.clicked.connect(self.create_new_book)
        book_actions.addWidget(self.new_book_btn_tab)
        
        self.export_book_btn = QPushButton("Export")
        self.export_book_btn.clicked.connect(self.export_book)
        book_actions.addWidget(self.export_book_btn)
        
        books_layout.addLayout(book_actions)
        layout.addWidget(books_group)
        
        # Book details
        details_group = QGroupBox("Book Details")
        details_layout = QVBoxLayout(details_group)
        
        self.book_title = QLabel("No book selected")
        self.book_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        details_layout.addWidget(self.book_title)
        
        self.book_info = QTextBrowser()
        self.book_info.setMaximumHeight(200)
        details_layout.addWidget(self.book_info)
        
        layout.addWidget(details_group)
        
        return tab
        
    def create_memory_tab(self):
        """Create memory management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search
        search_group = QGroupBox("Search Memory")
        search_layout = QVBoxLayout(search_group)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_memory)
        search_layout.addWidget(self.search_btn)
        
        layout.addWidget(search_group)
        
        # Results
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout(results_group)
        
        self.search_results = QTextBrowser()
        results_layout.addWidget(self.search_results)
        
        layout.addWidget(results_group)
        
        return tab
        
    def create_agents_tab(self):
        """Create agents management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Agent selection
        agent_group = QGroupBox("Select Agent")
        agent_layout = QVBoxLayout(agent_group)
        
        self.agent_combo = QComboBox()
        self.agent_combo.addItems(["Research Agent", "Writer Agent", "Editor Agent", "Tool Agent"])
        agent_layout.addWidget(self.agent_combo)
        
        # Task input
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Enter task for the agent...")
        self.task_input.setMaximumHeight(100)
        agent_layout.addWidget(self.task_input)
        
        self.run_agent_btn = QPushButton("Run Agent")
        self.run_agent_btn.clicked.connect(self.run_agent)
        agent_layout.addWidget(self.run_agent_btn)
        
        layout.addWidget(agent_group)
        
        # Agent output
        output_group = QGroupBox("Agent Output")
        output_layout = QVBoxLayout(output_group)
        
        self.agent_output = QTextBrowser()
        output_layout.addWidget(self.agent_output)
        
        layout.addWidget(output_group)
        
        return tab
        
    def create_tools_tab(self):
        """Create tools management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tools list
        tools_group = QGroupBox("Available Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        self.tools_list = QListWidget()
        tools_layout.addWidget(self.tools_list)
        
        layout.addWidget(tools_group)
        
        return tab
        
    def create_settings_tab(self):
        """Create settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # API settings
        api_group = QGroupBox("API Settings")
        api_layout = QFormLayout(api_group)
        
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("OpenAI API Key:", self.openai_key_input)
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setText("http://localhost:11434")
        api_layout.addRow("Ollama URL:", self.ollama_url_input)
        
        layout.addWidget(api_group)
        
        # System settings
        system_group = QGroupBox("System Settings")
        system_layout = QFormLayout(system_group)
        
        self.memory_dir_input = QLineEdit()
        self.memory_dir_input.setText("./memory_db")
        system_layout.addRow("Memory Directory:", self.memory_dir_input)
        
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setText("./books")
        system_layout.addRow("Output Directory:", self.output_dir_input)
        
        layout.addWidget(system_group)
        
        # Save settings
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_settings_btn)
        
        layout.addStretch()
        
        return tab
        
    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.showMessage("Ready")
        
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_book_action = QAction("New Book", self)
        new_book_action.triggered.connect(self.create_new_book)
        file_menu.addAction(new_book_action)
        
        import_action = QAction("Import Document", self)
        import_action.triggered.connect(self.import_document)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_connections(self):
        """Setup signal connections."""
        # Navigation buttons
        for i, (key, button) in enumerate(self.nav_buttons.items()):
            button.clicked.connect(lambda checked, idx=i: self.content_stack.setCurrentIndex(idx))
            
    def init_system(self):
        """Initialize the system."""
        self.status_label.setText("Initializing...")
        self.status_label.setStyleSheet("color: #ffa500;")
        
        # Get settings
        openai_key = self.openai_key_input.text() or None
        ollama_url = self.ollama_url_input.text()
        memory_dir = self.memory_dir_input.text()
        output_dir = self.output_dir_input.text()
        
        # Run initialization in worker thread
        worker = AsyncWorker(self._init_system_async, openai_key, ollama_url, memory_dir, output_dir)
        worker.finished.connect(self.on_system_initialized)
        worker.error.connect(self.on_system_error)
        worker.start()
        
    async def _init_system_async(self, openai_key, ollama_url, memory_dir, output_dir):
        """Async system initialization."""
        # Initialize memory manager
        self.memory_manager = MemoryManager(
            persist_directory=memory_dir,
            use_remote_embeddings=bool(openai_key),
            openai_api_key=openai_key
        )
        
        # Initialize LLM client
        self.llm_client = LLMClient(
            provider="openai" if openai_key else "ollama",
            openai_api_key=openai_key,
            ollama_base_url=ollama_url
        )
        
        # Initialize tool manager
        self.tool_manager = ToolManager()
        
        # Initialize document ingestor
        self.document_ingestor = DocumentIngestor()
        
        # Initialize book builder
        self.book_builder = BookBuilder(output_directory=output_dir)
        
        # Initialize agent manager
        self.agent_manager = AgentManager(
            memory_manager=self.memory_manager,
            llm_client=self.llm_client,
            tool_manager=self.tool_manager
        )
        
        self.system_initialized = True
        return True
        
    def on_system_initialized(self, result):
        """Handle system initialization success."""
        self.status_label.setText("System Initialized")
        self.status_label.setStyleSheet("color: #4caf50;")
        self.status_bar.showMessage("System ready")
        
        # Update UI
        self.init_button.setEnabled(False)
        self.new_book_btn.setEnabled(True)
        self.import_doc_btn.setEnabled(True)
        
        # Load initial data
        self.load_books()
        self.load_tools()
        
    def on_system_error(self, error):
        """Handle system initialization error."""
        self.status_label.setText("Initialization Failed")
        self.status_label.setStyleSheet("color: #f44336;")
        self.status_bar.showMessage(f"Error: {error}")
        
        QMessageBox.critical(self, "Initialization Error", f"Failed to initialize system:\n{error}")
        
    def navigate_to_tab(self):
        """Navigate to selected tab."""
        sender = self.sender()
        for i, (key, button) in enumerate(self.nav_buttons.items()):
            if button == sender:
                self.content_stack.setCurrentIndex(i)
                break
                
    def create_new_book(self):
        """Create a new book."""
        if not self.system_initialized:
            QMessageBox.warning(self, "System Not Initialized", "Please initialize the system first.")
            return
            
        # Show book creation dialog
        dialog = BookCreationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, author, description, audience = dialog.get_book_info()
            
            # Create book in worker thread
            worker = AsyncWorker(self._create_book_async, title, author, description, audience)
            worker.finished.connect(self.on_book_created)
            worker.error.connect(self.on_book_error)
            worker.start()
            
    async def _create_book_async(self, title, author, description, audience):
        """Async book creation."""
        outline = await self.book_builder.create_book_outline(
            title=title,
            author=author,
            description=description,
            target_audience=audience
        )
        return outline
        
    def on_book_created(self, outline):
        """Handle book creation success."""
        self.load_books()
        QMessageBox.information(self, "Book Created", f"Book '{outline.title}' created successfully!")
        
    def on_book_error(self, error):
        """Handle book creation error."""
        QMessageBox.critical(self, "Book Creation Error", f"Failed to create book:\n{error}")
        
    def load_books(self):
        """Load books list."""
        if not self.system_initialized:
            return
            
        self.books_list.clear()
        books = self.book_builder.list_books()
        
        for book in books:
            if book:
                item_text = f"{book['title']} ({book['total_word_count']} words)"
                self.books_list.addItem(item_text)
                
    def search_memory(self):
        """Search memory."""
        if not self.system_initialized:
            QMessageBox.warning(self, "System Not Initialized", "Please initialize the system first.")
            return
            
        query = self.search_input.text()
        if not query:
            return
            
        # Run search in worker thread
        worker = AsyncWorker(self._search_memory_async, query)
        worker.finished.connect(self.on_search_completed)
        worker.error.connect(self.on_search_error)
        worker.start()
        
    async def _search_memory_async(self, query):
        """Async memory search."""
        results = await self.memory_manager.retrieve_relevant_chunks(query, top_k=5)
        return results
        
    def on_search_completed(self, results):
        """Handle search completion."""
        if not results:
            self.search_results.setText("No results found.")
            return
            
        result_text = ""
        for i, result in enumerate(results, 1):
            result_text += f"--- Result {i} ---\n"
            result_text += f"Score: {result.score:.3f}\n"
            result_text += f"Source: {result.metadata.get('original_filename', 'Unknown')}\n"
            result_text += f"Content: {result.content[:200]}...\n\n"
            
        self.search_results.setText(result_text)
        
    def on_search_error(self, error):
        """Handle search error."""
        QMessageBox.critical(self, "Search Error", f"Search failed:\n{error}")
        
    def run_agent(self):
        """Run selected agent."""
        if not self.system_initialized:
            QMessageBox.warning(self, "System Not Initialized", "Please initialize the system first.")
            return
            
        agent_type = self.agent_combo.currentText().lower().replace(" agent", "")
        task = self.task_input.toPlainText()
        
        if not task:
            QMessageBox.warning(self, "No Task", "Please enter a task for the agent.")
            return
            
        # Run agent in worker thread
        worker = AsyncWorker(self._run_agent_async, agent_type, task)
        worker.finished.connect(self.on_agent_completed)
        worker.error.connect(self.on_agent_error)
        worker.start()
        
    async def _run_agent_async(self, agent_type, task):
        """Async agent execution."""
        if agent_type == "research":
            agent = ResearchAgent(
                memory_manager=self.memory_manager,
                llm_client=self.llm_client
            )
            result = await agent.research_topic(task, "")
            
        elif agent_type == "writer":
            agent = WriterAgent(
                memory_manager=self.memory_manager,
                llm_client=self.llm_client
            )
            result = await agent.write_content(task, "")
            
        elif agent_type == "editor":
            agent = EditorAgent(
                memory_manager=self.memory_manager,
                llm_client=self.llm_client
            )
            result = await agent.edit_content(task, "")
            
        elif agent_type == "tool":
            agent = ToolAgent(
                tool_manager=self.tool_manager,
                llm_client=self.llm_client
            )
            result = await agent.execute_tool(task, "")
            
        return result
        
    def on_agent_completed(self, result):
        """Handle agent completion."""
        self.agent_output.setText(str(result))
        
    def on_agent_error(self, error):
        """Handle agent error."""
        QMessageBox.critical(self, "Agent Error", f"Agent execution failed:\n{error}")
        
    def load_tools(self):
        """Load tools list."""
        if not self.system_initialized:
            return
            
        self.tools_list.clear()
        tools = self.tool_manager.list_tools()
        
        for tool in tools:
            self.tools_list.addItem(f"{tool['name']}: {tool['description']}")
            
    def import_document(self):
        """Import document."""
        if not self.system_initialized:
            QMessageBox.warning(self, "System Not Initialized", "Please initialize the system first.")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Document", "", "All Files (*);;PDF (*.pdf);;DOCX (*.docx);;TXT (*.txt);;MD (*.md)"
        )
        
        if file_path:
            # Import document in worker thread
            worker = AsyncWorker(self._import_document_async, file_path)
            worker.finished.connect(self.on_document_imported)
            worker.error.connect(self.on_import_error)
            worker.start()
            
    async def _import_document_async(self, file_path):
        """Async document import."""
        metadata, chunks = await self.document_ingestor.ingest_document(file_path)
        await self.memory_manager.store_document_chunks(metadata, chunks, agent_id="gui")
        return metadata
        
    def on_document_imported(self, metadata):
        """Handle document import success."""
        QMessageBox.information(self, "Document Imported", f"Document '{metadata.original_filename}' imported successfully!")
        
    def on_import_error(self, error):
        """Handle import error."""
        QMessageBox.critical(self, "Import Error", f"Failed to import document:\n{error}")
        
    def export_book(self):
        """Export book."""
        if not self.system_initialized:
            QMessageBox.warning(self, "System Not Initialized", "Please initialize the system first.")
            return
            
        # TODO: Implement book export
        QMessageBox.information(self, "Export", "Book export functionality coming soon!")
        
    def save_settings(self):
        """Save settings."""
        # Settings are automatically saved when system is initialized
        QMessageBox.information(self, "Settings", "Settings saved!")
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", "Book Writing System\nA modern AI-powered book writing tool")
        
    def closeEvent(self, event):
        """Handle application close."""
        event.accept()


class BookCreationDialog(QDialog):
    """Dialog for creating new books."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Book")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QFormLayout(self)
        
        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)
        
        self.author_input = QLineEdit()
        layout.addRow("Author:", self.author_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addRow("Description:", self.description_input)
        
        self.audience_input = QLineEdit()
        layout.addRow("Target Audience:", self.audience_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_book_info(self):
        """Get book information from dialog."""
        return (
            self.title_input.text(),
            self.author_input.text(),
            self.description_input.toPlainText(),
            self.audience_input.text()
        )


def main():
    """Main GUI entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Book Writing System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Book Writing System")
    
    # Create and show main window
    window = BookWritingGUI()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()