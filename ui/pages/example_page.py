"""
Example page demonstrating the Composition Over Inheritance principle.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ui.pages.content_page import ContentPage
from utils.logging import get_logger


logger = get_logger(__name__)


class ExamplePage(ContentPage):
    """Example page using ContentPage with composition."""
    
    def __init__(self, parent, controller):
        """Initialize the example page."""
        super().__init__(parent, title="Example Page", 
                       description="This page demonstrates the Composition Over Inheritance principle.")
        self.controller = controller
        
        # Add back button to footer
        self.add_footer_button(
            "back", "Back to Home", self.navigate_home, primary=False
        )
        
        # Add action button to footer
        self.add_footer_button(
            "action", "Perform Action", self.perform_action, primary=True
        )
        
        logger.debug("ExamplePage initialized")
    
    def setup_ui(self):
        """Set up the UI for the example page."""
        # Create a frame for the form
        form_frame = ttk.Frame(self.content_frame, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label
        ttk.Label(form_frame, text="Enter your name:").pack(anchor="w", pady=(0, 5))
        
        # Add a text entry
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        name_entry.pack(anchor="w", pady=(0, 20))
        
        # Add a checkbox
        self.agree_var = tk.BooleanVar()
        agree_check = ttk.Checkbutton(
            form_frame, 
            text="I agree to the terms and conditions",
            variable=self.agree_var
        )
        agree_check.pack(anchor="w", pady=(0, 20))
        
        # Add radio buttons
        ttk.Label(form_frame, text="Select an option:").pack(anchor="w", pady=(0, 5))
        
        option_frame = ttk.Frame(form_frame)
        option_frame.pack(anchor="w", pady=(0, 20))
        
        self.option_var = tk.StringVar(value="option1")
        
        ttk.Radiobutton(
            option_frame, 
            text="Option 1", 
            variable=self.option_var,
            value="option1"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            option_frame, 
            text="Option 2", 
            variable=self.option_var,
            value="option2"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            option_frame, 
            text="Option 3", 
            variable=self.option_var,
            value="option3"
        ).pack(side=tk.LEFT)
        
        # Add a button within the form
        submit_btn = ttk.Button(
            form_frame,
            text="Submit",
            command=self.submit_form
        )
        submit_btn.pack(anchor="w", pady=(0, 20))
        
        logger.debug("ExamplePage UI setup completed")
    
    def navigate_home(self):
        """Navigate back to the home page."""
        if hasattr(self.controller, "show_page"):
            self.controller.show_page("home")
            logger.debug("Navigating to home page")
    
    def perform_action(self):
        """Perform example action."""
        messagebox.showinfo(
            "Action",
            f"Action performed with option: {self.option_var.get()}"
        )
        logger.debug(f"Performed action with option: {self.option_var.get()}")
    
    def submit_form(self):
        """Handle form submission."""
        name = self.name_var.get()
        agrees = self.agree_var.get()
        option = self.option_var.get()
        
        if not name:
            messagebox.showwarning("Warning", "Please enter your name.")
            logger.warning("Form submission attempted without name")
            return
            
        if not agrees:
            messagebox.showwarning("Warning", "Please agree to the terms and conditions.")
            logger.warning("Form submission attempted without agreement")
            return
        
        messagebox.showinfo(
            "Form Submitted",
            f"Thank you, {name}!\nYou selected: {option}"
        )
        
        logger.info(f"Form submitted - Name: {name}, Option: {option}")
        
        # Clear form
        self.name_var.set("")
        self.agree_var.set(False)