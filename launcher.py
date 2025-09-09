#!/usr/bin/env python3
"""
BookWriter Pro Launcher

Simple launcher that works with minimal dependencies and provides
multiple interface options.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_basic_dependencies():
    """Check for basic dependencies."""
    basic_modules = ['tkinter', 'json', 'pathlib', 'datetime']
    missing = []
    
    for module in basic_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print("Missing basic dependencies:")
        for module in missing:
            print(f"  - {module}")
        return False
    
    return True

def run_stitch_like_gui():
    """Run the Stitch-like GUI interface."""
    try:
        from gui.stitch_like_app import main
        print("Starting Stitch-like GUI...")
        main()
        return True
    except ImportError as e:
        print(f"Failed to import GUI modules: {e}")
        return False
    except Exception as e:
        print(f"GUI startup failed: {e}")
        return False

def run_integrated_system():
    """Run the integrated system CLI."""
    try:
        from integrated_system import main
        print("Starting Integrated System...")
        main()
        return True
    except ImportError as e:
        print(f"Failed to import system modules: {e}")
        return False
    except Exception as e:
        print(f"System startup failed: {e}")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("✗ pip not found. Please install pip first.")
        return False

def main():
    """Main launcher function."""
    print("BookWriter Pro Launcher")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check basic dependencies
    if not check_basic_dependencies():
        print("\nSome basic dependencies are missing.")
        print("This might be due to a minimal Python installation.")
        print("Please ensure you have a full Python installation.")
        return 1
    
    # Show menu
    while True:
        print("\nAvailable options:")
        print("1. Run Stitch-like GUI (Recommended)")
        print("2. Run Integrated System CLI")
        print("3. Install Dependencies")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\nStarting Stitch-like GUI...")
            if run_stitch_like_gui():
                break
            else:
                print("GUI failed to start. Try option 2 or 3.")
        
        elif choice == "2":
            print("\nStarting Integrated System...")
            if run_integrated_system():
                break
            else:
                print("System failed to start.")
        
        elif choice == "3":
            if install_dependencies():
                print("Dependencies installed. You can now try option 1.")
            else:
                print("Failed to install dependencies.")
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)