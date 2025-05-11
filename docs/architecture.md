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

The cornerstone of the architecture is the dependency injection container (`services/container.py`), which:

- Manages service lifecycles
- Provides typed interfaces for service access
- Enables substitution of implementations
- Supports testing with provider overrides

```python
# Example: Getting a service through the container
from services.container import get_r_service

r_service = get_r_service()
r_service.execute_script("my_script.R")
```

### Service Registry and Provider Factories

The container includes:

- Factory functions for each provider
- A registry of providers by interface type
- Methods for overriding and resetting providers
- Utility functions for dynamic service resolution

```python
# Dynamic service resolution by interface type
service = get_service_by_interface(KaggleServiceInterface)
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

Test fixtures provide common test setup:

- Mock services for all dependencies
- Container overrides for service substitution
- UI testing utilities