"""
Example calculator UI plugin for the Universal App.

This module provides a UI plugin that adds a calculator page to the application.
It demonstrates how to implement a UIPlugin and integrate with the application's UI.
"""
import logging
import tkinter as tk
from typing import Dict, Optional, Callable, Any

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from services.plugins.base import UIPlugin
from services.plugins.examples.calculator_plugin import CalculatorServiceInterface
from services.container import container
from ui.components.page_container import PageContainer

logger = logging.getLogger(__name__)


class CalculatorUIPlugin(UIPlugin):
    """
    Example calculator UI plugin.
    
    This plugin adds a calculator page to the application.
    """
    # Plugin metadata
    plugin_id = "calculator_ui"
    plugin_name = "Calculator UI"
    plugin_version = "1.0.0"
    plugin_description = "Example calculator UI plugin"
    plugin_dependencies = ["calculator"]
    
    def __init__(self):
        """Initialize the calculator UI plugin."""
        super().__init__()
        self._calculator_service = None
        self._page = None
        
    def _initialize(self) -> bool:
        """Initialize the plugin."""
        self.logger.info("Initializing calculator UI plugin")
        
        # Check if calculator service is available
        try:
            # The plugin would be registered with the container
            self._calculator_service = container.get_plugin("calculator")
            return True
        except Exception as e:
            self.logger.error(f"Calculator service not available: {e}")
            return False
            
    def _shutdown(self) -> None:
        """Shut down the plugin."""
        self.logger.info("Shutting down calculator UI plugin")
        self._calculator_service = None
        self._page = None
        
    def _register_page(self, main_window) -> bool:
        """
        Register the calculator page with the main window.
        
        Args:
            main_window: The main window instance
            
        Returns:
            True if registration succeeded, False otherwise
        """
        try:
            # Create the calculator page
            self._page = CalculatorPage(
                main_window.content_frame,
                calculator_service=self._calculator_service,
                navigation_callback=main_window.navigate
            )
            
            # Register the page with the main window
            main_window.pages['calculator'] = self._page
            
            # Add to sidebar navigation
            main_window.sidebar.add_item(
                "calculator",
                "Calculator",
                row=3  # After Home, Actuarial, Finance
            )
            
            self.logger.info("Calculator page registered with main window")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering calculator page: {e}", exc_info=True)
            return False


