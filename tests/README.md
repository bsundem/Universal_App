# Testing Framework

This directory contains tests for the Universal App, organized by test type and component. The framework uses pytest and is designed to work with the application's dependency injection architecture.

## Test Structure

```
tests/
├── unit/              # Unit tests (testing individual components in isolation)
│   ├── core/          # Tests for core application functionality
│   ├── services/      # Tests for service layer components
│   └── ui/            # Tests for user interface components
├── integration/       # Integration tests (testing interactions between components)
├── functional/        # Functional tests (testing the system as a whole)
├── conftest.py        # Shared pytest fixtures and dependency injection setup
└── README.md          # This file
```

## Test Categories

### Unit Tests

Unit tests focus on testing individual components in isolation, mocking all dependencies. These tests should be:
- Fast: Execute quickly
- Isolated: Not depend on external systems
- Deterministic: Same result each time they run

### Integration Tests

Integration tests verify that different components work together correctly. They test the interfaces between components and may involve:
- Testing service interactions
- Database interactions
- File system interactions

### Functional Tests

Functional tests verify that the entire system works correctly from a user perspective. These might include:
- UI workflow tests
- End-to-end feature tests
- Scenario-based tests

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test category:

```bash
# Run only unit tests
pytest tests/unit

# Run only tests for services
pytest tests/unit/services
```

To run tests with specific markers:

```bash
# Run tests that don't require R
pytest -k "not r_dependent"

# Run only slow tests
pytest -m "slow"
```

## Test Markers

Tests can be marked with the following markers to categorize them:

- `unit`: Unit tests
- `integration`: Integration tests
- `functional`: Functional tests
- `container`: Tests that use the dependency injection container
- `slow`: Tests that take a long time to run
- `r_dependent`: Tests that require R to be installed
- `kaggle_dependent`: Tests that require Kaggle credentials
- `network`: Tests that require network access

Example of marking a test:

```python
import pytest

@pytest.mark.slow
@pytest.mark.r_dependent
def test_something_slow_with_r():
    # Test code here
    pass

@pytest.mark.container
def test_with_dependency_injection(mock_r_service):
    # This test uses the dependency injection container
    # and the mock_r_service fixture
    pass
```

## Fixtures

Common fixtures are defined in `conftest.py`, including:

### Dependency Injection Fixtures

- `reset_container`: Resets the DI container before and after each test
- `mock_r_service`: A mock of the R service
- `mock_actuarial_service`: A mock of the actuarial service
- `mock_actuarial_data_manager`: A mock of the actuarial data manager
- `mock_kaggle_service`: A mock of the Kaggle service
- `mock_kaggle_data_manager`: A mock of the Kaggle data manager

These fixtures automatically work with both direct access and interface-based resolution:

```python
# Test with direct access
def test_direct_access(mock_r_service):
    service = get_r_service()
    assert service is mock_r_service

# Test with interface-based resolution
def test_interface_resolution(mock_r_service):
    from services.interfaces.r_service import RServiceInterface
    service = get_service_by_interface(RServiceInterface)
    assert service is mock_r_service
```

You can also reset specific providers:

```python
from services.container import reset_single_provider

# Reset just one service
reset_single_provider("r_service")
```

### UI Testing Fixtures

- `tk_root`: A Tkinter root window for UI testing
- `mock_matplotlib`: Mocks matplotlib to avoid display issues in tests

### Miscellaneous Fixtures

- `mock_pandas`: Mocks pandas for testing without data processing
- `temp_dir`: A temporary directory for file operations

## Writing Tests

### Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`

### Best Practices

1. **Independence**: Each test should be independent of other tests
2. **Arrangement**: Clearly separate test setup, execution, and assertion phases
3. **Assertions**: Make specific assertions rather than general ones
4. **Mocking**: Use the DI container's override mechanism for mocking
5. **Coverage**: Aim for high test coverage, especially of critical code paths
6. **Isolation**: Test components in isolation using the container's mock services
7. **Reset State**: Use the `reset_container` fixture to clean up after tests
8. **Test Both Success and Failure**: Verify both success and error scenarios

