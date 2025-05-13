"""
Sidebar navigation component for the Universal App.

This module provides a sidebar navigation component with modern styling
that allows users to navigate between different pages of the application.
"""
import logging
from typing import Dict, List, Callable, Optional, Tuple, Any, Union

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

logger = logging.getLogger(__name__)


class SidebarItem:
    """
    Class representing a sidebar navigation item.
    
    This class encapsulates the data and UI elements for a single
    sidebar navigation item.
    """
    
    def __init__(
        self,
        parent: ttk.Frame,
        page_id: str,
        label: str,
        icon: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None,
        row: int = 0
    ):
        """
        Initialize a sidebar item.
        
        Args:
            parent: Parent frame
            page_id: Unique identifier for the page
            label: Display text
            icon: Icon (not implemented yet)
            callback: Function to call when clicked
            row: Row position in the sidebar
        """
        self.parent = parent
        self.page_id = page_id
        self.label = label
        self.icon = icon
        self.callback = callback
        self.row = row
        self.selected = False
        
        # Create the UI elements
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the sidebar item widgets."""
        # Container frame with padding for the item
        self.frame = ttk.Frame(self.parent)
        self.frame.grid(row=self.row, column=0, sticky="ew", padx=5, pady=2)
        
        # Style for the normal and selected states
        btn_style = "secondary.Outline.TButton" if not self.selected else "success.TButton"
        
        # Button that fills the frame
        self.button = ttk.Button(
            self.frame,
            text=self.label,
            style=btn_style,
            command=self._on_click,
            padding=(20, 10),
            width=15
        )
        self.button.pack(fill=tk.X, pady=2)
        
    def _on_click(self):
        """Handle click event."""
        if self.callback:
            self.callback(self.page_id)
            
    def select(self):
        """Mark this item as selected."""
        if not self.selected:
            self.selected = True
            self.button.configure(style="success.TButton")
            
    def deselect(self):
        """Mark this item as not selected."""
        if self.selected:
            self.selected = False
            self.button.configure(style="secondary.Outline.TButton")


class Sidebar(ttk.Frame):
    """
    Sidebar navigation component.
    
    This class provides a sidebar for navigation between different pages
    of the application.
    """
    
    def __init__(
        self,
        parent: ttk.Window,
        width: int = 200,
        navigate_handler: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the sidebar.
        
        Args:
            parent: Parent window or frame
            width: Width of the sidebar in pixels
            navigate_handler: Function to call when a page is selected
        """
        super().__init__(parent, width=width, bootstyle=SECONDARY)
        
        self.parent = parent
        self.width = width
        self.navigate_handler = navigate_handler
        self.nav_items = {}
        self.selected_item = None
        
        # Ensure the sidebar maintains its width
        self.pack_propagate(False)
        
        # Create the sidebar layout
        self._create_layout()
        
        logger.debug("Sidebar initialized")
        
    def _create_layout(self):
        """Create the sidebar layout."""
        # Title section
        title_frame = ttk.Frame(self, bootstyle=SECONDARY)
        title_frame.pack(fill=tk.X, padx=10, pady=20)
        
        app_title = ttk.Label(
            title_frame, 
            text="Universal App",
            font=("Helvetica", 16, "bold"),
            bootstyle="light"
        )
        app_title.pack(fill=tk.X, padx=5)
        
        version = ttk.Label(
            title_frame, 
            text=f"v{1.0}",
            font=("Helvetica", 10),
            bootstyle="light"
        )
        version.pack(fill=tk.X)
        
        # Separator
        ttk.Separator(self, bootstyle="light").pack(fill=tk.X, padx=10, pady=10)
        
        # Navigation section
        self.nav_frame = ttk.Frame(self, bootstyle=SECONDARY)
        self.nav_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure rows to stack items vertically
        self.nav_frame.grid_columnconfigure(0, weight=1)
        
        # Set up default navigation items
        self._setup_navigation()
        
        # Bottom section with settings/help
        ttk.Separator(self, bootstyle="light").pack(fill=tk.X, padx=10, pady=10)
        
        bottom_frame = ttk.Frame(self, bootstyle=SECONDARY)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        settings_btn = ttk.Button(
            bottom_frame,
            text="Settings",
            style="secondary.Outline.TButton",
            padding=(20, 10),
            command=lambda: self.navigate_handler("settings") if self.navigate_handler else None
        )
        settings_btn.pack(fill=tk.X, pady=5)
        
        help_btn = ttk.Button(
            bottom_frame,
            text="Help",
            style="secondary.Outline.TButton",
            padding=(20, 10),
            command=lambda: self.navigate_handler("help") if self.navigate_handler else None
        )
        help_btn.pack(fill=tk.X, pady=5)
        
    def _setup_navigation(self):
        """Set up the default navigation items."""
        # These are the default pages that will always be available
        self.add_item("home", "Home", row=0)
        self.add_item("actuarial", "Actuarial", row=1)
        self.add_item("finance", "Finance", row=2)
        
    def add_item(
        self,
        page_id: str,
        label: str,
        icon: Optional[str] = None,
        row: Optional[int] = None
    ):
        """
        Add a navigation item to the sidebar.
        
        Args:
            page_id: Unique identifier for the page
            label: Display text
            icon: Icon (not implemented yet)
            row: Row position in the sidebar (optional)
        """
        if row is None:
            row = len(self.nav_items)
            
        item = SidebarItem(
            self.nav_frame,
            page_id,
            label,
            icon,
            callback=self.navigate_handler,
            row=row
        )
        
        self.nav_items[page_id] = item
        logger.debug(f"Added navigation item: {page_id}")
        
    def select_item(self, page_id: str):
        """
        Select a navigation item.
        
        Args:
            page_id: ID of the item to select
        """
        if page_id not in self.nav_items:
            logger.warning(f"Attempted to select unknown navigation item: {page_id}")
            return
            
        # Deselect current item if there is one
        if self.selected_item and self.selected_item in self.nav_items:
            self.nav_items[self.selected_item].deselect()
            
        # Select new item
        self.nav_items[page_id].select()
        self.selected_item = page_id
        
        logger.debug(f"Selected navigation item: {page_id}")