# Services Directory

This directory contains service modules that implement the business logic for the Universal App.

## Purpose

The services in this directory follow the service-oriented architecture pattern, providing clear separation between UI components and business logic. Each service is responsible for a specific domain or cross-cutting concern.

## Architecture Principles

1. **Separation of Concerns**: Services contain business logic, while UI components handle presentation
2. **Single Responsibility**: Each service has a focused purpose
3. **Statelessness**: Services should be stateless when possible
4. **Reusability**: Services can be reused across different UI components

## Directory Structure

- `actuarial/`: Services for actuarial calculations
  - `actuarial_service.py`: Service for mortality tables and present value calculations
- `kaggle/`: Services for Kaggle data interaction
  - `kaggle_service.py`: Service for searching, downloading, and processing Kaggle datasets
- `r_service.py`: Service for R integration and executing R scripts

## Using Services

Services should be accessed through the dependency injection container to maintain proper dependency inversion:

```python
# Example: Using the Kaggle service through the container
from services.container import get_kaggle_service

# Get the service through the container
kaggle_service = get_kaggle_service()

# Use the service
datasets = kaggle_service.search_datasets(search_term="machine learning")
```

You can also access services by their interface type:

```python
# Using interface-based resolution
from services.container import get_service_by_interface
from services.interfaces.domain_services import KaggleServiceInterface

# Get by interface
kaggle_service = get_service_by_interface(KaggleServiceInterface)
```

## Adding New Services

When adding new services:

1. Create a new directory for domain-specific services
2. Define an interface Protocol in the `interfaces/` directory
3. Implement the service class with clear responsibilities
4. Export a singleton instance for registration
5. Create a factory function for the service provider
6. Register the service with the container using `register_service()`
7. Add a helper function to access the service
8. Use type hints for better code readability
9. Document the public methods and their parameters

```python
# Example: Registering a new service
from services.container import register_service
from services.interfaces.my_interface import MyServiceInterface

# Create singleton instance
my_service = MyService()

# Define factory function
def create_my_service_provider():
    from dependency_injector import providers
    return providers.Singleton(lambda: my_service)

# Register with container
register_service(
    name='my_service',
    instance=my_service,
    interface_type=MyServiceInterface,
    factory_fn=create_my_service_provider
)
```

## Dependencies

Services should follow these dependency rules:

1. Services should depend on interfaces, not concrete implementations
2. Services can depend on other services through the container
3. Services should not depend on UI components
4. UI components should depend on services through the container
5. Service implementations should be accessed via the DI container
6. Cross-cutting services (like `r_service.py`) should be used by domain-specific services

```python
# Example: A service depending on another service
class MyService:
    def __init__(self):
        # Get dependency through container
        from services.container import get_r_service
        self.r_service = get_r_service()

    def process_data(self, data):
        # Use dependency through its interface
        if self.r_service.is_available():
            return self.r_service.call_function("analyze", data)
```

## Configuration

Services that require configuration should:

1. Accept configuration parameters in their constructor
2. Provide sensible defaults when possible
3. Document required configuration