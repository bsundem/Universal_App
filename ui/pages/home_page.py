"""
Home page module for the Universal App.

This module provides the home page / dashboard for the application.
"""
import logging
from typing import Dict, Callable, Optional, Any, List

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Import UI components
from ui.components.page_container import PageContainer

# Import services
from services.container import get_r_service, get_actuarial_service, get_finance_service

logger = logging.getLogger(__name__)


class HomePage(PageContainer):
    """
    Home page / dashboard for the application.
    
    This page serves as the main landing page and dashboard for the app.
    """
    
    def __init__(self, parent: ttk.Frame, navigation_callback: Optional[Callable] = None):
        """
        Initialize the home page.
        
        Args:
            parent: Parent frame
            navigation_callback: Function to navigate to other pages
        """
        super().__init__(
            parent,
            page_id="home",
            title="Home",
            navigation_callback=navigation_callback
        )
        
        self.setup_content()
        logger.debug("Home page initialized")
        
    def setup_content(self):
        """Set up the page content."""
        # Configure grid layout for the content
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Welcome section
        self.content_frame.grid_rowconfigure(1, weight=1)  # Card section
        self.content_frame.grid_rowconfigure(2, weight=1)  # Recent activity
        
        # Welcome section
        self._create_welcome_section()
        
        # Main cards
        self._create_service_cards()
        
        # Recent activity
        self._create_activity_section()
        
    def _create_welcome_section(self):
        """Create the welcome section at the top of the page."""
        welcome_frame = ttk.Frame(self.content_frame)
        welcome_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        # Welcome message
        welcome_label = ttk.Label(
            welcome_frame,
            text="Welcome to the Universal App!",
            font=("Helvetica", 16),
            bootstyle="dark"
        )
        welcome_label.pack(anchor=tk.W, pady=(0, 5))
        
        description = ttk.Label(
            welcome_frame,
            text=(
                "This application provides various services and tools for data analysis, "
                "financial calculations, and more. Use the sidebar to navigate between "
                "different sections of the app."
            ),
            wraplength=800,
            justify=tk.LEFT,
            bootstyle="secondary"
        )
        description.pack(anchor=tk.W, pady=(0, 10))
        
        # Status section
        status_frame = ttk.Frame(welcome_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        # Check if R is available
        r_service = get_r_service()
        r_available = r_service.is_available()
        
        r_status = ttk.Label(
            status_frame,
            text="R Integration: ",
            font=("Helvetica", 11),
            bootstyle="dark"
        )
        r_status.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        r_status_value = ttk.Label(
            status_frame,
            text="Available" if r_available else "Not Available",
            font=("Helvetica", 11),
            bootstyle="success" if r_available else "danger"
        )
        r_status_value.grid(row=0, column=1, sticky=tk.W)
        
    def _create_service_cards(self):
        """Create service cards for quick navigation."""
        # Actuarial card
        actuarial_card = ttk.Frame(self.content_frame, bootstyle="primary")
        actuarial_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add a subtle hover effect with a bind
        actuarial_card.bind("<Enter>", lambda e: actuarial_card.configure(cursor="hand2"))
        actuarial_card.bind("<Leave>", lambda e: actuarial_card.configure(cursor=""))
        actuarial_card.bind("<Button-1>", lambda e: self.navigate("actuarial"))
        
        actuarial_title = ttk.Label(
            actuarial_card,
            text="Actuarial Tools",
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        )
        actuarial_title.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        actuarial_desc = ttk.Label(
            actuarial_card,
            text=(
                "Perform actuarial calculations including mortality tables "
                "and present value calculations."
            ),
            wraplength=350,
            justify=tk.LEFT,
            bootstyle="primary"
        )
        actuarial_desc.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        actuarial_features = ttk.Frame(actuarial_card)
        actuarial_features.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Feature list
        features = [
            "Mortality Table Visualization",
            "Present Value Calculator"
        ]
        
        for i, feature in enumerate(features):
            feature_label = ttk.Label(
                actuarial_features,
                text=f"• {feature}",
                bootstyle="primary"
            )
            feature_label.pack(anchor=tk.W, pady=2)
            
        # Launch button
        actuarial_btn = ttk.Button(
            actuarial_card,
            text="Open Actuarial Tools",
            command=lambda: self.navigate("actuarial"),
            bootstyle="primary-outline"
        )
        actuarial_btn.pack(anchor=tk.E, padx=15, pady=(5, 15))
        
        # Finance card
        finance_card = ttk.Frame(self.content_frame, bootstyle="info")
        finance_card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Add hover effect
        finance_card.bind("<Enter>", lambda e: finance_card.configure(cursor="hand2"))
        finance_card.bind("<Leave>", lambda e: finance_card.configure(cursor=""))
        finance_card.bind("<Button-1>", lambda e: self.navigate("finance"))
        
        finance_title = ttk.Label(
            finance_card,
            text="Finance Tools",
            font=("Helvetica", 14, "bold"),
            bootstyle="info"
        )
        finance_title.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        finance_desc = ttk.Label(
            finance_card,
            text=(
                "Analyze financial data including yield curves "
                "and options pricing models."
            ),
            wraplength=350,
            justify=tk.LEFT,
            bootstyle="info"
        )
        finance_desc.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        finance_features = ttk.Frame(finance_card)
        finance_features.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Feature list
        features = [
            "Yield Curve Visualization",
            "Option Pricing Calculator"
        ]
        
        for i, feature in enumerate(features):
            feature_label = ttk.Label(
                finance_features,
                text=f"• {feature}",
                bootstyle="info"
            )
            feature_label.pack(anchor=tk.W, pady=2)
            
        # Launch button
        finance_btn = ttk.Button(
            finance_card,
            text="Open Finance Tools",
            command=lambda: self.navigate("finance"),
            bootstyle="info-outline"
        )
        finance_btn.pack(anchor=tk.E, padx=15, pady=(5, 15))
        
    def _create_activity_section(self):
        """Create recent activity section at the bottom of the page."""
        activity_frame = ttk.LabelFrame(
            self.content_frame,
            text="Quick Start",
            bootstyle="default"
        )
        activity_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Configure grid
        activity_frame.grid_columnconfigure(0, weight=1)
        
        # Quick start list
        steps = [
            {
                "title": "Calculate mortality rates",
                "description": "Go to the Actuarial page to calculate and visualize mortality rates with custom parameters.",
                "action": lambda: self.navigate("actuarial")
            },
            {
                "title": "Analyze yield curves",
                "description": "Visit the Finance page to visualize and analyze yield curves with different date ranges.",
                "action": lambda: self.navigate("finance")
            },
            {
                "title": "Price options",
                "description": "Use the Finance tools to price options with the Black-Scholes model and custom parameters.",
                "action": lambda: self.navigate("finance", tab="options")
            }
        ]
        
        for i, step in enumerate(steps):
            step_frame = ttk.Frame(activity_frame)
            step_frame.grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            
            step_title = ttk.Label(
                step_frame,
                text=step["title"],
                font=("Helvetica", 12, "bold"),
                bootstyle="dark"
            )
            step_title.grid(row=0, column=0, sticky=tk.W)
            
            step_desc = ttk.Label(
                step_frame,
                text=step["description"],
                wraplength=700,
                justify=tk.LEFT,
                bootstyle="secondary"
            )
            step_desc.grid(row=1, column=0, sticky=tk.W)
            
            step_btn = ttk.Button(
                step_frame,
                text="Go",
                command=step["action"],
                bootstyle="primary-outline"
            )
            step_btn.grid(row=0, column=1, rowspan=2, padx=(20, 5))
            
            # Add separator except for the last item
            if i < len(steps) - 1:
                ttk.Separator(activity_frame).grid(row=i+1, column=0, sticky="ew", padx=10)
        
    def refresh(self):
        """Refresh the dashboard content."""
        # Check if R is available
        r_service = get_r_service()
        r_available = r_service.is_available()
        
        # Update the status
        # In a real app, we would update more dynamic content here
        logger.debug(f"Refreshed home page, R available: {r_available}")