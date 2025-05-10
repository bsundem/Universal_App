#!/usr/bin/env python3
"""
Universal App entry point script.
"""
import sys
import os

# Add the project root directory to the Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

from core.app import create_app

if __name__ == "__main__":
    app = create_app()
    sys.exit(app.run())