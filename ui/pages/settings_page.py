"""
Settings page of the application using composition.
"""
import tkinter as tk
from tkinter import ttk

from ui.pages.content_page import ContentPage
from utils.logging import get_logger
from core.config import config

logger = get_logger(__name__)

class SettingsPage(ContentPage):
    """Settings page of the application using ContentPage composition."""
    
    def __init__(self, parent, controller=None):
        super().__init__(
            parent=parent,
            title="Settings",
            description="Configure application settings here."
        )
        self.controller = controller
        logger.debug("SettingsPage initialized")
        
    def setup_ui(self):
        """Set up the UI components for the settings page."""
        # Create settings frame
        settings_frame = ttk.Frame(self.content_frame, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create sections for different settings
        self._create_appearance_section(settings_frame)
        self._create_logging_section(settings_frame)
        
        # Add save button to footer
        self.add_footer_button(
            "save", 
            "Save Settings", 
            self._save_settings, 
            primary=True
        )
        
        logger.debug("Settings UI setup completed")
        
    def _create_appearance_section(self, parent):
        """Create the appearance settings section."""
        appearance_frame = ttk.LabelFrame(parent, text="Appearance", padding="10")
        appearance_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Theme selection
        ttk.Label(appearance_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.theme_var = tk.StringVar(value=config.app.theme)
        theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var, width=15)
        theme_combo['values'] = ('default', 'clam', 'alt', 'classic')
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Title setting
        ttk.Label(appearance_frame, text="Application Title:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.title_var = tk.StringVar(value=config.app.title)
        title_entry = ttk.Entry(appearance_frame, textvariable=self.title_var, width=30)
        title_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
    def _create_logging_section(self, parent):
        """Create the logging settings section."""
        logging_frame = ttk.LabelFrame(parent, text="Logging", padding="10")
        logging_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Log level
        ttk.Label(logging_frame, text="Log Level:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.log_level_var = tk.StringVar(value=config.logging.level)
        log_level_combo = ttk.Combobox(logging_frame, textvariable=self.log_level_var, width=15)
        log_level_combo['values'] = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_level_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Log file
        ttk.Label(logging_frame, text="Log File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.log_file_var = tk.StringVar(value=config.logging.file or "")
        log_file_entry = ttk.Entry(logging_frame, textvariable=self.log_file_var, width=30)
        log_file_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
    def _save_settings(self):
        """Save the settings to config and update the application."""
        try:
            # Update config with new values
            config.app.theme = self.theme_var.get()
            config.app.title = self.title_var.get()
            config.logging.level = self.log_level_var.get()
            config.logging.file = self.log_file_var.get() or None
            
            # Save to config file
            config.save_to_file("config.json")
            
            # Apply changes that can be applied immediately
            if hasattr(self.controller, "root"):
                self.controller.root.title(config.app.title)
                
            logger.info("Settings saved successfully")
            
            # Show success in UI
            ttk.Label(
                self.content_frame, 
                text="Settings saved successfully! Some changes may require restart.", 
                foreground="green"
            ).pack(side=tk.BOTTOM, pady=10)
            
        except Exception as e:
            logger.error(f"Failed to save settings: {str(e)}")
            
            # Show error in UI
            ttk.Label(
                self.content_frame, 
                text=f"Error saving settings: {str(e)}", 
                foreground="red"
            ).pack(side=tk.BOTTOM, pady=10)