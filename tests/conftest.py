"""
Common test fixtures for pytest.

This module provides fixtures that can be used across all test modules.
"""
import pytest
from unittest.mock import MagicMock, patch
import os
import sys
import tkinter as tk

# Import container
from services.container import (
    container, 
    get_r_service, 
    get_actuarial_service, 
    get_actuarial_data_manager,
    get_kaggle_service, 
    get_kaggle_data_manager,
    override_provider,
    reset_overrides
)


@pytest.fixture(scope="function")
def reset_container():
    """Reset the container before and after each test."""
    # Reset before test
    reset_overrides()
    yield
    # Reset after test
    reset_overrides()


@pytest.fixture
def mock_r_service():
    """
    Provide a mocked R service.
    
    This fixture creates a mock R service and registers it with the container.
    """
    mock_service = MagicMock()
    mock_service.is_available.return_value = True
    mock_service.execute_script.return_value = True
    mock_service.call_function.return_value = "R result"
    mock_service.set_variable.return_value = True
    mock_service.get_variable.return_value = "R variable"
    
    # Override in the container
    override_provider("r_service", mock_service)
    
    yield mock_service
    
    # Reset is handled by reset_container fixture


@pytest.fixture
def mock_kaggle_service():
    """
    Provide a mocked Kaggle service.

    This fixture creates a mock Kaggle service and registers it with the container.
    """
    mock_service = MagicMock()
    mock_service.check_api_credentials.return_value = True
    mock_service.setup_credentials.return_value = True

    # Create proper callback implementations
    def mock_search_datasets_async(callback, **kwargs):
        callback([
            {"title": "Test Dataset", "ref": "test/dataset", "sizeMB": 10, "downloadCount": 100}
        ])
    mock_service.search_datasets_async.side_effect = mock_search_datasets_async

    def mock_get_dataset_files_async(callback, dataset_ref):
        callback([
            {"name": "data.csv", "sizeMB": 5}
        ])
    mock_service.get_dataset_files_async.side_effect = mock_get_dataset_files_async

    def mock_download_and_load_file_async(callback, dataset_ref, filename, output_dir=None):
        callback(MagicMock())  # Mock DataFrame
    mock_service.download_and_load_file_async.side_effect = mock_download_and_load_file_async

    mock_service.temp_dir = "/tmp/mock_kaggle"

    # Override in the container
    override_provider("kaggle_service", mock_service)

    yield mock_service


@pytest.fixture
def mock_kaggle_data_manager():
    """
    Provide a mocked Kaggle data manager.
    
    This fixture creates a mock Kaggle data manager and registers it with the container.
    """
    mock_manager = MagicMock()
    mock_manager.check_dependencies.return_value = {"pandas": True, "matplotlib": True}
    mock_manager.get_dataframe_info.return_value = {
        "rows": 100,
        "columns": 5,
        "memory_usage": 1.5,
        "dtypes": {"col1": "int64", "col2": "float64"}
    }
    mock_manager.export_dataframe.return_value = {"success": True, "rows": 100, "columns": 5}
    mock_manager.generate_plot_data.return_value = {"data": {"labels": ["A", "B"], "values": [1, 2]}}
    
    # Override in the container
    override_provider("kaggle_data_manager", mock_manager)
    
    yield mock_manager


@pytest.fixture
def mock_actuarial_service():
    """
    Provide a mocked actuarial service.
    
    This fixture creates a mock actuarial service and registers it with the container.
    """
    mock_service = MagicMock()
    mock_service.is_r_available.return_value = True
    mock_service.calculate_mortality_data.return_value = MagicMock()  # Mock DataFrame
    mock_service.calculate_present_value.return_value = {
        "present_value": 10000.0,
        "expected_duration": 20.5,
        "monthly_equivalent": 100.0
    }
    
    # Override in the container
    override_provider("actuarial_service", mock_service)
    
    yield mock_service


@pytest.fixture
def mock_actuarial_data_manager():
    """
    Provide a mocked actuarial data manager.
    
    This fixture creates a mock actuarial data manager and registers it with the container.
    """
    mock_manager = MagicMock()
    mock_manager.prepare_mortality_data_for_visualization.return_value = {
        "ages": [30, 40, 50],
        "mortality_rates": [0.001, 0.002, 0.003]
    }
    mock_manager.prepare_pv_data_for_visualization.return_value = {
        "present_value": "$10,000.00",
        "expected_duration": "20.50 years",
        "monthly_equivalent": "$100.00 / month",
        "summary": "Present Value: $10,000.00"
    }
    mock_manager.create_mortality_visualization.return_value = MagicMock()  # Mock Figure
    
    # Override in the container
    override_provider("actuarial_data_manager", mock_manager)
    
    yield mock_manager


@pytest.fixture
def tk_root():
    """Create a Tkinter root window for UI testing."""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
        yield root
    finally:
        # Destroy the window even if an exception was raised
        try:
            root.destroy()
        except:
            pass


@pytest.fixture
def mock_matplotlib():
    """Mock matplotlib to avoid display issues in tests."""
    with patch.dict('sys.modules', {
        'matplotlib': MagicMock(),
        'matplotlib.pyplot': MagicMock(),
        'matplotlib.figure': MagicMock(),
        'matplotlib.backends.backend_tkagg': MagicMock()
    }):
        yield


@pytest.fixture
def mock_pandas():
    """Mock pandas for testing without actual data processing."""
    with patch.dict('sys.modules', {
        'pandas': MagicMock(),
        'numpy': MagicMock()
    }):
        yield