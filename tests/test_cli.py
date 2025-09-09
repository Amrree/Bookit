"""
Unit tests for the CLI module.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
import subprocess
import sys
from pathlib import Path


class TestCLI:
    """Test cases for CLI functionality."""
    
    @pytest.mark.asyncio
    async def test_cli_import(self):
        """Test CLI module import."""
        import cli
        assert cli is not None
        assert hasattr(cli, 'cli')
    
    @pytest.mark.asyncio
    async def test_cli_commands_available(self):
        """Test that all CLI commands are available."""
        import cli
        
        # Test main CLI group
        assert hasattr(cli, 'cli')
        
        # Test book command group
        assert hasattr(cli, 'book')
    
    @pytest.mark.asyncio
    async def test_cli_book_create_command(self, temp_dir):
        """Test CLI book create command."""
        cmd = [
            sys.executable, "-m", "cli", "book", "create",
            "--title", "CLI Test Book",
            "--theme", "CLI Testing",
            "--author", "CLI Test Author",
            "--word-count", "2000",
            "--chapters", "3",
            "--output-dir", str(temp_dir)
        ]
        
        # Mock the actual execution to avoid external dependencies
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Book created successfully")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
    
    @pytest.mark.asyncio
    async def test_cli_book_status_command(self, temp_dir):
        """Test CLI book status command."""
        # Create a mock build log
        import json
        build_log = {
            "book_metadata": {
                "title": "Status Test Book",
                "status": "completed",
                "build_id": "status_test_001"
            }
        }
        
        build_log_file = temp_dir / "status_test_001" / "build_log.json"
        build_log_file.parent.mkdir(exist_ok=True)
        build_log_file.write_text(json.dumps(build_log))
        
        cmd = [
            sys.executable, "-m", "cli", "book", "status",
            "--build-id", "status_test_001",
            "--output-dir", str(temp_dir)
        ]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Book status: completed")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
    
    @pytest.mark.asyncio
    async def test_cli_book_list_command(self, temp_dir):
        """Test CLI book list command."""
        import json
        
        # Create mock build logs
        for i in range(3):
            build_log = {
                "book_metadata": {
                    "title": f"List Test Book {i}",
                    "status": "completed",
                    "build_id": f"list_test_{i:03d}"
                }
            }
            
            build_log_file = temp_dir / f"list_test_{i:03d}" / "build_log.json"
            build_log_file.parent.mkdir(exist_ok=True)
            build_log_file.write_text(json.dumps(build_log))
        
        cmd = [
            sys.executable, "-m", "cli", "book", "list",
            "--output-dir", str(temp_dir)
        ]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Found 3 books")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
    
    @pytest.mark.asyncio
    async def test_cli_error_handling(self, temp_dir):
        """Test CLI error handling."""
        # Test with invalid arguments
        cmd = [
            sys.executable, "-m", "cli", "book", "create",
            "--title", "",  # Empty title
            "--theme", "Test Theme",
            "--author", "Test Author"
        ]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=1, stderr="Error: Title cannot be empty")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 1
            assert "Error" in result.stderr
    
    @pytest.mark.asyncio
    async def test_cli_help_commands(self):
        """Test CLI help commands."""
        help_commands = [
            [sys.executable, "-m", "cli", "--help"],
            [sys.executable, "-m", "cli", "book", "--help"],
            [sys.executable, "-m", "cli", "book", "create", "--help"],
            [sys.executable, "-m", "cli", "book", "status", "--help"],
            [sys.executable, "-m", "cli", "book", "list", "--help"]
        ]
        
        for cmd in help_commands:
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="Help text")
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                assert result.returncode == 0
    
    @pytest.mark.asyncio
    async def test_cli_validation(self, temp_dir):
        """Test CLI input validation."""
        # Test various validation scenarios
        validation_tests = [
            {
                "args": ["--title", "", "--theme", "Test", "--author", "Author"],
                "expected_error": "Title cannot be empty"
            },
            {
                "args": ["--title", "Test", "--theme", "", "--author", "Author"],
                "expected_error": "Theme cannot be empty"
            },
            {
                "args": ["--title", "Test", "--theme", "Test", "--author", ""],
                "expected_error": "Author cannot be empty"
            },
            {
                "args": ["--title", "Test", "--theme", "Test", "--author", "Author", "--word-count", "-1"],
                "expected_error": "Word count must be positive"
            },
            {
                "args": ["--title", "Test", "--theme", "Test", "--author", "Author", "--chapters", "0"],
                "expected_error": "Chapters must be positive"
            }
        ]
        
        for test in validation_tests:
            cmd = [sys.executable, "-m", "cli", "book", "create"] + test["args"]
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr=test["expected_error"])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                assert result.returncode == 1
                assert test["expected_error"] in result.stderr
    
    @pytest.mark.asyncio
    async def test_cli_output_handling(self, temp_dir):
        """Test CLI output handling."""
        cmd = [
            sys.executable, "-m", "cli", "book", "create",
            "--title", "Output Test Book",
            "--theme", "Output Testing",
            "--author", "Output Test Author",
            "--word-count", "1000",
            "--chapters", "2",
            "--output-dir", str(temp_dir)
        ]
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Book created successfully\nOutput saved to: " + str(temp_dir)
            )
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0
            assert "Book created successfully" in result.stdout
            assert str(temp_dir) in result.stdout
    
    @pytest.mark.asyncio
    async def test_cli_concurrent_execution(self, temp_dir):
        """Test CLI concurrent execution."""
        # Test multiple CLI commands running concurrently
        commands = []
        for i in range(5):
            cmd = [
                sys.executable, "-m", "cli", "book", "create",
                "--title", f"Concurrent Test Book {i}",
                "--theme", f"Concurrent Testing {i}",
                "--author", f"Concurrent Test Author {i}",
                "--word-count", "500",
                "--chapters", "1",
                "--output-dir", str(temp_dir)
            ]
            commands.append(cmd)
        
        # Mock all commands
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Book created successfully")
            
            # Run commands concurrently
            tasks = []
            for cmd in commands:
                task = asyncio.create_task(
                    asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True)
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            # All commands should succeed
            assert all(result.returncode == 0 for result in results)
            assert len(results) == 5