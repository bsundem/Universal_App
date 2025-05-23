# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository serves as a container for multiple projects. It provides a universal application that hosts different projects in a single interface using a service-oriented architecture with clean interfaces and following SOLID design principles.

## Project Structure

- `.venv/`: Python virtual environment directory
- `.vscode/`: VSCode configuration
- `config.json`: Main configuration file
- `config.json.template`: Configuration template file
- `core/`: Core application functionality
  - `app.py`: Main application class
  - `config.py`: Configuration management system with Pydantic
- `services/`: Business logic services
  - `actuarial/`: Actuarial calculation services
  - `finance/`: Financial calculation services
  - `interfaces/`: Service interfaces (Interface Segregation Principle)
  - `container.py`: Dependency injection container (Dependency Inversion Principle)
  - `r_service.py`: R integration service
- `r_scripts/`: R scripts for specialized calculations
  - `actuarial/`: Actuarial R scripts (mortality tables, present value, etc.)
  - `finance/`: Finance R scripts (yield curves, option pricing, etc.)
  - `common/`: Common R utilities
- `tests/`: Testing framework
  - `unit/`: Unit tests for individual components
  - `integration/`: Tests for component interactions
  - `functional/`: End-to-end and UI tests
  - `conftest.py`: Shared pytest fixtures
- `ui/`: User interface components
  - `components/`: Reusable UI components
    - `page_container.py`: Page container component (Composition over Inheritance)
    - `sidebar.py`: Navigation sidebar component
  - `pages/`: Application pages
    - `home_page.py`: Application home page
    - `actuarial_page.py`: Actuarial calculations page
    - `finance_page.py`: Financial calculations page
    - `settings_page.py`: Application settings page
  - `main_window.py`: Main application window
- `utils/`: Utility functions and helpers
  - `error_handling.py`: Standardized error handling system
  - `logging.py`: Logging strategy implementation
- `requirements.txt`: Python dependencies (all required)
- `run.py`: Executable entry point script

## Development Environment

This is a Python-based project using ttkbootstrap (modern Tkinter) for the GUI with the following environment setup:
- Python virtual environment (`.venv/`)
- VSCode as the editor (`.vscode/`)
- Dependency-injector for service management
- ttkbootstrap for modern UI components
- R integration via rpy2
- Pandas and Matplotlib for data analysis
- Pydantic for configuration validation
- Pytest for testing with DI container support

## Setup and Running

### Installation
```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate     # Windows

# Install all dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Using run.py script
python run.py
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
     - Pages shown/hidden based on navigation
     - Includes standard header, footer, and loading indicators

2. **Service Layer**:
   - Service interfaces in `services/interfaces/` define contracts as protocols
   - Domain-specific services in the `services/` directory implement interfaces
   - Dependency injection container in `services/container.py` manages services
   - Service retrieval through container via `get_*_service()` functions
   - Each service provides business logic for a specific domain
   - Services should be stateless when possible
   - UI components call services through the container
   - Error handling is standardized via the error handling system

3. **External Integrations**:
   - R integration via `r_service.py` (implements RServiceInterface)
   - R scripts stored in the `r_scripts/` directory
   - Common utilities for both R scripts and Python services

4. **Application Core**:
   - `Application` class in `core/app.py` manages application lifecycle
   - Centralized configuration via `config.py` using Pydantic models
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
   - Test fixtures for common testing scenarios in `conftest.py`
   - Mock services via the DI container's `override_provider` mechanism
   - UI component testing with mocked service dependencies

## Adding New Projects

To add a new project module to the application:

1. **Define Service Interfaces**:
   - Create protocol classes in `services/interfaces/`
   - Define clear method signatures with proper type hints
   - Split large interfaces into smaller, focused ones (ISP)

2. **Implement Services**:
   - Create service implementations in a dedicated directory under `services/`
   - Implement all methods defined in the interfaces
   - Use error handling decorators for consistent error management
   - Add logging throughout using the logging utility

3. **Register with DI Container**:
   - Add service to the container in `services/container.py`
   - Create helper functions for retrieving the service
   - Ensure singleton behavior if appropriate

4. **Create UI Components**:
   - Add a new page class in `ui/pages/`
   - Retrieve services via the container in the constructor
   - Follow the composition pattern for UI elements
   - Delegate business logic to services

5. **Add Navigation**:
   - Add the page to `MainWindow.setup_pages()` method
   - Add a navigation button in `Sidebar._setup_navigation()`
   - Update page mapping for navigation by name

6. **Write Tests**:
   - Create unit tests with mocked services using the container
   - Add test fixtures for the new services in `conftest.py` if needed
   - Test the UI components with mocked services
   - Add integration tests for service interactions

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
   - `container`: Tests that use the dependency injection container
   - `r_dependent`: Tests requiring R installation
   - `slow`: Tests that take a long time to run

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
   - UI components depend on service interfaces, not concrete classes
   - Dependency injection container manages service instances
   - Services are accessed via their interfaces through the container
   - UI components get services through helper functions like `get_r_service()`
   - Mock implementations can be easily swapped in for testing

Additional architectural principles:

6. **Composition Over Inheritance**:
   - Use composition to share functionality
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
   - Code is designed with testing in mind
   - DI container facilitates service mocking via `override_provider`
   - Test fixtures provide standardized mock services
   - UI components can be tested with mocked services
   - Interfaces enable precise contract verification
   - Container-based tests ensure loose coupling

## Current Modules

The application currently includes the following modules:

1. **Core Application**: Basic application framework with configuration system

2. **Actuarial Module**:
   - Mortality table calculations
   - Present value calculations
   - Life expectancy projections
   - Visualizations for actuarial data

3. **Finance Module**:
   - Yield curve calculations
   - Option pricing models
   - Portfolio metrics
   - Financial visualization tools

## Future Direction

As the project expands:

1. Create dedicated modules for additional domain-specific projects
2. Update the navigation system to include new projects
3. Consider implementing a plugin architecture for more complex projects
4. Expand the testing framework as needed
5. Further improve these architectural components:
   - Enhance the dependency injection container with more features
   - Create a comprehensive event system for inter-service communication
   - Add more sophisticated caching mechanisms
   - Expand the R script integration capabilities
   - Add more visualization options using Matplotlib and other libraries
   - Implement a plugin architecture for dynamic module loading
   - Add automated UI testing