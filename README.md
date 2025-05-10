# Universal App

A unified application framework that hosts multiple projects in a single interface. This repository serves as a container for various projects until they grow large enough to be moved into their own repositories.

## Features

- Unified navigation system
- Modular project architecture
- Tkinter-based GUI (part of Python standard library)

## Project Structure

```
Universal_App/
├── core/             # Core application functionality
├── ui/               # User interface components
│   ├── components/   # Reusable UI components
│   └── pages/        # Application pages
└── utils/            # Utility functions and helpers
```

## Setup

### Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running the Application

#### Method 1: Using run.py
```bash
python run.py
```

#### Method 2: After installing the package
```bash
universal-app
```

## Development

### Adding New Projects

To add a new project module to the application:

1. Create a new page in `ui/pages/` (inherit from `BasePage`)
2. Add the page to the `MainWindow.setup_pages()` method in `ui/main_window.py`
3. Add a navigation button in the `Sidebar._setup_navigation()` method in `ui/components/sidebar.py`

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting

Run formatting and linting:
```bash
black core ui utils
flake8 core ui utils
```

### Testing

```bash
pytest
```