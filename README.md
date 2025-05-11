# Universal App

A unified application framework that hosts multiple projects in a single interface. This repository serves as a container for various projects until they grow large enough to be moved into their own repositories.

## Features

- Unified navigation system
- Modular project architecture
- Tkinter-based GUI (part of Python standard library)
- Service-oriented architecture with clean interfaces
- R integration for specialized calculations
- Kaggle data exploration capabilities
- Comprehensive testing framework
- Configuration management system
- Structured error handling
- Consistent logging strategy
- Implementation of SOLID design principles

## Project Structure

```
Universal_App/
├── config.json.template     # Configuration template
├── core/                    # Core application functionality
│   ├── app.py               # Main application class
│   └── config.py            # Configuration management
├── services/                # Business logic services
│   ├── actuarial/           # Actuarial calculation services
│   ├── interfaces/          # Service interfaces (ISP)
│   ├── kaggle/              # Kaggle data services
│   ├── container.py         # Dependency injection container (DIP)
│   ├── provider.py          # Legacy service provider (being replaced)
│   └── r_service.py         # R integration service
├── r_scripts/               # R scripts for specialized calculations
│   ├── actuarial/           # Actuarial R scripts
│   └── common/              # Common R utilities
├── tests/                   # Testing framework
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── functional/          # Functional tests
├── ui/                      # User interface components
│   ├── components/          # Reusable UI components
│   │   └── page_container.py # Page container (composition)
│   └── pages/               # Application pages
│       ├── content_page.py  # Base content page using composition
│       ├── home_page.py     # Home page
│       ├── kaggle_page.py   # Kaggle data explorer page
│       ├── actuarial_page.py # Actuarial calculations page
│       ├── settings_page.py # Settings page
│       └── example_page.py  # Example page demonstrating composition
└── utils/                   # Utility functions and helpers
    ├── error_handling.py    # Standardized error handling
    └── logging.py           # Logging strategy
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

### Optional Dependencies

For full functionality, the following optional packages can be installed:

- **R Integration**: Install R and the rpy2 package
  ```bash
  # Install R from https://cran.r-project.org/
  # Then install the Python interface
  pip install rpy2
  ```

- **Data Analysis**: For Kaggle data exploration and visualization
  ```bash
  pip install pandas matplotlib kaggle
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

1. Create a new page in `ui/pages/` using the `ContentPage` class as the base
2. Add any required business logic in the `services/` directory
3. Create interfaces for your services in `services/interfaces/`
4. Add the page to the `MainWindow.setup_pages()` method in `ui/main_window.py`
5. Add a navigation button in the `Sidebar._setup_navigation()` method in `ui/components/sidebar.py`

The application exclusively uses the composition pattern for page creation, which provides better flexibility and testability than inheritance.

### Services Architecture

The application follows a service-oriented architecture with interfaces:

1. UI components should delegate business logic to services
2. Services are organized by domain (e.g., `actuarial`, `kaggle`)
3. Service interfaces define contracts in `services/interfaces/`
4. Cross-cutting concerns have dedicated services (e.g., `r_service.py`)
5. Services are accessed through a dependency injection container to enforce the Dependency Inversion Principle
6. Error handling is standardized through the error handling utilities
7. Logging is consistent across all services

#### Dependency Injection Container

The application uses a proper dependency injection container to implement the Dependency Inversion Principle:

```python
from services.container import get_r_service, get_actuarial_service

# Get service implementations through the container
r_service = get_r_service()
actuarial_service = get_actuarial_service()

# Use services through their interfaces
if r_service.is_available():
    # Do something with the R service
```

This ensures that components depend on abstractions (interfaces/protocols) rather than concrete implementations.

#### Testing with the Container

For testing, the container provides utilities to override service implementations with mocks:

