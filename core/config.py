"""
Configuration management module for the Universal App.

This module provides centralized configuration management for the application,
supporting multiple sources of configuration including environment variables,
configuration files, and programmatically set values.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Set, Type
import dataclasses
from dataclasses import dataclass, field

from utils.error_handling import ConfigurationError


class ConfigSection:
    """Base class for configuration sections."""
    pass


@dataclass
class LoggingConfig(ConfigSection):
    """Logging configuration section."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file: Optional[str] = None
    max_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    
    def get_log_level(self) -> int:
        """Convert string log level to logging module constant."""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(self.level.upper(), logging.INFO)


@dataclass
class RConfig(ConfigSection):
    """R integration configuration section."""
    enabled: bool = True
    scripts_dir: str = "r_scripts"
    libraries: List[str] = field(default_factory=lambda: ["base", "stats"])


@dataclass
class KaggleConfig(ConfigSection):
    """Kaggle integration configuration section."""
    enabled: bool = True
    credentials_file: str = "~/.kaggle/kaggle.json"
    timeout: int = 60
    max_dataset_size_mb: int = 1000


@dataclass
class AppConfig(ConfigSection):
    """Main application configuration section."""
    debug: bool = False
    title: str = "Universal App"
    theme: str = "default"
    temp_dir: Optional[str] = None
    data_dir: str = "data"


class Config:
    """
    Configuration manager for the Universal App.
    
    This class provides centralized access to application configuration,
    supporting multiple configuration sources with overrides.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.app = AppConfig()
        self.logging = LoggingConfig()
        self.r = RConfig()
        self.kaggle = KaggleConfig()
        
        # Load configuration from various sources
        self._load_defaults()
        self._load_from_config_file()
        self._load_from_env()
    
    def _load_defaults(self):
        """Load default configuration values."""
        # Defaults are already set in the dataclasses
        pass
    
    def _load_from_config_file(self):
        """Load configuration from config files."""
        # Look for config file in multiple locations
        config_paths = [
            Path("./config.json"),
            Path("./config/config.json"),
            Path(os.path.expanduser("~/.config/universal_app/config.json")),
        ]
        
        config_file = None
        for path in config_paths:
            if path.exists():
                config_file = path
                break
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    self._apply_config_dict(config_data)
            except Exception as e:
                raise ConfigurationError(
                    f"Error loading configuration file {config_file}: {str(e)}",
                    section="file"
                )
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Environment variables override config file settings
        # Format: APP_SECTION_KEY=value (e.g., APP_LOGGING_LEVEL=DEBUG)
        for env_name, env_value in os.environ.items():
            if env_name.startswith("APP_"):
                parts = env_name.split("_", 2)
                if len(parts) == 3:
                    _, section, key = parts
                    section = section.lower()
                    key = key.lower()
                    
                    self._set_config_value(section, key, env_value)
    
    def _apply_config_dict(self, config_data: Dict[str, Any]):
        """Apply configuration from a dictionary."""
        for section_name, section_data in config_data.items():
            section_name = section_name.lower()
            
            if hasattr(self, section_name) and isinstance(section_data, dict):
                section = getattr(self, section_name)
                
                # Apply key/value pairs to the section
                for key, value in section_data.items():
                    if hasattr(section, key):
                        setattr(section, key, self._convert_value(value, type(getattr(section, key))))
    
    def _set_config_value(self, section: str, key: str, value: str):
        """Set a configuration value from a string."""
        if hasattr(self, section):
            section_obj = getattr(self, section)
            
            if hasattr(section_obj, key):
                current_value = getattr(section_obj, key)
                converted_value = self._convert_value(value, type(current_value))
                setattr(section_obj, key, converted_value)
    
    def _convert_value(self, value: Any, target_type: Type) -> Any:
        """Convert a value to the target type."""
        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "on")
            return bool(value)
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == List[str]:
            if isinstance(value, str):
                return [item.strip() for item in value.split(",")]
            elif isinstance(value, list):
                return value
            return [str(value)]
        else:
            return value
    
    def get_section(self, section_name: str) -> Optional[ConfigSection]:
        """
        Get a configuration section by name.
        
        Args:
            section_name: Name of the configuration section
            
        Returns:
            ConfigSection if found, None otherwise
        """
        section_name = section_name.lower()
        if hasattr(self, section_name):
            return getattr(self, section_name)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        result = {}
        for section_name in ["app", "logging", "r", "kaggle"]:
            section = getattr(self, section_name)
            result[section_name] = dataclasses.asdict(section)
        return result
    
    def save_to_file(self, filepath: str):
        """
        Save current configuration to a file.
        
        Args:
            filepath: Path to save the configuration file
            
        Raises:
            ConfigurationError: If saving fails
        """
        try:
            config_dict = self.to_dict()
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2)
        except Exception as e:
            raise ConfigurationError(
                f"Error saving configuration to {filepath}: {str(e)}",
                section="file"
            )


# Global configuration instance
config = Config()