class CalculatorPage(PageContainer):
    """
    Calculator page for the application.
    
    This page provides a simple calculator UI that uses the calculator service.
    """
    
    def __init__(
        self,
        parent: ttk.Frame,
        calculator_service: CalculatorServiceInterface,
        navigation_callback: Optional[Callable] = None
    ):
        """
        Initialize the calculator page.
        
        Args:
            parent: Parent frame
            calculator_service: Calculator service
            navigation_callback: Function to navigate to other pages
        """
        super().__init__(
            parent,
            page_id="calculator",
            title="Calculator",
            navigation_callback=navigation_callback
        )
        
        self.calculator_service = calculator_service
        self.setup_content()
        
        logger.debug("Calculator page initialized")
        
    def setup_content(self):
        """Set up the page content."""
        # Configure grid layout for the content
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Calculator
        self.content_frame.grid_rowconfigure(1, weight=1)  # History
        
        # Create calculator section
        self._create_calculator_section()
        
        # Create history section
        self._create_history_section()
        
    def _create_calculator_section(self):
        """Create the calculator section."""
        calculator_frame = ttk.LabelFrame(
            self.content_frame,
            text="Calculator",
            bootstyle="primary"
        )
        calculator_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Configure grid
        calculator_frame.grid_columnconfigure(0, weight=1)
        calculator_frame.grid_columnconfigure(1, weight=1)
        calculator_frame.grid_columnconfigure(2, weight=1)
        
        # Input fields
        input_frame = ttk.Frame(calculator_frame)
        input_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        # First number
        ttk.Label(
            input_frame,
            text="First Number:",
            width=15,
            anchor=tk.E
        ).grid(row=0, column=0, padx=5, pady=5)
        
        self.first_var = tk.DoubleVar(value=0.0)
        ttk.Entry(
            input_frame,
            textvariable=self.first_var,
            width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Second number
        ttk.Label(
            input_frame,
            text="Second Number:",
            width=15,
            anchor=tk.E
        ).grid(row=1, column=0, padx=5, pady=5)
        
        self.second_var = tk.DoubleVar(value=0.0)
        ttk.Entry(
            input_frame,
            textvariable=self.second_var,
            width=10
        ).grid(row=1, column=1, padx=5, pady=5)
        
        # Result
        ttk.Label(
            input_frame,
            text="Result:",
            width=15,
            anchor=tk.E
        ).grid(row=2, column=0, padx=5, pady=5)
        
        self.result_var = tk.StringVar(value="0.0")
        result_entry = ttk.Entry(
            input_frame,
            textvariable=self.result_var,
            width=20,
            state="readonly"
        )
        result_entry.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Operation buttons
        operations_frame = ttk.Frame(calculator_frame)
        operations_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        # Add button
        ttk.Button(
            operations_frame,
            text="Add",
            command=self._add,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=5)
        
        # Subtract button
        ttk.Button(
            operations_frame,
            text="Subtract",
            command=self._subtract,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=5)
        
        # Multiply button
        ttk.Button(
            operations_frame,
            text="Multiply",
            command=self._multiply,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=5)
        
        # Divide button
        ttk.Button(
            operations_frame,
            text="Divide",
            command=self._divide,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=5)
        
    def _create_history_section(self):
        """Create the history section."""
        history_frame = ttk.LabelFrame(
            self.content_frame,
            text="Calculation History",
            bootstyle="secondary"
        )
        history_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(0, weight=1)
        
        # Create a treeview for the history
        columns = ("operation", "inputs", "result", "timestamp")
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            bootstyle="primary"
        )
        
        # Configure columns
        self.history_tree.heading("operation", text="Operation")
        self.history_tree.heading("inputs", text="Inputs")
        self.history_tree.heading("result", text="Result")
        self.history_tree.heading("timestamp", text="Timestamp")
        
        self.history_tree.column("operation", width=100)
        self.history_tree.column("inputs", width=200)
        self.history_tree.column("result", width=100)
        self.history_tree.column("timestamp", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        
        # Controls
        controls_frame = ttk.Frame(history_frame)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Refresh button
        ttk.Button(
            controls_frame,
            text="Refresh History",
            command=self._refresh_history,
            bootstyle="secondary"
        ).pack(side=tk.RIGHT, padx=5)
        
    def _add(self):
        """Perform addition."""
        try:
            a = self.first_var.get()
            b = self.second_var.get()
            result = self.calculator_service.add(a, b)
            self.result_var.set(str(result))
            self._refresh_history()
        except Exception as e:
            self.show_error(f"Error performing addition: {e}")
            
    def _subtract(self):
        """Perform subtraction."""
        try:
            a = self.first_var.get()
            b = self.second_var.get()
            result = self.calculator_service.subtract(a, b)
            self.result_var.set(str(result))
            self._refresh_history()
        except Exception as e:
            self.show_error(f"Error performing subtraction: {e}")
            
    def _multiply(self):
        """Perform multiplication."""
        try:
            a = self.first_var.get()
            b = self.second_var.get()
            result = self.calculator_service.multiply(a, b)
            self.result_var.set(str(result))
            self._refresh_history()
        except Exception as e:
            self.show_error(f"Error performing multiplication: {e}")
            
    def _divide(self):
        """Perform division."""
        try:
            a = self.first_var.get()
            b = self.second_var.get()
            result = self.calculator_service.divide(a, b)
            self.result_var.set(str(result))
            self._refresh_history()
        except ZeroDivisionError:
            self.show_error("Cannot divide by zero")
        except Exception as e:
            self.show_error(f"Error performing division: {e}")
            
    def _refresh_history(self):
        """Refresh the history treeview."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Get history from service
        history = self.calculator_service.get_history()
        
        # Add items to treeview
        for i, record in enumerate(history):
            # Format inputs
            inputs_str = ", ".join(f"{k}={v}" for k, v in record["inputs"].items())
            
            # Format timestamp
            import time
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record["timestamp"]))
            
            self.history_tree.insert(
                "",
                "end",
                values=(
                    record["operation"],
                    inputs_str,
                    record["result"],
                    timestamp
                )
            )
            
    def refresh(self):
        """Refresh the page."""
        self._refresh_history()