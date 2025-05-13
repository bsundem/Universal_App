"""
Tests for the UI page container component in ui/components/page_container.py.
"""
import pytest
from unittest.mock import MagicMock, patch

import tkinter as tk
from tkinter import ttk

from ui.components.page_container import PageContainer


@pytest.fixture
def mock_tk_frame():
    """Create a mock for the tkinter Frame."""
    mock = MagicMock()
    mock.grid = MagicMock()
    mock.grid_remove = MagicMock()
    mock.grid_columnconfigure = MagicMock()
    mock.grid_rowconfigure = MagicMock()
    mock.update_idletasks = MagicMock()
    return mock


@pytest.fixture
def mock_tk_label():
    """Create a mock for the tkinter Label."""
    mock = MagicMock()
    mock.grid = MagicMock()
    return mock


@pytest.fixture
def mock_tk_button():
    """Create a mock for the tkinter Button."""
    mock = MagicMock()
    mock.grid = MagicMock()
    return mock


@pytest.fixture
def mock_tk_separator():
    """Create a mock for the tkinter Separator."""
    mock = MagicMock()
    mock.grid = MagicMock()
    return mock


@pytest.fixture
def mock_tkinter():
    """Mock all tkinter components."""
    with patch('ui.components.page_container.ttk') as mock_ttk:
        # Setup Frame mock
        mock_ttk.Frame = MagicMock(return_value=MagicMock())
        mock_ttk.Frame().winfo_exists.return_value = True
        mock_ttk.Frame().grid = MagicMock()
        mock_ttk.Frame().grid_remove = MagicMock()
        mock_ttk.Frame().grid_columnconfigure = MagicMock()
        mock_ttk.Frame().grid_rowconfigure = MagicMock()
        
        # Setup Label mock
        mock_ttk.Label = MagicMock(return_value=MagicMock())
        mock_ttk.Label().grid = MagicMock()
        
        # Setup Button mock
        mock_ttk.Button = MagicMock(return_value=MagicMock())
        mock_ttk.Button().grid = MagicMock()
        
        # Setup Separator mock
        mock_ttk.Separator = MagicMock(return_value=MagicMock())
        mock_ttk.Separator().grid = MagicMock()
        
        # Setup Progressbar mock
        mock_ttk.Progressbar = MagicMock(return_value=MagicMock())
        mock_ttk.Progressbar().pack = MagicMock()
        mock_ttk.Progressbar().start = MagicMock()
        mock_ttk.Progressbar().stop = MagicMock()
        
        with patch('ui.components.page_container.tk') as mock_tk:
            mock_tk.CENTER = 'center'
            yield mock_ttk


@pytest.fixture
def mock_error_handling():
    """Mock error handling utilities."""
    with patch('ui.components.page_container.report_error') as mock:
        yield mock


@pytest.fixture
def page_container(mock_tkinter, mock_error_handling):
    """Create a page container instance."""
    parent = mock_tkinter.Frame()
    return PageContainer(parent, "test_page", "Test Page")


