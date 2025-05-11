"""
Page container component for the application.

This module provides a standard container for pages,
promoting composition over inheritance.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any

from utils.logging import get_logger


logger = get_logger(__name__)


class PageHeader:
    """
    Header component for a page.
    
    This component displays a title and an optional description.
    """
    
    def __init__(self, parent, title: str = "", description: str = ""):
        """
        Initialize the page header.
        
        Args:
            parent: Parent widget
            title: Title to display
            description: Optional description to display
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.title = title
        self.description = description
        
        # Create UI elements
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI elements for the header."""
        # Page title
        if self.title:
            title_label = ttk.Label(
                self.frame,
                text=self.title,
                font=("Arial", 20, "bold"),
                foreground="#2C3E50"
            )
            title_label.pack(anchor="w", padx=20, pady=(20, 10))

            # Separator
            separator = ttk.Separator(self.frame, orient="horizontal")
            separator.pack(fill="x", padx=20)

        # Description
        if self.description:
            desc_label = ttk.Label(
                self.frame,
                text=self.description,
                font=("Arial", 12),
                foreground="#333333",
                wraplength=600
            )
            desc_label.pack(anchor="w", padx=20, pady=(20, 10))
    
    def update_title(self, title: str):
        """
        Update the header title.
        
        Args:
            title: New title to display
        """
        self.title = title
        
        # Destroy existing UI
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Recreate UI with new title
        self._setup_ui()
    
    def update_description(self, description: str):
        """
        Update the header description.
        
        Args:
            description: New description to display
        """
        self.description = description
        
        # Destroy existing UI
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Recreate UI with new description
        self._setup_ui()
    
    def pack(self, **kwargs):
        """Pack the header frame into its parent."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the header frame into its parent."""
        self.frame.grid(**kwargs)


class PageFooter:
    """
    Footer component for a page.
    
    This component displays action buttons and other controls at the bottom of a page.
    """
    
    def __init__(self, parent):
        """
        Initialize the page footer.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        # Dictionary to store buttons by ID
        self.buttons = {}
        
        # Create UI elements
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI elements for the footer."""
        # Add separator
        separator = ttk.Separator(self.frame, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=(10, 0))
        
        # Container for buttons
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(fill="x", padx=20, pady=10, anchor="e")
    
    def add_button(self, button_id: str, text: str, command: Callable, 
                  primary: bool = False, **kwargs):
        """
        Add a button to the footer.
        
        Args:
            button_id: Unique ID for the button
            text: Button text
            command: Function to call when the button is clicked
            primary: Whether this is a primary button
            **kwargs: Additional arguments to pass to the Button constructor
        """
        # Use different style for primary buttons
        style = "Accent.TButton" if primary else "TButton"
        
        # Create button
        button = ttk.Button(
            self.button_frame,
            text=text,
            command=command,
            style=style,
            **kwargs
        )
        button.pack(side="right", padx=(5, 0))
        
        # Store button reference
        self.buttons[button_id] = button
        
        return button
    
    def remove_button(self, button_id: str):
        """
        Remove a button from the footer.
        
        Args:
            button_id: ID of the button to remove
        """
        if button_id in self.buttons:
            self.buttons[button_id].destroy()
            del self.buttons[button_id]
    
    def enable_button(self, button_id: str, enable: bool = True):
        """
        Enable or disable a button.
        
        Args:
            button_id: ID of the button to enable/disable
            enable: Whether to enable or disable the button
        """
        if button_id in self.buttons:
            state = "normal" if enable else "disabled"
            self.buttons[button_id].configure(state=state)
    
    def pack(self, **kwargs):
        """Pack the footer frame into its parent."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the footer frame into its parent."""
        self.frame.grid(**kwargs)


class PageContainer:
    """
    Container component for a page.
    
    This component provides a standard container for page content,
    including a header, content area, and footer.
    """
    
    def __init__(self, parent, title: str = "", description: str = ""):
        """
        Initialize the page container.
        
        Args:
            parent: Parent widget
            title: Page title
            description: Page description
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)  # Content area expands
        
        # Create header
        self.header = PageHeader(self.frame, title, description)
        self.header.grid(row=0, column=0, sticky="ew")
        
        # Create content area
        self.content = ttk.Frame(self.frame)
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Create footer
        self.footer = PageFooter(self.frame)
        self.footer.grid(row=2, column=0, sticky="ew")
        
        logger.debug(f"PageContainer initialized with title: {title}")
    
    def set_title(self, title: str):
        """Set the page title."""
        self.header.update_title(title)
    
    def set_description(self, description: str):
        """Set the page description."""
        self.header.update_description(description)
    
    def add_footer_button(self, button_id: str, text: str, command: Callable, 
                         primary: bool = False, **kwargs):
        """Add a button to the footer."""
        return self.footer.add_button(button_id, text, command, primary, **kwargs)
    
    def remove_footer_button(self, button_id: str):
        """Remove a button from the footer."""
        self.footer.remove_button(button_id)
    
    def enable_footer_button(self, button_id: str, enable: bool = True):
        """Enable or disable a footer button."""
        self.footer.enable_button(button_id, enable)
    
    def show(self):
        """Show the page container."""
        self.frame.pack(fill=tk.BOTH, expand=True)
        logger.debug("PageContainer shown")
    
    def hide(self):
        """Hide the page container."""
        self.frame.pack_forget()
        logger.debug("PageContainer hidden")
        
    def get_content_frame(self) -> ttk.Frame:
        """Get the content frame for adding page-specific content."""
        return self.content