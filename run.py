#!/usr/bin/env python3
"""
Main entry point for the Book Writing System.

This script provides a unified entry point for both CLI and GUI interfaces.
"""

import sys
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Book Writing System - AI-powered non-fiction book creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --cli                    # Run CLI interface
  python run.py --gui                    # Run GUI interface
  python run.py --cli init               # Initialize system via CLI
  python run.py --cli book create "My Book" --author "John Doe"
        """
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true', 
        help='Run CLI interface'
    )
    parser.add_argument(
        '--gui', 
        action='store_true', 
        help='Run GUI interface'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Book Writing System 1.0.0'
    )
    
    # Parse arguments
    args, remaining_args = parser.parse_known_args()
    
    if args.cli:
        # Import and run CLI
        from cli import main as cli_main
        sys.argv = ['run.py'] + remaining_args
        cli_main()
        
    elif args.gui:
        # Import and run GUI
        try:
            from gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"GUI not available: {e}")
            print("Please install PyQt6 to use the GUI interface.")
            sys.exit(1)
            
    else:
        # Default to CLI
        from cli import main as cli_main
        cli_main()

if __name__ == '__main__':
    main()