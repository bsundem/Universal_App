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
        # Create a content frame for our actual page content
        self.content_frame = ttk.Frame(self.frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Page title
        if title:
            title_label = ttk.Label(
                self.content_frame,
                text=title,
                font=("Arial", 20, "bold"),
                foreground="#2C3E50"
            )
            title_label.pack(anchor="w", padx=20, pady=(20, 10))

            # Separator
            separator = ttk.Separator(self.content_frame, orient="horizontal")
            separator.pack(fill="x", padx=20)

        # Description
        if description:
            desc_label = ttk.Label(
                self.content_frame,
                text=description,
                font=("Arial", 12),
                foreground="#333333",
                wraplength=600
            )
            desc_label.pack(anchor="w", padx=20, pady=(20, 10))