class TestPageContainer:
    """Test cases for the PageContainer class."""
    
    def test_init(self, page_container, mock_tkinter):
        """Test initialization of page container."""
        assert page_container.page_id == "test_page"
        assert page_container.title == "Test Page"
        assert page_container.navigation_callback is None
        
        # Verify that the frame is created and configured
        mock_tkinter.Frame.assert_called()
        page_container.grid.assert_called_once()
        page_container.grid_remove.assert_called_once()
        page_container.grid_columnconfigure.assert_called_with(0, weight=1)
        page_container.grid_rowconfigure.assert_called()
    
    def test_create_layout(self, mock_tkinter):
        """Test _create_layout method."""
        parent = mock_tkinter.Frame()
        container = PageContainer(parent, "test_page", "Test Page")
        
        # Verify that layout components were created
        assert hasattr(container, 'header_frame')
        assert hasattr(container, 'content_frame')
        assert hasattr(container, 'title_label')
        assert hasattr(container, 'separator')
        
        # Verify that layout was configured
        container.header_frame.grid.assert_called()
        container.header_frame.grid_columnconfigure.assert_called_with(0, weight=1)
        container.title_label.grid.assert_called()
        container.separator.grid.assert_called()
        container.content_frame.grid.assert_called()
        container.content_frame.grid_columnconfigure.assert_called_with(0, weight=1)
        container.content_frame.grid_rowconfigure.assert_called_with(0, weight=1)
    
    def test_show(self, page_container):
        """Test show method."""
        # Setup a spy on update_content
        page_container.update_content = MagicMock()
        
        # Call the show method with some kwargs
        test_kwargs = {'param1': 'value1', 'param2': 'value2'}
        page_container.show(**test_kwargs)
        
        # Verify grid() was called to show the page
        page_container.grid.assert_called()
        
        # Verify update_content was called with the kwargs
        page_container.update_content.assert_called_with(**test_kwargs)
    
    def test_show_with_error(self, page_container, mock_error_handling):
        """Test show method with error handling."""
        # Setup update_content to raise an exception
        page_container.update_content = MagicMock(side_effect=Exception("Test error"))
        
        # Call the show method
        page_container.show()
        
        # Verify grid() was called to show the page
        page_container.grid.assert_called()
        
        # Verify error was reported
        mock_error_handling.assert_called_with(
            Exception("Test error"),
            f"Error showing page {page_container.page_id}",
            show_details=True
        )
    
    def test_hide(self, page_container):
        """Test hide method."""
        page_container.hide()
        page_container.grid_remove.assert_called()
    
    def test_update_content(self, page_container):
        """Test update_content method."""
        # Base implementation is a no-op
        result = page_container.update_content(param='value')
        assert result is None
    
    def test_refresh(self, page_container):
        """Test refresh method."""
        # Base implementation is a no-op
        result = page_container.refresh()
        assert result is None
    
    def test_navigate_with_callback(self, mock_tkinter):
        """Test navigate method with a callback."""
        # Create a navigation callback
        nav_callback = MagicMock()
        
        # Create a page container with the callback
        parent = mock_tkinter.Frame()
        container = PageContainer(parent, "test_page", "Test Page", nav_callback)
        
        # Call navigate
        container.navigate("other_page", param="value")
        
        # Verify callback was called with correct args
        nav_callback.assert_called_with("other_page", param="value")
    
    def test_navigate_without_callback(self, page_container):
        """Test navigate method without a callback."""
        # This should log a warning but not raise an error
        page_container.navigate("other_page")
    
    def test_add_header_button(self, page_container, mock_tkinter):
        """Test add_header_button method."""
        # Create a callback
        callback = MagicMock()
        
        # Add a button
        button = page_container.add_header_button("Test Button", callback, 1, "primary")
        
        # Verify button was created with correct params
        mock_tkinter.Button.assert_called_with(
            page_container.header_frame,
            text="Test Button",
            command=callback,
            bootstyle="primary"
        )
        
        # Verify button was added to the header
        button.grid.assert_called_with(row=0, column=1, padx=(5, 0))
        
        # Verify the method returns the button
        assert button is mock_tkinter.Button()
    
    def test_show_loader(self, page_container, mock_tkinter):
        """Test show_loader method."""
        page_container.show_loader("Loading test...")
        
        # Verify loader frame was created
        mock_tkinter.Frame.assert_called()
        
        # Verify spinner was created and started
        mock_tkinter.Progressbar.assert_called()
        page_container.loader_spinner.start.assert_called_with(15)
        
        # Verify label was created with correct message
        mock_tkinter.Label.assert_called_with(
            page_container.loader_frame,
            text="Loading test...",
            font=("Helvetica", 12),
            bootstyle="primary"
        )
        
        # Verify UI was updated
        page_container.update_idletasks.assert_called()
    
    def test_hide_loader(self, page_container, mock_tkinter):
        """Test hide_loader method."""
        # First create a loader
        page_container.show_loader()
        
        # Then hide it
        page_container.hide_loader()
        
        # Verify spinner was stopped
        page_container.loader_spinner.stop.assert_called()
        
        # Verify frame was destroyed
        page_container.loader_frame.destroy.assert_called()
    
    def test_show_error(self, page_container, mock_tkinter):
        """Test show_error method."""
        page_container.show_error("Test error", "Error details")
        
        # Verify error frame was created
        mock_tkinter.Frame.assert_called_with(
            page_container.content_frame, bootstyle="danger"
        )
        
        # Verify error message labels were created
        mock_tkinter.Label.assert_any_call(
            mock_tkinter.Frame(),
            text="Test error",
            font=("Helvetica", 12, "bold"),
            bootstyle="danger"
        )
        
        mock_tkinter.Label.assert_any_call(
            mock_tkinter.Frame(),
            text="Error details",
            bootstyle="danger",
            wraplength=600
        )
        
        # Verify dismiss button was created
        mock_tkinter.Button.assert_called()
    
    def test_show_error_without_detail(self, page_container, mock_tkinter):
        """Test show_error method without detail."""
        page_container.show_error("Test error")
        
        # Only verify the main error label, detail label should not be created
        mock_tkinter.Label.assert_called_with(
            mock_tkinter.Frame(),
            text="Test error",
            font=("Helvetica", 12, "bold"),
            bootstyle="danger"
        )
    
    def test_show_success(self, page_container, mock_tkinter):
        """Test show_success method."""
        page_container.show_success("Test success", auto_dismiss_ms=1000)
        
        # Verify success frame was created
        mock_tkinter.Frame.assert_called_with(
            page_container.content_frame, bootstyle="success"
        )
        
        # Verify success message label was created
        mock_tkinter.Label.assert_called_with(
            mock_tkinter.Frame(),
            text="Test success",
            font=("Helvetica", 12),
            bootstyle="success"
        )
        
        # Verify auto-dismiss was set up
        page_container.after.assert_called_with(1000, mock_tkinter.Frame().destroy)