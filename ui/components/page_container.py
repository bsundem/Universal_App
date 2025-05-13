"""
Page container component for the Universal App.

This module provides a base container for pages that can be shown or hidden
in the main content area of the application.
"""
import logging
from typing import Dict, Callable, Optional, Any, List, Type

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from utils.error_handling import report_error

logger = logging.getLogger(__name__)


class PageContainer(ttk.Frame):
    """
    Base class for all application pages.
    
    This class provides a common interface and functionality for all
    application pages, following the Composition over Inheritance principle.
    """
    
    def __init__(
        self,
        parent: ttk.Frame,
        page_id: str,
        title: str,
        navigation_callback: Optional[Callable] = None
    ):
        """
        Initialize a page container.
        
        Args:
            parent: Parent frame
            page_id: Unique identifier for the page
            title: Page title
            navigation_callback: Function to navigate to other pages
        """
        super().__init__(parent)
        
        self.parent = parent
        self.page_id = page_id
        self.title = title
        self.navigation_callback = navigation_callback
        
        # Grid configuration for the frame
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_remove()  # Hide by default
        
        # Configure grid layout for the page
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Row 0 is header, row 1 is content
        
        # Create the page layout
        self._create_layout()
        
        logger.debug(f"Initialized page: {page_id}")
        
    def _create_layout(self):
        """Create the basic page layout with header and content area."""
        # Header frame
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ttk.Label(
            self.header_frame,
            text=self.title,
            font=("Helvetica", 18, "bold"),
            bootstyle="dark"
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Separator
        self.separator = ttk.Separator(self)
        self.separator.grid(row=0, column=0, sticky="ew", padx=10, pady=(40, 0))
        
        # Content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
    def setup_content(self):
        """
        Set up the page content.
        
        This method should be overridden by subclasses to create
        the actual content of the page.
        """
        pass
        
    def show(self, **kwargs):
        """
        Show this page.
        
        Args:
            **kwargs: Additional arguments to configure the page
        """
        try:
            self.grid()
            self.update_content(**kwargs)
            logger.debug(f"Showing page: {self.page_id}")
        except Exception as e:
            report_error(e, f"Error showing page {self.page_id}", show_details=True)
            
    def hide(self):
        """Hide this page."""
        self.grid_remove()
        logger.debug(f"Hiding page: {self.page_id}")
        
    def update_content(self, **kwargs):
        """
        Update the page content with new data.
        
        Args:
            **kwargs: Parameters to update the content
        """
        # No-op in the base class, override in subclasses
        pass
        
    def refresh(self):
        """Refresh the page content."""
        # No-op in the base class, override in subclasses
        pass
        
    def navigate(self, page_id: str, **kwargs):
        """
        Navigate to another page.
        
        Args:
            page_id: ID of the page to navigate to
            **kwargs: Arguments to pass to the page
        """
        if self.navigation_callback:
            self.navigation_callback(page_id, **kwargs)
        else:
            logger.warning(f"No navigation callback for page: {self.page_id}")
            
    def add_header_button(self, text: str, command: Callable, column: int, style: str = "primary"):
        """
        Add a button to the header.
        
        Args:
            text: Button text
            command: Function to call when clicked
            column: Column position in the header
            style: Button style (bootstrap style name)
        """
        button = ttk.Button(
            self.header_frame,
            text=text,
            command=command,
            bootstyle=style
        )
        button.grid(row=0, column=column, padx=(5, 0))
        return button
        
    def show_loader(self, message: str = "Loading..."):
        """
        Show a loading indicator.
        
        Args:
            message: Loading message to display
        """
        # Create a frame on top of everything else
        self.loader_frame = ttk.Frame(self, bootstyle="light")
        self.loader_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Add spinner and message
        self.loader_spinner = ttk.Progressbar(
            self.loader_frame,
            mode="indeterminate",
            bootstyle="primary"
        )
        self.loader_spinner.pack(pady=(0, 10))
        self.loader_spinner.start(15)
        
        self.loader_label = ttk.Label(
            self.loader_frame,
            text=message,
            font=("Helvetica", 12),
            bootstyle="primary"
        )
        self.loader_label.pack()
        
        # Update the UI
        self.update_idletasks()
        
    def hide_loader(self):
        """Hide the loading indicator."""
        if hasattr(self, 'loader_frame') and self.loader_frame.winfo_exists():
            self.loader_spinner.stop()
            self.loader_frame.destroy()
            
    def show_error(self, message: str, detail: Optional[str] = None):
        """
        Show an error message on the page.
        
        Args:
            message: Error message
            detail: Detailed error information
        """
        # Create a frame for the error
        error_frame = ttk.Frame(self.content_frame, bootstyle="danger")
        error_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Main error message
        error_label = ttk.Label(
            error_frame,
            text=message,
            font=("Helvetica", 12, "bold"),
            bootstyle="danger"
        )
        error_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Detail if provided
        if detail:
            detail_label = ttk.Label(
                error_frame,
                text=detail,
                bootstyle="danger",
                wraplength=600
            )
            detail_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))
            
        # Dismiss button
        dismiss_btn = ttk.Button(
            error_frame,
            text="Dismiss",
            command=lambda: error_frame.destroy(),
            bootstyle="danger-outline"
        )
        dismiss_btn.grid(row=2, column=0, sticky="e", padx=10, pady=5)
        
        logger.error(f"Page error: {message} - {detail}")
        
    def show_success(self, message: str, auto_dismiss_ms: int = 3000):
        """
        Show a success message on the page.
        
        Args:
            message: Success message
            auto_dismiss_ms: Time in ms after which the message auto-dismisses
        """
        # Create a frame for the success message
        success_frame = ttk.Frame(self.content_frame, bootstyle="success")
        success_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Message
        success_label = ttk.Label(
            success_frame,
            text=message,
            font=("Helvetica", 12),
            bootstyle="success"
        )
        success_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Auto-dismiss after specified time
        if auto_dismiss_ms > 0:
            self.after(auto_dismiss_ms, lambda: success_frame.destroy())