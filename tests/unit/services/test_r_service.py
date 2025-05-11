"""
Unit tests for the R service.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from services.r_service import RService


@pytest.mark.r_dependent
class TestRService:
    """Test cases for the RService class."""

    @pytest.fixture
    def r_service(self):
        """Fixture to create an R service for testing."""
        with patch('importlib.util.find_spec') as mock_find_spec:
            # Pretend that rpy2 is available
            mock_find_spec.return_value = MagicMock()
            
            # Mock rpy2 modules
            with patch.dict('sys.modules', {
                'rpy2': MagicMock(),
                'rpy2.robjects': MagicMock(),
                'rpy2.robjects.pandas2ri': MagicMock(),
                'rpy2.robjects.packages': MagicMock()
            }):
                # Mock rpy2.robjects
                with patch('services.r_service.robjects') as mock_robjects:
                    # Setup r to return a value when called
                    mock_robjects.r.return_value = "R result"
                    
                    # Create the service
                    service = RService()
                    service.r_available = True  # Force availability
                    
                    # Store the mock for assertions
                    service._mock_robjects = mock_robjects
                    
                    yield service

    def test_is_available(self, r_service):
        """Test checking if R is available."""
        assert r_service.is_available() is True

    def test_execute_script_not_found(self, r_service, monkeypatch):
        """Test executing a script that doesn't exist."""
        # Mock os.path.exists to return False
        monkeypatch.setattr(os.path, 'exists', lambda path: False)

        # Import the ServiceError
        from utils.error_handling import ServiceError

        # Call the method - should raise ServiceError
        with pytest.raises(ServiceError) as excinfo:
            r_service.execute_script("nonexistent.R")

        # Check the error message contains the expected text
        assert "not found" in str(excinfo.value)

    def test_execute_script_success(self, r_service, monkeypatch):
        """Test successfully executing a script."""
        # Mock os.path.exists to return True
        monkeypatch.setattr(os.path, 'exists', lambda path: True)
        
        # Call the method
        result = r_service.execute_script("test.R")
        
        # Check that r() was called with the correct script
        r_service._mock_robjects.r.assert_called()
        assert "source" in r_service._mock_robjects.r.call_args[0][0]
        
        # Check the result
        assert result is not None

    def test_run_r_code(self, r_service):
        """Test running R code."""
        # Call the method
        result = r_service.run_r_code("1 + 1")
        
        # Check that r() was called with the correct code
        r_service._mock_robjects.r.assert_called_with("1 + 1")
        
        # Check the result
        assert result == "R result"

    def test_set_variable(self, r_service):
        """Test setting a variable in R."""
        # Setup
        r_service._mock_robjects.StrVector = MagicMock(return_value="string vector")
        r_service._mock_robjects.FloatVector = MagicMock(return_value="float vector")
        r_service._mock_robjects.BoolVector = MagicMock(return_value="bool vector")
        
        # Test with different types
        assert r_service.set_variable("str_var", "test") is True
        assert r_service.set_variable("int_var", 123) is True
        assert r_service.set_variable("float_var", 123.45) is True
        assert r_service.set_variable("bool_var", True) is True
        
        # Check that the right vector types were created
        r_service._mock_robjects.StrVector.assert_called_with(["test"])
        r_service._mock_robjects.FloatVector.assert_any_call([123])
        r_service._mock_robjects.FloatVector.assert_any_call([123.45])
        r_service._mock_robjects.BoolVector.assert_called_with([True])
        
        # Check that assign was called
        assert r_service._mock_robjects.r.assign.call_count == 4

    def test_call_function(self, r_service):
        """Test calling an R function."""
        # Call the method
        result = r_service.call_function("test_func", arg1="value1", arg2=123)
        
        # Check that set_variable was used for each argument
        assert r_service._mock_robjects.r.assign.call_count >= 2
        
        # Check that the function was called
        r_service._mock_robjects.r.assert_called_with("test_func(arg1, arg2)")
        
        # Check the result
        assert result == "R result"
        
    def test_get_script_path(self, r_service):
        """Test getting the path to an R script."""
        # Call the method
        path = r_service.get_script_path("test.R")
        
        # Check the result
        assert "r_scripts" in path
        assert path.endswith("test.R")