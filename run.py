#!/usr/bin/env python3
"""
Main entry point for the Non-Fiction Book-Writing System.

This script provides both CLI and GUI entry points for the system.
"""

import sys
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Non-Fiction Book-Writing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py cli --help                    # Show CLI help
  python run.py gui                           # Start GUI
  python run.py cli init                      # Initialize system
  python run.py cli ingest document file.pdf  # Ingest document
        """
    )
    
    subparsers = parser.add_subparsers(dest='interface', help='Interface to use')
    
    # CLI subcommand
    cli_parser = subparsers.add_parser('cli', help='Use command-line interface')
    cli_parser.add_argument('cli_args', nargs='*', help='CLI arguments')
    
    # GUI subcommand
    gui_parser = subparsers.add_parser('gui', help='Use graphical interface')
    gui_parser.add_argument('--port', type=int, default=8501, help='Port for GUI server')
    gui_parser.add_argument('--host', default='localhost', help='Host for GUI server')
    
    args = parser.parse_args()
    
    if args.interface == 'cli':
        # Import and run CLI
        from cli import cli
        sys.argv = ['cli'] + args.cli_args
        cli()
    
    elif args.interface == 'gui':
        # Import and run GUI
        try:
            import streamlit.web.cli as stcli
            sys.argv = [
                'streamlit', 'run', 'gui.py',
                '--server.port', str(args.port),
                '--server.address', args.host
            ]
            stcli.main()
        except ImportError:
            print("❌ Streamlit not installed. Install with: pip install streamlit")
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()