"""
Unit tests for the R service using the dependency injection container.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

# Import container and service
from services.container import get_r_service


@pytest.mark.container
@pytest.mark.r_dependent
class TestRServiceContainer:
    """Test cases for the RService class using the container."""
    
    def test_is_available(self, mock_r_service):
        """Test checking if R is available using the container."""
        # Get service from container (will be our mock)
        r_service = get_r_service()
        
        # Call the method
        result = r_service.is_available()
        
        # Verify the mock was called
        mock_r_service.is_available.assert_called_once()
        
        # Check the result
        assert result is True
    
    def test_execute_script(self, mock_r_service):
        """Test executing a script using the container."""
        # Get service from container (will be our mock)
        r_service = get_r_service()
        
        # Call the method
        result = r_service.execute_script("test_script.R")
        
        # Verify the mock was called correctly
        mock_r_service.execute_script.assert_called_once_with("test_script.R")
        
        # Check the result
        assert result is True
    
    def test_call_function(self, mock_r_service):
        """Test calling an R function using the container."""
        # Get service from container (will be our mock)
        r_service = get_r_service()
        
        # Test data
        test_args = {"arg1": "value1", "arg2": 123}
        
        # Call the method
        result = r_service.call_function("test_function", **test_args)
        
        # Verify the mock was called correctly
        mock_r_service.call_function.assert_called_once_with("test_function", **test_args)
        
        # Check the result
        assert result == "R result"
    
    def test_set_variable(self, mock_r_service):
        """Test setting an R variable using the container."""
        # Get service from container (will be our mock)
        r_service = get_r_service()
        
        # Call the method
        result = r_service.set_variable("test_var", "test_value")
        
        # Verify the mock was called correctly
        mock_r_service.set_variable.assert_called_once_with("test_var", "test_value")
        
        # Check the result
        assert result is True
    
    def test_get_variable(self, mock_r_service):
        """Test getting an R variable using the container."""
        # Get service from container (will be our mock)
        r_service = get_r_service()
        
        # Call the method
        result = r_service.get_variable("test_var")
        
        # Verify the mock was called correctly
        mock_r_service.get_variable.assert_called_once_with("test_var")
        
        # Check the result
        assert result == "R variable"