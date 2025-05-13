"""
Help page module for the Universal App.

This module provides the help page for user assistance and documentation.
"""
import logging
from typing import Dict, Callable, Optional, Any, List
import webbrowser

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Import UI components
from ui.components.page_container import PageContainer

# Import config
from core.config import config_manager

logger = logging.getLogger(__name__)


class HelpPage(PageContainer):
    """
    Help page for the application.
    
    This page provides user assistance, documentation, and FAQs.
    """
    
    def __init__(self, parent: ttk.Frame, navigation_callback: Optional[Callable] = None):
        """
        Initialize the help page.
        
        Args:
            parent: Parent frame
            navigation_callback: Function to navigate to other pages
        """
        super().__init__(
            parent,
            page_id="help",
            title="Help",
            navigation_callback=navigation_callback
        )
        
        self.setup_content()
        logger.debug("Help page initialized")
        
    def setup_content(self):
        """Set up the page content."""
        # Configure grid layout for the content
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Header
        self.content_frame.grid_rowconfigure(1, weight=1)  # Content area
        
        # Header section
        self._create_header_section()
        
        # Help content with tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create help tabs
        self._create_getting_started_tab()
        self._create_features_tab()
        self._create_faq_tab()
        self._create_support_tab()
        
    def _create_header_section(self):
        """Create the header section at the top of the page."""
        header_frame = ttk.Frame(self.content_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Help & Documentation",
            font=("Helvetica", 16),
            bootstyle="dark"
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Description
        description = ttk.Label(
            header_frame,
            text=(
                f"Welcome to {config_manager.app.title} {config_manager.app.version} help. "
                "Find guides, FAQs, and support information below."
            ),
            wraplength=800,
            justify=tk.LEFT,
            bootstyle="secondary"
        )
        description.pack(anchor=tk.W, pady=(0, 10))
        
        # Separator
        ttk.Separator(header_frame).pack(fill=tk.X, pady=5)
        
    def _create_getting_started_tab(self):
        """Create getting started tab with basic usage instructions."""
        getting_started_frame = ttk.Frame(self.notebook)
        self.notebook.add(getting_started_frame, text="Getting Started")
        
        # Force update to prevent blank display until mouse movement
        self.notebook.update_idletasks()
        
        # Configure scrolling
        outer_frame = ttk.Frame(getting_started_frame)
        outer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a canvas with scrollbar
        canvas = tk.Canvas(outer_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas to hold the content
        content_frame = ttk.Frame(canvas)
        
        # Add the content frame to the canvas
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # Configure the content frame and canvas
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
            
        content_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Welcome section
        welcome_frame = ttk.Frame(content_frame)
        welcome_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            welcome_frame,
            text="Welcome to Universal App!",
            font=("Helvetica", 14, "bold"),
            bootstyle="dark"
        ).pack(anchor=tk.W)
        
        ttk.Label(
            welcome_frame,
            text=(
                "Universal App is a platform that hosts multiple services and tools "
                "for data analysis, financial calculations, and actuarial modeling. "
                "This guide will help you get started with the application."
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=5)
        
        # Navigation section
        nav_frame = ttk.LabelFrame(content_frame, text="Navigation")
        nav_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            nav_frame,
            text=(
                "The Universal App uses a sidebar navigation system that allows you "
                "to switch between different services and tools. The sidebar is located "
                "on the left side of the application window."
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        navigation_steps = [
            "Click on a navigation item in the sidebar to switch to that page.",
            "The Home page provides quick access to all available services.",
            "The Actuarial page contains tools for actuarial calculations.",
            "The Finance page provides financial modeling and analysis tools.",
            "The Settings page allows you to customize the application.",
            "The Help page (this page) provides documentation and support resources."
        ]
        
        for i, step in enumerate(navigation_steps):
            step_frame = ttk.Frame(nav_frame)
            step_frame.pack(fill=tk.X, padx=10, pady=2)
            
            ttk.Label(
                step_frame,
                text=f"{i+1}. ",
                width=3,
                anchor=tk.E
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                step_frame,
                text=step,
                wraplength=650,
                justify=tk.LEFT
            ).pack(side=tk.LEFT)
        
        # Available Services section
        services_frame = ttk.LabelFrame(content_frame, text="Available Services")
        services_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            services_frame,
            text=(
                "The Universal App includes the following services:"
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        services = [
            {
                "name": "Actuarial Tools",
                "description": (
                    "Tools for actuarial calculations and analysis, including "
                    "mortality tables and present value calculations."
                ),
                "navigate": "actuarial"
            },
            {
                "name": "Finance Tools",
                "description": (
                    "Financial modeling and analysis tools, including yield curve "
                    "visualization and option pricing."
                ),
                "navigate": "finance"
            }
        ]
        
        for service in services:
            service_item = ttk.Frame(services_frame)
            service_item.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                service_item,
                text=service["name"],
                font=("Helvetica", 11, "bold"),
                bootstyle="primary"
            ).pack(anchor=tk.W)
            
            ttk.Label(
                service_item,
                text=service["description"],
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=3)
            
            ttk.Button(
                service_item,
                text=f"Open {service['name']}",
                command=lambda s=service["navigate"]: self.navigate(s),
                bootstyle="primary-outline"
            ).pack(anchor=tk.W, pady=3)
            
        # Key Concepts section
        concepts_frame = ttk.LabelFrame(content_frame, text="Key Concepts")
        concepts_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            concepts_frame,
            text=(
                "Here are some key concepts to help you understand how the Universal App works:"
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        concepts = [
            {
                "name": "Services",
                "description": (
                    "Services are the core components that provide specific functionality. "
                    "Each service is independent and can be enabled or disabled in the settings."
                )
            },
            {
                "name": "R Integration",
                "description": (
                    "The R Integration service allows the application to run R scripts "
                    "for specialized calculations and analysis. This integration is used "
                    "by both the Actuarial and Finance services."
                )
            },
            {
                "name": "Data Storage",
                "description": (
                    "Data is stored in the data directory specified in the application settings. "
                    "Each service has its own subdirectory for storing service-specific data."
                )
            }
        ]
        
        for concept in concepts:
            concept_item = ttk.Frame(concepts_frame)
            concept_item.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                concept_item,
                text=concept["name"],
                font=("Helvetica", 11, "bold"),
                bootstyle="dark"
            ).pack(anchor=tk.W)
            
            ttk.Label(
                concept_item,
                text=concept["description"],
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=3)
            
    def _create_features_tab(self):
        """Create features tab with detailed information about app features."""
        features_frame = ttk.Frame(self.notebook)
        self.notebook.add(features_frame, text="Features")
        
        # Configure scrolling
        outer_frame = ttk.Frame(features_frame)
        outer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a canvas with scrollbar
        canvas = tk.Canvas(outer_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas to hold the content
        content_frame = ttk.Frame(canvas)
        
        # Add the content frame to the canvas
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # Configure the content frame and canvas
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
            
        content_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Actuarial Features
        actuarial_frame = ttk.LabelFrame(content_frame, text="Actuarial Features")
        actuarial_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            actuarial_frame,
            text=(
                "The Actuarial service provides tools for actuarial calculations and analysis:"
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        actuarial_features = [
            {
                "name": "Mortality Tables",
                "description": (
                    "Calculate and visualize mortality tables based on various mortality models. "
                    "Supports different table types, gender adjustments, and age ranges."
                ),
                "details": [
                    "Supports multiple mortality table types",
                    "Calculates qx, px, lx, ex, and ax values",
                    "Visualizes mortality data with interactive charts",
                    "Exports results to various formats"
                ]
            },
            {
                "name": "Present Value Calculator",
                "description": (
                    "Calculate the present value of annuities and other payment streams "
                    "with various parameters and mortality assumptions."
                ),
                "details": [
                    "Calculates present value of annuities",
                    "Supports different payment frequencies",
                    "Adjusts for mortality using selected tables",
                    "Provides expected duration and monthly equivalents"
                ]
            }
        ]
        
        for feature in actuarial_features:
            feature_item = ttk.Frame(actuarial_frame)
            feature_item.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                feature_item,
                text=feature["name"],
                font=("Helvetica", 11, "bold"),
                bootstyle="primary"
            ).pack(anchor=tk.W)
            
            ttk.Label(
                feature_item,
                text=feature["description"],
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=3)
            
            details_frame = ttk.Frame(feature_item)
            details_frame.pack(fill=tk.X, padx=20, pady=3)
            
            for detail in feature["details"]:
                detail_item = ttk.Frame(details_frame)
                detail_item.pack(fill=tk.X, pady=2)
                
                ttk.Label(
                    detail_item,
                    text="•",
                    width=2,
                    anchor=tk.E
                ).pack(side=tk.LEFT)
                
                ttk.Label(
                    detail_item,
                    text=detail,
                    wraplength=600,
                    justify=tk.LEFT
                ).pack(side=tk.LEFT)
                
        # Finance Features
        finance_frame = ttk.LabelFrame(content_frame, text="Finance Features")
        finance_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            finance_frame,
            text=(
                "The Finance service provides tools for financial modeling and analysis:"
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        finance_features = [
            {
                "name": "Yield Curve Visualization",
                "description": (
                    "Visualize and analyze yield curves for different date ranges and curve types. "
                    "Compare yields across different maturities and time periods."
                ),
                "details": [
                    "Supports nominal and real yield curves",
                    "Visualizes yield curves with interactive charts",
                    "Allows date range selection for historical analysis",
                    "Exports results to various formats"
                ]
            },
            {
                "name": "Option Pricing Calculator",
                "description": (
                    "Price options using the Black-Scholes model with custom parameters. "
                    "Calculate option greeks for risk analysis."
                ),
                "details": [
                    "Supports call and put options",
                    "Calculates option price using Black-Scholes model",
                    "Provides delta, gamma, theta, and vega calculations",
                    "Allows custom parameters for spot price, strike price, volatility, etc."
                ]
            },
            {
                "name": "Portfolio Metrics",
                "description": (
                    "Calculate portfolio risk and return metrics based on asset returns and weights. "
                    "Analyze portfolio performance and risk characteristics."
                ),
                "details": [
                    "Calculates expected return, volatility, and Sharpe ratio",
                    "Supports custom asset weights",
                    "Handles multiple assets with different return distributions",
                    "Provides performance metrics for portfolio analysis"
                ]
            }
        ]
        
        for feature in finance_features:
            feature_item = ttk.Frame(finance_frame)
            feature_item.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                feature_item,
                text=feature["name"],
                font=("Helvetica", 11, "bold"),
                bootstyle="info"
            ).pack(anchor=tk.W)
            
            ttk.Label(
                feature_item,
                text=feature["description"],
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=3)
            
            details_frame = ttk.Frame(feature_item)
            details_frame.pack(fill=tk.X, padx=20, pady=3)
            
            for detail in feature["details"]:
                detail_item = ttk.Frame(details_frame)
                detail_item.pack(fill=tk.X, pady=2)
                
                ttk.Label(
                    detail_item,
                    text="•",
                    width=2,
                    anchor=tk.E
                ).pack(side=tk.LEFT)
                
                ttk.Label(
                    detail_item,
                    text=detail,
                    wraplength=600,
                    justify=tk.LEFT
                ).pack(side=tk.LEFT)
                
        # Settings Features
        settings_frame = ttk.LabelFrame(content_frame, text="Settings & Customization")
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            settings_frame,
            text=(
                "The Settings page allows you to customize the application:"
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        settings_features = [
            {
                "name": "General Settings",
                "description": (
                    "Configure general application settings such as application name, "
                    "version, debug mode, and data directory."
                )
            },
            {
                "name": "Appearance Settings",
                "description": (
                    "Customize the application appearance, including theme, window size, "
                    "and sidebar width."
                )
            },
            {
                "name": "Service Settings",
                "description": (
                    "Enable or disable services, configure R integration, and set service-specific "
                    "parameters."
                )
            }
        ]
        
        for feature in settings_features:
            feature_item = ttk.Frame(settings_frame)
            feature_item.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                feature_item,
                text=feature["name"],
                font=("Helvetica", 11, "bold"),
                bootstyle="success"
            ).pack(anchor=tk.W)
            
            ttk.Label(
                feature_item,
                text=feature["description"],
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=3)
            
    def _create_faq_tab(self):
        """Create FAQ tab with frequently asked questions."""
        faq_frame = ttk.Frame(self.notebook)
        self.notebook.add(faq_frame, text="FAQ")
        
        # Configure scrolling
        outer_frame = ttk.Frame(faq_frame)
        outer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a canvas with scrollbar
        canvas = tk.Canvas(outer_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        
        # Configure scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas to hold the content
        content_frame = ttk.Frame(canvas)
        
        # Add the content frame to the canvas
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # Configure the content frame and canvas
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
            
        content_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        # Add mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Introduction
        intro_frame = ttk.Frame(content_frame)
        intro_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            intro_frame,
            text="Frequently Asked Questions",
            font=("Helvetica", 14, "bold"),
            bootstyle="dark"
        ).pack(anchor=tk.W)
        
        ttk.Label(
            intro_frame,
            text=(
                "Find answers to common questions about the Universal App. "
                "If you don't see your question here, please contact support."
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=5)
        
        # FAQ items
        faqs = [
            {
                "question": "What is Universal App?",
                "answer": (
                    "Universal App is a comprehensive application that provides various services "
                    "and tools for data analysis, financial calculations, and actuarial modeling. "
                    "It serves as a container for multiple projects until they grow large enough "
                    "to be moved into their own repositories."
                )
            },
            {
                "question": "How do I install R for the R integration?",
                "answer": (
                    "To use the R integration features, you need to have R installed on your system. "
                    "You can download R from the official R website (https://www.r-project.org/) and "
                    "follow the installation instructions for your operating system. After installing R, "
                    "make sure it's available in your system PATH. The Universal App uses rpy2 to "
                    "interface with R."
                )
            },
            {
                "question": "What mortality tables are available in the Actuarial service?",
                "answer": (
                    "The Actuarial service includes various mortality tables such as the Society of "
                    "Actuaries 2012 Individual Annuity Mortality (SOA 2012 IAM) table and the 2001 "
                    "Commissioners Standard Ordinary (CSO 2001) table. You can select the table type "
                    "in the mortality calculation form."
                )
            },
            {
                "question": "Can I export the results from the calculation tools?",
                "answer": (
                    "Yes, all calculation tools provide options to export results in various formats, "
                    "including CSV, Excel, and PDF. Look for the export button in the results section "
                    "of each tool."
                )
            },
            {
                "question": "Does the application save my work?",
                "answer": (
                    "The application does not automatically save your work. If you want to save your "
                    "results, you should export them using the export options provided in each tool. "
                    "The application does save your settings and preferences."
                )
            },
            {
                "question": "How can I reset the application settings?",
                "answer": (
                    "You can reset the application settings to defaults by going to the Settings page "
                    "and clicking the 'Reset to Defaults' button. This will reset all settings to their "
                    "factory defaults, but you'll need to click 'Save Changes' to apply the reset."
                )
            },
            {
                "question": "Can I add my own R scripts to the application?",
                "answer": (
                    "Yes, you can add your own R scripts to the application by placing them in the "
                    "R scripts directory specified in the Settings page under Service Settings. The "
                    "scripts should follow the conventions used by the existing scripts and should be "
                    "placed in the appropriate subdirectory (actuarial, finance, or common)."
                )
            },
            {
                "question": "How do I report a bug or request a feature?",
                "answer": (
                    "If you encounter a bug or would like to request a feature, please submit an issue "
                    "through the support channels listed in the Support tab of this Help page. "
                    "Please include as much detail as possible, including steps to reproduce the issue "
                    "and the expected behavior."
                )
            }
        ]
        
        for i, faq in enumerate(faqs):
            faq_item = ttk.Frame(content_frame)
            faq_item.pack(fill=tk.X, padx=20, pady=5)
            
            question_frame = ttk.Frame(faq_item)
            question_frame.pack(fill=tk.X, anchor=tk.W)
            
            ttk.Label(
                question_frame,
                text=f"Q{i+1}:",
                font=("Helvetica", 11, "bold"),
                bootstyle="primary",
                width=3
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                question_frame,
                text=faq["question"],
                font=("Helvetica", 11, "bold"),
                wraplength=650,
                justify=tk.LEFT,
                bootstyle="dark"
            ).pack(side=tk.LEFT)
            
            answer_frame = ttk.Frame(faq_item)
            answer_frame.pack(fill=tk.X, anchor=tk.W, padx=(30, 0), pady=5)
            
            ttk.Label(
                answer_frame,
                text=faq["answer"],
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W)
            
            # Add separator except for the last item
            if i < len(faqs) - 1:
                ttk.Separator(content_frame).pack(fill=tk.X, padx=20, pady=5)
        
    def _create_support_tab(self):
        """Create support tab with contact information and resources."""
        support_frame = ttk.Frame(self.notebook)
        self.notebook.add(support_frame, text="Support")
        
        # Configure frame
        support_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(support_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        ttk.Label(
            header_frame,
            text="Support and Resources",
            font=("Helvetica", 14, "bold"),
            bootstyle="dark"
        ).pack(anchor=tk.W)
        
        ttk.Label(
            header_frame,
            text=(
                "Find help resources and support information for the Universal App. "
                "If you encounter any issues or have questions, these resources can help you."
            ),
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=5)
        
        # Contact Information
        contact_frame = ttk.LabelFrame(support_frame, text="Contact Information")
        contact_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        ttk.Label(
            contact_frame,
            text="For support inquiries, please contact:",
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        email_frame = ttk.Frame(contact_frame)
        email_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            email_frame,
            text="Email:",
            font=("Helvetica", 11, "bold"),
            width=10,
            anchor=tk.E
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            email_frame,
            text="support@universalapp.example.com",
            wraplength=650,
            justify=tk.LEFT
        ).pack(side=tk.LEFT, padx=5)
        
        # Documentation
        docs_frame = ttk.LabelFrame(support_frame, text="Documentation")
        docs_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        ttk.Label(
            docs_frame,
            text="Access the official documentation for the Universal App:",
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        docs_button = ttk.Button(
            docs_frame,
            text="Open Documentation",
            bootstyle="primary",
            # This is a placeholder URL - in a real app, you'd use a real documentation URL
            command=lambda: webbrowser.open("https://example.com/docs")
        )
        docs_button.pack(anchor=tk.W, padx=10, pady=5)
        
        # Resources
        resources_frame = ttk.LabelFrame(support_frame, text="Additional Resources")
        resources_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        ttk.Label(
            resources_frame,
            text="Explore additional resources for the Universal App:",
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        resources = [
            {
                "name": "Video Tutorials",
                "description": "Watch video tutorials for using the Universal App.",
                "url": "https://example.com/tutorials"
            },
            {
                "name": "Knowledge Base",
                "description": "Browse the knowledge base for articles and guides.",
                "url": "https://example.com/kb"
            },
            {
                "name": "Community Forum",
                "description": "Join the community forum to ask questions and share ideas.",
                "url": "https://example.com/forum"
            }
        ]
        
        for resource in resources:
            resource_item = ttk.Frame(resources_frame)
            resource_item.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(
                resource_item,
                text=resource["name"],
                font=("Helvetica", 11, "bold"),
                bootstyle="primary"
            ).pack(anchor=tk.W)
            
            ttk.Label(
                resource_item,
                text=resource["description"],
                wraplength=650,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=3)
            
            ttk.Button(
                resource_item,
                text=f"Visit {resource['name']}",
                command=lambda url=resource["url"]: webbrowser.open(url),
                bootstyle="primary-outline"
            ).pack(anchor=tk.W, pady=3)
        
    def refresh(self):
        """Refresh the help page."""
        # Currently nothing to refresh dynamically
        logger.debug("Refreshed help page")