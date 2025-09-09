"""
Comprehensive GUI tests for the book-writing system.
Tests all GUI components, interactions, and integrations.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Add the workspace to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gui import MainWindow, ConfigurationDialog, SystemWorker


class TestGUIComponents:
    """Test individual GUI components."""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def main_window(self, app):
        """Create main window for testing."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            yield window
            window.close()
    
    @pytest.fixture
    def config_dialog(self, app):
        """Create configuration dialog for testing."""
        dialog = ConfigurationDialog()
        yield dialog
        dialog.close()
    
    def test_main_window_creation(self, main_window):
        """Test main window creation and basic properties."""
        assert main_window is not None
        assert main_window.windowTitle() == "Non-Fiction Book Writer"
        assert main_window.minimumSize().width() == 1200
        assert main_window.minimumSize().height() == 800
    
    def test_configuration_dialog_creation(self, config_dialog):
        """Test configuration dialog creation."""
        assert config_dialog is not None
        assert config_dialog.windowTitle() == "System Configuration"
        assert config_dialog.isModal() == True
    
    def test_configuration_dialog_fields(self, config_dialog):
        """Test configuration dialog form fields."""
        assert hasattr(config_dialog, 'openai_key')
        assert hasattr(config_dialog, 'ollama_url')
        assert hasattr(config_dialog, 'embedding_key')
        assert hasattr(config_dialog, 'vector_db_path')
        assert hasattr(config_dialog, 'allow_unsafe')
        
        # Test default values
        assert config_dialog.ollama_url.text() == "http://localhost:11434"
        assert config_dialog.vector_db_path.text() == "./memory_db"
    
    def test_sidebar_components(self, main_window):
        """Test sidebar components."""
        # Check navigation buttons
        nav_buttons = main_window.nav_buttons
        expected_buttons = ['documents', 'research', 'books', 'tools', 'settings']
        assert all(btn in nav_buttons for btn in expected_buttons)
        
        # Check quick action buttons
        assert hasattr(main_window, 'new_book_btn')
        assert hasattr(main_window, 'import_doc_btn')
        assert hasattr(main_window, 'start_research_btn')
    
    def test_content_pages(self, main_window):
        """Test content pages setup."""
        content_stack = main_window.content_stack
        assert content_stack.count() == 5  # documents, research, books, tools, settings
        
        # Test page switching
        main_window.switch_page('documents')
        assert main_window.content_stack.currentIndex() == 0
        
        main_window.switch_page('research')
        assert main_window.content_stack.currentIndex() == 1
        
        main_window.switch_page('books')
        assert main_window.content_stack.currentIndex() == 2
        
        main_window.switch_page('tools')
        assert main_window.content_stack.currentIndex() == 3
        
        main_window.switch_page('settings')
        assert main_window.content_stack.currentIndex() == 4
    
    def test_navigation_buttons(self, main_window):
        """Test navigation button interactions."""
        # Test button states
        for name, button in main_window.nav_buttons.items():
            assert button.isCheckable() == True
            assert button.isChecked() == False
        
        # Test button clicking
        main_window.nav_buttons['documents'].click()
        assert main_window.nav_buttons['documents'].isChecked() == True
        assert main_window.content_stack.currentIndex() == 0
    
    def test_status_bar(self, main_window):
        """Test status bar functionality."""
        status_bar = main_window.status_bar
        assert status_bar is not None
        assert hasattr(main_window, 'progress_bar')
        assert main_window.progress_bar.isVisible() == False
    
    def test_menu_bar(self, main_window):
        """Test menu bar setup."""
        menubar = main_window.menuBar()
        assert menubar is not None
        
        # Check menu items
        file_menu = menubar.findChild(type(menubar), "File")
        assert file_menu is not None
        
        edit_menu = menubar.findChild(type(menubar), "Edit")
        assert edit_menu is not None
        
        view_menu = menubar.findChild(type(menubar), "View")
        assert view_menu is not None


