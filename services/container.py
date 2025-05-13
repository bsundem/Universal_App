"""
Dependency Injection Container for the Universal App.

This module provides a dependency injection container using the 
dependency-injector library, following the Dependency Inversion Principle.
The container manages service instances and their dependencies.
"""
import logging
import importlib
from typing import Dict, Any, Optional, Type, List, Set, Callable
from dependency_injector import containers, providers

# Import config
from core.config import config_manager

# Import event system
from utils.events import event_bus, SystemEvent, ServiceEvent, Event
from utils.events import ServiceInitializedEvent, ConfigurationChangedEvent

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection container that manages all application services.
    
    This container follows the Dependency Inversion Principle, allowing high-level
    modules to depend on abstractions rather than concrete implementations.
    
    Note: This container is now primarily used for configuration and resources,
    as service implementation is handled by the plugin system.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Event bus instance
    event_bus_provider = providers.Object(event_bus)
    
    # Other resources can be added here
    resources = providers.Dict({})
    
    # Provider for the application instance
    app = providers.Dependency()
    
    # Other resources
    # Initialize with empty dict that can be updated
    resources = providers.Dict({})
    
    # Provider for the application instance
    app = providers.Dependency()
    
    # Dynamic plugin providers
    plugins = providers.Dict({})
    
    @classmethod
    def register_plugin_provider(cls, name: str, provider: providers.Provider) -> None:
        """
        Register a plugin provider with the container.
        
        Args:
            name: Name of the plugin
            provider: Provider for the plugin
        """
        # Get the plugins dict provider from the container
        plugins_provider = cls.plugins
        
        # Update the provider's dict with the new plugin
        plugins_dict = plugins_provider.provided or {}
        plugins_dict[name] = provider
        plugins_provider.override(providers.Dict(plugins_dict))
    

