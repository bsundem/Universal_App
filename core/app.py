import sys
import tkinter as tk
from tkinter import ttk
from ui.main_window import MainWindow

class Application:
    """Main application class using Tkinter."""
    
    def __init__(self):
        # Create the root Tkinter window
        self.root = tk.Tk()
        self.root.title("Universal App")
        self.root.geometry("900x600")
        
        # Set theme to a more modern look
        style = ttk.Style()
        try:
            # Try to use a more modern theme if available
            style.theme_use("clam")  # Options include: clam, alt, default, classic
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