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
from typing import Optional

import tkinter as tk
from tkinter import ttk

# Import ttkbootstrap for modern UI styling
import ttkbootstrap as ttk

# Import core modules
from core.config import config_manager

# Import services container
from services.container import container

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
        self._init_ui()
        
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
        
    def _init_ui(self) -> None:
        """Initialize the application UI."""
        # Create the root window
        # Use ttkbootstrap instead of regular tk
        self.root = ttk.Window(
            title=config_manager.ui.window.title,
            themename=config_manager.app.theme,
            size=(config_manager.ui.window.width, config_manager.ui.window.height)
        )
        
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
        
        logger.debug("UI initialized")
        
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