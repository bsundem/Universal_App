"""
Base classes and interfaces for the plugin system.

This module provides the core abstractions for implementing plugins,
including the Plugin protocol and the PluginBase abstract class.
"""
import abc
import logging
import importlib.util
import pkgutil
import inspect
import os
import sys
from typing import Dict, List, Any, Optional, Type, ClassVar, Set, Protocol, runtime_checkable

from utils.events import Event, event_bus, ServiceEvent

logger = logging.getLogger(__name__)


@runtime_checkable
class Plugin(Protocol):
    """
    Protocol defining the interface for a plugin.
    
    All plugins must implement this interface to be recognized by the plugin system.
    """
    # Class attributes that must be defined by implementations
    plugin_id: ClassVar[str]
    plugin_name: ClassVar[str]
    plugin_version: ClassVar[str]
    plugin_description: ClassVar[str]
    
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        ...
        
    def shutdown(self) -> None:
        """Shut down the plugin and release resources."""
        ...
        
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata.
        
        Returns:
            Dictionary with plugin metadata
        """
        ...


class PluginBase(abc.ABC):
    """
    Abstract base class for plugins.
    
    This class provides a base implementation of the Plugin protocol
    that plugins can inherit from.
    """
    # Class attributes that must be defined by subclasses
    plugin_id: ClassVar[str] = ""
    plugin_name: ClassVar[str] = ""
    plugin_version: ClassVar[str] = "0.1.0"
    plugin_description: ClassVar[str] = ""
    plugin_dependencies: ClassVar[List[str]] = []
    
    def __init__(self):
        """Initialize the plugin base."""
        self._initialized = False
        
        # Check required class attributes
        if not self.plugin_id:
            raise ValueError(f"Plugin {self.__class__.__name__} must define plugin_id")
        if not self.plugin_name:
            raise ValueError(f"Plugin {self.__class__.__name__} must define plugin_name")
            
        # Set up plugin-specific logger
        self.logger = logging.getLogger(f"plugin.{self.plugin_id}")
        
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Subclasses should override _initialize() instead of this method.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        if self._initialized:
            self.logger.warning(f"Plugin {self.plugin_id} already initialized")
            return True
            
        self.logger.info(f"Initializing plugin {self.plugin_name} v{self.plugin_version}")
        
        try:
            result = self._initialize()
            self._initialized = result
            
            if result:
                # Publish event that plugin was initialized
                event_bus.publish(PluginInitializedEvent(
                    source=f"plugin.{self.plugin_id}",
                    plugin_id=self.plugin_id,
                    plugin_name=self.plugin_name,
                    plugin_version=self.plugin_version
                ))
                self.logger.info(f"Plugin {self.plugin_name} initialized successfully")
            else:
                self.logger.error(f"Plugin {self.plugin_name} initialization failed")
                
            return result
        except Exception as e:
            self.logger.error(f"Error initializing plugin {self.plugin_name}: {e}", exc_info=True)
            
            # Publish error event
            event_bus.publish(PluginErrorEvent(
                source=f"plugin.{self.plugin_id}",
                plugin_id=self.plugin_id,
                error_message=str(e)
            ))
            
            return False
        
    @abc.abstractmethod
    def _initialize(self) -> bool:
        """
        Initialize the plugin implementation.
        
        This method should be implemented by subclasses to perform
        the actual initialization.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        pass
        
    def shutdown(self) -> None:
        """
        Shut down the plugin and release resources.
        
        Subclasses should override _shutdown() instead of this method.
        """
        if not self._initialized:
            self.logger.warning(f"Plugin {self.plugin_id} not initialized, nothing to shut down")
            return
            
        self.logger.info(f"Shutting down plugin {self.plugin_name}")
        
        try:
            self._shutdown()
            
            # Publish event that plugin was shut down
            event_bus.publish(PluginShutdownEvent(
                source=f"plugin.{self.plugin_id}",
                plugin_id=self.plugin_id,
                plugin_name=self.plugin_name
            ))
            
            self._initialized = False
            self.logger.info(f"Plugin {self.plugin_name} shut down successfully")
        except Exception as e:
            self.logger.error(f"Error shutting down plugin {self.plugin_name}: {e}", exc_info=True)
            
            # Publish error event
            event_bus.publish(PluginErrorEvent(
                source=f"plugin.{self.plugin_id}",
                plugin_id=self.plugin_id,
                error_message=f"Shutdown error: {str(e)}"
            ))
        
    def _shutdown(self) -> None:
        """
        Shut down the plugin implementation.
        
        This method should be implemented by subclasses to perform
        the actual shutdown.
        """
        # Default implementation does nothing
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata.
        
        Returns:
            Dictionary with plugin metadata
        """
        return {
            "id": self.plugin_id,
            "name": self.plugin_name,
            "version": self.plugin_version,
            "description": self.plugin_description,
            "dependencies": self.plugin_dependencies,
            "initialized": self._initialized,
            "class": self.__class__.__name__
        }


class ServicePlugin(PluginBase):
    """
    Base class for plugins that provide services.
    
    Service plugins implement one or more service interfaces and
    can be registered with the dependency injection container.
    """
    # Service interface implemented by this plugin
    service_interface: ClassVar[Type] = None
    
    def register_service(self, container_manager) -> bool:
        """
        Register the plugin's service with the container.
        
        Args:
            container_manager: The container manager
            
        Returns:
            True if registration succeeded, False otherwise
        """
        if not self._initialized:
            self.logger.error(f"Cannot register service for uninitialized plugin {self.plugin_id}")
            return False
            
        self.logger.info(f"Registering service for plugin {self.plugin_name}")
        
        try:
            # Register the plugin as a service
            container_manager.register_plugin(
                self.plugin_id,
                self.__class__,
                singleton=True
            )
            
            self.logger.info(f"Service registered for plugin {self.plugin_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error registering service for plugin {self.plugin_name}: {e}", exc_info=True)
            return False


class UIPlugin(PluginBase):
    """
    Base class for plugins that provide UI components.
    
    UI plugins provide UI components that can be integrated into
    the application's user interface.
    """
    def register_page(self, main_window) -> bool:
        """
        Register the plugin's page with the main window.
        
        Args:
            main_window: The main window instance
            
        Returns:
            True if registration succeeded, False otherwise
        """
        if not self._initialized:
            self.logger.error(f"Cannot register page for uninitialized plugin {self.plugin_id}")
            return False
            
        self.logger.info(f"Registering UI page for plugin {self.plugin_name}")
        
        try:
            # This should be implemented by subclasses
            # to create and register the actual page
            return self._register_page(main_window)
        except Exception as e:
            self.logger.error(f"Error registering page for plugin {self.plugin_name}: {e}", exc_info=True)
            return False
            
    @abc.abstractmethod
    def _register_page(self, main_window) -> bool:
        """
        Register the plugin's page with the main window.
        
        This method should be implemented by subclasses to perform
        the actual page registration.
        
        Args:
            main_window: The main window instance
            
        Returns:
            True if registration succeeded, False otherwise
        """
        pass


# Plugin-related events

class PluginEvent(Event):
    """Base class for plugin-related events."""
    plugin_id: str


class PluginInitializedEvent(PluginEvent):
    """Event published when a plugin is initialized."""
    plugin_name: str
    plugin_version: str


class PluginShutdownEvent(PluginEvent):
    """Event published when a plugin is shut down."""
    plugin_name: str


class PluginErrorEvent(PluginEvent):
    """Event published when a plugin encounters an error."""
    error_message: str


class PluginManager:
    """
    Manager class for discovering, loading, and managing plugins.
    
    This class provides methods for discovering plugins in packages,
    loading plugin modules, and managing plugin lifecycle.
    """
    
    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}
        self._loaded_modules: Set[str] = set()
        
        logger.debug("Plugin manager initialized")
        
    def discover_plugins(self, package_name: str) -> List[str]:
        """
        Discover plugins in a package.
        
        This method searches for modules in the specified package,
        loads them, and registers any plugin classes it finds.
        
        Args:
            package_name: Name of the package to search
            
        Returns:
            List of discovered plugin IDs
        """
        logger.info(f"Discovering plugins in package {package_name}")
        
        discovered_plugins = []
        
        try:
            # Import the package
            package = importlib.import_module(package_name)
            package_path = os.path.dirname(package.__file__)
            
            # Find all modules in the package
            for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
                # Skip packages, only look at modules
                if is_pkg:
                    continue
                    
                # Full module name
                full_module_name = f"{package_name}.{module_name}"
                
                # Skip already loaded modules
                if full_module_name in self._loaded_modules:
                    continue
                    
                # Load the module and check for plugin classes
                try:
                    module = importlib.import_module(full_module_name)
                    self._loaded_modules.add(full_module_name)
                    
                    # Scan for plugin classes in the module
                    plugin_ids = self._scan_module_for_plugins(module)
                    discovered_plugins.extend(plugin_ids)
                    
                except Exception as e:
                    logger.error(f"Error loading module {full_module_name}: {e}", exc_info=True)
            
            logger.info(f"Discovered {len(discovered_plugins)} plugins in {package_name}")
            return discovered_plugins
        
        except Exception as e:
            logger.error(f"Error discovering plugins in {package_name}: {e}", exc_info=True)
            return []
            
    def _scan_module_for_plugins(self, module) -> List[str]:
        """
        Scan a module for plugin classes.
        
        This method looks for classes in the module that implement
        the Plugin protocol or inherit from PluginBase.
        
        Args:
            module: The module to scan
            
        Returns:
            List of plugin IDs found in the module
        """
        plugin_ids = []
        
        for name, obj in inspect.getmembers(module):
            # Check if it's a class and a potential plugin
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                # Check if it's a plugin class
                if issubclass(obj, PluginBase) and obj is not PluginBase:
                    try:
                        # Make sure required attributes are defined
                        if not obj.plugin_id:
                            logger.warning(f"Plugin class {obj.__name__} in {module.__name__} has no plugin_id")
                            continue
                            
                        # Check if this plugin is already registered
                        if obj.plugin_id in self._plugin_classes:
                            logger.warning(
                                f"Plugin {obj.plugin_id} already registered from "
                                f"{self._plugin_classes[obj.plugin_id].__module__}"
                            )
                            continue
                            
                        # Register the plugin class
                        self._plugin_classes[obj.plugin_id] = obj
                        plugin_ids.append(obj.plugin_id)
                        
                        logger.debug(
                            f"Found plugin {obj.plugin_id} ({obj.plugin_name}) in {module.__name__}"
                        )
                        
                    except Exception as e:
                        logger.error(
                            f"Error registering plugin class {obj.__name__} from {module.__name__}: {e}",
                            exc_info=True
                        )
        
        return plugin_ids
        
    def load_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Load and initialize a plugin.
        
        This method instantiates the plugin class and initializes it.
        
        Args:
            plugin_id: ID of the plugin to load
            
        Returns:
            The plugin instance if successful, None otherwise
        """
        # Check if plugin is already loaded
        if plugin_id in self._plugins:
            logger.warning(f"Plugin {plugin_id} already loaded")
            return self._plugins[plugin_id]
            
        # Check if plugin class is registered
        if plugin_id not in self._plugin_classes:
            logger.error(f"Plugin {plugin_id} not registered")
            return None
            
        logger.info(f"Loading plugin {plugin_id}")
        
        try:
            # Instantiate the plugin
            plugin_class = self._plugin_classes[plugin_id]
            plugin = plugin_class()
            
            # Initialize the plugin
            if plugin.initialize():
                # Store the plugin instance
                self._plugins[plugin_id] = plugin
                
                logger.info(f"Plugin {plugin_id} ({plugin.plugin_name}) loaded successfully")
                return plugin
            else:
                logger.error(f"Failed to initialize plugin {plugin_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}", exc_info=True)
            return None
            
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        This method shuts down the plugin and removes it from the loaded plugins.
        
        Args:
            plugin_id: ID of the plugin to unload
            
        Returns:
            True if the plugin was unloaded, False otherwise
        """
        if plugin_id not in self._plugins:
            logger.warning(f"Plugin {plugin_id} not loaded")
            return False
            
        logger.info(f"Unloading plugin {plugin_id}")
        
        try:
            # Get the plugin instance
            plugin = self._plugins[plugin_id]
            
            # Shut down the plugin
            plugin.shutdown()
            
            # Remove the plugin instance
            del self._plugins[plugin_id]
            
            logger.info(f"Plugin {plugin_id} unloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}", exc_info=True)
            return False
            
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to get
            
        Returns:
            The plugin instance if loaded, None otherwise
        """
        return self._plugins.get(plugin_id)
        
    def get_plugin_class(self, plugin_id: str) -> Optional[Type[Plugin]]:
        """
        Get a plugin class by ID.
        
        Args:
            plugin_id: ID of the plugin class to get
            
        Returns:
            The plugin class if registered, None otherwise
        """
        return self._plugin_classes.get(plugin_id)
        
    def list_plugins(self) -> List[str]:
        """
        Get a list of loaded plugin IDs.
        
        Returns:
            List of loaded plugin IDs
        """
        return list(self._plugins.keys())
        
    def list_plugin_classes(self) -> List[str]:
        """
        Get a list of registered plugin class IDs.
        
        Returns:
            List of registered plugin class IDs
        """
        return list(self._plugin_classes.keys())
        
    def get_plugin_metadata(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin metadata dictionary if found, None otherwise
        """
        plugin = self.get_plugin(plugin_id)
        if plugin:
            return plugin.get_metadata()
            
        # If plugin not loaded, check if class is registered
        plugin_class = self.get_plugin_class(plugin_id)
        if plugin_class:
            return {
                "id": plugin_class.plugin_id,
                "name": plugin_class.plugin_name,
                "version": plugin_class.plugin_version,
                "description": plugin_class.plugin_description,
                "dependencies": getattr(plugin_class, "plugin_dependencies", []),
                "initialized": False,
                "class": plugin_class.__name__
            }
            
        return None


# Create a global plugin manager instance
plugin_manager = PluginManager()