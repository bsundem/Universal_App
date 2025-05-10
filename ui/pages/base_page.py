import tkinter as tk
from tkinter import ttk

class BasePage:
    """Base class for all pages in the application using Tkinter."""
    
    def __init__(self, parent, title="", description=""):
        # Create the main frame for this page
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        
        # Add title and description
        self._setup_ui(title, description)
    
    def _setup_ui(self, title, description):
        """Setup the basic UI elements for the page."""
        current_row = 0
        
        # Page title
        if title:
            title_label = ttk.Label(
                self.frame, 
                text=title,
                font=("Arial", 20, "bold"),
                foreground="#2C3E50"
            )
            title_label.grid(row=current_row, column=0, sticky="w", padx=20, pady=(20, 10))
            current_row += 1
            
            # Separator
            separator = ttk.Separator(self.frame, orient="horizontal")
            separator.grid(row=current_row, column=0, sticky="ew", padx=20)
            current_row += 1
        
        # Description
        if description:
            desc_label = ttk.Label(
                self.frame, 
                text=description,
                font=("Arial", 12),
                foreground="#333333",
                wraplength=600
            )
            desc_label.grid(row=current_row, column=0, sticky="w", padx=20, pady=(20, 10))
            current_row += 1
        
        # Add an empty frame at the bottom to push content to the top
        spacer = ttk.Frame(self.frame)
        spacer.grid(row=current_row, column=0, sticky="ew")
        self.frame.rowconfigure(current_row, weight=1)