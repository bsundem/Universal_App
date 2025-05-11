"""
Pytest configuration file with shared fixtures.
"""
import sys
import os
import pytest
import tkinter as tk
import tempfile
from unittest.mock import MagicMock

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))


# Check if R is available
def is_r_available():
    """Check if R and rpy2 are available."""
    try:
        import rpy2.robjects
        # Try to evaluate a simple R expression
        rpy2.robjects.r('1+1')
        return True
    except (ImportError, Exception):
        return False


# Skip tests that require R if it's not available
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "r_dependent: mark test as requiring R installation")


def pytest_runtest_setup(item):
    """Skip tests marked as r_dependent if R is not available."""
    if "r_dependent" in item.keywords and not is_r_available():
        pytest.skip("R and rpy2 are required for this test")


@pytest.fixture
def tk_root():
    """Fixture for creating a Tkinter root window."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    yield root
    root.update()  # Process any pending events
    root.destroy()  # Destroy the window after the test


@pytest.fixture
def temp_dir():
    """Fixture for creating a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_r_service():
    """Fixture for mocking the R service."""
    mock = MagicMock()
    mock.is_available.return_value = True
    mock.execute_script.return_value = True
    mock.run_r_code.return_value = True
    mock.call_function.return_value = MagicMock()
    return mock