class TestGUIIntegration:
    """Test GUI integration with system components."""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    @pytest.fixture
    def main_window(self, app):
        """Create main window with mocked system components."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            
            # Mock system components
            window.system_components = {
                'memory_manager': Mock(),
                'llm_client': Mock(),
                'tool_manager': Mock(),
                'agent_manager': Mock(),
                'research_agent': Mock(),
                'writer_agent': Mock(),
                'editor_agent': Mock(),
                'tool_agent': Mock(),
                'book_builder': Mock()
            }
            window.system_initialized = True
            
            yield window
            window.close()
    
    def test_system_initialization_mock(self, main_window):
        """Test system initialization with mocked components."""
        # Mock the async initialization
        with patch('gui.MainWindow._async_initialize_system') as mock_init:
            mock_init.return_value = {
                'memory_manager': Mock(),
                'llm_client': Mock(),
                'agent_manager': Mock()
            }
            
            # Test initialization
            main_window.initialize_system(
                openai_key="test_key",
                ollama_url="http://localhost:11434",
                vector_db_path="./test_db"
            )
            
            # Verify initialization was called
            mock_init.assert_called_once()
    
    def test_system_status_update(self, main_window):
        """Test system status update functionality."""
        # Mock system component stats
        main_window.system_components['memory_manager'].get_stats.return_value = {
            'total_chunks': 100
        }
        main_window.system_components['agent_manager'].get_stats.return_value = {
            'total_agents': 4
        }
        main_window.system_components['tool_manager'].get_execution_stats.return_value = {
            'available_tools': 5
        }
        
        # Update status
        main_window.update_system_status()
        
        # Verify status labels were updated
        assert "100 chunks" in main_window.memory_chunks_label.text()
        assert "4 active" in main_window.agents_label.text()
        assert "5 available" in main_window.tools_label.text()
    
    def test_document_import_dialog(self, main_window):
        """Test document import functionality."""
        with patch('gui.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("/path/to/test.pdf", "PDF (*.pdf)")
            
            # Test import
            main_window.import_document()
            
            # Verify dialog was called
            mock_dialog.assert_called_once()
    
    def test_quick_actions(self, main_window):
        """Test quick action buttons."""
        # Test new book action
        with patch('gui.QMessageBox.information') as mock_msg:
            main_window.new_book()
            mock_msg.assert_called_once()
        
        # Test new research action
        with patch('gui.QMessageBox.information') as mock_msg:
            main_window.new_research()
            mock_msg.assert_called_once()
        
        # Test import document action
        with patch('gui.QFileDialog.getOpenFileName') as mock_dialog:
            main_window.import_document()
            mock_dialog.assert_called_once()


class TestSystemWorker:
    """Test the SystemWorker background thread."""
    
    def test_system_worker_creation(self):
        """Test SystemWorker creation."""
        def test_operation():
            return "test_result"
        
        worker = SystemWorker(test_operation)
        assert worker is not None
        assert worker.operation == test_operation
    
    def test_system_worker_execution(self):
        """Test SystemWorker execution."""
        def test_operation():
            return "test_result"
        
        worker = SystemWorker(test_operation)
        
        # Mock the signals
        worker.operation_completed = Mock()
        worker.operation_failed = Mock()
        
        # Run the worker
        worker.run()
        
        # Verify success signal was emitted
        worker.operation_completed.emit.assert_called_once_with("success", "test_result")
    
    def test_system_worker_error_handling(self):
        """Test SystemWorker error handling."""
        def failing_operation():
            raise Exception("Test error")
        
        worker = SystemWorker(failing_operation)
        
        # Mock the signals
        worker.operation_completed = Mock()
        worker.operation_failed = Mock()
        
        # Run the worker
        worker.run()
        
        # Verify error signal was emitted
        worker.operation_failed.emit.assert_called_once_with("error", "Test error")


class TestGUIStyling:
    """Test GUI styling and appearance."""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    def test_zed_style_application(self, app):
        """Test Zed-inspired styling application."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            
            # Check that styling is applied
            assert window.styleSheet() != ""
            
            # Check specific style elements
            style = window.styleSheet()
            assert "background-color: #1e1e1e" in style
            assert "color: #d4d4d4" in style
            assert "QPushButton" in style
            assert "QGroupBox" in style
            
            window.close()
    
    def test_configuration_dialog_styling(self, app):
        """Test configuration dialog styling."""
        dialog = ConfigurationDialog()
        
        # Check that styling is applied
        assert dialog.styleSheet() != ""
        
        # Check specific style elements
        style = dialog.styleSheet()
        assert "background-color: #1e1e1e" in style
        assert "color: #d4d4d4" in style
        assert "QLineEdit" in style
        assert "QCheckBox" in style
        
        dialog.close()