### Example Test Structures

#### Testing with the Container

```python
import pytest
from unittest.mock import MagicMock
from services.container import (
    get_r_service,
    get_service_by_interface,
    get_all_services_by_interface,
    override_provider,
    reset_overrides,
    reset_single_provider
)
from services.interfaces.r_service import RServiceInterface

@pytest.mark.container
class TestRServiceContainer:
    """Test the R service using the DI container."""

    def test_is_available(self, mock_r_service):
        """Test checking if R is available."""
        # Get the service through the container (will be the mock)
        r_service = get_r_service()

        # Set up the mock behavior
        mock_r_service.is_available.return_value = True

        # Act
        result = r_service.is_available()

        # Assert
        mock_r_service.is_available.assert_called_once()
        assert result is True

    def test_interface_resolution(self, mock_r_service):
        """Test resolving service by interface."""
        # Get service by interface type
        r_service = get_service_by_interface(RServiceInterface)

        # Verify it's our mock
        assert r_service is mock_r_service

        # Use the service
        mock_r_service.execute_script.return_value = "success"
        result = r_service.execute_script("test.R")
        assert result == "success"

    def test_multiple_implementations(self):
        """Test working with multiple implementations."""
        # Create two mock loggers
        mock_basic_logger = MagicMock()
        mock_advanced_logger = MagicMock()

        # Override both implementations
        from services.interfaces.logging import LoggerInterface
        override_provider("basic_logger", mock_basic_logger)
        override_provider("advanced_logger", mock_advanced_logger)

        try:
            # Get all logger implementations
            loggers = get_all_services_by_interface(LoggerInterface)

            # Verify we have both
            assert len(loggers) == 2
            assert "basic_logger" in loggers
            assert "advanced_logger" in loggers

            # Use all loggers
            for name, logger in loggers.items():
                logger.log("Test message")

            # Verify both were called
            mock_basic_logger.log.assert_called_with("Test message")
            mock_advanced_logger.log.assert_called_with("Test message")

            # Reset just one logger
            reset_single_provider("basic_logger")

            # Advanced logger should still be mocked
            get_service_by_interface(LoggerInterface).log("Still mocked")
            mock_advanced_logger.log.assert_called_with("Still mocked")
        finally:
            # Reset all services
            reset_overrides()
```

#### Testing UI Components

```python
import pytest
from unittest.mock import MagicMock
from tkinter import ttk
from ui.pages.some_page import SomePage

@pytest.mark.container
class TestSomePage:
    """Test cases for SomePage."""

    @pytest.fixture
    def some_page(self, tk_root, mock_r_service):
        """Create a SomePage instance with mocked dependencies."""
        # The page will get the mock_r_service from the container
        controller = MagicMock()
        page = SomePage(tk_root, controller)
        return page

    def test_perform_calculation(self, some_page, mock_r_service):
        """Test calculation using the R service."""
        # Arrange
        mock_r_service.call_function.return_value = "expected result"

        # Act
        some_page.calculate_button.invoke()

        # Assert
        mock_r_service.call_function.assert_called_once()
        assert some_page.result_label.cget("text") == "expected result"
```

#### Testing Error Handling

```python
import pytest
from unittest.mock import MagicMock
from services.container import get_r_service
from utils.error_handling import ServiceError

@pytest.mark.container
def test_error_handling(mock_r_service):
    """Test error handling in the R service."""
    # Arrange
    mock_r_service.execute_script.side_effect = ServiceError(
        "Failed to execute script",
        service="R",
        operation="execute_script"
    )

    # Act with expected exception
    with pytest.raises(ServiceError) as excinfo:
        get_r_service().execute_script("test.R")

    # Assert exception details
    assert "Failed to execute script" in str(excinfo.value)
    assert excinfo.value.service == "R"
```