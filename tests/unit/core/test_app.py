"""
Unit tests for the core application.
"""
import pytest
from unittest.mock import patch, MagicMock
from core.app import Application, create_app


class TestApplication:
    """Test cases for the Application class."""

    def test_init(self):
        """Test initialization of the Application class."""
        with patch('tkinter.Tk') as mock_tk, \
             patch('tkinter.ttk.Style') as mock_style:
            # Setup
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Mock config
            with patch('core.app.config') as mock_config:
                # Create mock app config section
                mock_app_config = MagicMock()
                mock_app_config.title = "Universal App"
                mock_app_config.temp_dir = None
                mock_app_config.data_dir = None
                mock_app_config.theme = "default"
                
                # Set the app property on the mock config
                mock_config.app = mock_app_config
                
                # Mock the MainWindow
                with patch('core.app.MainWindow') as mock_main_window:
                    # Create the application
                    app = Application()
                    
                    # Check that Tk was initialized
                    mock_tk.assert_called_once()
                    
                    # Check that the window was configured
                    assert app.root == mock_root
                    assert app.root.title.call_args[0][0] == "Universal App"
                    assert app.root.geometry.call_args[0][0] == "900x600"
                    
                    # Check that the style was configured
                    mock_style_instance.theme_use.assert_called_once_with("default")
                    
                    # Check that MainWindow was created
                    mock_main_window.assert_called_once_with(mock_root)
                    
                    # Check that the grid was configured
                    mock_root.columnconfigure.assert_called_once_with(0, weight=1)
                    mock_root.rowconfigure.assert_called_once_with(0, weight=1)

    def test_run(self):
        """Test running the application."""
        with patch('tkinter.Tk') as mock_tk, \
             patch('tkinter.ttk.Style') as mock_style:
            # Setup
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            mock_style_instance = MagicMock()
            mock_style.return_value = mock_style_instance

            # Mock config
            with patch('core.app.config') as mock_config:
                # Create mock app config section
                mock_app_config = MagicMock()
                mock_app_config.title = "Universal App"
                mock_app_config.temp_dir = None
                mock_app_config.data_dir = None
                mock_app_config.theme = "default"
                
                # Set the app property on the mock config
                mock_config.app = mock_app_config
                
                # Mock the MainWindow
                with patch('core.app.MainWindow') as mock_main_window:
                    # Create the application
                    app = Application()
                    
                    # Run the application
                    result = app.run()
                    
                    # Check that mainloop was called
                    mock_root.mainloop.assert_called_once()
                    
                    # Check the return value
                    assert result == 0

    def test_create_app(self):
        """Test the create_app factory function."""
        with patch('core.app.Application') as mock_application:
            # Setup
            mock_app = MagicMock()
            mock_application.return_value = mock_app
            
            # Call the function
            app = create_app()
            
            # Check the result
            assert app == mock_app
            mock_application.assert_called_once()