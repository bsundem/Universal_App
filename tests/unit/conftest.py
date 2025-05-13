"""
Common test fixtures for unit tests.

This module provides fixtures that can be used across all unit tests
to ensure consistent testing patterns.
"""
import os
import json
import pytest
import tempfile
from unittest.mock import MagicMock, patch

from core.config import Config, ConfigManager
from services.container import Container, ContainerManager
from services.r_service import RService
from services.actuarial.actuarial_service import ActuarialService
from services.finance.finance_service import FinanceService


@pytest.fixture
def sample_config_dict():
    """Provide a sample configuration dictionary."""
    return {
        "app": {
            "debug": True,
            "title": "Test App",
            "version": "1.0.0-test"
        },
        "logging": {
            "level": "DEBUG",
            "file": "test.log"
        },
        "services": {
            "r_integration": {
                "enabled": True,
                "scripts_dir": "test_scripts"
            },
            "actuarial": {
                "enabled": True,
                "data_dir": "test_data/actuarial"
            },
            "finance": {
                "enabled": True,
                "data_dir": "test_data/finance"
            }
        },
        "ui": {
            "window": {
                "title": "Test Window",
                "width": 1000,
                "height": 600
            }
        }
    }


@pytest.fixture
def temp_config_file(sample_config_dict):
    """Create a temporary config file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    
    with open(temp_file.name, 'w') as f:
        json.dump(sample_config_dict, f)
    
    yield temp_file.name
    
    # Cleanup temporary file
    os.unlink(temp_file.name)


@pytest.fixture
def config(sample_config_dict):
    """Provide a Config instance."""
    return Config(**sample_config_dict)


@pytest.fixture
def config_manager(temp_config_file):
    """Provide a ConfigManager instance."""
    return ConfigManager(temp_config_file)


@pytest.fixture
def mock_r_service():
    """Provide a mock R service."""
    mock = MagicMock(spec=RService)
    mock.is_available.return_value = True
    mock.execute_script.return_value = True
    mock.call_function.return_value = MagicMock()
    mock.run_r_code.return_value = MagicMock()
    mock.set_variable.return_value = True
    mock.get_variable.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_actuarial_service():
    """Provide a mock actuarial service."""
    mock = MagicMock(spec=ActuarialService)
    mock.is_r_available.return_value = True
    mock.calculate_mortality_data.return_value = MagicMock()
    mock.calculate_present_value.return_value = {
        'present_value': 100000.0,
        'expected_duration': 15.3,
        'monthly_equivalent': 550.0
    }
    mock.get_available_mortality_tables.return_value = [
        {"id": "table1", "name": "Table 1", "description": "Test table 1"},
        {"id": "table2", "name": "Table 2", "description": "Test table 2"}
    ]
    return mock


@pytest.fixture
def mock_finance_service():
    """Provide a mock finance service."""
    mock = MagicMock(spec=FinanceService)
    mock.is_r_available.return_value = True
    mock.calculate_yield_curve.return_value = MagicMock()
    mock.price_option.return_value = {
        'price': 25.32,
        'delta': 0.65,
        'gamma': 0.02,
        'theta': -0.15,
        'vega': 0.35
    }
    mock.calculate_portfolio_metrics.return_value = {
        'expected_return': 0.08,
        'volatility': 0.12,
        'sharpe_ratio': 0.67
    }
    return mock


@pytest.fixture
def container():
    """Provide a dependency injection container."""
    container = Container()
    container.config.from_dict({
        'services': {
            'r_integration': {'scripts_dir': 'test_scripts', 'enabled': True},
            'actuarial': {'data_dir': 'test_actuarial_data', 'enabled': True},
            'finance': {'data_dir': 'test_finance_data', 'enabled': True}
        }
    })
    return container


@pytest.fixture
def container_manager(container, mock_r_service, mock_actuarial_service, mock_finance_service):
    """Provide a container manager with mock services."""
    manager = ContainerManager()
    
    # Override the container with our test container
    manager._container = container
    
    # Override services with mocks
    manager.override_provider('r_service', mock_r_service)
    manager.override_provider('actuarial_service', mock_actuarial_service)
    manager.override_provider('finance_service', mock_finance_service)
    
    return manager


@pytest.fixture
def tk_frame():
    """Provide a mock tkinter Frame."""
    mock = MagicMock()
    mock.grid = MagicMock()
    mock.grid_remove = MagicMock()
    mock.grid_columnconfigure = MagicMock()
    mock.grid_rowconfigure = MagicMock()
    mock.update_idletasks = MagicMock()
    mock.winfo_exists = MagicMock(return_value=True)
    return mock


@pytest.fixture
def ttk_mock():
    """Provide a mock ttk module."""
    mock = MagicMock()
    # Setup Frame mock
    mock.Frame = MagicMock(return_value=MagicMock())
    mock.Frame().grid = MagicMock()
    mock.Frame().grid_remove = MagicMock()
    mock.Frame().grid_columnconfigure = MagicMock()
    mock.Frame().grid_rowconfigure = MagicMock()
    
    # Setup Label, Button, etc.
    mock.Label = MagicMock(return_value=MagicMock())
    mock.Button = MagicMock(return_value=MagicMock())
    mock.Progressbar = MagicMock(return_value=MagicMock())
    mock.Separator = MagicMock(return_value=MagicMock())
    
    return mock