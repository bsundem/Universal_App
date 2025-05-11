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

# Import actuarial services and R service
from services.actuarial.actuarial_service import actuarial_service
from services.actuarial.actuarial_data_manager import actuarial_data_manager
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

            # Display data as text instead using the data manager
            text_frame = ttk.Frame(self.plot_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            data_text = tk.Text(text_frame, height=20, width=50)
            data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=data_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            data_text.config(yscrollcommand=scrollbar.set)

            try:
                # Use the data manager to get formatted text
                text_data = actuarial_data_manager.get_mortality_data_as_text(df)
                data_text.insert(tk.END, text_data)
            except Exception as e:
                data_text.insert(tk.END, f"Error formatting data: {str(e)}")

            data_text.config(state=tk.DISABLED)
            return

        try:
            # Use the data manager to prepare data for visualization
            visualization_data = actuarial_data_manager.prepare_mortality_data_for_visualization(df)

            # Use the data manager to create the figure
            fig = actuarial_data_manager.create_mortality_visualization(visualization_data)

            if fig:
                # Create canvas for the figure
                canvas = FigureCanvasTkAgg(fig, self.plot_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                # If visualization creation failed
                message = ttk.Label(
                    self.plot_frame,
                    text="Failed to create visualization.",
                    foreground="red"
                )
                message.pack(expand=True)
        except Exception as e:
            # Handle errors
            error_message = ttk.Label(
                self.plot_frame,
                text=f"Error creating visualization: {str(e)}",
                foreground="red"
            )
            error_message.pack(expand=True)
        
    def export_mortality_data(self):
        """Export mortality data to CSV, Excel or JSON."""
        # Get the current mortality data
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

            if mortality_df is None:
                messagebox.showerror("Error", "No data to export. Please calculate first.")
                return

            # Ask user for file format
            format_dialog = tk.Toplevel(self)
            format_dialog.title("Export Format")
            format_dialog.geometry("300x200")
            format_dialog.resizable(False, False)
            format_dialog.transient(self)  # Set as transient to main window
            format_dialog.grab_set()  # Modal dialog

            # Center the dialog
            format_dialog.update_idletasks()
            width = format_dialog.winfo_width()
            height = format_dialog.winfo_height()
            x = (format_dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (format_dialog.winfo_screenheight() // 2) - (height // 2)
            format_dialog.geometry(f"+{x}+{y}")

            # Add format selection
            ttk.Label(format_dialog, text="Select export format:").pack(pady=10)

            format_var = tk.StringVar(value="csv")
            ttk.Radiobutton(format_dialog, text="CSV", variable=format_var, value="csv").pack(anchor=tk.W, padx=20)
            ttk.Radiobutton(format_dialog, text="Excel", variable=format_var, value="excel").pack(anchor=tk.W, padx=20)
            ttk.Radiobutton(format_dialog, text="JSON", variable=format_var, value="json").pack(anchor=tk.W, padx=20)

            def on_export():
                export_format = format_var.get()
                format_dialog.destroy()

                try:
                    file_formats = {
                        "csv": (".csv", "CSV files"),
                        "excel": (".xlsx", "Excel files"),
                        "json": (".json", "JSON files")
                    }

                    file_ext, file_type = file_formats.get(export_format, (".csv", "CSV files"))

                    # Ask for save location
                    filename = table_type.replace(" ", "_").lower() + "_mortality_data" + file_ext
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=file_ext,
                        filetypes=[(file_type, f"*{file_ext}"), ("All files", "*.*")],
                        initialfile=filename
                    )

                    if not file_path:
                        return

                    # Use the data manager to export the data
                    if export_format == "csv":
                        actuarial_data_manager.export_mortality_data_to_csv(mortality_df, file_path)
                    elif export_format == "excel":
                        actuarial_data_manager.export_mortality_data_to_excel(mortality_df, file_path)
                    elif export_format == "json":
                        actuarial_data_manager.export_mortality_data_to_json(mortality_df, file_path)

                    messagebox.showinfo(
                        "Export Complete",
                        f"Data successfully exported to {file_path}"
                    )

                except Exception as e:
                    messagebox.showerror(
                        "Export Error",
                        f"Failed to export data: {str(e)}"
                    )

            # Add buttons
            button_frame = ttk.Frame(format_dialog)
            button_frame.pack(side=tk.BOTTOM, pady=20)

            ttk.Button(button_frame, text="Export", command=on_export).pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="Cancel", command=format_dialog.destroy).pack(side=tk.LEFT, padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
        
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

            # Use the actuarial service to calculate present value
            pv_results = actuarial_service.calculate_present_value(
                age,
                payment,
                interest_rate,
                term,
                frequency,
                table_type,
                gender
            )

            if pv_results is None:
                messagebox.showerror("Error", "Failed to calculate present value.")
                return

            # Use the data manager to prepare display data
            params = {
                'age': age,
                'payment': payment,
                'interest_rate': interest_rate,
                'term': term,
                'frequency': frequency,
                'table_type': table_type,
                'gender': gender
            }

            formatted_results = actuarial_data_manager.prepare_pv_data_for_visualization(pv_results, params)

            # Update result labels
            self.pv_result.config(text=formatted_results['present_value'])
            self.duration_result.config(text=formatted_results['expected_duration'])
            self.monthly_result.config(text=formatted_results['monthly_equivalent'])

            # Update info text
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, formatted_results['summary'])
            self.info_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate present value: {str(e)}")