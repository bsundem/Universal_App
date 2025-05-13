"""
Finance page module for the Universal App.

This module provides the finance page with visualizations
for yield curves and option pricing models.
"""
import logging
from typing import Dict, Callable, Optional, Any, List, Tuple
from datetime import datetime, timedelta
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
import matplotlib.dates as mdates

# Import UI components
from ui.components.page_container import PageContainer

# Import services
from services.container import get_finance_service, get_r_service

logger = logging.getLogger(__name__)


class FinancePage(PageContainer):
    """
    Finance page with visualizations and calculators.
    
    This page provides financial tools including yield curve
    visualization and option pricing calculators.
    """
    
    def __init__(self, parent: ttk.Frame, navigation_callback: Optional[Callable] = None):
        """
        Initialize the finance page.
        
        Args:
            parent: Parent frame
            navigation_callback: Function to navigate to other pages
        """
        super().__init__(
            parent,
            page_id="finance",
            title="Finance Tools",
            navigation_callback=navigation_callback
        )
        
        # Initialize service
        self.finance_service = get_finance_service()
        
        # Check if R is available
        self.r_service = get_r_service()
        self.r_available = self.r_service.is_available()
        
        # Set up tab control for different tools
        self._create_tab_control()
        
        # Set up the page content
        self.setup_content()
        
        # Show warning banner if R is not available
        if not self.r_available:
            self.show_message(
                "R integration is not available. To enable: 1) pip install rpy2, 2) Install R from cran.r-project.org",
                kind="warning",
                duration=None
            )
        
        logger.debug("Finance page initialized")
        
    def _create_tab_control(self):
        """Create a tab control for different financial tools."""
        self.tab_control = ttk.Notebook(self.content_frame)
        self.tab_control.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Yield curve tab
        self.yield_curve_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.yield_curve_tab, text="Yield Curves")
        
        # Options pricing tab
        self.options_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.options_tab, text="Options Pricing")
        
        # Configure tab layouts
        for tab in [self.yield_curve_tab, self.options_tab]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
        
        # Connect tab selection to function
        self.tab_control.bind("<<NotebookTabChanged>>", self._on_tab_changed)
            
    def _on_tab_changed(self, event):
        """Handle tab change event."""
        # Get the current tab
        current_tab = self.tab_control.select()
        tab_name = self.tab_control.tab(current_tab, "text")
        logger.debug(f"Selected tab: {tab_name}")
        
    def setup_content(self):
        """Set up the page content."""
        # Set up yield curve visualization
        self._setup_yield_curve_visualization()
        
        # Set up options pricing calculator
        self._setup_options_pricing_calculator()
        
    def _setup_yield_curve_visualization(self):
        """Set up the yield curve visualization tab."""
        # Main frame with left panel for controls and right panel for visualization
        main_frame = ttk.Frame(self.yield_curve_tab)
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
        
        # Date range
        date_frame = ttk.Frame(controls_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="Date Range:").pack(anchor=tk.W)
        
        # Start date
        start_date_frame = ttk.Frame(date_frame)
        start_date_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(start_date_frame, text="From:").grid(row=0, column=0, sticky=tk.W)
        
        # Default to 1 year ago
        one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        self.start_date_var = tk.StringVar(value=one_year_ago)
        ttk.Entry(start_date_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, padx=(5, 0))
        ttk.Label(start_date_frame, text="(YYYY-MM-DD)").grid(row=0, column=2, padx=(5, 0))
        
        # End date
        end_date_frame = ttk.Frame(date_frame)
        end_date_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(end_date_frame, text="To:").grid(row=0, column=0, sticky=tk.W)
        
        # Default to today
        today = datetime.now().strftime("%Y-%m-%d")
        self.end_date_var = tk.StringVar(value=today)
        ttk.Entry(end_date_frame, textvariable=self.end_date_var, width=12).grid(row=0, column=1, padx=(5, 0))
        ttk.Label(end_date_frame, text="(YYYY-MM-DD)").grid(row=0, column=2, padx=(5, 0))
        
        # Curve type
        curve_frame = ttk.Frame(controls_frame)
        curve_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(curve_frame, text="Curve Type:").pack(anchor=tk.W)
        
        self.curve_type_var = tk.StringVar(value="nominal")
        
        for curve_type in [("nominal", "Nominal"), ("real", "Real/Inflation-Adjusted")]:
            curve_radio = ttk.Radiobutton(
                curve_frame, 
                text=curve_type[1],
                variable=self.curve_type_var,
                value=curve_type[0]
            )
            curve_radio.pack(anchor=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Display options
        display_frame = ttk.Frame(controls_frame)
        display_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(display_frame, text="Display Options:").pack(anchor=tk.W)
        
        # Display all maturities or select specific ones
        self.show_all_maturities_var = tk.BooleanVar(value=True)
        show_all = ttk.Checkbutton(
            display_frame,
            text="Show all maturities",
            variable=self.show_all_maturities_var,
            command=self._toggle_maturity_selection
        )
        show_all.pack(anchor=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Maturity selection (disabled by default)
        self.maturity_frame = ttk.Frame(display_frame)
        self.maturity_frame.pack(fill=tk.X, padx=(10, 0), pady=(5, 0))
        
        # Common maturities (in months)
        self.maturities = [1, 2, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360]
        self.maturity_vars = {}
        
        # Create checkbuttons for each maturity
        for i, maturity in enumerate(self.maturities):
            # Format label based on months
            if maturity < 12:
                label = f"{maturity}m"
            else:
                years = maturity // 12
                label = f"{years}y"
                
            # Create variable and checkbutton
            self.maturity_vars[maturity] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                self.maturity_frame,
                text=label,
                variable=self.maturity_vars[maturity]
            )
            
            # Grid layout with 4 columns
            row, col = divmod(i, 4)
            cb.grid(row=row, column=col, sticky=tk.W, padx=(0, 10), pady=(0, 5))
            
        # Disable maturity selection initially
        self._toggle_maturity_selection()
        
        # Plot type
        plot_frame = ttk.Frame(controls_frame)
        plot_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(plot_frame, text="Plot Type:").pack(anchor=tk.W)
        
        self.plot_type_var = tk.StringVar(value="3d")
        
        for plot_type in [("3d", "3D Surface"), ("lines", "Line Series")]:
            plot_radio = ttk.Radiobutton(
                plot_frame, 
                text=plot_type[1],
                variable=self.plot_type_var,
                value=plot_type[0]
            )
            plot_radio.pack(anchor=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Calculate button
        ttk.Separator(controls_frame).pack(fill=tk.X, pady=10)
        
        calculate_btn = ttk.Button(
            controls_frame,
            text="Generate Yield Curve",
            command=self._calculate_yield_curve,
            bootstyle="primary"
        )
        calculate_btn.pack(pady=10)
        
        # Status display
        self.yield_status_var = tk.StringVar()
        status_label = ttk.Label(
            controls_frame, 
            textvariable=self.yield_status_var,
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
            text="Yield Curve Visualization",
            font=("Helvetica", 12, "bold")
        )
        viz_title.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Figure for visualization
        self.yield_fig = Figure(figsize=(6, 4), dpi=100)
        
        # Default message plot
        self.yield_ax = self.yield_fig.add_subplot(111)
        self.yield_ax.set_title("No data yet. Click Generate to visualize yield curves.")
        self.yield_ax.set_xlabel("Date")
        self.yield_ax.set_ylabel("Maturity")
        
        self.yield_canvas = FigureCanvasTkAgg(self.yield_fig, master=viz_frame)
        self.yield_canvas_widget = self.yield_canvas.get_tk_widget()
        self.yield_canvas_widget.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
    def _toggle_maturity_selection(self):
        """Toggle the maturity selection frame based on checkbox."""
        show_all = self.show_all_maturities_var.get()
        
        # Configure all widgets in the maturity frame
        for widget in self.maturity_frame.winfo_children():
            if show_all:
                widget.configure(state="disabled")
            else:
                widget.configure(state="normal")
                
    def _calculate_yield_curve(self):
        """Calculate and display yield curve data."""
        try:
            # Check if R is available
            if not self.r_available:
                self.yield_status_var.set("R integration is not available. Run 'pip install rpy2' and install R to use this feature.")
                return
                
            # Get input values
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            curve_type = self.curve_type_var.get()
            plot_type = self.plot_type_var.get()
            
            # Validate dates
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                self.yield_status_var.set("Invalid date format. Use YYYY-MM-DD.")
                return
                
            # Show loading indicator
            self.show_loader("Calculating yield curves...")
            
            # Calculate yield curve data
            df = self.finance_service.calculate_yield_curve(
                start_date, end_date, curve_type
            )
            
            # Filter maturities if needed
            if not self.show_all_maturities_var.get():
                selected_maturities = [
                    m for m in self.maturities 
                    if self.maturity_vars[m].get()
                ]
                
                if not selected_maturities:
                    self.yield_status_var.set("Please select at least one maturity.")
                    self.hide_loader()
                    return
                    
                df = df[df["Maturity"].isin(selected_maturities)]
            
            # Update the visualization
            if plot_type == "3d":
                self._update_yield_curve_3d(df)
            else:
                self._update_yield_curve_lines(df)
            
            # Hide loader
            self.hide_loader()
            
            # Update status
            self.yield_status_var.set(f"Generated yield curve data from {start_date} to {end_date}.")
            
        except Exception as e:
            # Hide loader
            self.hide_loader()
            
            # Show error
            self.yield_status_var.set(f"Error: {str(e)}")
            logger.error(f"Error calculating yield curve: {e}", exc_info=True)
            
    def _update_yield_curve_3d(self, df: pd.DataFrame):
        """
        Update the yield curve visualization with 3D surface plot.
        
        Args:
            df: DataFrame with yield curve data
        """
        # Clear the figure
        self.yield_fig.clear()
        
        # Convert to pivot table for 3D plotting
        pivot_df = df.pivot_table(index="Date", columns="Maturity", values="Yield")
        
        # Create 3D axes
        ax = self.yield_fig.add_subplot(111, projection="3d")
        
        # Get X (dates) and Y (maturities) from the pivot table
        dates = pd.to_datetime(pivot_df.index)
        maturities = pivot_df.columns
        
        # Convert to numeric for plotting
        date_nums = mdates.date2num(dates)
        
        # Create meshgrid
        X, Y = np.meshgrid(date_nums, maturities)
        Z = pivot_df.T.values
        
        # Create the 3D surface plot
        surf = ax.plot_surface(
            X, Y, Z, 
            cmap="viridis",
            linewidth=0, 
            antialiased=True,
            alpha=0.8
        )
        
        # Add a color bar
        self.yield_fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        # Set labels and title
        ax.set_xlabel("Date")
        ax.set_ylabel("Maturity (months)")
        ax.set_zlabel("Yield")
        
        # Format the date ticks
        date_formatter = mdates.DateFormatter("%Y-%m-%d")
        date_locator = mdates.AutoDateLocator()
        
        # Get the x-axis
        xaxis = ax.xaxis
        
        # Set the locator and formatter
        xaxis.set_major_locator(date_locator)
        xaxis.set_major_formatter(date_formatter)
        
        # Rotate labels for better visibility
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        
        # Add title
        curve_type = "Nominal" if self.curve_type_var.get() == "nominal" else "Real"
        ax.set_title(f"{curve_type} Yield Curve Surface")
        
        # Adjust the view angle for better visualization
        ax.view_init(elev=20, azim=-35)
        
        # Make the plot more readable
        self.yield_fig.tight_layout()
        
        # Redraw the canvas
        self.yield_canvas.draw()
        
    def _update_yield_curve_lines(self, df: pd.DataFrame):
        """
        Update the yield curve visualization with line plots.
        
        Args:
            df: DataFrame with yield curve data
        """
        # Clear the figure
        self.yield_fig.clear()
        
        # Create a pivot table for easier plotting
        pivot_df = df.pivot_table(index="Date", columns="Maturity", values="Yield")
        
        # Convert index to datetime
        pivot_df.index = pd.to_datetime(pivot_df.index)
        
        # Create subplot
        ax = self.yield_fig.add_subplot(111)
        
        # Get a color map for the lines
        cmap = plt.cm.viridis
        
        # Plot each maturity as a line
        for i, maturity in enumerate(pivot_df.columns):
            # Format label based on months
            if maturity < 12:
                label = f"{maturity} month"
            else:
                years = maturity // 12
                label = f"{years} year"
                
            # Plot the line
            color = cmap(i / len(pivot_df.columns))
            ax.plot(
                pivot_df.index, 
                pivot_df[maturity], 
                marker="o", 
                markersize=4, 
                label=label,
                color=color
            )
        
        # Add labels and title
        ax.set_xlabel("Date")
        ax.set_ylabel("Yield")
        
        # Format x-axis with dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Rotate labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        
        # Add grid
        ax.grid(True, linestyle="--", alpha=0.7)
        
        # Add legend
        ax.legend(
            title="Maturity", 
            loc="best", 
            fontsize="small",
            ncol=2
        )
        
        # Add title
        curve_type = "Nominal" if self.curve_type_var.get() == "nominal" else "Real"
        ax.set_title(f"{curve_type} Yield Curves by Maturity")
        
        # Make the plot more readable
        self.yield_fig.tight_layout()
        
        # Redraw the canvas
        self.yield_canvas.draw()
        
    def _setup_options_pricing_calculator(self):
        """Set up the options pricing calculator tab."""
        # Main frame with left panel for inputs and right panel for results
        main_frame = ttk.Frame(self.options_tab)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - inputs
        inputs_frame = ttk.Frame(main_frame)
        inputs_frame.grid(row=0, column=0, sticky="ns", padx=(5, 10), pady=5)
        
        # Title for inputs
        ttk.Label(
            inputs_frame, 
            text="Option Parameters",
            font=("Helvetica", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Option type
        type_frame = ttk.Frame(inputs_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Option Type:").pack(anchor=tk.W)
        
        self.option_type_var = tk.StringVar(value="call")
        
        for option_type in [("call", "Call"), ("put", "Put")]:
            option_radio = ttk.Radiobutton(
                type_frame, 
                text=option_type[1],
                variable=self.option_type_var,
                value=option_type[0]
            )
            option_radio.pack(anchor=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Stock price
        stock_frame = ttk.Frame(inputs_frame)
        stock_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(stock_frame, text="Stock Price:").grid(row=0, column=0, sticky=tk.W)
        
        self.spot_price_var = tk.StringVar(value="100")
        spot_entry = ttk.Entry(stock_frame, textvariable=self.spot_price_var, width=10)
        spot_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Strike price
        strike_frame = ttk.Frame(inputs_frame)
        strike_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strike_frame, text="Strike Price:").grid(row=0, column=0, sticky=tk.W)
        
        self.strike_price_var = tk.StringVar(value="100")
        strike_entry = ttk.Entry(strike_frame, textvariable=self.strike_price_var, width=10)
        strike_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Time to expiry
        time_frame = ttk.Frame(inputs_frame)
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text="Time to Expiry (years):").grid(row=0, column=0, sticky=tk.W)
        
        self.time_to_expiry_var = tk.StringVar(value="1")
        time_entry = ttk.Entry(time_frame, textvariable=self.time_to_expiry_var, width=6)
        time_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Risk-free rate
        rate_frame = ttk.Frame(inputs_frame)
        rate_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rate_frame, text="Risk-Free Rate:").grid(row=0, column=0, sticky=tk.W)
        
        self.risk_free_rate_var = tk.StringVar(value="0.03")
        rate_entry = ttk.Entry(rate_frame, textvariable=self.risk_free_rate_var, width=6)
        rate_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(rate_frame, text=" (0-1)").grid(row=0, column=2, sticky=tk.W)
        
        # Volatility
        vol_frame = ttk.Frame(inputs_frame)
        vol_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(vol_frame, text="Volatility:").grid(row=0, column=0, sticky=tk.W)
        
        self.volatility_var = tk.StringVar(value="0.2")
        vol_entry = ttk.Entry(vol_frame, textvariable=self.volatility_var, width=6)
        vol_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(vol_frame, text=" (0-1)").grid(row=0, column=2, sticky=tk.W)
        
        # Dividend yield
        div_frame = ttk.Frame(inputs_frame)
        div_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(div_frame, text="Dividend Yield:").grid(row=0, column=0, sticky=tk.W)
        
        self.dividend_yield_var = tk.StringVar(value="0")
        div_entry = ttk.Entry(div_frame, textvariable=self.dividend_yield_var, width=6)
        div_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(div_frame, text=" (0-1)").grid(row=0, column=2, sticky=tk.W)
        
        # Calculate button
        ttk.Separator(inputs_frame).pack(fill=tk.X, pady=10)
        
        calculate_btn = ttk.Button(
            inputs_frame,
            text="Calculate Option Price",
            command=self._calculate_option_price,
            bootstyle="primary"
        )
        calculate_btn.pack(pady=10)
        
        # Status display
        self.option_status_var = tk.StringVar()
        status_label = ttk.Label(
            inputs_frame, 
            textvariable=self.option_status_var,
            wraplength=200
        )
        status_label.pack(pady=(0, 10))
        
        # Right panel - results
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        
        # Title for results
        results_title = ttk.Label(
            results_frame, 
            text="Option Pricing Results",
            font=("Helvetica", 12, "bold")
        )
        results_title.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Create cards for results
        self.results_cards_frame = ttk.Frame(results_frame)
        self.results_cards_frame.grid(row=1, column=0, sticky="nsew")
        self.results_cards_frame.grid_columnconfigure(0, weight=1)
        
        # Visualization frame
        self.option_viz_frame = ttk.Frame(results_frame)
        self.option_viz_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.option_viz_frame.grid_columnconfigure(0, weight=1)
        self.option_viz_frame.grid_rowconfigure(0, weight=1)
        
        # Default visualization
        self.option_fig = Figure(figsize=(6, 4), dpi=100)
        self.option_ax = self.option_fig.add_subplot(111)
        self.option_ax.set_title("Option Value vs. Stock Price")
        self.option_ax.set_xlabel("Stock Price")
        self.option_ax.set_ylabel("Option Value")
        
        self.option_canvas = FigureCanvasTkAgg(self.option_fig, master=self.option_viz_frame)
        self.option_canvas_widget = self.option_canvas.get_tk_widget()
        self.option_canvas_widget.grid(row=0, column=0, sticky="nsew")
        
        # Result variables
        self.option_price_var = tk.StringVar(value="$0.00")
        self.delta_var = tk.StringVar(value="0.000")
        self.gamma_var = tk.StringVar(value="0.000")
        self.theta_var = tk.StringVar(value="0.000")
        self.vega_var = tk.StringVar(value="0.000")
        
        # Create default result cards
        self._create_option_result_cards()
        
    def _create_option_result_cards(self):
        """Create result cards for option pricing."""
        # Clear existing cards
        for widget in self.results_cards_frame.winfo_children():
            widget.destroy()
        
        # Option price card
        price_card = ttk.Frame(self.results_cards_frame, bootstyle="primary")
        price_card.grid(row=0, column=0, sticky="ew", pady=5)
        
        ttk.Label(
            price_card,
            text="Option Price",
            font=("Helvetica", 11, "bold"),
            bootstyle="primary-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        ttk.Label(
            price_card,
            textvariable=self.option_price_var,
            font=("Helvetica", 16),
            padding=(10, 10)
        ).pack()
        
        # Create a grid for the Greeks
        greeks_frame = ttk.Frame(self.results_cards_frame)
        greeks_frame.grid(row=1, column=0, sticky="ew", pady=5)
        greeks_frame.grid_columnconfigure(0, weight=1)
        greeks_frame.grid_columnconfigure(1, weight=1)
        
        # Delta card
        delta_card = ttk.Frame(greeks_frame, bootstyle="info")
        delta_card.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ttk.Label(
            delta_card,
            text="Delta",
            font=("Helvetica", 11, "bold"),
            bootstyle="info-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        ttk.Label(
            delta_card,
            textvariable=self.delta_var,
            font=("Helvetica", 14),
            padding=(10, 10)
        ).pack()
        
        # Gamma card
        gamma_card = ttk.Frame(greeks_frame, bootstyle="info")
        gamma_card.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        ttk.Label(
            gamma_card,
            text="Gamma",
            font=("Helvetica", 11, "bold"),
            bootstyle="info-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        ttk.Label(
            gamma_card,
            textvariable=self.gamma_var,
            font=("Helvetica", 14),
            padding=(10, 10)
        ).pack()
        
        # Theta card
        theta_card = ttk.Frame(greeks_frame, bootstyle="info")
        theta_card.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(5, 0))
        
        ttk.Label(
            theta_card,
            text="Theta (daily)",
            font=("Helvetica", 11, "bold"),
            bootstyle="info-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        ttk.Label(
            theta_card,
            textvariable=self.theta_var,
            font=("Helvetica", 14),
            padding=(10, 10)
        ).pack()
        
        # Vega card
        vega_card = ttk.Frame(greeks_frame, bootstyle="info")
        vega_card.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
        
        ttk.Label(
            vega_card,
            text="Vega",
            font=("Helvetica", 11, "bold"),
            bootstyle="info-inverse",
            padding=(10, 5)
        ).pack(fill=tk.X)
        
        ttk.Label(
            vega_card,
            textvariable=self.vega_var,
            font=("Helvetica", 14),
            padding=(10, 10)
        ).pack()
        
    def _calculate_option_price(self):
        """Calculate and display option pricing results."""
        try:
            # Check if R is available
            if not self.r_available:
                self.option_status_var.set("R integration is not available. Run 'pip install rpy2' and install R to use this feature.")
                return
                
            # Get input values
            option_type = self.option_type_var.get()
            spot_price = float(self.spot_price_var.get())
            strike_price = float(self.strike_price_var.get())
            time_to_expiry = float(self.time_to_expiry_var.get())
            risk_free_rate = float(self.risk_free_rate_var.get())
            volatility = float(self.volatility_var.get())
            dividend_yield = float(self.dividend_yield_var.get())
            
            # Validate inputs
            if spot_price <= 0 or strike_price <= 0:
                self.option_status_var.set("Prices must be positive.")
                return
                
            if time_to_expiry <= 0:
                self.option_status_var.set("Time to expiry must be positive.")
                return
                
            if volatility <= 0:
                self.option_status_var.set("Volatility must be positive.")
                return
                
            # Show loading indicator
            self.show_loader("Calculating option price...")
            
            # Calculate option price
            result = self.finance_service.price_option(
                option_type, spot_price, strike_price, time_to_expiry,
                risk_free_rate, volatility, dividend_yield
            )
            
            # Update result displays
            self.option_price_var.set(f"${result['price']:.2f}")
            self.delta_var.set(f"{result['delta']:.4f}")
            self.gamma_var.set(f"{result['gamma']:.4f}")
            self.theta_var.set(f"${result['theta']:.4f}")
            self.vega_var.set(f"{result['vega']:.4f}")
            
            # Update visualization
            self._update_option_visualization(
                option_type, spot_price, strike_price, time_to_expiry,
                risk_free_rate, volatility, dividend_yield
            )
            
            # Hide loader
            self.hide_loader()
            
            # Update status
            self.option_status_var.set("Option pricing completed successfully.")
            
        except Exception as e:
            # Hide loader
            self.hide_loader()
            
            # Show error
            self.option_status_var.set(f"Error: {str(e)}")
            logger.error(f"Error calculating option price: {e}", exc_info=True)
            
    def _update_option_visualization(
        self, 
        option_type: str, 
        spot_price: float, 
        strike_price: float, 
        time_to_expiry: float,
        risk_free_rate: float, 
        volatility: float, 
        dividend_yield: float
    ):
        """
        Update option pricing visualization.
        
        This creates a plot showing option value vs. stock price for
        different stock prices around the current spot price.
        """
        # Check if R is available
        if not self.r_available:
            self.option_status_var.set("R integration is not available. Cannot create visualization.")
            return
            
        # Clear the figure
        self.option_fig.clear()
        
        # Create subplot
        ax = self.option_fig.add_subplot(111)
        
        # Generate a range of stock prices
        price_range = 0.5  # +/- 50% of spot price
        min_price = spot_price * (1 - price_range)
        max_price = spot_price * (1 + price_range)
        prices = np.linspace(min_price, max_price, 100)
        
        # Calculate option values for each price
        values = []
        for p in prices:
            try:
                result = self.finance_service.price_option(
                    option_type, p, strike_price, time_to_expiry,
                    risk_free_rate, volatility, dividend_yield
                )
                values.append(result["price"])
            except Exception as e:
                logger.error(f"Error calculating option price: {e}")
                self.option_status_var.set(f"Error during visualization: {str(e)}")
                return
            
        # Convert to array
        values = np.array(values)
        
        # Plot option value vs. price
        ax.plot(prices, values, "b-", linewidth=2)
        
        # Mark the current spot price
        current_value_idx = np.abs(prices - spot_price).argmin()
        current_value = values[current_value_idx]
        
        ax.plot(
            spot_price, 
            current_value, 
            "ro", 
            markersize=8,
            label=f"Current ({spot_price:.2f}, {current_value:.2f})"
        )
        
        # Mark the strike price
        strike_value_idx = np.abs(prices - strike_price).argmin()
        strike_value = values[strike_value_idx]
        
        ax.plot(
            strike_price, 
            strike_value, 
            "go", 
            markersize=8,
            label=f"Strike ({strike_price:.2f}, {strike_value:.2f})"
        )
        
        # Add labels
        ax.set_xlabel("Stock Price")
        ax.set_ylabel("Option Value")
        
        # Add grid
        ax.grid(True, linestyle="--", alpha=0.7)
        
        # Add title
        option_name = "Call" if option_type == "call" else "Put"
        ax.set_title(f"{option_name} Option Price vs. Stock Price")
        
        # Add legend
        ax.legend()
        
        # Adjust layout
        self.option_fig.tight_layout()
        
        # Redraw canvas
        self.option_canvas.draw()
        
    def refresh(self):
        """Refresh the page content."""
        # Could refresh data if needed
        logger.debug("Refreshed finance page")
        
    def show(self, **kwargs):
        """
        Show this page with optional parameters.
        
        Args:
            **kwargs: Optional parameters, including:
                - tab: Name of tab to select ("yield_curves" or "options")
        """
        super().show(**kwargs)
        
        # Select tab if specified
        if "tab" in kwargs:
            tab = kwargs["tab"]
            if tab == "options":
                self.tab_control.select(1)  # Options tab index
            else:
                self.tab_control.select(0)  # Yield curves tab index