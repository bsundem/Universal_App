"""
Plugin registry for the Universal App.

This module provides a registry for plugins and integrates the plugin system
with the dependency injection container.
"""
import logging
from typing import Dict, List, Any, Optional, Type, Set

from utils.events import event_bus, subscribe, ServiceEvent, SystemEvent
from services.plugins.base import Plugin, PluginManager, PluginInitializedEvent
from services.container import container

# Import plugin_manager only when needed to avoid circular imports

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Registry for managing and activating plugins.
    
    This class connects the plugin system to the dependency injection container
    and manages plugin activation and service registration.
    """
    
    def __init__(self, plugin_manager=None, container_manager=None):
        """
        Initialize the plugin registry.
        
        Args:
            plugin_manager: Plugin manager instance (default: global instance)
            container_manager: Container manager instance (default: global instance)
        """
        # Import here to avoid circular imports
        from services.plugins.base import plugin_manager as global_plugin_manager
        
        self._plugin_manager = plugin_manager or global_plugin_manager
        self._container_manager = container_manager or container
        self._active_plugins: Dict[str, Plugin] = {}
        self._plugin_packages: Set[str] = set()
        
        # Register event handlers
        event_bus.subscribe(PluginInitializedEvent, self._on_plugin_initialized)
        event_bus.subscribe(SystemEvent, self._on_system_event)
        
        logger.debug("Plugin registry initialized")
        
    def register_plugin_package(self, package_name: str) -> List[str]:
        """
        Register a package for plugin discovery.
        
        This method adds the package to the list of packages to scan for plugins
        and performs an initial discovery.
        
        Args:
            package_name: Name of the package to register
            
        Returns:
            List of discovered plugin IDs
        """
        if package_name in self._plugin_packages:
            logger.warning(f"Package {package_name} already registered")
            return []
            
        logger.info(f"Registering plugin package {package_name}")
        
        # Add to registered packages
        self._plugin_packages.add(package_name)
        
        # Discover plugins
        plugin_ids = self._plugin_manager.discover_plugins(package_name)
        
        logger.info(f"Registered package {package_name} with {len(plugin_ids)} plugins")
        return plugin_ids
        
    def activate_plugin(self, plugin_id: str) -> bool:
        """
        Activate a plugin.
        
        This method loads and initializes the plugin, and registers its services
        with the dependency injection container.
        
        Args:
            plugin_id: ID of the plugin to activate
            
        Returns:
            True if activation succeeded, False otherwise
        """
        if plugin_id in self._active_plugins:
            logger.warning(f"Plugin {plugin_id} already active")
            return True
            
        logger.info(f"Activating plugin {plugin_id}")
        
        # Load the plugin
        plugin = self._plugin_manager.load_plugin(plugin_id)
        if not plugin:
            logger.error(f"Failed to load plugin {plugin_id}")
            return False
            
        # Check if it's a service plugin
        from services.plugins.base import ServicePlugin
        if isinstance(plugin, ServicePlugin):
            # Register the service
            if not plugin.register_service(self._container_manager):
                logger.error(f"Failed to register service for plugin {plugin_id}")
                self._plugin_manager.unload_plugin(plugin_id)
                return False
                
        # Store the active plugin
        self._active_plugins[plugin_id] = plugin
        
        logger.info(f"Plugin {plugin_id} activated successfully")
        return True
        
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        Deactivate a plugin.
        
        This method unloads the plugin and removes its services from the
        dependency injection container.
        
        Args:
            plugin_id: ID of the plugin to deactivate
            
        Returns:
            True if deactivation succeeded, False otherwise
        """
        if plugin_id not in self._active_plugins:
            logger.warning(f"Plugin {plugin_id} not active")
            return False
            
        logger.info(f"Deactivating plugin {plugin_id}")
        
        # Unload the plugin
        if not self._plugin_manager.unload_plugin(plugin_id):
            logger.error(f"Failed to unload plugin {plugin_id}")
            return False
            
        # Remove from active plugins
        del self._active_plugins[plugin_id]
        
        logger.info(f"Plugin {plugin_id} deactivated successfully")
        return True
        
    def activate_all_plugins(self) -> Dict[str, bool]:
        """
        Activate all discovered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to activation status
        """
        logger.info("Activating all plugins")
        
        results = {}
        plugin_ids = self._plugin_manager.list_plugin_classes()
        
        for plugin_id in plugin_ids:
            if plugin_id not in self._active_plugins:
                results[plugin_id] = self.activate_plugin(plugin_id)
            else:
                results[plugin_id] = True
                
        logger.info(f"Activated {sum(1 for success in results.values() if success)} out of {len(results)} plugins")
        return results
        
    def deactivate_all_plugins(self) -> Dict[str, bool]:
        """
        Deactivate all active plugins.
        
        Returns:
            Dictionary mapping plugin IDs to deactivation status
        """
        logger.info("Deactivating all plugins")
        
        results = {}
        plugin_ids = list(self._active_plugins.keys())
        
        for plugin_id in plugin_ids:
            results[plugin_id] = self.deactivate_plugin(plugin_id)
                
        logger.info(f"Deactivated {sum(1 for success in results.values() if success)} out of {len(results)} plugins")
        return results
        
    def list_active_plugins(self) -> List[str]:
        """
        Get a list of active plugin IDs.
        
        Returns:
            List of active plugin IDs
        """
        return list(self._active_plugins.keys())
        
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get a plugin instance by ID.
        
        Args:
            plugin_id: ID of the plugin to get
            
        Returns:
            The plugin instance if found, None otherwise
        """
        if plugin_id in self._active_plugins:
            return self._active_plugins[plugin_id]
        return None
        
    def get_plugin_metadata(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin metadata dictionary if found, None otherwise
        """
        return self._plugin_manager.get_plugin_metadata(plugin_id)
        
    def list_all_plugin_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all discovered plugins.
        
        Returns:
            Dictionary mapping plugin IDs to metadata dictionaries
        """
        result = {}
        plugin_ids = self._plugin_manager.list_plugin_classes()
        
        for plugin_id in plugin_ids:
            metadata = self.get_plugin_metadata(plugin_id)
            if metadata:
                result[plugin_id] = metadata
                
        return result
        
    def _on_plugin_initialized(self, event: PluginInitializedEvent) -> None:
        """
        Handle plugin initialized event.
        
        Args:
            event: The plugin initialized event
        """
        logger.debug(f"Plugin {event.plugin_id} initialized")
        
    def _on_system_event(self, event: SystemEvent) -> None:
        """
        Handle system events.
        
        Args:
            event: The system event
        """
        # Handle application shutdown
        if event.event_id == "application_shutting_down":
            logger.info("Application shutting down, deactivating all plugins")
            self.deactivate_all_plugins()


# Create a global plugin registry instance - only if not already created
def _create_plugin_registry():
    """Create the plugin registry instance safely"""
    try:
        from services.plugins.base import plugin_manager as global_plugin_manager
        return PluginRegistry(plugin_manager=global_plugin_manager)
    except Exception as e:
        logger.error(f"Error creating plugin registry: {e}")
        # Create a minimal plugin registry - fallback for test environments
        return PluginRegistry()

plugin_registry = _create_plugin_registry()