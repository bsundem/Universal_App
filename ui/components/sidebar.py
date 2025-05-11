import tkinter as tk
from tkinter import ttk

class Sidebar:
    """Main navigation sidebar component using Tkinter."""
    
    def __init__(self, parent):
        # Create the sidebar frame
        self.frame = ttk.Frame(parent, width=200)
        self.frame.grid_propagate(False)  # Don't shrink
        
        # Style for the sidebar
        self.frame.configure(style="Sidebar.TFrame")
        
        # Create a style for the sidebar
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#2C3E50")
        style.configure("SidebarTitle.TLabel", 
                        background="#2C3E50", 
                        foreground="white", 
                        font=("Arial", 16, "bold"))
        style.configure("SidebarButton.TButton", 
                        background="#2C3E50", 
                        foreground="white", 
                        font=("Arial", 11))
        style.map("SidebarButton.TButton",
                  background=[("active", "#34495E"), ("pressed", "#3498DB")],
                  relief=[("pressed", "flat"), ("!pressed", "flat")])
        
        # Variable to store the callback function
        self.on_page_changed = None
        
        # Create layout
        self._setup_layout()
        
    def _setup_layout(self):
        """Setup the sidebar layout."""
        # Add title
        title_label = ttk.Label(self.frame, text="Universal App", style="SidebarTitle.TLabel")
        title_label.pack(pady=(20, 10), fill="x", padx=10)
        
        # Add separator
        separator = ttk.Separator(self.frame, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=(0, 20))
        
        # Navigation buttons
        self.nav_buttons = []
        self._setup_navigation()
    
    def _setup_navigation(self):
        """Setup the navigation buttons."""
        nav_items = [
            {"name": "Home", "id": 0},
            {"name": "Actuarial Tools", "id": 1},
            {"name": "Kaggle Explorer", "id": 2},
            {"name": "Project Three", "id": 3},
            {"name": "Settings", "id": 4}
        ]

        # Variable to track the selected button
        self.selected_btn = tk.IntVar(value=0)

        for item in nav_items:
            # Create a custom styled button for each nav item
            button = ttk.Radiobutton(
                self.frame,
                text=item["name"],
                value=item["id"],
                variable=self.selected_btn,
                style="SidebarButton.TButton",
                command=lambda idx=item["id"]: self._handle_nav_click(idx)
            )
            button.pack(fill="x", padx=5, pady=2)
            self.nav_buttons.append(button)
    
    def _handle_nav_click(self, index):
        """Handle navigation button clicks."""
        # Call the callback function if it exists
        if self.on_page_changed:
            self.on_page_changed(index)