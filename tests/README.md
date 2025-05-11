# Testing Framework

This directory contains tests for the Universal App, organized by test type and component.

## Test Structure

```
tests/
├── unit/              # Unit tests (testing individual components in isolation)
│   ├── core/          # Tests for core application functionality
│   ├── services/      # Tests for service layer components
│   └── ui/            # Tests for user interface components
├── integration/       # Integration tests (testing interactions between components)
├── functional/        # Functional tests (testing the system as a whole)
├── conftest.py        # Shared pytest fixtures and configuration
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
- `slow`: Tests that take a long time to run
- `r_dependent`: Tests that require R to be installed
- `network`: Tests that require network access

Example of marking a test:

```python
import pytest

@pytest.mark.slow
@pytest.mark.r_dependent
def test_something_slow_with_r():
    # Test code here
    pass
```

## Fixtures

Common fixtures are defined in `conftest.py`, including:

- `tk_root`: A Tkinter root window for UI testing
- `temp_dir`: A temporary directory for file operations
- `mock_r_service`: A mock of the R service for testing without R

## Writing Tests

### Naming Conventions

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test methods should be named `test_*`

### Best Practices

1. **Independence**: Each test should be independent of other tests
2. **Arrangement**: Clearly separate test setup, execution, and assertion phases
3. **Assertions**: Make specific assertions rather than general ones
4. **Mocking**: Use mocks for external dependencies, not for the code under test
5. **Coverage**: Aim for high test coverage, especially of critical code paths

### Example Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock

class TestSomeService:
    """Test cases for SomeService."""

    @pytest.fixture
    def some_service(self):
        """Fixture to create a service for testing."""
        # Setup code
        service = SomeService()
        return service

    def test_some_method(self, some_service):
        """Test the behavior of some_method."""
        # Arrange
        expected_result = "expected output"
        
        # Act
        result = some_service.some_method()
        
        # Assert
        assert result == expected_result
```