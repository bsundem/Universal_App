"""
Tests for the R integration service in services/r_service.py.
"""
import os
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from services.r_service import RService
from utils.error_handling import ServiceError


@pytest.fixture
def mock_robjects():
    """Create a mock for rpy2.robjects."""
    with patch('services.r_service.robjects') as mock:
        # Setup basic mocks
        mock.r.return_value = MagicMock()
        mock.StrVector.return_value = MagicMock()
        mock.FloatVector.return_value = MagicMock()
        mock.BoolVector.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_importr():
    """Create a mock for rpy2.robjects.packages.importr."""
    with patch('services.r_service.importr') as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def r_service(mock_robjects, mock_importr):
    """Create an R service instance with mocked dependencies."""
    with patch('os.path.abspath') as mock_abspath:
        mock_abspath.return_value = '/test/path/to/r_scripts'
        return RService()


class TestRService:
    """Test cases for the RService class."""
    
    def test_init(self, r_service, mock_importr):
        """Test initialization of R service."""
        assert r_service.scripts_dir == '/test/path/to/r_scripts'
        
        # Check that base R packages were imported
        mock_importr.assert_any_call('base')
        mock_importr.assert_any_call('stats')
    
    def test_is_available_success(self, r_service, mock_robjects):
        """Test is_available method when R is available."""
        mock_robjects.r.return_value = [2]
        
        result = r_service.is_available()
        
        assert result is True
        mock_robjects.r.assert_called_with('1+1')
    
    def test_is_available_failure(self, r_service, mock_robjects):
        """Test is_available method when R is not available."""
        mock_robjects.r.side_effect = Exception("R not available")
        
        result = r_service.is_available()
        
        assert result is False
    
    def test_execute_script_success(self, r_service, mock_robjects):
        """Test execute_script method for successful execution."""
        with patch('os.path.exists', return_value=True):
            result = r_service.execute_script('test_script.R')
            
            assert result is True
            mock_robjects.r.assert_called_with('source("/test/path/to/r_scripts/test_script.R")')
    
    def test_execute_script_file_not_found(self, r_service):
        """Test execute_script method when file is not found."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(ServiceError) as excinfo:
                r_service.execute_script('nonexistent.R')
            
            assert "R script not found" in str(excinfo.value)
    
    def test_run_r_code(self, r_service, mock_robjects):
        """Test run_r_code method."""
        mock_robjects.r.return_value = "R result"
        
        result = r_service.run_r_code('print("Hello")')
        
        assert result == "R result"
        mock_robjects.r.assert_called_with('print("Hello")')
    
    def test_set_variable_string(self, r_service, mock_robjects):
        """Test set_variable method with string value."""
        result = r_service.set_variable('test_var', 'test_value')
        
        assert result is True
        mock_robjects.StrVector.assert_called_with(['test_value'])
        mock_robjects.r.assign.assert_called_once()
    
    def test_set_variable_number(self, r_service, mock_robjects):
        """Test set_variable method with numeric value."""
        result = r_service.set_variable('test_var', 42)
        
        assert result is True
        mock_robjects.FloatVector.assert_called_with([42])
        mock_robjects.r.assign.assert_called_once()
    
    def test_set_variable_boolean(self, r_service, mock_robjects):
        """Test set_variable method with boolean value."""
        result = r_service.set_variable('test_var', True)
        
        assert result is True
        mock_robjects.BoolVector.assert_called_with([True])
        mock_robjects.r.assign.assert_called_once()
    
    def test_set_variable_list(self, r_service, mock_robjects):
        """Test set_variable method with list value."""
        result = r_service.set_variable('test_var', [1, 2, 3])
        
        assert result is True
        mock_robjects.FloatVector.assert_called_with([1, 2, 3])
        mock_robjects.r.assign.assert_called_once()
    
    def test_set_variable_dataframe(self, r_service, mock_robjects):
        """Test set_variable method with DataFrame value."""
        with patch('services.r_service.pandas2ri.py2rpy') as mock_py2rpy:
            df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
            mock_py2rpy.return_value = "Converted DataFrame"
            
            result = r_service.set_variable('test_df', df)
            
            assert result is True
            mock_py2rpy.assert_called_once()
            mock_robjects.r.assign.assert_called_once()
    
    def test_set_variable_numpy_array(self, r_service, mock_robjects):
        """Test set_variable method with numpy array value."""
        with patch('services.r_service.numpy2ri.py2rpy') as mock_py2rpy:
            arr = np.array([1, 2, 3])
            mock_py2rpy.return_value = "Converted Array"
            
            result = r_service.set_variable('test_arr', arr)
            
            assert result is True
            mock_py2rpy.assert_called_once()
            mock_robjects.r.assign.assert_called_once()
    
    def test_set_variable_unsupported_mixed_list(self, r_service):
        """Test set_variable method with unsupported mixed type list."""
        with pytest.raises(ServiceError) as excinfo:
            r_service.set_variable('test_var', [1, 'string', True])
        
        assert "Mixed type lists are not supported" in str(excinfo.value)
    
    def test_call_function(self, r_service, mock_robjects):
        """Test call_function method."""
        # Setup mocks
        mock_robjects.r.return_value = "Function result"
        
        # Test calling a function with arguments
        result = r_service.call_function('test_func', arg1=1, arg2='test')
        
        assert result == "Function result"
        mock_robjects.r.assert_called_with('test_func(arg1, arg2)')
    
    def test_get_variable(self, r_service, mock_robjects):
        """Test get_variable method."""
        mock_robjects.r.return_value = "Variable value"
        
        result = r_service.get_variable('test_var')
        
        assert result == "Variable value"
        mock_robjects.r.assert_called_with('test_var')
    
    def test_get_dataframe_success(self, r_service, mock_robjects):
        """Test get_dataframe method for successful conversion."""
        with patch('services.r_service.pandas2ri.rpy2py') as mock_rpy2py:
            mock_df = pd.DataFrame({'a': [1, 2, 3]})
            mock_rpy2py.return_value = mock_df
            
            result = r_service.get_dataframe('test_data')
            
            assert result is mock_df
            mock_robjects.r.assert_called_with('test_data')
    
    def test_get_dataframe_conversion_failure(self, r_service, mock_robjects):
        """Test get_dataframe method when conversion fails."""
        with patch('services.r_service.pandas2ri.rpy2py') as mock_rpy2py:
            mock_rpy2py.side_effect = Exception("Conversion failed")
            
            with pytest.raises(ServiceError) as excinfo:
                r_service.get_dataframe('test_data')
            
            assert "Failed to convert R result to DataFrame" in str(excinfo.value)
    
    def test_get_dataframe_wrong_type(self, r_service, mock_robjects):
        """Test get_dataframe method when result is not a DataFrame."""
        with patch('services.r_service.pandas2ri.rpy2py') as mock_rpy2py:
            mock_rpy2py.return_value = "Not a DataFrame"
            
            with pytest.raises(ServiceError) as excinfo:
                r_service.get_dataframe('test_data')
            
            assert "Failed to convert R result to DataFrame" in str(excinfo.value)
    
    def test_get_script_path(self, r_service):
        """Test get_script_path method."""
        with patch('os.path.exists', return_value=True):
            result = r_service.get_script_path('test_dir/test_script.R')
            
            assert result == '/test/path/to/r_scripts/test_dir/test_script.R'
    
    def test_get_script_path_missing_directory(self, r_service):
        """Test get_script_path method with missing directory."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(ServiceError) as excinfo:
                r_service.get_script_path('test_dir/test_script.R')
            
            assert "Directory does not exist for script" in str(excinfo.value)