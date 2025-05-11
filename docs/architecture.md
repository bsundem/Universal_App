# Architecture Overview

This document provides a comprehensive overview of the Universal App architecture, focusing on the key design principles and patterns used throughout the codebase.

## Architectural Principles

The Universal App is built on several key architectural principles:

### SOLID Design Principles

- **Single Responsibility Principle (SRP)**: Each class has a single responsibility (e.g., separate service and data manager classes)
- **Open/Closed Principle (OCP)**: Classes are open for extension but closed for modification (e.g., using Protocol-based interfaces)
- **Liskov Substitution Principle (LSP)**: Implementations are substitutable for their interfaces (e.g., mock services in tests)
- **Interface Segregation Principle (ISP)**: Clients depend only on the interfaces they use (e.g., focused service interfaces)
- **Dependency Inversion Principle (DIP)**: High-level modules depend on abstractions (e.g., dependency injection container)

### Clean Architecture

- Clear separation of UI, services, and utilities
- Dependency flow from outer layers (UI) to inner layers (services)
- Domain-specific interfaces for clear boundaries

### Composition Over Inheritance

- UI components built using composition rather than inheritance
- PageContainer pattern for consistent UI components
- Service composition through dependency injection

## High-Level Structure

The application is organized into several main components:

```
Universal_App/
├── core/             # Core application functionality
├── services/         # Business logic services
│   ├── adapters/     # Adapters for service compatibility
│   └── interfaces/   # Service interfaces (protocols)
├── ui/               # User interface components
│   ├── components/   # Reusable UI components
│   └── pages/        # Application pages
└── utils/            # Utility functions and helpers
```

## Core Components

### Dependency Injection Container

The cornerstone of the architecture is the registration-based dependency injection container (`services/container.py`), which:

- Manages service lifecycles through a service registry
- Provides typed interfaces for service access
- Supports dynamic service registration
- Enables interface-based service resolution
- Handles multiple implementations of the same interface
- Maintains service identity through tests
- Supports provider overrides for testing

```python
# Direct service access
from services.container import get_r_service
r_service = get_r_service()
r_service.execute_script("my_script.R")

# Interface-based resolution
from services.container import get_service_by_interface
from services.interfaces.r_service import RServiceInterface
r_service = get_service_by_interface(RServiceInterface)

# Working with multiple implementations
from services.container import get_all_services_by_interface
from services.interfaces.logging import LoggerInterface
loggers = get_all_services_by_interface(LoggerInterface)
for name, logger in loggers.items():
    logger.log("Using multiple implementations")
```

### ServiceRegistry and Dynamic Registration

The container includes a full registration system:

- `ServiceRegistry`: Class for tracking service metadata
- Registration functions for dynamic service addition
- Factory functions for creating providers
- Interface-to-service mapping for runtime resolution
- Methods for overriding and resetting providers

```python
# Registering a new service
from services.container import register_service

# Define factory function
def create_service_provider():
    return providers.Singleton(lambda: my_service)

# Register with the container
register_service(
    name='my_service',
    instance=my_service,
    interface_type=MyServiceInterface,
    factory_fn=create_service_provider
)
```

### Service Adapters

Adapters provide compatibility layers between different components, such as:

- R service adapter for converter compatibility
- Legacy service provider adapter for backward compatibility

```python
# Example: Adapting R results
from services.adapters.r_adapter import RServiceAdapter

result = r_service.call_function("some_r_function")
adapted_result = RServiceAdapter.adapt_result(result)
```

## User Interface Architecture

### Page Container Pattern

UI components use a composition-based pattern:

- `PageContainer`: Base container with header, content area, and footer
- `ContentPage`: Composition-based page using `PageContainer`
- Pages delegate presentation to the container

```python
class SomePage(ContentPage):
    def __init__(self, parent, controller):
        super().__init__(parent, title="Some Page")
        # Initialize with services from container
        self.service = get_some_service()
    
    def setup_ui(self):
        # Add UI elements to the content frame
        pass
```

### UI Service Integration

Pages integrate with services through the container:

- Services are obtained through the container
- UI components remain decoupled from service implementations
- Callbacks used for asynchronous operations

## Service Layer

### Interface-Based Design

Services are defined through Protocol interfaces:

- `RServiceInterface`: Interface for R language integration
- `KaggleServiceInterface`: Interface for Kaggle API integration
- `ActuarialServiceInterface`: Interface for actuarial calculations

### Domain-Specific Services

Services are organized by domain:

- `actuarial/`: Actuarial calculation services
- `kaggle/`: Kaggle data services
- Core services like `r_service.py`

### Data Managers

Data-specific operations are separated into data managers:

- `ActuarialDataManager`: Data operations for actuarial calculations
- `KaggleDataManager`: Data operations for Kaggle datasets

## Error Handling

The application uses a hierarchical error system:

- `AppError`: Base exception class
- `ServiceError`: For service-level errors
- `ValidationError`: For input validation
- `DataError`: For data-related issues
- `ConfigurationError`: For configuration problems

Error handlers and decorators standardize error processing:

```python
@handle_service_errors("MyService")
def some_service_function():
    # Function will have standardized error handling
    pass
```

## Configuration System

Configuration is managed through a centralized system:

- Multiple sources (environment variables, files, defaults)
- Type validation and conversion
- Hierarchical structure with sections
- Default fallbacks

## Design Patterns Used

The codebase employs several design patterns:

- **Dependency Injection**: For service access and testability
- **Factory Method**: For creating service instances
- **Adapter**: For compatibility between systems (e.g., R adapter)
- **Singleton**: For shared service instances
- **Observer**: For event handling (callbacks)
- **Strategy**: For pluggable implementations
- **Composite**: For UI component composition

## Testing Architecture

The testing framework is designed for comprehensive coverage:

- **Unit Tests**: For testing components in isolation
- **Integration Tests**: For testing component interactions
- **Functional Tests**: For testing complete features

The DI container provides robust testing support:

- **Service Overrides**: Replace real services with mocks
- **Identity Preservation**: Maintain service identity across resets
- **Interface Testing**: Test services by their interface types
- **Multiple Implementation Testing**: Test systems with multiple implementations
- **Reset Capabilities**: Safely reset to original implementations
- **Selective Resets**: Reset specific services while keeping others mocked

```python
# Container testing example
def test_service_interaction(mock_r_service):
    # mock_r_service is automatically injected via fixture
    # and registered with the container

    # Get service from container (it will be our mock)
    r_service = get_r_service()

    # Verify it's our mock
    assert r_service is mock_r_service

    # Interface-based testing
    same_service = get_service_by_interface(RServiceInterface)
    assert same_service is mock_r_service

    # Test with multiple implementations
    mock_r_service.is_available.return_value = True
    assert r_service.is_available() is True
```

Test fixtures provide common test setup:

- Mock services for all dependencies
- Container overrides for service substitution
- UI testing utilities
- Automatic provider reset after tests