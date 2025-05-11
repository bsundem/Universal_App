# Extending the Dependency Injection Container

This guide explains how to extend the Universal App's dependency injection container with new services. The container has been designed with extensibility in mind, allowing you to easily add new services while maintaining the benefits of Dependency Inversion.

## Container Architecture

The DI container uses a registration-based system where services register themselves with the container. This provides several benefits:

1. **Extensibility**: New services can be added without modifying the container code
2. **Type Safety**: Services are registered with their interface types for type checking
3. **Identity Preservation**: Original service instances are preserved for testing
4. **Dynamic Resolution**: Services can be resolved by interface at runtime

## Registering a New Service

### Step 1: Define Your Service Interface

First, define a Protocol interface for your service in the appropriate file under `services/interfaces/`:

```python
# services/interfaces/my_services.py
from typing import Protocol, Dict, Any

class MyServiceInterface(Protocol):
    """Protocol defining the interface for my service."""
    
    def do_something(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Do something with the provided data.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        ...
```

### Step 2: Implement Your Service

Create your service implementation in a dedicated module:

```python
# services/my_module/my_service.py
from typing import Dict, Any
from utils.error_handling import handle_service_errors

class MyService:
    """Implementation of my service."""
    
    def __init__(self):
        """Initialize the service."""
        self.name = "MyService"
    
    @handle_service_errors("MyService")
    def do_something(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        # Process the data
        result = {"processed": True, "data": data}
        return result

# Create singleton instance
my_service = MyService()
```

### Step 3: Define a Factory Function

Create a factory function for your service provider:

```python
# In the same file or a central factory file
def create_my_service_provider():
    """Factory function for my service provider."""
    return providers.Singleton(lambda: my_service)
```

### Step 4: Register Your Service

Register your service with the container using the registration system:

```python
# In your module's __init__.py or another central location
from services.container import register_service
from services.interfaces.my_services import MyServiceInterface
from services.my_module.my_service import my_service, create_my_service_provider

# Register the service
register_service(
    name='my_service',
    instance=my_service,
    interface_type=MyServiceInterface, 
    factory_fn=create_my_service_provider
)
```

### Step 5: Create an Access Function

Create a helper function to access your service:

```python
# In services/container.py or your module
def get_my_service() -> MyServiceInterface:
    """Get the my service implementation."""
    return container.my_service_provider()
```

## Using Your Service

Now you can use your service through the container:

```python
from services.container import get_my_service

# Get the service
my_service = get_my_service()

# Use the service
result = my_service.do_something({"key": "value"})
```

## Dynamic Service Resolution

You can resolve services dynamically by interface type:

```python
from services.container import get_service_by_interface
from services.interfaces.my_services import MyServiceInterface

# Get the service by interface type
my_service = get_service_by_interface(MyServiceInterface)

# Use the service
result = my_service.do_something({"key": "value"})
```

### Multiple Implementations for the Same Interface

When registering multiple services with the same interface, be aware that the latest registration will be the one returned by `get_service_by_interface()`. This is useful when you want to provide different implementations in different contexts.

For example:

```python
# Register a basic implementation
register_service(
    name='basic_logger',
    instance=basic_logger,
    interface_type=LoggerInterface,
    factory_fn=create_basic_logger_provider
)

# Later register an advanced implementation with the same interface
register_service(
    name='advanced_logger',
    instance=advanced_logger,
    interface_type=LoggerInterface,
    factory_fn=create_advanced_logger_provider
)

# This will return the advanced_logger since it was registered last
logger = get_service_by_interface(LoggerInterface)
```

You can get specific services by using dedicated getter functions:

```python
from services.container import get_basic_logger, get_advanced_logger

# Get specific implementations
basic = get_basic_logger()
advanced = get_advanced_logger()
```

### Getting All Implementations of an Interface

If you need to access all implementations of a particular interface, you can use `get_all_services_by_interface()`:

```python
from services.container import get_all_services_by_interface
from services.interfaces.my_services import LoggerInterface

# Get all logger implementations
loggers = get_all_services_by_interface(LoggerInterface)

# Use specific implementations by name
basic_logger = loggers['basic_logger']
advanced_logger = loggers['advanced_logger']

# Or iterate through all implementations
for name, logger in loggers.items():
    print(f"Using {name}:")
    logger.log("Test message")
```

