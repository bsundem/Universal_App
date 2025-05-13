"""
Settings page module for the Universal App.

This module provides the settings page for configuring the application.
"""
import logging
import json
from typing import Dict, Callable, Optional, Any, List

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Import UI components
from ui.components.page_container import PageContainer

# Import config
from core.config import config_manager

logger = logging.getLogger(__name__)


class SettingsPage(PageContainer):
    """
    Settings page for the application.
    
    This page allows users to customize application settings.
    """
    
    def __init__(self, parent: ttk.Frame, navigation_callback: Optional[Callable] = None):
        """
        Initialize the settings page.
        
        Args:
            parent: Parent frame
            navigation_callback: Function to navigate to other pages
        """
        super().__init__(
            parent,
            page_id="settings",
            title="Settings",
            navigation_callback=navigation_callback
        )
        
        # Save references to original settings to detect changes
        self.original_settings = {}
        self.settings_vars = {}
        
        self.setup_content()
        logger.debug("Settings page initialized")
        
    def setup_content(self):
        """Set up the page content."""
        # Configure grid layout for the content
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Header
        self.content_frame.grid_rowconfigure(1, weight=1)  # Settings area
        self.content_frame.grid_rowconfigure(2, weight=0)  # Buttons area
        
        # Header section
        self._create_header_section()
        
        # Settings section with tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create settings tabs
        self._create_general_settings()
        self._create_appearance_settings()
        self._create_service_settings()
        
        # Create buttons section
        self._create_buttons_section()
        
    def _create_header_section(self):
        """Create the header section at the top of the page."""
        header_frame = ttk.Frame(self.content_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Application Settings",
            font=("Helvetica", 16),
            bootstyle="dark"
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Description
        description = ttk.Label(
            header_frame,
            text=(
                "Configure application settings to customize your experience. "
                "Changes will be applied after saving."
            ),
            wraplength=800,
            justify=tk.LEFT,
            bootstyle="secondary"
        )
        description.pack(anchor=tk.W, pady=(0, 10))
        
        # Separator
        ttk.Separator(header_frame).pack(fill=tk.X, pady=5)
        
    def _create_general_settings(self):
        """Create general settings tab."""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")
        
        # Configure frame
        general_frame.grid_columnconfigure(0, weight=0)  # Label column
        general_frame.grid_columnconfigure(1, weight=1)  # Input column
        
        # Application Name
        app_name_label = ttk.Label(
            general_frame,
            text="Application Name:",
            width=20,
            anchor=tk.E
        )
        app_name_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        
        app_name_var = tk.StringVar(value=config_manager.app.title)
        self.settings_vars["app.title"] = app_name_var
        self.original_settings["app.title"] = config_manager.app.title
        
        app_name_entry = ttk.Entry(
            general_frame,
            textvariable=app_name_var,
            width=30
        )
        app_name_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        # Application Version
        version_label = ttk.Label(
            general_frame,
            text="Version:",
            width=20,
            anchor=tk.E
        )
        version_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        
        version_var = tk.StringVar(value=config_manager.app.version)
        self.settings_vars["app.version"] = version_var
        self.original_settings["app.version"] = config_manager.app.version
        
        version_entry = ttk.Entry(
            general_frame,
            textvariable=version_var,
            width=10
        )
        version_entry.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        # Debug Mode
        debug_label = ttk.Label(
            general_frame,
            text="Debug Mode:",
            width=20,
            anchor=tk.E
        )
        debug_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        
        debug_var = tk.BooleanVar(value=config_manager.app.debug)
        self.settings_vars["app.debug"] = debug_var
        self.original_settings["app.debug"] = config_manager.app.debug
        
        debug_check = ttk.Checkbutton(
            general_frame,
            text="Enable Debug Mode",
            variable=debug_var,
            onvalue=True,
            offvalue=False
        )
        debug_check.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        # Data Directory
        data_dir_label = ttk.Label(
            general_frame,
            text="Data Directory:",
            width=20,
            anchor=tk.E
        )
        data_dir_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)
        
        data_dir_var = tk.StringVar(value=config_manager.app.data_dir)
        self.settings_vars["app.data_dir"] = data_dir_var
        self.original_settings["app.data_dir"] = config_manager.app.data_dir
        
        data_dir_frame = ttk.Frame(general_frame)
        data_dir_frame.grid(row=3, column=1, sticky="w", padx=10, pady=10)
        
        data_dir_entry = ttk.Entry(
            data_dir_frame,
            textvariable=data_dir_var,
            width=30
        )
        data_dir_entry.pack(side=tk.LEFT)
        
        def browse_data_dir():
            directory = filedialog.askdirectory(
                initialdir=data_dir_var.get()
            )
            if directory:
                data_dir_var.set(directory)
                
        browse_button = ttk.Button(
            data_dir_frame,
            text="Browse...",
            command=browse_data_dir
        )
        browse_button.pack(side=tk.LEFT, padx=5)
        
    def _create_appearance_settings(self):
        """Create appearance settings tab."""
        appearance_frame = ttk.Frame(self.notebook)
        self.notebook.add(appearance_frame, text="Appearance")
        
        # Configure frame
        appearance_frame.grid_columnconfigure(0, weight=0)  # Label column
        appearance_frame.grid_columnconfigure(1, weight=1)  # Input column
        
        # Theme
        theme_label = ttk.Label(
            appearance_frame,
            text="Theme:",
            width=20,
            anchor=tk.E
        )
        theme_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        
        theme_var = tk.StringVar(value=config_manager.app.theme)
        self.settings_vars["app.theme"] = theme_var
        self.original_settings["app.theme"] = config_manager.app.theme
        
        themes = ["cosmo", "flatly", "litera", "minty", "lumen", "sandstone", 
                 "yeti", "pulse", "united", "morph", "journal", "darkly"]
        
        theme_combo = ttk.Combobox(
            appearance_frame,
            textvariable=theme_var,
            values=themes,
            state="readonly",
            width=20
        )
        theme_combo.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        # Window Size
        window_size_label = ttk.Label(
            appearance_frame,
            text="Window Size:",
            width=20,
            anchor=tk.E
        )
        window_size_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        
        window_size_frame = ttk.Frame(appearance_frame)
        window_size_frame.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        width_var = tk.IntVar(value=config_manager.ui.window.width)
        self.settings_vars["ui.window.width"] = width_var
        self.original_settings["ui.window.width"] = config_manager.ui.window.width
        
        width_label = ttk.Label(window_size_frame, text="Width:")
        width_label.pack(side=tk.LEFT, padx=(0, 5))
        
        width_entry = ttk.Entry(
            window_size_frame,
            textvariable=width_var,
            width=6
        )
        width_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        height_var = tk.IntVar(value=config_manager.ui.window.height)
        self.settings_vars["ui.window.height"] = height_var
        self.original_settings["ui.window.height"] = config_manager.ui.window.height
        
        height_label = ttk.Label(window_size_frame, text="Height:")
        height_label.pack(side=tk.LEFT, padx=(0, 5))
        
        height_entry = ttk.Entry(
            window_size_frame,
            textvariable=height_var,
            width=6
        )
        height_entry.pack(side=tk.LEFT)
        
        # Sidebar width
        sidebar_width_label = ttk.Label(
            appearance_frame,
            text="Sidebar Width:",
            width=20,
            anchor=tk.E
        )
        sidebar_width_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        
        sidebar_width_var = tk.IntVar(value=config_manager.ui.sidebar.width)
        self.settings_vars["ui.sidebar.width"] = sidebar_width_var
        self.original_settings["ui.sidebar.width"] = config_manager.ui.sidebar.width
        
        sidebar_width_entry = ttk.Entry(
            appearance_frame,
            textvariable=sidebar_width_var,
            width=6
        )
        sidebar_width_entry.grid(row=2, column=1, sticky="w", padx=10, pady=10)
    
    def _create_service_settings(self):
        """Create service settings tab."""
        service_frame = ttk.Frame(self.notebook)
        self.notebook.add(service_frame, text="Services")
        
        # Configure frame
        service_frame.grid_columnconfigure(0, weight=0)  # Label column
        service_frame.grid_columnconfigure(1, weight=1)  # Input column
        
        # R Integration
        r_label = ttk.Label(
            service_frame,
            text="R Integration:",
            width=20,
            anchor=tk.E
        )
        r_label.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        
        r_enabled_var = tk.BooleanVar(value=config_manager.services.r_integration.enabled)
        self.settings_vars["services.r_integration.enabled"] = r_enabled_var
        self.original_settings["services.r_integration.enabled"] = config_manager.services.r_integration.enabled
        
        r_check = ttk.Checkbutton(
            service_frame,
            text="Enable R Integration",
            variable=r_enabled_var,
            onvalue=True,
            offvalue=False
        )
        r_check.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        # R Scripts Directory
        r_scripts_label = ttk.Label(
            service_frame,
            text="R Scripts Directory:",
            width=20,
            anchor=tk.E
        )
        r_scripts_label.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        
        r_scripts_var = tk.StringVar(value=config_manager.services.r_integration.scripts_dir)
        self.settings_vars["services.r_integration.scripts_dir"] = r_scripts_var
        self.original_settings["services.r_integration.scripts_dir"] = config_manager.services.r_integration.scripts_dir
        
        r_scripts_frame = ttk.Frame(service_frame)
        r_scripts_frame.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        r_scripts_entry = ttk.Entry(
            r_scripts_frame,
            textvariable=r_scripts_var,
            width=30
        )
        r_scripts_entry.pack(side=tk.LEFT)
        
        def browse_r_scripts():
            directory = filedialog.askdirectory(
                initialdir=r_scripts_var.get()
            )
            if directory:
                r_scripts_var.set(directory)
                
        browse_button = ttk.Button(
            r_scripts_frame,
            text="Browse...",
            command=browse_r_scripts
        )
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Actuarial Service
        actuarial_label = ttk.Label(
            service_frame,
            text="Actuarial Service:",
            width=20,
            anchor=tk.E
        )
        actuarial_label.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        
        actuarial_enabled_var = tk.BooleanVar(value=config_manager.services.actuarial.enabled)
        self.settings_vars["services.actuarial.enabled"] = actuarial_enabled_var
        self.original_settings["services.actuarial.enabled"] = config_manager.services.actuarial.enabled
        
        actuarial_check = ttk.Checkbutton(
            service_frame,
            text="Enable Actuarial Service",
            variable=actuarial_enabled_var,
            onvalue=True,
            offvalue=False
        )
        actuarial_check.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        # Finance Service
        finance_label = ttk.Label(
            service_frame,
            text="Finance Service:",
            width=20,
            anchor=tk.E
        )
        finance_label.grid(row=3, column=0, sticky="e", padx=10, pady=10)
        
        finance_enabled_var = tk.BooleanVar(value=config_manager.services.finance.enabled)
        self.settings_vars["services.finance.enabled"] = finance_enabled_var
        self.original_settings["services.finance.enabled"] = config_manager.services.finance.enabled
        
        finance_check = ttk.Checkbutton(
            service_frame,
            text="Enable Finance Service",
            variable=finance_enabled_var,
            onvalue=True,
            offvalue=False
        )
        finance_check.grid(row=3, column=1, sticky="w", padx=10, pady=10)
        
    def _create_buttons_section(self):
        """Create buttons section at the bottom of the page."""
        buttons_frame = ttk.Frame(self.content_frame)
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        # Save button
        save_button = ttk.Button(
            buttons_frame,
            text="Save Changes",
            bootstyle="success",
            command=self._save_settings
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # Reset button
        reset_button = ttk.Button(
            buttons_frame,
            text="Reset to Defaults",
            bootstyle="warning",
            command=self._reset_to_defaults
        )
        reset_button.pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            bootstyle="secondary",
            command=self._cancel_changes
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def _save_settings(self):
        """Save the settings to the configuration file."""
        # Get the config object
        config = config_manager.get_config()
        
        # Update the configuration with new values
        for key, var in self.settings_vars.items():
            parts = key.split('.')
            obj = config
            for i in range(len(parts) - 1):
                obj = getattr(obj, parts[i])
            # Set the final attribute
            setattr(obj, parts[-1], var.get())
            
        # Save the configuration to file
        if config_manager.save_config():
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
            # Update original settings
            for key, var in self.settings_vars.items():
                self.original_settings[key] = var.get()
            
            # Notify the user that some changes require a restart
            messagebox.showinfo(
                "Restart Required",
                "Some changes will take effect after restarting the application."
            )
        else:
            messagebox.showerror("Error", "Failed to save settings.")
        
    def _reset_to_defaults(self):
        """Reset settings to factory defaults."""
        if messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults? This cannot be undone."
        ):
            # Create a new default config
            default_config = config_manager._load_config()
            
            # Update our variables with the default values
            for key, var in self.settings_vars.items():
                parts = key.split('.')
                obj = default_config
                for part in parts:
                    obj = getattr(obj, part)
                
                if isinstance(var, tk.BooleanVar):
                    var.set(bool(obj))
                elif isinstance(var, tk.IntVar):
                    var.set(int(obj))
                else:
                    var.set(str(obj))
                    
            messagebox.showinfo(
                "Settings Reset",
                "Settings have been reset to defaults. Click Save to apply the changes."
            )
        
    def _cancel_changes(self):
        """Cancel changes and navigate back."""
        # Check if there are unsaved changes
        changes_made = False
        for key, var in self.settings_vars.items():
            if var.get() != self.original_settings[key]:
                changes_made = True
                break
                
        if changes_made:
            if messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to discard them?"
            ):
                # Navigate back to home
                self.navigate("home")
        else:
            # No changes, just navigate back
            self.navigate("home")
        
    def refresh(self):
        """Refresh the settings page."""
        # Update settings variables from config
        for key, var in self.settings_vars.items():
            parts = key.split('.')
            obj = config_manager
            for part in parts:
                obj = getattr(obj, part)
                
            if isinstance(var, tk.BooleanVar):
                var.set(bool(obj))
            elif isinstance(var, tk.IntVar):
                var.set(int(obj))
            else:
                var.set(str(obj))
                
        # Update original settings
        for key, var in self.settings_vars.items():
            self.original_settings[key] = var.get()
            
        logger.debug("Refreshed settings page")