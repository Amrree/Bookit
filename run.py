#!/usr/bin/env python3
"""
Main entry point for the Enhanced Book Writing System.

This script provides a unified entry point for both CLI and GUI interfaces
with all new features including templates, style guides, and advanced export.
"""

import sys
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Book Writing System - AI-powered non-fiction book creation with templates, style guides, and advanced export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --cli                    # Run CLI interface
  python run.py --gui                    # Run GUI interface
  python run.py --cli init               # Initialize system via CLI
  python run.py --cli book create "My Book" --author "John Doe" --template "business_white_paper"
  python run.py --cli template list      # List available templates
  python run.py --cli style list         # List available style guides
  python run.py --cli export --book-id BOOK_ID --formats pdf,docx,epub
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
        '--enhanced',
        action='store_true',
        help='Run enhanced system with all new features'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Enhanced Book Writing System 2.0.0'
    )
    
    # Parse arguments
    args, remaining_args = parser.parse_known_args()
    
    if args.enhanced:
        # Run enhanced system
        try:
            import asyncio
            from enhanced_system import main as enhanced_main
            asyncio.run(enhanced_main())
        except ImportError as e:
            print(f"Enhanced system not available: {e}")
            print("Please ensure all dependencies are installed.")
            sys.exit(1)
    
    elif args.cli:
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