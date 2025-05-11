"""
Unit tests for the KagglePage UI component.
"""
import pytest
from unittest.mock import patch, MagicMock
import tkinter as tk

from ui.pages.kaggle_page import KagglePage


@pytest.mark.container
class TestKagglePage:
    """Test cases for the KagglePage class."""
    
    @pytest.fixture
    def kaggle_page(self, tk_root, mock_kaggle_service, mock_kaggle_data_manager):
        """Create a KagglePage instance for testing."""
        # Create a frame to hold the page
        frame = tk.Frame(tk_root)
        
        # Create a mock controller
        controller = MagicMock()
        
        # Create the page
        page = KagglePage(frame, controller)
        
        return page
    
    def test_init(self, kaggle_page, mock_kaggle_service):
        """Test KagglePage initialization."""
        # Check that the page has a reference to the kaggle service
        assert kaggle_page.kaggle_service is not None
        
        # Check that the temperature directory is set correctly
        assert kaggle_page.temp_dir == mock_kaggle_service.temp_dir
    
    def test_check_credentials(self, kaggle_page):
        """Test credentials check during initialization."""
        # The setup_ui method should have been called during initialization
        # and it should have checked API credentials
        assert kaggle_page.kaggle_service.check_api_credentials.called
    
    def test_save_credentials(self, kaggle_page):
        """Test saving credentials."""
        # Set up test data
        kaggle_page.username_var = MagicMock()
        kaggle_page.username_var.get.return_value = "test_user"
        kaggle_page.key_var = MagicMock()
        kaggle_page.key_var.get.return_value = "test_key"
        
        # Mock the setup_main_ui method to prevent UI updates
        kaggle_page.setup_main_ui = MagicMock()
        
        # Mock the messagebox module
        with patch("ui.pages.kaggle_page.messagebox") as mock_messagebox:
            # Call the method
            kaggle_page.save_credentials()
            
            # Verify the service was called correctly
            kaggle_page.kaggle_service.setup_credentials.assert_called_once_with("test_user", "test_key")
            
            # Verify a success message was shown
            mock_messagebox.showinfo.assert_called_once()
            
            # Verify the main UI was set up
            kaggle_page.setup_main_ui.assert_called_once()
    
    def test_search_datasets(self, kaggle_page):
        """Test searching for datasets."""
        # Set up mock variables and objects
        kaggle_page.search_var = MagicMock()
        kaggle_page.search_var.get.return_value = "test"
        kaggle_page.max_size_var = MagicMock()
        kaggle_page.max_size_var.get.return_value = "100"
        kaggle_page.max_results_var = MagicMock()
        kaggle_page.max_results_var.get.return_value = "20"
        kaggle_page.file_type_var = MagicMock()
        kaggle_page.file_type_var.get.return_value = "csv"
        
        # Mock the dataset_tree
        kaggle_page.dataset_tree = MagicMock()
        kaggle_page.dataset_tree.get_children.return_value = []
        
        # Mock the update_idletasks method
        kaggle_page.update_idletasks = MagicMock()
        
        # Mock the after method
        kaggle_page.after = MagicMock()
        
        # Call the method
        kaggle_page.search_datasets()
        
        # Verify the service was called correctly
        kaggle_page.kaggle_service.search_datasets_async.assert_called_once()
        
        # Get the callback and kwargs
        callback = kaggle_page.kaggle_service.search_datasets_async.call_args[1]["callback"]
        search_term = kaggle_page.kaggle_service.search_datasets_async.call_args[1]["search_term"]
        max_size = kaggle_page.kaggle_service.search_datasets_async.call_args[1]["max_size_mb"]
        file_type = kaggle_page.kaggle_service.search_datasets_async.call_args[1]["file_type"]
        max_results = kaggle_page.kaggle_service.search_datasets_async.call_args[1]["max_results"]
        
        # Verify the parameters
        assert search_term == "test"
        assert max_size == 100
        assert file_type == "csv"
        assert max_results == 20
    
    def test_export_data(self, kaggle_page):
        """Test exporting data."""
        # Set up mock current DataFrame
        kaggle_page.current_df = MagicMock()
        
        # Mock the filedialog module to return a file path
        with patch("ui.pages.kaggle_page.filedialog") as mock_filedialog:
            mock_filedialog.asksaveasfilename.return_value = "/tmp/test.csv"
            
            # Mock the messagebox module
            with patch("ui.pages.kaggle_page.messagebox") as mock_messagebox:
                # Call the method
                kaggle_page.export_data()
                
                # Verify the data manager was called correctly
                assert kaggle_page.kaggle_data_manager.export_dataframe.called
                
                # Verify a success message was shown
                mock_messagebox.showinfo.assert_called_once()