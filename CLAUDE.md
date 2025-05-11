# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository serves as a container for multiple projects until they grow large enough to be moved into their own repositories. It provides a universal application that hosts different projects in a single interface using a service-oriented architecture.

## Project Structure

- `.venv/`: Python virtual environment directory
- `.vscode/`: VSCode configuration
- `core/`: Core application functionality
- `services/`: Business logic services
  - `actuarial/`: Actuarial calculation services
  - `kaggle/`: Kaggle data services
  - `r_service.py`: R integration service
- `r_scripts/`: R scripts for specialized calculations
  - `actuarial/`: Actuarial R scripts
  - `common/`: Common R utilities
- `tests/`: Testing framework
  - `unit/`: Unit tests for individual components
  - `integration/`: Tests for component interactions
  - `functional/`: End-to-end and UI tests
  - `conftest.py`: Shared pytest fixtures
- `ui/`: User interface components
  - `components/`: Reusable UI components
  - `pages/`: Application pages
- `utils/`: Utility functions and helpers
- `requirements.txt`: Python dependencies (for development)
- `setup.py`: Package setup configuration
- `run.py`: Executable entry point script
- `pytest.ini`: Configuration for the pytest framework

## Development Environment

This is a Python-based project using Tkinter for the GUI with the following environment setup:
- Python virtual environment (`.venv/`)
- VSCode as the editor (`.vscode/`)
- Tkinter for GUI components (part of Python standard library)
- R integration via rpy2 (optional)
- Pandas, Matplotlib for data analysis (optional)
- Black for code formatting
- Flake8 for linting
- Pytest for testing

## Setup and Running

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the application (method 1)
python run.py

# Run the application (method 2, after installing)
universal-app
```

## Application Architecture

The application follows a clean architecture pattern with clear separation of concerns:

1. **User Interface Layer**:
   - `MainWindow`: The primary container class (in `ui/main_window.py`)
     - Contains a sidebar for navigation and a content frame
     - Manages page transitions
   - `Sidebar`: Navigation component (in `ui/components/sidebar.py`)
     - Left sidebar with navigation buttons for different projects/sections
     - Uses callback to notify when navigation items are selected
   - Page System:
     - `BasePage`: Base class for all pages (in `ui/pages/base_page.py`)
     - Specialized page classes for each section (in `ui/pages/`)
     - Pages are shown/hidden based on navigation

2. **Service Layer**:
   - Domain-specific services in the `services/` directory
   - Each service provides business logic for a specific domain
   - Services should be stateless when possible
   - UI components call services to perform business operations

3. **External Integrations**:
   - R integration via `r_service.py`
   - R scripts stored in the `r_scripts/` directory
   - External APIs accessed through appropriate services (e.g., Kaggle API)

4. **Application Core**:
   - `Application` class in `core/app.py` manages application lifecycle
   - Centralized configuration and initialization

5. **Testing Layer**:
   - Unit tests for isolated component testing
   - Integration tests for component interactions
   - Functional tests for end-to-end workflows
   - Mock objects for isolating tests from external dependencies

## Adding New Projects

To add a new project module to the application:

1. Create a new page class in `ui/pages/` (inherit from `BasePage`)
2. Create any required services in the `services/` directory
3. Add the page to the `MainWindow.setup_pages()` method in `ui/main_window.py`
4. Add a navigation button in the `Sidebar._setup_navigation()` method in `ui/components/sidebar.py`
5. Add appropriate tests in the `tests/` directory

## Development Workflow

1. Make changes to the codebase
2. Write tests for new functionality
3. Run tests: `pytest`
4. Format code: `black core ui utils services r_scripts tests`
5. Run linting: `flake8 core ui utils services tests`

## Testing Approach

The project uses pytest for testing with different test categories:

1. **Unit Tests** (`tests/unit/`):
   - Test individual components in isolation
   - Mock all dependencies
   - Should be fast and reliable

2. **Integration Tests** (`tests/integration/`):
   - Test interactions between components
   - May use partial mocking
   - Focus on component interfaces

3. **Functional Tests** (`tests/functional/`):
   - Test complete workflows
   - Focus on user perspective
   - May involve UI testing

4. **Test Markers**:
   - `unit`: Unit tests
   - `integration`: Integration tests
   - `functional`: Functional tests
   - `r_dependent`: Tests requiring R installation
   - `slow`: Tests that take a long time to run
   - `network`: Tests requiring network access

## Design Principles

1. **Separation of Concerns**:
   - UI components should not contain business logic
   - Business logic should be in services
   - Services should not depend on UI components

2. **Dependency Inversion**:
   - Higher-level modules (UI) should not depend on implementation details of lower-level modules
   - Both should depend on abstractions

3. **Single Responsibility**:
   - Each class and module should have a single responsibility
   - Services should focus on specific domains

4. **Testability**:
   - Code should be designed with testing in mind
   - Use dependency injection to facilitate mocking
   - Avoid tight coupling between components

## Future Direction

As projects are added to this repository:
1. Create dedicated modules for each project
2. Update the navigation system to include new projects
3. Consider implementing a plugin architecture for more complex projects
4. Add proper dependency injection for services
5. Expand the testing framework as needed