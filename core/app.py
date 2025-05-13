"""
Core application module for the Universal App.

This module contains the main Application class which is responsible for
initializing and running the application, including:
- Configuration loading
- Service initialization
- UI setup
- Logging configuration
"""
import os
import sys
import logging
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any

import tkinter as tk
from tkinter import ttk as tk_ttk  # Original ttk

# Import ttkbootstrap for modern UI styling
try:
    import ttkbootstrap as ttk
    USING_BOOTSTRAP = True
except ImportError:
    # Fall back to standard ttk if ttkbootstrap is not available
    ttk = tk_ttk
    USING_BOOTSTRAP = False

# Import core modules
from core.config import config_manager

# Import services container
from services.container import container

# Import event system
from utils.events import event_bus, SystemEvent, ApplicationStartedEvent, ApplicationShuttingDownEvent

# Import plugin system
from services.plugins.registry import plugin_registry

# Get logger
logger = logging.getLogger(__name__)

# Import UI components
from ui.main_window import MainWindow

logger = logging.getLogger(__name__)


class Application:
    """
    Main application class for the Universal App.
    
    This class is responsible for initializing and running the application,
    including configuration, services, and UI setup.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the application.
        
        Args:
            config_path: Path to the configuration file. If None, the default
                config path will be used.
        """
        self._setup_paths()
        self._configure_logging()
        self._init_services()
        self._init_plugins()
        self._init_ui()
        
        # Publish application started event
        event_bus.publish(ApplicationStartedEvent(
            source="application",
            version=config_manager.app.version
        ))
        
        logger.info(f"Application initialized: {config_manager.app.title} {config_manager.app.version}")
    
    def _setup_paths(self) -> None:
        """Set up application paths and directories."""
        # Get the root directory
        self.root_dir = Path(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        
        # Set up temporary directory if specified
        if config_manager.app.temp_dir:
            self.temp_dir = Path(config_manager.app.temp_dir)
        else:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="universal_app_"))
            
        # Set up data directory
        self.data_dir = self.root_dir / config_manager.app.data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # Set up service data directories
        for service_name in ["actuarial", "finance"]:
            service_config = getattr(config_manager.services, service_name)
            if service_config.enabled:
                data_dir = Path(service_config.data_dir)
                # If relative path, make it relative to the root directory
                if not data_dir.is_absolute():
                    data_dir = self.root_dir / data_dir
                data_dir.mkdir(exist_ok=True, parents=True)
        
        logger.debug(f"Application paths initialized. Root: {self.root_dir}, Temp: {self.temp_dir}, Data: {self.data_dir}")
        
    def _configure_logging(self) -> None:
        """Configure the logging system based on the application configuration."""
        log_config = config_manager.logging
        
        # Get the log level
        log_level = getattr(logging, log_config.level)
        
        # Configure the root logger
        logging.basicConfig(
            level=log_level,
            format=log_config.format,
            datefmt=log_config.date_format
        )
        
        # Add file handler if specified
        if log_config.file:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                log_config.file,
                maxBytes=log_config.max_size,
                backupCount=log_config.backup_count
            )
            file_handler.setFormatter(logging.Formatter(log_config.format))
            logging.getLogger().addHandler(file_handler)
            
        logger.debug("Logging configured")
        
    def _init_services(self) -> None:
        """Initialize application services."""
        # Initialize service container
        container.init_resources(app=self)
        
        logger.debug("Services initialized")
        
    def _init_plugins(self) -> None:
        """Initialize and load plugins."""
        # Get plugin directories from config
        plugin_packages = getattr(config_manager.get_config(), "plugins", {}).get("packages", [])
        
        # Always include our plugin packages
        core_plugin_packages = [
            "services.plugins",      # Main plugin package
            "services.plugins.examples"  # Example plugins
        ]
        
        for pkg in core_plugin_packages:
            if pkg not in plugin_packages:
                plugin_packages.append(pkg)
        
        # Register plugin packages
        discovered_plugins = []
        for package in plugin_packages:
            try:
                discovered = plugin_registry.register_plugin_package(package)
                discovered_plugins.extend(discovered)
                logger.info(f"Registered plugin package {package} with {len(discovered)} plugins")
            except Exception as e:
                logger.error(f"Error registering plugin package {package}: {e}", exc_info=True)
                
        # Activate plugins that should be auto-loaded
        auto_load_plugins = getattr(config_manager.get_config(), "plugins", {}).get("auto_load", [])
        
        # Always activate our core service plugins
        core_service_plugins = [
            "r_service",
            "actuarial_service",
            "finance_service"
        ]
        
        for plugin_id in core_service_plugins:
            if plugin_id not in auto_load_plugins:
                auto_load_plugins.append(plugin_id)
        
        # Always load example plugins in development
        if config_manager.app.debug:
            auto_load_plugins.extend([
                "calculator",
                "calculator_ui"
            ])
            
        activated_plugins = []
        for plugin_id in auto_load_plugins:
            try:
                if plugin_registry.activate_plugin(plugin_id):
                    activated_plugins.append(plugin_id)
                    logger.info(f"Activated plugin {plugin_id}")
                else:
                    logger.error(f"Failed to activate plugin {plugin_id}")
            except Exception as e:
                logger.error(f"Error activating plugin {plugin_id}: {e}", exc_info=True)
                
        logger.info(f"Discovered {len(discovered_plugins)} plugins, activated {len(activated_plugins)}")
        
        # Provide a list of the active plugins
        active_plugin_ids = plugin_registry.list_active_plugins()
        if active_plugin_ids:
            logger.info(f"Active plugins: {', '.join(active_plugin_ids)}")
        else:
            logger.info("No active plugins")
        
    def _init_ui(self) -> None:
        """Initialize the application UI."""
        # Create the root window
        if USING_BOOTSTRAP:
            # Use ttkbootstrap for modern styling
            self.root = ttk.Window(
                title=config_manager.ui.window.title,
                themename=config_manager.app.theme,
                size=(config_manager.ui.window.width, config_manager.ui.window.height)
            )
        else:
            # Fall back to standard tkinter
            self.root = tk.Tk()
            self.root.title(config_manager.ui.window.title)
            self.root.geometry(f"{config_manager.ui.window.width}x{config_manager.ui.window.height}")
            
        logger.info(f"UI initialized with {'ttkbootstrap' if USING_BOOTSTRAP else 'standard tkinter'}")
        
        # Set window minimum size
        self.root.minsize(
            config_manager.ui.window.min_width,
            config_manager.ui.window.min_height
        )
        
        # Set application icon if available
        icon_path = self.root_dir / "assets" / "icon.png"
        if icon_path.exists():
            # PhotoImage works differently between tk and ttkbootstrap
            try:
                icon = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon)
            except Exception as e:
                logger.warning(f"Failed to load application icon: {e}")
        
        # Create main window
        self.main_window = MainWindow(self.root)
        
        # Register UI plugins with the main window
        self._register_ui_plugins()
        
        logger.debug("UI initialized")
        
    def _register_ui_plugins(self) -> None:
        """Register UI plugins with the main window."""
        # Get active plugins
        active_plugins = plugin_registry.list_active_plugins()
        
        # Find UI plugins
        from services.plugins.base import UIPlugin
        ui_plugins = []
        
        for plugin_id in active_plugins:
            plugin = plugin_registry._plugin_manager.get_plugin(plugin_id)
            if isinstance(plugin, UIPlugin):
                ui_plugins.append(plugin)
                
        # Register UI plugins with main window
        for plugin in ui_plugins:
            try:
                if plugin.register_page(self.main_window):
                    logger.info(f"Registered UI plugin {plugin.plugin_id} with main window")
                else:
                    logger.error(f"Failed to register UI plugin {plugin.plugin_id} with main window")
            except Exception as e:
                logger.error(f"Error registering UI plugin {plugin.plugin_id}: {e}", exc_info=True)
        
    def run(self) -> int:
        """
        Run the application main loop.
        
        Returns:
            Exit code (0 for normal exit)
        """
        try:
            logger.info(f"Starting {config_manager.app.title} {config_manager.app.version}")
            self.root.mainloop()
            return 0
        except Exception as e:
            logger.exception(f"Unhandled exception in main loop: {e}")
            return 1
        finally:
            # Publish application shutting down event
            event_bus.publish(ApplicationShuttingDownEvent(
                source="application"
            ))
            
            # Perform cleanup
            self._cleanup()
            
    def _cleanup(self) -> None:
        """Clean up resources before application exit."""
        logger.info("Application shutting down, cleaning up resources")
        
        # Clean up temporary directory if we created it
        if config_manager.app.temp_dir is None and hasattr(self, "temp_dir"):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Removed temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory: {e}")
                
        logger.info("Application shutdown complete")