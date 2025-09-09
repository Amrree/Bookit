#!/usr/bin/env python3
"""
BookWriter Pro - Main Entry Point

Unified entry point for the complete book writing system with modern GUI.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are available."""
    required_modules = [
        'customtkinter',
        'pydantic',
        'tkinter'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required dependencies:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def run_gui():
    """Run the modern GUI application."""
    try:
        from gui.modern_main import ModernBookWriterApp
        
        logger.info("Starting BookWriter Pro GUI...")
        app = ModernBookWriterApp()
        app.run()
        
    except ImportError as e:
        logger.error(f"Failed to import GUI modules: {e}")
        print(f"Error: {e}")
        print("Please ensure all dependencies are installed.")
        return False
    except Exception as e:
        logger.error(f"GUI startup failed: {e}")
        print(f"Error: {e}")
        return False
    
    return True


def run_cli():
    """Run the CLI interface."""
    try:
        from cli.cli import cli
        cli()
    except ImportError as e:
        logger.error(f"Failed to import CLI modules: {e}")
        print(f"Error: {e}")
        return False
    except Exception as e:
        logger.error(f"CLI startup failed: {e}")
        print(f"Error: {e}")
        return False
    
    return True


def run_enhanced():
    """Run the enhanced system."""
    try:
        import asyncio
        from enhanced_system import main as enhanced_main
        asyncio.run(enhanced_main())
    except ImportError as e:
        logger.error(f"Failed to import enhanced system: {e}")
        print(f"Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Enhanced system startup failed: {e}")
        print(f"Error: {e}")
        return False
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="BookWriter Pro - AI-powered book writing system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run GUI interface
  python main.py --cli              # Run CLI interface
  python main.py --enhanced         # Run enhanced system
  python main.py --check-deps       # Check dependencies
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run CLI interface'
    )
    
    parser.add_argument(
        '--enhanced',
        action='store_true',
        help='Run enhanced system'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check dependencies and exit'
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if args.check_deps:
        if check_dependencies():
            print("✓ All dependencies are available")
            return 0
        else:
            return 1
    
    # Check dependencies before running
    if not check_dependencies():
        return 1
    
    # Run appropriate interface
    if args.cli:
        return 0 if run_cli() else 1
    elif args.enhanced:
        return 0 if run_enhanced() else 1
    else:
        # Default to GUI
        return 0 if run_gui() else 1


if __name__ == "__main__":
    sys.exit(main())