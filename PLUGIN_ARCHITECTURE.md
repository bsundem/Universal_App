# Plugin Architecture Implementation

This document outlines the implementation of the plugin architecture in the Universal App and the conversion of core services to use this architecture.

## Overview

The plugin architecture provides a flexible, extensible system for adding new functionality to the application. It allows services to be developed, deployed, and tested independently while maintaining a clean separation of concerns.

Key features of the plugin architecture:
- Dynamic loading of plugin modules
- Service registration with the dependency injection container
- Event-based communication between plugins and the application
- Support for UI plugins that can add pages to the application

## Implemented Components

### 1. Plugin System Core (`services/plugins/base.py`)

- **PluginBase**: Abstract base class for all plugins
- **ServicePlugin**: Base class for service plugins that provide business logic
- **UIPlugin**: Base class for UI plugins that provide user interface components
- **PluginManager**: Class for discovering, loading, and managing plugins

### 2. Plugin Registry (`services/plugins/registry.py`)

- **PluginRegistry**: Registry for managing and activating plugins, integrating them with the dependency injection container

### 3. Event System (`utils/events.py`)

- **EventBus**: Central event dispatcher for the application
- **Event**: Base class for all events in the system
- **Decorators**: `subscribe` and `publish` decorators for event handling

### 4. Plugin Service Implementations

The following services have been converted to plugins:

#### R Service Plugin (`services/plugins/r_service_plugin.py`)
- Provides R integration for statistical and actuarial calculations
- Publishes events when scripts are executed or functions are called

#### Actuarial Service Plugin (`services/plugins/actuarial_service_plugin.py`)
- Implements mortality calculations and present value analysis
- Depends on the R Service plugin

#### Finance Service Plugin (`services/plugins/finance_service_plugin.py`)
- Implements yield curve analysis, option pricing, and portfolio metrics
- Depends on the R Service plugin

### 5. Container Integration

The `services/container.py` file was updated to:
- Provide helper functions that first try to get the plugin version of a service
- Fall back to the traditional service if the plugin is not available
- Use dynamic imports to avoid hard dependencies on service classes

### 6. Application Integration

The `core/app.py` file was updated to:
- Discover and register plugin packages
- Activate core service plugins at startup
- Register UI plugins with the main window

## Usage

### Using Service Plugins

Services can be accessed through the existing helper functions in `services/container.py`:

```python
from services.container import get_r_service, get_actuarial_service, get_finance_service

# These will return the plugin version if available, or fall back to the traditional service
r_service = get_r_service()
actuarial_service = get_actuarial_service()
finance_service = get_finance_service()
```

### Creating a New Plugin

To create a new service plugin:

1. Create a new module in `services/plugins/` (e.g., `my_service_plugin.py`)
2. Define a class that inherits from `ServicePlugin`
3. Implement the required methods
4. Register the plugin package in `core/app.py`

Example:

```python
from services.plugins.base import ServicePlugin
from utils.events import Event, event_bus

class MyServicePlugin(ServicePlugin):
    # Plugin metadata
    plugin_id = "my_service"
    plugin_name = "My Service"
    plugin_version = "1.0.0"
    plugin_description = "Provides my custom functionality"
    
    def _initialize(self) -> bool:
        # Initialize the plugin
        return True
        
    def _shutdown(self) -> None:
        # Clean up resources
        pass
        
    def my_method(self) -> str:
        # Plugin functionality
        return "Hello from my service!"
```

## Benefits of the Plugin Architecture

1. **Loose Coupling**: Services are no longer tightly coupled to each other or the UI
2. **Dynamic Loading**: Plugins can be loaded and unloaded at runtime
3. **Event-Based Communication**: Services can communicate without direct dependencies
4. **Testability**: Plugins can be tested in isolation
5. **Extensibility**: New functionality can be added without modifying existing code
6. **Separation of Concerns**: Each plugin is responsible for a single domain

## Next Steps

1. Convert more components to plugins as needed
2. Consider implementing a plugin marketplace
3. Add configuration UI for enabling/disabling plugins
4. Create automated tests for the plugin system
5. Create documentation for plugin developers