This is particularly useful for scenarios like:

- Strategy pattern implementations
- Plugin systems where multiple implementations of the same interface exist
- Composite patterns where you need to execute operations across all implementations

## Testing with Your Service

The container makes it easy to test with your service:

```python
from unittest.mock import MagicMock
from services.container import override_provider, reset_overrides
from services.container import get_my_service

def test_with_mock_service():
    # Create a mock implementation
    mock_my_service = MagicMock()
    mock_my_service.do_something.return_value = {"mocked": True}
    
    try:
        # Override the service provider
        override_provider("my_service", mock_my_service)
        
        # Get the service - will be our mock
        service = get_my_service()
        
        # Use the service
        result = service.do_something({"test": "data"})
        
        # Assert the mock was called correctly
        mock_my_service.do_something.assert_called_once_with({"test": "data"})
        assert result == {"mocked": True}
        
    finally:
        # Reset all overrides to not affect other tests
        reset_overrides()
```

## Complete Example

Here's a complete example of adding a new service to the container:

```python
# services/interfaces/weather_services.py
from typing import Protocol, Dict, Any

class WeatherServiceInterface(Protocol):
    """Protocol defining the interface for weather services."""
    
    def get_forecast(self, location: str) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: Location name or coordinates
            
        Returns:
            Weather forecast data
        """
        ...

# services/weather/weather_service.py
from typing import Dict, Any
from utils.error_handling import handle_service_errors
from services.interfaces.weather_services import WeatherServiceInterface

class WeatherService:
    """Service for retrieving weather information."""
    
    def __init__(self):
        """Initialize the weather service."""
        self.api_key = "your_api_key"
        
    @handle_service_errors("Weather")
    def get_forecast(self, location: str) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: Location name or coordinates
            
        Returns:
            Weather forecast data
        """
        # In a real implementation, this would call a weather API
        return {
            "location": location,
            "forecast": [
                {"day": "Monday", "temp": 72, "condition": "Sunny"},
                {"day": "Tuesday", "temp": 68, "condition": "Cloudy"}
            ]
        }

# Create singleton instance
weather_service = WeatherService()

# Define factory function
def create_weather_service_provider():
    """Factory function for weather service provider."""
    from dependency_injector import providers
    return providers.Singleton(lambda: weather_service)

# Register with the container
from services.container import register_service
register_service(
    name='weather_service',
    instance=weather_service,
    interface_type=WeatherServiceInterface,
    factory_fn=create_weather_service_provider
)

# Add helper function to container.py
from services.interfaces.weather_services import WeatherServiceInterface
def get_weather_service() -> WeatherServiceInterface:
    """Get the weather service implementation."""
    return container.weather_service_provider()
```

## Error Handling

The registration system includes robust error handling to prevent common issues:

### Registration Errors

When registering services, these errors might occur:

1. **Duplicate Service Name**: If you try to register a service with a name that's already registered, a `ValueError` will be raised. This prevents accidentally overwriting existing services.

    ```python
    # This will raise ValueError: "Service 'my_service' already registered"
    register_service('my_service', another_instance, MyInterface, factory_fn)
    ```

2. **Provider Access Errors**: If you try to access a provider that doesn't exist, appropriate errors will be raised to help you identify the issue.

### Testing Support

The reset functions are designed to be robust and handle edge cases:

- `reset_overrides()` safely resets all registered providers
- `reset_single_provider(service_name)` resets a specific provider
- Both functions handle the case where a service is registered but the provider doesn't exist

## Best Practices

When extending the container:

1. **Always define interfaces**: Create Protocol interfaces for all services
2. **Use singleton instances**: Create a singleton instance for each service
3. **Register explicitly**: Always register services explicitly with the container
4. **Follow naming conventions**: Use consistent naming patterns for service names
5. **Document your services**: Add clear docstrings to interfaces and implementations
6. **Test with mocks**: Use the override_provider mechanism for testing
7. **Handle special cases**: Use the ServiceRegistry to handle special service resolution cases
8. **Clean up in tests**: Always reset overrides in tests to prevent test pollution