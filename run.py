#!/usr/bin/env python3
"""
Universal App entry point script.

This is the main entry point for launching the Universal App.
It initializes the application with proper configuration and runs it.
"""
import sys
import os
import logging

# Add the project root directory to the Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

from core.app import Application

if __name__ == "__main__":
    # Setup basic logging (will be configured properly by the app)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    # Create and start application
    app = Application()
    sys.exit(app.run())