```python
from services.container import override_provider, reset_overrides
from unittest.mock import MagicMock

# Create a mock implementation
mock_r_service = MagicMock()
mock_r_service.is_available.return_value = True

# Override the service for testing
override_provider("r_service", mock_r_service)

# Run tests with the mock service

# Reset all overrides when done
reset_overrides()
```

This makes it easy to test components in isolation without dependencies on actual implementations.

### Design Principles

The application implements SOLID design principles:

1. **Single Responsibility Principle**: Each class has one responsibility
2. **Open/Closed Principle**: Classes are open for extension but closed for modification
3. **Liskov Substitution Principle**: Subtypes must be substitutable for their base types
4. **Interface Segregation Principle**: Clients shouldn't depend on methods they don't use
5. **Dependency Inversion Principle**: High-level modules depend on abstractions, not implementations
   - Interfaces defined as protocols in `services/interfaces/`
   - Service provider mechanism in `services/provider.py`
   - Components request services by interface rather than importing concrete implementations

Additionally, the application follows:

1. **Composition Over Inheritance**: Using composition (e.g., `PageContainer`) instead of inheritance
2. **Dependency Injection**: Services are injected into classes that need them
3. **Separation of Concerns**: UI, business logic, and data access are separated

### R Integration

For R-based calculations:

1. Place R scripts in the `r_scripts/` directory
2. Use the `r_service` to execute R code and exchange data
3. Create domain-specific services that use the R service

### Configuration Management

The application uses a centralized configuration system:

1. **Configuration Sources**:
   - Default values defined in config.py
   - Environment variables (e.g., `APP_LOGGING_LEVEL=DEBUG`)
   - Configuration files (searched for in standard locations)

2. **Creating a Configuration File**:
   ```bash
   # Copy the template
   cp config.json.template config.json

   # Edit as needed
   nano config.json
   ```

3. **Configuration Sections**:
   - `app`: General application settings
   - `logging`: Logging configuration
   - `r`: R integration settings
   - `kaggle`: Kaggle API settings

### Error Handling

The application uses a standardized error handling approach:

1. **Error Classes**:
   - `AppError`: Base exception class
   - `ServiceError`: For service-related errors
   - `ValidationError`: For input validation
   - `DataError`: For data-related issues
   - `ConfigurationError`: For configuration problems

2. **Using Error Handling**:
   ```python
   from utils.error_handling import ServiceError, handle_service_errors

   @handle_service_errors("MyService")
   def my_function():
       # Function body
       if error_condition:
           raise ServiceError("Error message", "service", "operation")
   ```

### Logging System

The application includes a comprehensive logging system:

1. **Getting a Logger**:
   ```python
   from utils.logging import get_logger

   logger = get_logger(__name__)
   logger.info("This is an info message")
   logger.error("This is an error message")
   ```

2. **Logging Context**:
   ```python
   from utils.logging import LoggingContext

   with LoggingContext(logger, user_id="123", action="login"):
       logger.info("User action")  # Will include user_id and action in log
   ```

3. **Logging Function Calls**:
   ```python
   from utils.logging import log_function_call

   @log_function_call()
   def my_function():
       # Function body
   ```

### Testing Framework

The project includes a comprehensive testing framework:

1. **Unit Tests**: Test individual components in isolation
   ```bash
   # Run all unit tests
   pytest tests/unit

   # Run unit tests for specific components
   pytest tests/unit/services
   ```

2. **Integration Tests**: Test interactions between components
   ```bash
   pytest tests/integration
   ```

3. **Functional Tests**: Test the system from a user perspective
   ```bash
   pytest tests/functional
   ```

4. **Test Categories**: Tests are categorized with markers
   ```bash
   # Run only tests that require R
   pytest -m r_dependent

   # Skip tests that require R
   pytest -k "not r_dependent"
   ```

For more details on the testing framework, see the [tests README](tests/README.md).

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting
- Type annotations throughout

Run formatting and linting:
```bash
black core ui utils services r_scripts tests
flake8 core ui utils services tests
```