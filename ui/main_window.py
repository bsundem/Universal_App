"""
Main window module for the Universal App.

This module provides the main application window that contains the sidebar
navigation and content frame for displaying pages.
"""
import logging
from typing import Dict, Any, Callable, Optional, Type, Union, List

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Import UI components
from ui.components.sidebar import Sidebar

# Import config
from core.config import config_manager

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Main application window class.
    
    This class manages the main application window, including the sidebar
    navigation and content frame for displaying different pages.
    """
    
    def __init__(self, root: ttk.Window):
        """
        Initialize the main window.
        
        Args:
            root: The root Tk window
        """
        self.root = root
        self.pages = {}
        self.current_page = None
        
        # Create the main layout
        self._create_layout()
        
        # Set up pages
        self._setup_pages()
        
        logger.info("Main window initialized")
        
    def _create_layout(self):
        """Create the main window layout."""
        # Configure main window layout
        self.root.grid_columnconfigure(1, weight=1)  # Content column expands
        self.root.grid_rowconfigure(0, weight=1)     # Row expands
        
        # Get sidebar width from config
        sidebar_width = config_manager.ui.sidebar.width
        
        # Create the sidebar and pass in the navigation handler
        self.sidebar = Sidebar(
            self.root, 
            width=sidebar_width,
            navigate_handler=self.navigate
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Create content frame
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        logger.debug("Main window layout created")
        
    def _setup_pages(self):
        """Set up application pages."""
        # Import pages here to avoid circular imports
        from ui.pages.home_page import HomePage
        from ui.pages.actuarial_page import ActuarialPage
        from ui.pages.finance_page import FinancePage
        from ui.pages.settings_page import SettingsPage
        from ui.pages.help_page import HelpPage
        
        # Create instances of each page
        # This will also register them with the sidebar
        self.pages['home'] = HomePage(
            self.content_frame, 
            navigation_callback=self.navigate
        )
        self.pages['actuarial'] = ActuarialPage(
            self.content_frame, 
            navigation_callback=self.navigate
        )
        self.pages['finance'] = FinancePage(
            self.content_frame, 
            navigation_callback=self.navigate
        )
        self.pages['settings'] = SettingsPage(
            self.content_frame, 
            navigation_callback=self.navigate
        )
        self.pages['help'] = HelpPage(
            self.content_frame, 
            navigation_callback=self.navigate
        )
        
        # Start with home page
        self.navigate('home')
        
        logger.debug("Pages set up")
        
    def navigate(self, page_name: str, **kwargs):
        """
        Navigate to a specific page.
        
        Args:
            page_name: Name of the page to navigate to
            **kwargs: Additional arguments to pass to the page
        """
        if page_name not in self.pages:
            logger.error(f"Attempted to navigate to unknown page: {page_name}")
            return
            
        # Hide current page if there is one
        if self.current_page:
            self.pages[self.current_page].hide()
            
        # Show new page
        self.pages[page_name].show(**kwargs)
        self.current_page = page_name
        
        # Update selected item in sidebar
        self.sidebar.select_item(page_name)
        
        # Force update the UI immediately
        self.root.update_idletasks()
        
        logger.info(f"Navigated to {page_name} page")
        
    def refresh_current_page(self):
        """Refresh the current page."""
        if self.current_page:
            self.pages[self.current_page].refresh()
            logger.debug(f"Refreshed {self.current_page} page")