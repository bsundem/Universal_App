# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository serves as a container for multiple projects until they grow large enough to be moved into their own repositories. It provides a universal application that hosts different projects in a single interface.

## Project Structure

- `.venv/`: Python virtual environment directory
- `.vscode/`: VSCode configuration
- `main.py`: Main application entry point with PySide6 UI
- `requirements.txt`: Python dependencies

## Development Environment

This is a Python-based project using PySide6 for the GUI with the following environment setup:
- Python virtual environment (`.venv/`)
- VSCode as the editor (`.vscode/`)
- PySide6 for GUI components

## Setup and Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Application Architecture

The application uses a sidebar navigation pattern with a stacked widget system:

1. `MainWindow`: The primary container window
   - Contains a sidebar for navigation and a content area
   - Manages page transitions

2. Navigation System:
   - Left sidebar with buttons for different projects/sections
   - Content stack that switches between different pages

## Adding New Projects

To add a new project module to the application:

1. Create a new page/widget for your project
2. Add a navigation button in the sidebar
3. Connect the new page to the content stack

## Future Direction

As projects are added to this repository:
1. Create dedicated modules for each project
2. Update the navigation system to include new projects
3. Consider implementing a plugin architecture for more complex projects