class ContainerManager:
    """
    Manager class for the dependency injection container.
    
    This class provides a simplified interface to the container and helper
    methods for service retrieval.
    """
    
    def __init__(self):
        """Initialize the container manager."""
        self._container = Container()
        self._container.config.from_dict(config_manager.get_config().model_dump())
        self._initialized = False
        self._plugins = {}
        
    def init_resources(self, **kwargs) -> None:
        """
        Initialize container resources.
        
        Args:
            **kwargs: Resources to add to the container
        """
        if not self._initialized:
            # Set the app dependency if provided
            if 'app' in kwargs:
                self._container.app.override(kwargs['app'])
            
            # Create a new dict provider with the combined resources
            resources_dict = {}
            resources_dict.update(kwargs)
            self._container.resources.override(providers.Dict(resources_dict))
            
            self._initialized = True
            logger.info("Container resources initialized")
            
            # Publish event that container is initialized
            event_bus.publish(SystemEvent(
                source="container",
                event_id="container_initialized"
            ))
    
    def get_container(self) -> Container:
        """
        Get the dependency injection container.
        
        Returns:
            The container instance
        """
        return self._container
    
    def override_provider(self, provider_name: str, provider_instance: Any) -> None:
        """
        Override a provider with a different implementation.
        
        This is useful for testing when you want to inject mock services.
        
        Args:
            provider_name: Name of the provider to override
            provider_instance: Instance to use instead
        """
        if hasattr(self._container, provider_name):
            provider = getattr(self._container, provider_name)
            provider.override(providers.Object(provider_instance))
            logger.debug(f"Provider {provider_name} overridden")
            
            # Publish event for provider override
            event_bus.publish(ServiceEvent(
                source="container",
                event_id=f"provider_override_{provider_name}",
                service_name=provider_name
            ))
        else:
            logger.warning(f"Provider {provider_name} not found, cannot override")
    
    def reset_overrides(self) -> None:
        """Reset all provider overrides to their original implementations."""
        self._container.reset_override()
        logger.debug("All provider overrides reset")
        
        # Publish event for overrides reset
        event_bus.publish(SystemEvent(
            source="container",
            event_id="container_overrides_reset"
        ))
        
    def register_plugin(self, name: str, plugin_class: Type, singleton: bool = True, **kwargs) -> Any:
        """
        Register a plugin with the container.
        
        This method creates a provider for the plugin and registers it with the container.
        
        Args:
            name: Name of the plugin
            plugin_class: The plugin class to instantiate
            singleton: Whether to use a singleton provider
            **kwargs: Additional arguments to pass to the plugin constructor
            
        Returns:
            The plugin instance
        """
        if name in self._plugins:
            logger.warning(f"Plugin {name} already registered, overriding")
        
        # Create the provider based on singleton flag
        if singleton:
            provider = providers.Singleton(plugin_class, **kwargs)
        else:
            provider = providers.Factory(plugin_class, **kwargs)
            
        # Register with container
        Container.register_plugin_provider(name, provider)
        
        # Add to local cache
        self._plugins[name] = provider
        
        # Get and return the instance
        plugin_instance = provider()
        
        logger.info(f"Plugin {name} registered with container")
        
        # Publish plugin registration event
        event_bus.publish(ServiceEvent(
            source="container",
            event_id=f"plugin_registered_{name}",
            service_name=name
        ))
        
        return plugin_instance
    
    def get_plugin(self, name: str) -> Any:
        """
        Get a plugin instance by name.
        
        Args:
            name: Name of the plugin
            
        Returns:
            The plugin instance
            
        Raises:
            KeyError: If the plugin is not registered
        """
        if name not in self._plugins:
            raise KeyError(f"Plugin {name} not registered")
            
        return self._plugins[name]()
    
    def list_plugins(self) -> List[str]:
        """
        Get a list of registered plugin names.
        
        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())
    
    def discover_plugins(self, package_name: str) -> List[str]:
        """
        Discover plugins in a package.
        
        This method searches for plugin modules in the specified package and
        registers any plugin classes it finds.
        
        A plugin class is identified by having a `plugin_name` class attribute
        and implementing the Plugin interface or inheriting from PluginBase.
        
        Args:
            package_name: Name of the package to search
            
        Returns:
            List of discovered plugin names
        """
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.error(f"Cannot import package {package_name}")
            return []
            
        # This would scan the package for plugin classes and register them
        # The actual implementation would depend on how plugins are defined
        # For now, this is a placeholder
        
        logger.info(f"Scanning package {package_name} for plugins")
        
        # Return a list of discovered plugin names
        return []


# Global container manager instance
container = ContainerManager()


# Helper functions for retrieving services
def get_r_service():
    """
    Get the R service instance.
    
    Returns:
        R service plugin instance
        
    Raises:
        RuntimeError: If the R service plugin is not available
    """
    from services.plugins.registry import plugin_registry
    plugin = plugin_registry.get_plugin("r_service")
    if not plugin:
        raise RuntimeError("R service plugin is not available. Make sure the plugin is properly registered and activated.")
    return plugin


def get_actuarial_service():
    """
    Get the actuarial service instance.
    
    Returns:
        Actuarial service plugin instance
        
    Raises:
        RuntimeError: If the actuarial service plugin is not available
    """
    from services.plugins.registry import plugin_registry
    plugin = plugin_registry.get_plugin("actuarial_service")
    if not plugin:
        raise RuntimeError("Actuarial service plugin is not available. Make sure the plugin is properly registered and activated.")
    return plugin


def get_finance_service():
    """
    Get the finance service instance.
    
    Returns:
        Finance service plugin instance
        
    Raises:
        RuntimeError: If the finance service plugin is not available
    """
    from services.plugins.registry import plugin_registry
    plugin = plugin_registry.get_plugin("finance_service")
    if not plugin:
        raise RuntimeError("Finance service plugin is not available. Make sure the plugin is properly registered and activated.")
    return plugin


def get_plugin(plugin_id):
    """
    Get any plugin by its ID.
    
    Args:
        plugin_id: The ID of the plugin to retrieve
        
    Returns:
        The plugin instance
        
    Raises:
        RuntimeError: If the plugin is not available
    """
    from services.plugins.registry import plugin_registry
    plugin = plugin_registry.get_plugin(plugin_id)
    if not plugin:
        raise RuntimeError(f"Plugin '{plugin_id}' is not available. Make sure the plugin is properly registered and activated.")
    return plugin