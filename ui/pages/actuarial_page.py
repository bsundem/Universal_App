"""
Actuarial page module for the Universal App.

This module provides the actuarial page with visualizations
for mortality table analysis and present value calculations.
"""
import logging
from typing import Dict, Callable, Optional, Any, List, Tuple
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Import UI components
from ui.components.page_container import PageContainer

# Import services
from services.container import get_actuarial_service, get_r_service

logger = logging.getLogger(__name__)


class ActuarialPage(PageContainer):
    """
    Actuarial page with visualizations and calculators.
    
    This page provides actuarial tools including mortality table
    visualization and present value calculations.
    """
    
    def __init__(self, parent: ttk.Frame, navigation_callback: Optional[Callable] = None):
        """
        Initialize the actuarial page.
        
        Args:
            parent: Parent frame
            navigation_callback: Function to navigate to other pages
        """
        super().__init__(
            parent,
            page_id="actuarial",
            title="Actuarial Tools",
            navigation_callback=navigation_callback
        )
        
        # Initialize service
        self.actuarial_service = get_actuarial_service()
        
        # Set up tab control for different tools
        self._create_tab_control()
        
        # Set up the page content
        self.setup_content()
        
        logger.debug("Actuarial page initialized")
        
    def _create_tab_control(self):
        """Create a tab control for different actuarial tools."""
        self.tab_control = ttk.Notebook(self.content_frame)
        self.tab_control.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Mortality table tab
        self.mortality_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.mortality_tab, text="Mortality Tables")
        
        # Present value tab
        self.pv_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.pv_tab, text="Present Value Calculator")
        
        # Configure tab layouts
        for tab in [self.mortality_tab, self.pv_tab]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            
    def setup_content(self):
        """Set up the page content."""
        # Set up mortality table visualization
        self._setup_mortality_visualization()
        
        # Set up present value calculator
        self._setup_present_value_calculator()
        
    def _setup_mortality_visualization(self):
        """Set up the mortality table visualization tab."""
        # Main frame with left panel for controls and right panel for visualization
        main_frame = ttk.Frame(self.mortality_tab)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky="ns", padx=(5, 10), pady=5)
        
        # Title for controls
        ttk.Label(
            controls_frame, 
            text="Parameters",
            font=("Helvetica", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Age range
        age_frame = ttk.Frame(controls_frame)
        age_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(age_frame, text="Age Range:").grid(row=0, column=0, sticky=tk.W)
        
        # Age from
        age_from_frame = ttk.Frame(age_frame)
        age_from_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(age_from_frame, text="From:").pack(side=tk.LEFT, padx=(0, 5))
        self.age_from_var = tk.StringVar(value="30")
        age_from_entry = ttk.Entry(age_from_frame, textvariable=self.age_from_var, width=5)
        age_from_entry.pack(side=tk.LEFT)
        
        # Age to
        age_to_frame = ttk.Frame(age_frame)
        age_to_frame.grid(row=1, column=1, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        
        ttk.Label(age_to_frame, text="To:").pack(side=tk.LEFT, padx=(0, 5))
        self.age_to_var = tk.StringVar(value="90")
        age_to_entry = ttk.Entry(age_to_frame, textvariable=self.age_to_var, width=5)
        age_to_entry.pack(side=tk.LEFT)
        
        # Interest rate
        interest_frame = ttk.Frame(controls_frame)
        interest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(interest_frame, text="Interest Rate:").grid(row=0, column=0, sticky=tk.W)
        
        interest_input_frame = ttk.Frame(interest_frame)
        interest_input_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.interest_rate_var = tk.StringVar(value="0.04")
        interest_entry = ttk.Entry(interest_input_frame, textvariable=self.interest_rate_var, width=8)
        interest_entry.pack(side=tk.LEFT)
        ttk.Label(interest_input_frame, text=" (0-1)").pack(side=tk.LEFT)
        
        # Mortality table
        table_frame = ttk.Frame(controls_frame)
        table_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(table_frame, text="Mortality Table:").pack(anchor=tk.W)
        
        self.table_type_var = tk.StringVar(value="soa_2012")
        
        # Get available tables (in a real app, this would be dynamic)
        tables = [
            {"id": "soa_2012", "name": "SOA 2012 IAM"},
            {"id": "cso_2001", "name": "CSO 2001"}
        ]
        
        for table in tables:
            table_radio = ttk.Radiobutton(
                table_frame, 
                text=table["name"],
                variable=self.table_type_var,
                value=table["id"]
            )
            table_radio.pack(anchor=tk.W, padx=(10, 0))
        
        # Gender
        gender_frame = ttk.Frame(controls_frame)
        gender_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gender_frame, text="Gender:").pack(anchor=tk.W)
        
        self.gender_var = tk.StringVar(value="male")
        
        for gender in ["male", "female", "unisex"]:
            gender_radio = ttk.Radiobutton(
                gender_frame, 
                text=gender.capitalize(),
                variable=self.gender_var,
                value=gender
            )
            gender_radio.pack(anchor=tk.W, padx=(10, 0))
        
        # Calculate button
        ttk.Separator(controls_frame).pack(fill=tk.X, pady=10)
        
        calculate_btn = ttk.Button(
            controls_frame,
            text="Calculate",
            command=self._calculate_mortality,
            bootstyle="primary"
        )
        calculate_btn.pack(pady=10)
        
        # Status display
        self.status_var = tk.StringVar()
        status_label = ttk.Label(
            controls_frame, 
            textvariable=self.status_var,
            wraplength=200
        )
        status_label.pack(pady=(0, 10))
        
        # Right panel - visualization
        viz_frame = ttk.Frame(main_frame)
        viz_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        viz_frame.grid_columnconfigure(0, weight=1)
        viz_frame.grid_rowconfigure(1, weight=1)
        
        # Title for visualization
        viz_title = ttk.Label(
            viz_frame, 
            text="Mortality Table Visualization",
            font=("Helvetica", 12, "bold")
        )
        viz_title.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Tabs for different visualizations
        viz_tabs = ttk.Notebook(viz_frame)
        viz_tabs.grid(row=1, column=0, sticky="nsew")
        
        # Graph tab
        self.graph_tab = ttk.Frame(viz_tabs)
        viz_tabs.add(self.graph_tab, text="Graphs")
        self.graph_tab.grid_columnconfigure(0, weight=1)
        self.graph_tab.grid_rowconfigure(0, weight=1)
        
        # Table tab
        self.table_tab = ttk.Frame(viz_tabs)
        viz_tabs.add(self.table_tab, text="Data Table")
        self.table_tab.grid_columnconfigure(0, weight=1)
        self.table_tab.grid_rowconfigure(0, weight=1)
        
        # Default plot with message
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("No data yet. Click Calculate to generate mortality data.")
        self.ax.set_xlabel("Age")
        self.ax.set_ylabel("Value")
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_tab)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Empty table view
        self.table_view = ttk.Treeview(self.table_tab)
        self.table_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        table_scrollbar_y = ttk.Scrollbar(self.table_tab, orient="vertical", command=self.table_view.yview)
        table_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.table_view.configure(yscrollcommand=table_scrollbar_y.set)
        
        # Define columns
        self.table_view["columns"] = ("age", "qx", "px", "lx", "ex", "ax")
        
        # Format columns
        self.table_view.column("#0", width=0, stretch=tk.NO)
        self.table_view.column("age", anchor=tk.CENTER, width=50)
        self.table_view.column("qx", anchor=tk.CENTER, width=80)
        self.table_view.column("px", anchor=tk.CENTER, width=80)
        self.table_view.column("lx", anchor=tk.CENTER, width=100)
        self.table_view.column("ex", anchor=tk.CENTER, width=80)
        self.table_view.column("ax", anchor=tk.CENTER, width=80)
        
        # Create headings
        self.table_view.heading("#0", text="", anchor=tk.CENTER)
        self.table_view.heading("age", text="Age", anchor=tk.CENTER)
        self.table_view.heading("qx", text="qx", anchor=tk.CENTER)
        self.table_view.heading("px", text="px", anchor=tk.CENTER)
        self.table_view.heading("lx", text="lx", anchor=tk.CENTER)
        self.table_view.heading("ex", text="ex", anchor=tk.CENTER)
        self.table_view.heading("ax", text="ax", anchor=tk.CENTER)
        
    def _calculate_mortality(self):
        """Calculate and display mortality data."""
        try:
            # Get input values
            age_from = int(self.age_from_var.get())
            age_to = int(self.age_to_var.get())
            interest_rate = float(self.interest_rate_var.get())
            table_type = self.table_type_var.get()
            gender = self.gender_var.get()
            
            # Validate inputs
            if age_from < 0 or age_to > 120 or age_from >= age_to:
                self.status_var.set("Invalid age range. Must be between 0 and 120, and From must be less than To.")
                return
                
            if interest_rate < 0 or interest_rate > 1:
                self.status_var.set("Invalid interest rate. Must be between 0 and 1.")
                return
                
            # Show loading indicator
            self.show_loader("Calculating mortality data...")
            
            # Calculate mortality data
            df = self.actuarial_service.calculate_mortality_data(
                age_from, age_to, interest_rate, table_type, gender
            )
            
            # Update the visualization
            self._update_mortality_visualization(df)
            
            # Update the table
            self._update_mortality_table(df)
            
            # Hide loader
            self.hide_loader()
            
            # Update status
            self.status_var.set(f"Calculated mortality data for ages {age_from}-{age_to}.")
            
        except Exception as e:
            # Hide loader
            self.hide_loader()
            
            # Show error
            self.status_var.set(f"Error: {str(e)}")
            logger.error(f"Error calculating mortality data: {e}", exc_info=True)
            
    def _update_mortality_visualization(self, df: pd.DataFrame):
        """
        Update the mortality visualization with new data.
        
        Args:
            df: DataFrame with mortality data
        """
        # Clear the figure
        self.fig.clear()
        
        # Create subplot layout
        ax1 = self.fig.add_subplot(221)  # qx
        ax2 = self.fig.add_subplot(222)  # lx
        ax3 = self.fig.add_subplot(223)  # ex
        ax4 = self.fig.add_subplot(224)  # ax
        
        # Plot mortality rate (qx)
        ax1.plot(df["Age"], df["qx"], "r-", marker="o", markersize=3)
        ax1.set_title("Mortality Rate (qx)")
        ax1.set_xlabel("Age")
        ax1.set_ylabel("Rate")
        ax1.grid(True, linestyle="--", alpha=0.7)
        
        # Plot number of lives (lx)
        ax2.plot(df["Age"], df["lx"], "b-", marker="o", markersize=3)
        ax2.set_title("Number of Lives (lx)")
        ax2.set_xlabel("Age")
        ax2.set_ylabel("Lives")
        ax2.grid(True, linestyle="--", alpha=0.7)
        
        # Plot life expectancy (ex)
        ax3.plot(df["Age"], df["ex"], "g-", marker="o", markersize=3)
        ax3.set_title("Life Expectancy (ex)")
        ax3.set_xlabel("Age")
        ax3.set_ylabel("Years")
        ax3.grid(True, linestyle="--", alpha=0.7)
        
        # Plot present value of annuity (ax)
        ax4.plot(df["Age"], df["ax"], "m-", marker="o", markersize=3)
        ax4.set_title("Present Value of Annuity (ax)")
        ax4.set_xlabel("Age")
        ax4.set_ylabel("Value")
        ax4.grid(True, linestyle="--", alpha=0.7)
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Redraw the canvas
        self.canvas.draw()
        
    def _update_mortality_table(self, df: pd.DataFrame):
        """
        Update the mortality data table with new data.
        
        Args:
            df: DataFrame with mortality data
        """
        # Clear existing data
        for item in self.table_view.get_children():
            self.table_view.delete(item)
            
        # Format function for float values
        def format_float(value):
            return f"{value:.6f}"
            
        # Add data to the table
        for i, row in df.iterrows():
            self.table_view.insert(
                "",
                tk.END,
                values=(
                    int(row["Age"]),
                    format_float(row["qx"]),
                    format_float(row["px"]),
                    int(row["lx"]),
                    format_float(row["ex"]),
                    format_float(row["ax"])
                )
            )
            
    def _setup_present_value_calculator(self):
        """Set up the present value calculator tab."""
        # Main frame with left panel for inputs and right panel for results
        main_frame = ttk.Frame(self.pv_tab)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - inputs
        inputs_frame = ttk.Frame(main_frame)
        inputs_frame.grid(row=0, column=0, sticky="ns", padx=(5, 10), pady=5)
        
        # Title for inputs
        ttk.Label(
            inputs_frame, 
            text="Annuity Parameters",
            font=("Helvetica", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Annuitant age
        age_frame = ttk.Frame(inputs_frame)
        age_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(age_frame, text="Annuitant Age:").grid(row=0, column=0, sticky=tk.W)
        
        self.pv_age_var = tk.StringVar(value="65")
        age_entry = ttk.Entry(age_frame, textvariable=self.pv_age_var, width=5)
        age_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Payment amount
        payment_frame = ttk.Frame(inputs_frame)
        payment_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(payment_frame, text="Annual Payment:").grid(row=0, column=0, sticky=tk.W)
        
        self.pv_payment_var = tk.StringVar(value="10000")
        payment_entry = ttk.Entry(payment_frame, textvariable=self.pv_payment_var, width=10)
        payment_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Interest rate
        interest_frame = ttk.Frame(inputs_frame)
        interest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(interest_frame, text="Interest Rate:").grid(row=0, column=0, sticky=tk.W)
        
        self.pv_interest_var = tk.StringVar(value="0.04")
        interest_entry = ttk.Entry(interest_frame, textvariable=self.pv_interest_var, width=8)
        interest_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(interest_frame, text=" (0-1)").grid(row=0, column=2, sticky=tk.W)
        
        # Term
        term_frame = ttk.Frame(inputs_frame)
        term_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(term_frame, text="Term (years):").grid(row=0, column=0, sticky=tk.W)
        
        self.pv_term_var = tk.StringVar(value="20")
        term_entry = ttk.Entry(term_frame, textvariable=self.pv_term_var, width=5)
        term_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Payment frequency
        freq_frame = ttk.Frame(inputs_frame)
        freq_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(freq_frame, text="Payment Frequency:").pack(anchor=tk.W)
        
        self.pv_freq_var = tk.StringVar(value="Annual")
        
        freq_options = ["Annual", "Semi-annual", "Quarterly", "Monthly"]
        for i, freq in enumerate(freq_options):
            freq_radio = ttk.Radiobutton(
                freq_frame, 
                text=freq,
                variable=self.pv_freq_var,
                value=freq
            )
            freq_radio.pack(anchor=tk.W, padx=(10, 0))
        
        # Mortality table
        table_frame = ttk.Frame(inputs_frame)
        table_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(table_frame, text="Mortality Table:").pack(anchor=tk.W)
        
        self.pv_table_var = tk.StringVar(value="soa_2012")
        
        # Get available tables (in a real app, this would be dynamic)
        tables = [
            {"id": "soa_2012", "name": "SOA 2012 IAM"},
            {"id": "cso_2001", "name": "CSO 2001"}
        ]
        
        for table in tables:
            table_radio = ttk.Radiobutton(
                table_frame, 
                text=table["name"],
                variable=self.pv_table_var,
                value=table["id"]
            )
            table_radio.pack(anchor=tk.W, padx=(10, 0))
        
        # Gender
        gender_frame = ttk.Frame(inputs_frame)
        gender_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gender_frame, text="Gender:").pack(anchor=tk.W)
        
        self.pv_gender_var = tk.StringVar(value="male")
        
        for gender in ["male", "female", "unisex"]:
            gender_radio = ttk.Radiobutton(
                gender_frame, 
                text=gender.capitalize(),
                variable=self.pv_gender_var,
                value=gender
            )
            gender_radio.pack(anchor=tk.W, padx=(10, 0))
        
        # Calculate button
        ttk.Separator(inputs_frame).pack(fill=tk.X, pady=10)
        
        calculate_btn = ttk.Button(
            inputs_frame,
            text="Calculate Present Value",
            command=self._calculate_present_value,
            bootstyle="primary"
        )
        calculate_btn.pack(pady=10)
        
        # Status display
        self.pv_status_var = tk.StringVar()
        status_label = ttk.Label(
            inputs_frame, 
            textvariable=self.pv_status_var,
            wraplength=200
        )
        status_label.pack(pady=(0, 10))
        
        # Right panel - results
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Title for results
        results_title = ttk.Label(
            results_frame, 
            text="Present Value Results",
            font=("Helvetica", 12, "bold")
        )
        results_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Results display
        self.results_frame = ttk.Frame(results_frame, bootstyle="default")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Default results
        self.pv_result_var = tk.StringVar(value="No calculation performed yet")
        self.duration_var = tk.StringVar(value="")
        self.monthly_var = tk.StringVar(value="")
        
        # Create card widgets for results
        self._create_result_widgets()
        
    def _create_result_widgets(self):
        """Create the result widgets for present value calculator."""
        # Clear existing widgets
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Present value result
        pv_card = ttk.Frame(self.results_frame, bootstyle="primary")
        pv_card.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            pv_card,
            text="Present Value",
            font=("Helvetica", 11, "bold"),
            bootstyle="primary-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        pv_result_label = ttk.Label(
            pv_card,
            textvariable=self.pv_result_var,
            font=("Helvetica", 16),
            padding=(10, 15)
        )
        pv_result_label.pack(fill=tk.X)
        
        # Expected duration
        duration_card = ttk.Frame(self.results_frame, bootstyle="info")
        duration_card.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            duration_card,
            text="Expected Payment Duration (years)",
            font=("Helvetica", 11, "bold"),
            bootstyle="info-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        duration_result_label = ttk.Label(
            duration_card,
            textvariable=self.duration_var,
            font=("Helvetica", 14),
            padding=(10, 10)
        )
        duration_result_label.pack(fill=tk.X)
        
        # Monthly equivalent
        monthly_card = ttk.Frame(self.results_frame, bootstyle="success")
        monthly_card.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            monthly_card,
            text="Monthly Equivalent Payment",
            font=("Helvetica", 11, "bold"),
            bootstyle="success-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        monthly_result_label = ttk.Label(
            monthly_card,
            textvariable=self.monthly_var,
            font=("Helvetica", 14),
            padding=(10, 10)
        )
        monthly_result_label.pack(fill=tk.X)
        
    def _calculate_present_value(self):
        """Calculate and display present value results."""
        try:
            # Get input values
            age = int(self.pv_age_var.get())
            payment = float(self.pv_payment_var.get())
            interest_rate = float(self.pv_interest_var.get())
            term = int(self.pv_term_var.get())
            frequency = self.pv_freq_var.get()
            table_type = self.pv_table_var.get()
            gender = self.pv_gender_var.get()
            
            # Validate inputs
            if age < 0 or age > 120:
                self.pv_status_var.set("Invalid age. Must be between 0 and 120.")
                return
                
            if payment <= 0:
                self.pv_status_var.set("Payment must be positive.")
                return
                
            if interest_rate < 0 or interest_rate > 1:
                self.pv_status_var.set("Invalid interest rate. Must be between 0 and 1.")
                return
                
            if term <= 0:
                self.pv_status_var.set("Term must be positive.")
                return
                
            # Show loading indicator
            self.show_loader("Calculating present value...")
            
            # Calculate present value
            result = self.actuarial_service.calculate_present_value(
                age, payment, interest_rate, term, frequency, table_type, gender
            )
            
            # Hide loader
            self.hide_loader()
            
            # Update result displays
            self.pv_result_var.set(f"${result['present_value']:,.2f}")
            self.duration_var.set(f"{result['expected_duration']:.2f} years")
            self.monthly_var.set(f"${result['monthly_equivalent']:,.2f} per month")
            
            # Update status
            self.pv_status_var.set("Present value calculated successfully.")
            
        except Exception as e:
            # Hide loader
            self.hide_loader()
            
            # Show error
            self.pv_status_var.set(f"Error: {str(e)}")
            logger.error(f"Error calculating present value: {e}", exc_info=True)
            
    def refresh(self):
        """Refresh the page content."""
        # Could refresh data if needed
        logger.debug("Refreshed actuarial page")