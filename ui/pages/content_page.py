"""
Content page module providing an alternative to BasePage using composition.

This module implements the Composition Over Inheritance principle by using
a PageContainer component rather than inheriting from a base class.
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any

from ui.components.page_container import PageContainer
from utils.logging import get_logger


logger = get_logger(__name__)


class ContentPage:
    """
    Base content page using composition instead of inheritance.
    
    This class uses a PageContainer component to provide common page functionality
    rather than inheriting from a base class.
    """
    
    def __init__(self, parent, title: str = "", description: str = ""):
        """
        Initialize the content page.
        
        Args:
            parent: Parent widget
            title: Page title
            description: Page description
        """
        self.parent = parent
        self.container = PageContainer(parent, title, description)
        self.content_frame = self.container.get_content_frame()
        
        # Hook for subclasses to initialize UI
        self.setup_ui()
        
        logger.debug(f"ContentPage initialized with title: {title}")
    
    def setup_ui(self):
        """
        Setup the UI for this page.
        
        This method should be overridden by subclasses to provide
        page-specific UI elements.
        """
        pass
    
    def show(self):
        """Show this page."""
        self.container.show()
        logger.debug("ContentPage shown")
    
    def hide(self):
        """Hide this page."""
        self.container.hide()
        logger.debug("ContentPage hidden")
    
    def add_footer_button(self, button_id: str, text: str, command: Callable, 
                         primary: bool = False, **kwargs):
        """Add a button to the page footer."""
        return self.container.add_footer_button(button_id, text, command, primary, **kwargs)
    
    def remove_footer_button(self, button_id: str):
        """Remove a button from the page footer."""
        self.container.remove_footer_button(button_id)
    
    def enable_footer_button(self, button_id: str, enable: bool = True):
        """Enable or disable a footer button."""
        self.container.enable_footer_button(button_id, enable)
    
    def set_title(self, title: str):
        """Set the page title."""
        self.container.set_title(title)
    
    def set_description(self, description: str):
        """Set the page description."""
        self.container.set_description(description)