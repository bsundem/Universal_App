"""
Actuarial calculations page with R integration.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile
import importlib.util

# Check for numpy
if importlib.util.find_spec("numpy") is not None:
    import numpy as np
else:
    np = None

# Check for pandas
try:
    import pandas as pd
except ImportError:
    pd = None

# Check for matplotlib
if importlib.util.find_spec("matplotlib") is not None:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
else:
    matplotlib = None
    plt = None
    FigureCanvasTkAgg = None

# Import the base page class
from ui.pages.base_page import BasePage

# Import actuarial service and R service
from services.actuarial.actuarial_service import actuarial_service
from services.r_service import r_service


class ActuarialPage(BasePage):
    """Page for actuarial calculations using R integration."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, title="Actuarial Calculations")
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components for the actuarial page."""
        # Main container frame with padding
        main_frame = ttk.Frame(self.content_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(main_frame, text="Actuarial Calculations with R", 
                           font=("Helvetica", 16))
        header.pack(pady=(0, 10))
        
        # Check if R is available
        if not r_service.is_available():
            error_frame = ttk.Frame(main_frame, padding="20")
            error_frame.pack(fill=tk.BOTH, expand=True)
            error_msg = ttk.Label(
                error_frame, 
                text="R integration is not available.\nPlease install R and rpy2 package.",
                font=("Helvetica", 12),
                foreground="red"
            )
            error_msg.pack(pady=20)
            
            install_guide = ttk.Label(
                error_frame,
                text="Installation Guide:\n1. Install R from https://cran.r-project.org/\n"
                     "2. Install required R packages: install.packages(c('lifecycle'))\n"
                     "3. Install Python packages: pip install rpy2",
                justify=tk.LEFT
            )
            install_guide.pack(pady=10)
            return
        
        # Create tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Mortality Table
        tab_mortality = ttk.Frame(notebook, padding=10)
        notebook.add(tab_mortality, text="Mortality Tables")
        self.setup_mortality_tab(tab_mortality)
        
        # Tab 2: Present Value Calculations
        tab_pv = ttk.Frame(notebook, padding=10)
        notebook.add(tab_pv, text="Present Value")
        self.setup_pv_tab(tab_pv)
        
    def setup_mortality_tab(self, parent):
        """Set up the mortality tables tab."""
        # Control panel (left side)
        control_frame = ttk.Frame(parent, padding="5")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Parameters section
        params_lf = ttk.LabelFrame(control_frame, text="Parameters", padding="10")
        params_lf.pack(fill=tk.X, pady=5)
        
        # Age range
        ttk.Label(params_lf, text="Age Range:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        age_frame = ttk.Frame(params_lf)
        age_frame.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(age_frame, text="From:").pack(side=tk.LEFT)
        self.age_from = ttk.Spinbox(age_frame, from_=0, to=100, width=5)
        self.age_from.set(30)
        self.age_from.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(age_frame, text="To:").pack(side=tk.LEFT)
        self.age_to = ttk.Spinbox(age_frame, from_=0, to=100, width=5)
        self.age_to.set(90)
        self.age_to.pack(side=tk.LEFT, padx=5)
        
        # Mortality table selection
        ttk.Label(params_lf, text="Mortality Table:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.mortality_table = ttk.Combobox(params_lf, values=[
            "Standard Mortality", 
            "Annuitant Mortality", 
            "Custom"
        ], width=20)
        self.mortality_table.current(0)
        self.mortality_table.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Gender selection
        ttk.Label(params_lf, text="Gender:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.gender = ttk.Combobox(params_lf, values=["Male", "Female", "Unisex"], width=20)
        self.gender.current(0)
        self.gender.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Interest rate
        ttk.Label(params_lf, text="Interest Rate (%):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.interest_rate = ttk.Spinbox(params_lf, from_=0.0, to=20.0, increment=0.25, width=5)
        self.interest_rate.set(3.5)
        self.interest_rate.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Buttons
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.calculate_btn = ttk.Button(
            buttons_frame, 
            text="Calculate", 
            command=self.calculate_mortality
        )
        self.calculate_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(
            buttons_frame, 
            text="Export Data", 
            command=self.export_mortality_data
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Results panel (right side)
        results_frame = ttk.Frame(parent)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create a frame for the plot
        self.plot_frame = ttk.Frame(results_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initial empty plot
        self.create_empty_plot()
        
    def setup_pv_tab(self, parent):
        """Set up the present value calculations tab."""
        # Left side - controls
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Parameters
        params_lf = ttk.LabelFrame(left_frame, text="Annuity Parameters", padding="10")
        params_lf.pack(fill=tk.X, pady=5)
        
        # Age
        ttk.Label(params_lf, text="Age:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pv_age = ttk.Spinbox(params_lf, from_=0, to=100, width=5)
        self.pv_age.set(65)
        self.pv_age.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Payment amount
        ttk.Label(params_lf, text="Annual Payment:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.payment = ttk.Entry(params_lf, width=10)
        self.payment.insert(0, "10000")
        self.payment.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Payment frequency
        ttk.Label(params_lf, text="Payment Frequency:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.frequency = ttk.Combobox(params_lf, values=["Annual", "Semi-annual", "Quarterly", "Monthly"], width=12)
        self.frequency.current(0)
        self.frequency.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Term
        ttk.Label(params_lf, text="Term (years):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.term = ttk.Spinbox(params_lf, from_=1, to=50, width=5)
        self.term.set(20)
        self.term.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Interest rate
        ttk.Label(params_lf, text="Interest Rate (%):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.pv_interest_rate = ttk.Spinbox(params_lf, from_=0.0, to=20.0, increment=0.25, width=5)
        self.pv_interest_rate.set(3.5)
        self.pv_interest_rate.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Mortality assumptions
        ttk.Label(params_lf, text="Mortality Table:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.pv_mortality_table = ttk.Combobox(params_lf, values=[
            "Standard Mortality", 
            "Annuitant Mortality", 
            "None (Fixed Term)"
        ], width=20)
        self.pv_mortality_table.current(0)
        self.pv_mortality_table.grid(row=5, column=1, sticky=tk.W, pady=2)
        
        # Gender
        ttk.Label(params_lf, text="Gender:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.pv_gender = ttk.Combobox(params_lf, values=["Male", "Female", "Unisex"], width=12)
        self.pv_gender.current(0)
        self.pv_gender.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # Calculate button
        self.pv_calculate_btn = ttk.Button(
            left_frame, 
            text="Calculate Present Value", 
            command=self.calculate_present_value
        )
        self.pv_calculate_btn.pack(pady=10)
        
        # Right side - results
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Results frame
        results_lf = ttk.LabelFrame(right_frame, text="Results", padding="10")
        results_lf.pack(fill=tk.BOTH, expand=True)
        
        # Present Value result
        ttk.Label(results_lf, text="Present Value:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.pv_result = ttk.Label(results_lf, text="$0.00", font=("Helvetica", 16))
        self.pv_result.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # Expected payment duration
        ttk.Label(results_lf, text="Expected Duration:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.duration_result = ttk.Label(results_lf, text="0.00 years", font=("Helvetica", 12))
        self.duration_result.grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # Monthly equivalent
        ttk.Label(results_lf, text="Monthly Equivalent:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.monthly_result = ttk.Label(results_lf, text="$0.00 / month", font=("Helvetica", 12))
        self.monthly_result.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Additional info section
        info_frame = ttk.Frame(results_lf)
        info_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=20)
        
        self.info_text = tk.Text(info_frame, height=8, width=40, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
    def create_empty_plot(self):
        """Create an empty plot in the plot frame."""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if matplotlib is None or plt is None or FigureCanvasTkAgg is None:
            # Create a message indicating matplotlib is not available
            message = ttk.Label(
                self.plot_frame,
                text="Matplotlib is not available. Please install with: pip install matplotlib",
                foreground="red"
            )
            message.pack(expand=True)
            return

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "Click 'Calculate' to generate mortality data",
                ha='center', va='center', fontsize=12)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_axis_off()

        canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def calculate_mortality(self):
        """Calculate mortality data using R and display results."""
        if not r_service.is_available():
            messagebox.showerror("Error", "R integration is not available.")
            return
            
        try:
            # Get input values
            age_from = int(self.age_from.get())
            age_to = int(self.age_to.get())
            interest_rate = float(self.interest_rate.get()) / 100
            table_type = self.mortality_table.get()
            gender = self.gender.get().lower()
            
            # Use the actuarial service to calculate mortality data
            mortality_df = actuarial_service.calculate_mortality_data(
                age_from, 
                age_to, 
                interest_rate, 
                table_type, 
                gender
            )
            
            if mortality_df is not None:
                # Create plot
                self.plot_mortality_data(mortality_df)
            else:
                messagebox.showerror("Error", "Failed to calculate mortality data.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate mortality data: {str(e)}")
            
    def plot_mortality_data(self, df):
        """Plot mortality data."""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if matplotlib is None or plt is None or FigureCanvasTkAgg is None:
            # Create a message indicating matplotlib is not available
            message = ttk.Label(
                self.plot_frame,
                text="Matplotlib is not available. Please install with: pip install matplotlib",
                foreground="red"
            )
            message.pack(expand=True)

            # Display data as text instead
            text_frame = ttk.Frame(self.plot_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            data_text = tk.Text(text_frame, height=20, width=50)
            data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=data_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            data_text.config(yscrollcommand=scrollbar.set)

            # Insert dataframe as text
            data_text.insert(tk.END, "Mortality Data:\n\n")
            data_text.insert(tk.END, df.to_string())
            data_text.config(state=tk.DISABLED)
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), gridspec_kw={'height_ratios': [1, 1]})

        # Plot mortality rates
        ax1.plot(df['Age'], df['qx'], 'b-', label='Mortality Rate (qx)')
        ax1.set_title('Mortality Rates by Age')
        ax1.set_xlabel('Age')
        ax1.set_ylabel('Rate')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Plot life expectancy
        ax2.plot(df['Age'], df['ex'], 'r-', label='Life Expectancy (ex)')
        ax2.set_title('Life Expectancy by Age')
        ax2.set_xlabel('Age')
        ax2.set_ylabel('Years')
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def export_mortality_data(self):
        """Export mortality data to CSV."""
        messagebox.showinfo(
            "Export Data", 
            "Export functionality not implemented in this demo."
        )
        
    def calculate_present_value(self):
        """Calculate present value of an annuity."""
        if not r_service.is_available():
            messagebox.showerror("Error", "R integration is not available.")
            return
            
        try:
            # Get input values
            age = int(self.pv_age.get())
            payment = float(self.payment.get())
            interest_rate = float(self.pv_interest_rate.get()) / 100
            term = int(self.term.get())
            frequency = self.frequency.get()
            table_type = self.pv_mortality_table.get()
            gender = self.pv_gender.get().lower()
            
            # Determine payment frequency factor
            freq_map = {"Annual": 1, "Semi-annual": 2, "Quarterly": 4, "Monthly": 12}
            freq_factor = freq_map.get(frequency, 1)
            
            # Use the actuarial service to calculate present value
            pv_results = actuarial_service.calculate_present_value(
                age,
                payment,
                interest_rate,
                term,
                frequency,  # pass the frequency name
                table_type,
                gender
            )
            
            if pv_results is None:
                messagebox.showerror("Error", "Failed to calculate present value.")
                return
                
            # Extract results
            pv = pv_results.get('present_value')
            duration = pv_results.get('expected_duration')
            monthly = pv_results.get('monthly_equivalent')
            
            # Update result labels
            self.pv_result.config(text=f"${pv:,.2f}")
            self.duration_result.config(text=f"{duration:.2f} years")
            self.monthly_result.config(text=f"${monthly:,.2f} / month")
            
            # Update info text
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            
            info = (f"Present Value: ${pv:,.2f}\n\n"
                   f"This represents the lump sum amount needed today to fund "
                   f"the specified stream of payments.\n\n"
                   f"Based on a {frequency.lower()} payment of ${payment:,.2f} "
                   f"for {term} years or life, using an interest rate of "
                   f"{interest_rate*100:.2f}%.\n\n"
                   f"The expected duration of payments is {duration:.2f} years.")
                   
            self.info_text.insert(tk.END, info)
            self.info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate present value: {str(e)}")