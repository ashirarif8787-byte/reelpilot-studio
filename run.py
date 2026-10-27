"""
Main Application Entry Point for Social Media Automation & Scheduler App.
Run this script to launch the desktop GUI.
"""
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()
