import tkinter as tk
from tkinter import ttk
from ui.components.sidebar import Sidebar
from ui.pages.home_page import HomePage
from ui.pages.project_page import ProjectPage
from ui.pages.settings_page import SettingsPage
from ui.pages.actuarial_page import ActuarialPage
from ui.pages.kaggle_page import KagglePage

class MainWindow:
    """Main application window using Tkinter."""
    
    def __init__(self, parent):
        # Store the parent
        self.parent = parent
        
        # Create main frame that will contain everything
        self.main_frame = ttk.Frame(parent)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure the main frame to expand
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Create sidebar for navigation
        self.sidebar = Sidebar(self.main_frame)
        self.sidebar.frame.grid(row=0, column=0, sticky="ns")
        self.sidebar.on_page_changed = self.change_page
        
        # Create frame for content pages
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Create pages
        self.pages = []
        self.setup_pages()
        
        # Show the initial page
        self.current_page = 0
        self.show_page(0)
    
    def setup_pages(self):
        """Setup the application pages."""
        # Create pages
        home_page = HomePage(self.content_frame)
        actuarial_page = ActuarialPage(self.content_frame, self)
        kaggle_page = KagglePage(self.content_frame, self)
        project_three = ProjectPage(self.content_frame, "Project Three")
        settings_page = SettingsPage(self.content_frame)

        # Add pages to our list
        self.pages = [
            home_page,
            actuarial_page,
            kaggle_page,
            project_three,
            settings_page
        ]
    
    def change_page(self, index):
        """Change the current page."""
        if 0 <= index < len(self.pages):
            # Hide current page
            self.pages[self.current_page].frame.grid_forget()
            
            # Update current page index
            self.current_page = index
            
            # Show new page
            self.show_page(index)
    
    def show_page(self, index):
        """Show the page at the given index."""
        self.pages[index].frame.grid(row=0, column=0, sticky="nsew")