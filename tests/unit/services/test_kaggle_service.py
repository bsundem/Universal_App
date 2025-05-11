"""
Unit tests for the Kaggle service.
"""
import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from services.kaggle.kaggle_service import KaggleService


class TestKaggleService:
    """Test cases for the KaggleService class."""

    @pytest.fixture
    def kaggle_service(self):
        """Fixture to create a Kaggle service for testing."""
        with patch('importlib.util.find_spec') as mock_find_spec:
            # Pretend that the kaggle module is available
            mock_find_spec.return_value = MagicMock()
            service = KaggleService()
            return service

    def test_check_api_credentials_no_file(self, kaggle_service, monkeypatch):
        """Test checking API credentials when no file exists."""
        # Mock os.path.exists to return False
        monkeypatch.setattr(os.path, 'exists', lambda path: False)
        
        # Call the method
        result = kaggle_service.check_api_credentials()
        
        # Check the result
        assert result is False

    def test_check_api_credentials_valid_file(self, kaggle_service, monkeypatch, tmp_path):
        """Test checking API credentials with a valid file."""
        # Create a temporary credential file
        temp_file = tmp_path / "kaggle.json"
        with open(temp_file, 'w') as f:
            json.dump({"username": "test_user", "key": "test_key"}, f)
        
        # Mock os.path.exists and open
        monkeypatch.setattr(os.path, 'exists', lambda path: True)
        monkeypatch.setattr(os.path, 'expanduser', lambda path: str(temp_file))
        
        # Call the method
        result = kaggle_service.check_api_credentials()
        
        # Check the result
        assert result is True

    def test_setup_credentials(self, kaggle_service, monkeypatch, tmp_path):
        """Test setting up credentials."""
        # Create a temporary directory
        temp_dir = tmp_path / ".kaggle"
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / "kaggle.json"
        
        # Mock os.path.expanduser, os.makedirs, and os.chmod
        monkeypatch.setattr(os.path, 'expanduser', lambda path: str(temp_dir))
        monkeypatch.setattr(os, 'makedirs', lambda path, exist_ok: None)
        monkeypatch.setattr(os, 'chmod', lambda path, mode: None)
        
        # Call the method
        result = kaggle_service.setup_credentials("test_user", "test_key")
        
        # Check the result
        assert result is True
        
        # Verify the file was created correctly
        with open(temp_file, 'r') as f:
            credentials = json.load(f)
            assert credentials == {"username": "test_user", "key": "test_key"}

    @patch('services.kaggle.kaggle_service.importlib.util.find_spec')
    @patch('threading.Thread')
    def test_search_datasets_async(self, mock_thread, mock_find_spec, kaggle_service):
        """Test asynchronous dataset search."""
        # Setup
        mock_find_spec.return_value = MagicMock()
        mock_callback = MagicMock()
        
        # Call the method
        kaggle_service.search_datasets_async(
            callback=mock_callback,
            search_term="test",
            max_size_mb=100,
            max_results=10
        )
        
        # Check that thread was started with the correct args
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        
        # Check that daemon was set
        assert mock_thread.return_value.daemon is True