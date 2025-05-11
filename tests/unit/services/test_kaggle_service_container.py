"""
Unit tests for the Kaggle service using the dependency injection container.
"""
import pytest
from unittest.mock import patch, MagicMock, call

# Import container and services
from services.container import get_kaggle_service, get_kaggle_data_manager


@pytest.mark.container
@pytest.mark.kaggle_dependent
class TestKaggleServiceContainer:
    """Test cases for the KaggleService class using the container."""
    
    def test_check_api_credentials(self, mock_kaggle_service):
        """Test checking API credentials."""
        # Get service from container (will be our mock)
        kaggle_service = get_kaggle_service()
        
        # Call the method
        result = kaggle_service.check_api_credentials()
        
        # Verify the mock was called
        mock_kaggle_service.check_api_credentials.assert_called_once()
        
        # Check the result
        assert result is True
    
    def test_setup_credentials(self, mock_kaggle_service):
        """Test setting up credentials."""
        # Get service from container (will be our mock)
        kaggle_service = get_kaggle_service()
        
        # Test parameters
        username = "test_user"
        key = "test_key"
        
        # Call the method
        result = kaggle_service.setup_credentials(username, key)
        
        # Verify the mock was called correctly
        mock_kaggle_service.setup_credentials.assert_called_once_with(username, key)
        
        # Check the result
        assert result is True
    
    def test_search_datasets_async(self, mock_kaggle_service):
        """Test searching datasets asynchronously."""
        # Get service from container (will be our mock)
        kaggle_service = get_kaggle_service()
        
        # Create a mock callback
        callback = MagicMock()
        
        # Test parameters
        test_params = {
            "search_term": "test",
            "max_size_mb": 100,
            "file_type": "csv",
            "max_results": 20
        }
        
        # Call the method
        kaggle_service.search_datasets_async(callback, **test_params)
        
        # Verify the mock was called correctly
        mock_kaggle_service.search_datasets_async.assert_called_once()
        
        # Extract the callback and kwargs from the call
        _, called_kwargs = mock_kaggle_service.search_datasets_async.call_args
        assert called_kwargs.get("search_term") == "test"
        assert called_kwargs.get("max_size_mb") == 100
        assert called_kwargs.get("file_type") == "csv"
        assert called_kwargs.get("max_results") == 20
        
        # Check that our callback was called with the expected data
        callback.assert_called_once()
        datasets = callback.call_args[0][0]
        assert len(datasets) == 1
        assert datasets[0]["title"] == "Test Dataset"
    
    def test_get_dataset_files_async(self, mock_kaggle_service):
        """Test getting dataset files asynchronously."""
        # Get service from container (will be our mock)
        kaggle_service = get_kaggle_service()
        
        # Create a mock callback
        callback = MagicMock()
        
        # Test parameters
        dataset_ref = "test/dataset"
        
        # Call the method
        kaggle_service.get_dataset_files_async(callback, dataset_ref)
        
        # Verify the mock was called correctly
        mock_kaggle_service.get_dataset_files_async.assert_called_once()
        
        # Check that our callback was called with the expected data
        callback.assert_called_once()
        files = callback.call_args[0][0]
        assert len(files) == 1
        assert files[0]["name"] == "data.csv"
    
    def test_download_and_load_file_async(self, mock_kaggle_service):
        """Test downloading and loading a file asynchronously."""
        # Get service from container (will be our mock)
        kaggle_service = get_kaggle_service()
        
        # Create a mock callback
        callback = MagicMock()
        
        # Test parameters
        dataset_ref = "test/dataset"
        filename = "data.csv"
        output_dir = "/tmp/test"
        
        # Call the method
        kaggle_service.download_and_load_file_async(callback, dataset_ref, filename, output_dir)
        
        # Verify the mock was called correctly
        mock_kaggle_service.download_and_load_file_async.assert_called_once()
        
        # Check that our callback was called
        callback.assert_called_once()


@pytest.mark.container
class TestKaggleDataManagerContainer:
    """Test cases for the KaggleDataManager class using the container."""
    
    def test_check_dependencies(self, mock_kaggle_data_manager):
        """Test checking dependencies."""
        # Get service from container (will be our mock)
        data_manager = get_kaggle_data_manager()
        
        # Call the method
        result = data_manager.check_dependencies()
        
        # Verify the mock was called
        mock_kaggle_data_manager.check_dependencies.assert_called_once()
        
        # Check the result structure
        assert "pandas" in result
        assert "matplotlib" in result
        assert result["pandas"] is True
    
    def test_get_dataframe_info(self, mock_kaggle_data_manager):
        """Test getting DataFrame information."""
        # Get service from container (will be our mock)
        data_manager = get_kaggle_data_manager()
        
        # Create a mock DataFrame
        mock_df = MagicMock()
        
        # Call the method
        result = data_manager.get_dataframe_info(mock_df)
        
        # Verify the mock was called correctly
        mock_kaggle_data_manager.get_dataframe_info.assert_called_once_with(mock_df)
        
        # Check the result structure
        assert "rows" in result
        assert "columns" in result
        assert "dtypes" in result
    
    def test_export_dataframe(self, mock_kaggle_data_manager):
        """Test exporting a DataFrame."""
        # Get service from container (will be our mock)
        data_manager = get_kaggle_data_manager()
        
        # Create a mock DataFrame
        mock_df = MagicMock()
        file_path = "/tmp/test.csv"
        
        # Call the method
        result = data_manager.export_dataframe(mock_df, file_path)
        
        # Verify the mock was called correctly
        mock_kaggle_data_manager.export_dataframe.assert_called_once_with(mock_df, file_path)
        
        # Check the result structure
        assert "success" in result
        assert result["success"] is True
    
    def test_generate_plot_data(self, mock_kaggle_data_manager):
        """Test generating plot data."""
        # Get service from container (will be our mock)
        data_manager = get_kaggle_data_manager()
        
        # Create a mock DataFrame
        mock_df = MagicMock()
        
        # Test parameters
        chart_type = "Bar Chart"
        x_column = "Category"
        y_column = "Value"
        
        # Call the method
        result = data_manager.generate_plot_data(mock_df, chart_type, x_column, y_column)
        
        # Verify the mock was called correctly
        mock_kaggle_data_manager.generate_plot_data.assert_called_once_with(
            mock_df, chart_type, x_column, y_column
        )
        
        # Check the result structure
        assert "data" in result
        assert "labels" in result["data"]
        assert "values" in result["data"]