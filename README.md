# Universal App

A unified application framework that hosts multiple projects in a single interface. This repository serves as a container for various projects until they grow large enough to be moved into their own repositories.

## Features

- Unified navigation system
- Modular project architecture
- PySide6-based GUI

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Structure

The application provides a sidebar navigation system that allows switching between different projects/modules. Each project operates within its own section of the application, sharing common UI elements and resources.

## Adding New Projects

To add a new project to the universal app:

1. Create your project's main widget/page
2. Add a navigation entry in the sidebar
3. Connect your project to the main application flow

See the code comments for more detailed instructions on integration.