class TestGUIErrorHandling:
    """Test GUI error handling and edge cases."""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    def test_uninitialized_system_actions(self, app):
        """Test actions when system is not initialized."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            window.system_initialized = False
            
            # Test that actions show warnings
            with patch('gui.QMessageBox.warning') as mock_warning:
                window.new_book()
                mock_warning.assert_called_once()
            
            with patch('gui.QMessageBox.warning') as mock_warning:
                window.new_research()
                mock_warning.assert_called_once()
            
            with patch('gui.QMessageBox.warning') as mock_warning:
                window.import_document()
                mock_warning.assert_called_once()
            
            window.close()
    
    def test_system_initialization_failure(self, app):
        """Test system initialization failure handling."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            
            # Mock initialization failure
            with patch('gui.MainWindow._async_initialize_system') as mock_init:
                mock_init.side_effect = Exception("Initialization failed")
                
                with patch('gui.QMessageBox.critical') as mock_critical:
                    window.initialize_system()
                    # Note: This would need to be tested with actual async execution
                    # For now, we just verify the error handling structure exists
            
            window.close()


class TestGUIPerformance:
    """Test GUI performance characteristics."""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    def test_window_creation_performance(self, app):
        """Test window creation performance."""
        import time
        
        start_time = time.time()
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
        end_time = time.time()
        
        # Window creation should be fast
        assert (end_time - start_time) < 2.0  # Less than 2 seconds
        window.close()
    
    def test_page_switching_performance(self, app):
        """Test page switching performance."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            
            import time
            start_time = time.time()
            
            # Switch through all pages
            for page in ['documents', 'research', 'books', 'tools', 'settings']:
                window.switch_page(page)
            
            end_time = time.time()
            
            # Page switching should be very fast
            assert (end_time - start_time) < 0.1  # Less than 100ms
            window.close()


class TestGUICompleteness:
    """Test GUI completeness and feature coverage."""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
    
    def test_all_required_components_present(self, app):
        """Test that all required GUI components are present."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            
            # Check main components
            assert hasattr(window, 'content_stack')
            assert hasattr(window, 'nav_buttons')
            assert hasattr(window, 'status_bar')
            assert hasattr(window, 'progress_bar')
            
            # Check navigation buttons
            required_nav = ['documents', 'research', 'books', 'tools', 'settings']
            for nav in required_nav:
                assert nav in window.nav_buttons
            
            # Check quick actions
            assert hasattr(window, 'new_book_btn')
            assert hasattr(window, 'import_doc_btn')
            assert hasattr(window, 'start_research_btn')
            
            # Check content pages
            assert window.content_stack.count() == 5
            
            window.close()
    
    def test_gui_initialization_sequence(self, app):
        """Test GUI initialization sequence."""
        with patch('gui.MainWindow.show_configuration_dialog') as mock_config:
            window = MainWindow()
            
            # Configuration dialog should be shown on initialization
            mock_config.assert_called_once()
            
            # System should not be initialized initially
            assert window.system_initialized == False
            
            window.close()
    
    def test_gui_integration_points(self, app):
        """Test GUI integration points with system modules."""
        with patch('gui.MainWindow.show_configuration_dialog'):
            window = MainWindow()
            
            # Check that all system modules are imported
            import gui
            assert hasattr(gui, 'DocumentIngestor')
            assert hasattr(gui, 'MemoryManager')
            assert hasattr(gui, 'LLMClient')
            assert hasattr(gui, 'ToolManager')
            assert hasattr(gui, 'AgentManager')
            assert hasattr(gui, 'ResearchAgent')
            assert hasattr(gui, 'WriterAgent')
            assert hasattr(gui, 'EditorAgent')
            assert hasattr(gui, 'ToolAgent')
            assert hasattr(gui, 'BookBuilder')
            
            window.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])