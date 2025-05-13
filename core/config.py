"""
Configuration management for the Universal App.

This module provides functionality for loading, accessing, and validating
application configuration from various sources with a clean interface.
"""
import os
import json
import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel, field_validator, model_validator

logger = logging.getLogger(__name__)

# Configuration models
class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file: Optional[str] = None
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    
    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that the log level is a valid Python logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v

class RIntegrationConfig(BaseModel):
    """R integration service configuration."""
    enabled: bool = True
    scripts_dir: str = "r_scripts"
    libraries: list[str] = ["base", "stats"]

class ServiceConfig(BaseModel):
    """Generic service configuration."""
    enabled: bool = True
    data_dir: str = "data"

class WindowConfig(BaseModel):
    """Main window configuration."""
    title: str = "Universal App"
    width: int = 1280
    height: int = 800
    min_width: int = 800
    min_height: int = 600

class SidebarConfig(BaseModel):
    """Sidebar configuration."""
    width: int = 240

class UIConfig(BaseModel):
    """UI configuration."""
    window: WindowConfig = WindowConfig()
    sidebar: SidebarConfig = SidebarConfig()

class AppConfig(BaseModel):
    """Application-wide configuration."""
    debug: bool = False
    title: str = "Universal App"
    version: str = "1.0.0"
    theme: str = "cosmo"
    temp_dir: Optional[str] = None
    data_dir: str = "data"

class ServicesConfig(BaseModel):
    """Services configuration."""
    r_integration: RIntegrationConfig = RIntegrationConfig()
    actuarial: ServiceConfig = ServiceConfig(data_dir="data/actuarial")
    finance: ServiceConfig = ServiceConfig(data_dir="data/finance")

class Config(BaseModel):
    """Root configuration model."""
    app: AppConfig = AppConfig()
    logging: LoggingConfig = LoggingConfig()
    services: ServicesConfig = ServicesConfig()
    ui: UIConfig = UIConfig()


class ConfigManager:
    """
    Configuration manager for the Universal App.
    
    This class is responsible for loading, accessing, and validating
    configuration from various sources.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, looks for
                config.json in the current directory.
        """
        self._config_path = config_path or "config.json"
        self._config = self._load_config()
        
    def _load_config(self) -> Config:
        """
        Load configuration from the specified path.
        
        Returns:
            A validated Config object
        """
        # Start with default configuration
        config_dict = {}
        
        # Load from file if it exists
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r") as f:
                    config_dict = json.load(f)
                logger.info(f"Loaded configuration from {self._config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration from {self._config_path}: {e}")
                logger.info("Using default configuration")
        else:
            logger.warning(f"Configuration file {self._config_path} not found, using defaults")
        
        # Create and validate the configuration
        return Config(**config_dict)
    
    def get_config(self) -> Config:
        """Get the current configuration object."""
        return self._config
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        Save the current configuration to a file.
        
        Args:
            config_path: Path to save the configuration to. If None, uses the
                original config path.
                
        Returns:
            True if successful, False otherwise
        """
        save_path = config_path or self._config_path
        try:
            with open(save_path, "w") as f:
                json.dump(self._config.model_dump(), f, indent=2)
            logger.info(f"Saved configuration to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration to {save_path}: {e}")
            return False
            
    def reload_config(self) -> None:
        """Reload configuration from the file."""
        self._config = self._load_config()
        logger.info("Configuration reloaded")
        
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the underlying Config object.
        
        This allows for syntax like config_manager.app.debug instead of
        config_manager.get_config().app.debug.
        """
        return getattr(self._config, name)


# Global configuration manager instance for easy access
config_manager = ConfigManager()