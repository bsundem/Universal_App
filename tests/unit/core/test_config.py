"""
Tests for the configuration management system in core/config.py.
"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch, mock_open

from core.config import ConfigManager, Config, LoggingConfig


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    config_data = {
        "app": {
            "debug": True,
            "title": "Test App",
            "version": "1.1.0"
        },
        "logging": {
            "level": "DEBUG",
            "file": "test.log"
        },
        "services": {
            "r_integration": {
                "enabled": False
            }
        }
    }
    
    with open(temp_file.name, 'w') as f:
        json.dump(config_data, f)
    
    yield temp_file.name
    
    # Cleanup temporary file
    os.unlink(temp_file.name)


class TestConfigManager:
    """Test cases for the ConfigManager class."""
    
    def test_init_with_default_path(self):
        """Test initialization with default path."""
        with patch('os.path.exists', return_value=False):
            config_manager = ConfigManager()
            assert config_manager._config_path == "config.json"
            assert isinstance(config_manager._config, Config)
    
    def test_init_with_custom_path(self):
        """Test initialization with custom path."""
        with patch('os.path.exists', return_value=False):
            config_manager = ConfigManager("custom_config.json")
            assert config_manager._config_path == "custom_config.json"
    
    def test_load_config_from_file(self, temp_config_file):
        """Test loading configuration from a file."""
        config_manager = ConfigManager(temp_config_file)
        assert config_manager.app.debug is True
        assert config_manager.app.title == "Test App"
        assert config_manager.app.version == "1.1.0"
        assert config_manager.logging.level == "DEBUG"
        assert config_manager.logging.file == "test.log"
        assert config_manager.services.r_integration.enabled is False
    
    def test_load_config_fallback_to_defaults(self):
        """Test fallback to defaults when file is not found."""
        with patch('os.path.exists', return_value=False):
            config_manager = ConfigManager("nonexistent.json")
            # Verify defaults were used
            assert config_manager.app.debug is False
            assert config_manager.app.title == "Universal App"
            assert config_manager.app.version == "1.0.0"
            assert config_manager.logging.level == "INFO"
    
    def test_get_config(self, temp_config_file):
        """Test get_config method."""
        config_manager = ConfigManager(temp_config_file)
        config = config_manager.get_config()
        assert isinstance(config, Config)
        assert config.app.title == "Test App"
    
    def test_save_config(self):
        """Test saving configuration to a file."""
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            with patch('json.dump') as mock_json_dump:
                config_manager = ConfigManager()
                result = config_manager.save_config("test_save.json")
                assert result is True
                mock_file.assert_called_once_with("test_save.json", "w")
                mock_json_dump.assert_called_once()
    
    def test_save_config_handles_error(self):
        """Test that save_config handles errors gracefully."""
        with patch('builtins.open', side_effect=IOError("Test error")):
            config_manager = ConfigManager()
            result = config_manager.save_config("test_error.json")
            assert result is False
    
    def test_reload_config(self, temp_config_file):
        """Test reloading configuration."""
        config_manager = ConfigManager(temp_config_file)
        original_title = config_manager.app.title
        
        # Modify the config file
        with open(temp_config_file, 'r') as f:
            config_data = json.load(f)
        
        config_data["app"]["title"] = "Modified Title"
        
        with open(temp_config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Reload and verify changes
        config_manager.reload_config()
        assert config_manager.app.title == "Modified Title"
        assert config_manager.app.title != original_title
    
    def test_attribute_delegation(self):
        """Test attribute delegation to the underlying Config object."""
        with patch('os.path.exists', return_value=False):
            config_manager = ConfigManager()
            # Access attributes via delegation
            assert config_manager.app is config_manager._config.app
            assert config_manager.logging is config_manager._config.logging
            assert config_manager.services is config_manager._config.services


class TestConfigModels:
    """Test cases for the configuration model classes."""
    
    def test_logging_config_validation(self):
        """Test validation in LoggingConfig."""
        # Valid log level
        valid_config = LoggingConfig(level="DEBUG")
        assert valid_config.level == "DEBUG"
        
        # Invalid log level
        with pytest.raises(ValueError):
            LoggingConfig(level="INVALID_LEVEL")
    
    def test_config_defaults(self):
        """Test default values in Config models."""
        config = Config()
        assert config.app.debug is False
        assert config.app.title == "Universal App"
        assert config.logging.level == "INFO"
        assert config.services.r_integration.enabled is True
        assert config.services.actuarial.data_dir == "data/actuarial"
    
    def test_config_override(self):
        """Test overriding default values."""
        config = Config(
            app={"debug": True, "title": "Custom App"},
            logging={"level": "ERROR"},
            services={"r_integration": {"enabled": False}}
        )
        assert config.app.debug is True
        assert config.app.title == "Custom App"
        assert config.logging.level == "ERROR"
        assert config.services.r_integration.enabled is False
        
        # Verify other defaults remain
        assert config.app.version == "1.0.0"
        assert config.services.actuarial.enabled is True