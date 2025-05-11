import tkinter as tk
from tkinter import ttk
from ui.components.sidebar import Sidebar
from ui.pages.home_page import HomePage
from ui.pages.project_page import ProjectPage
from ui.pages.settings_page import SettingsPage
from ui.pages.actuarial_page import ActuarialPage
from ui.pages.kaggle_page import KagglePage
from ui.pages.example_page import ExamplePage
from utils.logging import get_logger

logger = get_logger(__name__)

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
        # Create pages - all pages use ContentPage (composition)
        home_page = HomePage(self.content_frame, self)
        actuarial_page = ActuarialPage(self.content_frame, self)
        kaggle_page = KagglePage(self.content_frame, self)
        project_three = ProjectPage(self.content_frame, "Project Three", self)
        example_page = ExamplePage(self.content_frame, self)  # Uses ContentPage
        settings_page = SettingsPage(self.content_frame, self)

        # Add pages to our list
        self.pages = [
            home_page,
            actuarial_page,
            kaggle_page,
            project_three,
            example_page,
            settings_page
        ]

        logger.debug(f"Set up {len(self.pages)} pages")
    
    def change_page(self, index):
        """Change the current page."""
        if 0 <= index < len(self.pages):
            logger.debug(f"Changing page to index {index}")

            # Hide current page
            self._hide_current_page()

            # Update current page index
            self.current_page = index

            # Show new page
            self.show_page(index)

    def _hide_current_page(self):
        """Hide the current page using ContentPage's hide method."""
        current_page = self.pages[self.current_page]
        current_page.hide()
        logger.debug(f"Hid page at index {self.current_page}")

    def show_page(self, index_or_name):
        """
        Show a page by index or name.

        Args:
            index_or_name: Either a numeric index or a string name of the page
        """
        # Convert name to index if a string is provided
        if isinstance(index_or_name, str):
            page_map = {
                "home": 0,
                "actuarial": 1,
                "kaggle": 2,
                "project_three": 3,
                "example": 4,
                "settings": 5
            }

            if index_or_name in page_map:
                index = page_map[index_or_name]
                logger.debug(f"Showing page '{index_or_name}' (index {index})")
            else:
                logger.warning(f"Unknown page name: {index_or_name}")
                index = 0  # Default to home page
        else:
            index = index_or_name

        # All pages use ContentPage with a show method
        page = self.pages[index]
        page.show()

        logger.debug(f"Showed page at index {index}")