# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository serves as a container for multiple projects until they grow large enough to be moved into their own repositories. It provides a universal application that hosts different projects in a single interface using a service-oriented architecture with clean interfaces and following SOLID design principles.

## Project Structure

- `.venv/`: Python virtual environment directory
- `.vscode/`: VSCode configuration
- `config.json.template`: Configuration template file
- `core/`: Core application functionality
  - `app.py`: Main application class
  - `config.py`: Configuration management system
- `services/`: Business logic services
  - `actuarial/`: Actuarial calculation services
  - `interfaces/`: Service interfaces (Interface Segregation Principle)
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
    - `page_container.py`: Page container component (Composition over Inheritance)
  - `pages/`: Application pages
    - `base_page.py`: Legacy base page (inheritance approach)
    - `content_page.py`: Modern content page (composition approach)
- `utils/`: Utility functions and helpers
  - `error_handling.py`: Standardized error handling system
  - `logging.py`: Logging strategy implementation
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

The application follows a clean architecture pattern with clear separation of concerns and SOLID principles:

1. **User Interface Layer**:
   - `MainWindow`: The primary container class (in `ui/main_window.py`)
     - Contains a sidebar for navigation and a content frame
     - Manages page transitions
   - `Sidebar`: Navigation component (in `ui/components/sidebar.py`)
     - Left sidebar with navigation buttons for different projects/sections
     - Uses callback to notify when navigation items are selected
   - Page System (using composition):
     - `PageContainer`: Component for page layout (in `ui/components/page_container.py`)
     - `ContentPage`: Uses composition to create pages (in `ui/pages/content_page.py`)
     - Pages are shown/hidden based on navigation

2. **Service Layer**:
   - Service interfaces in `services/interfaces/` define contracts
   - Domain-specific services in the `services/` directory implement interfaces
   - Each service provides business logic for a specific domain
   - Services should be stateless when possible
   - UI components call services to perform business operations
   - Error handling is standardized via the error handling system

3. **External Integrations**:
   - R integration via `r_service.py` (implements RServiceInterface)
   - R scripts stored in the `r_scripts/` directory
   - External APIs accessed through appropriate services (e.g., Kaggle API)

4. **Application Core**:
   - `Application` class in `core/app.py` manages application lifecycle
   - Centralized configuration via `config.py`
   - Configuration loading from multiple sources
   - Logging setup and management

5. **Cross-Cutting Concerns**:
   - Error handling via `utils/error_handling.py`
   - Logging via `utils/logging.py`
   - Configuration management via `core/config.py`

6. **Testing Layer**:
   - Unit tests for isolated component testing
   - Integration tests for component interactions
   - Functional tests for end-to-end workflows
   - Mock objects for isolating tests from external dependencies

## Adding New Projects

To add a new project module to the application:

1. Create a new page class in `ui/pages/`:
   - Use `ContentPage` as the base class (using composition)
   - **Do not** use `BasePage` which is deprecated
2. Create interfaces for your services in `services/interfaces/`
3. Implement the service interfaces in the `services/` directory
4. Use error handling and logging utilities in your services and pages
5. Configure any needed settings in the configuration system
6. Add the page to the `MainWindow.setup_pages()` method in `ui/main_window.py`
7. Add a navigation button in the `Sidebar._setup_navigation()` method in `ui/components/sidebar.py`
8. Add appropriate tests in the `tests/` directory

For an example of creating a page using composition, refer to `ui/pages/example_page.py`.

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

The application implements SOLID design principles:

1. **Single Responsibility Principle**:
   - Each class has one responsibility
   - UI components handle only presentation
   - Services handle only business logic
   - Data managers handle only data transformations

2. **Open/Closed Principle**:
   - Classes are open for extension but closed for modification
   - Service interfaces allow new implementations without changing existing code
   - Decorators like `@handle_service_errors` extend functionality without modification

3. **Liskov Substitution Principle**:
   - Subtypes must be substitutable for their base types
   - Services implementing interfaces must fulfill the interface contract
   - Error handling and logging should work consistently across implementations

4. **Interface Segregation Principle**:
   - Clients shouldn't depend on methods they don't use
   - Service interfaces are focused and specific
   - UI components only use the services they need

5. **Dependency Inversion Principle**:
   - High-level modules depend on abstractions, not implementations
   - UI components depend on service interfaces
   - Services depend on configuration and infrastructure abstractions

Additional architectural principles:

6. **Composition Over Inheritance**:
   - Use composition (e.g., `PageContainer`) to share functionality
   - Favor object composition over class inheritance
   - Enables more flexible designs and avoids inheritance hierarchies

7. **Separation of Concerns**:
   - UI components should not contain business logic
   - Business logic should be in services
   - Services should not depend on UI components
   - Error handling and logging are cross-cutting concerns

8. **Explicit Dependencies**:
   - Dependencies should be explicitly declared
   - Services should receive dependencies rather than create them
   - Configuration should be externalized

9. **Testability**:
   - Code should be designed with testing in mind
   - Use dependency injection to facilitate mocking
   - Avoid tight coupling between components
   - Interfaces enable easy mocking

## Future Direction

As projects are added to this repository:

1. Create dedicated modules for each project
2. Update the navigation system to include new projects
3. Consider implementing a plugin architecture for more complex projects
4. Expand the testing framework as needed
5. Further improve these architectural components:
   - Add a proper dependency injection container
   - Implement a service locator pattern
   - Create a comprehensive event system for inter-service communication
   - Add a transaction management system for multi-step operations
   - Implement robust validation frameworks for inputs and outputs
   - Add more sophisticated caching mechanisms