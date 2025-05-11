import sys
import os
import tkinter as tk
from tkinter import ttk
from ui.main_window import MainWindow
from core.config import config

class Application:
    """Main application class using Tkinter."""
    
    def __init__(self):
        # Create the root Tkinter window
        self.root = tk.Tk()
        self.root.title(config.app.title)
        self.root.geometry("900x600")

        # Set up temp directory if configured
        if config.app.temp_dir:
            os.makedirs(config.app.temp_dir, exist_ok=True)

        # Set up data directory if configured
        if config.app.data_dir:
            os.makedirs(config.app.data_dir, exist_ok=True)

        # Set theme to a more modern look
        style = ttk.Style()
        try:
            # Try to use the configured theme if available
            style.theme_use(config.app.theme)
        except tk.TclError:
            # Fallback to default if the theme isn't available
            print(f"Theme {config.app.theme} not available, using default")
            try:
                # Try 'clam' as a backup
                style.theme_use("clam")
            except tk.TclError:
                # Fallback to default if the theme isn't available
                print("Clam theme not available, using default")

        # Create main window
        self.window = MainWindow(self.root)

        # Configure window to expand with root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
        return 0
        
def create_app():
    """Create and return an application instance."""
    return Application()