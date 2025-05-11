import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import tempfile
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import the base page class
from ui.pages.base_page import BasePage

try:
    import rpy2.robjects as robjects
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.packages import importr
    
    # Enable pandas to R conversion
    pandas2ri.activate()
    
    # Import R packages
    base = importr('base')
    stats = importr('stats')
    lifecycle = importr('lifecycle')
    
    R_AVAILABLE = True
except ImportError:
    R_AVAILABLE = False
    

class ActuarialPage(BasePage):
    """Page for actuarial calculations using R integration."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.title = "Actuarial Calculations"
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components for the actuarial page."""
        # Main container frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(main_frame, text="Actuarial Calculations with R", 
                           font=("Helvetica", 16))
        header.pack(pady=(0, 10))
        
        # Check if R is available
        if not R_AVAILABLE:
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
        if not R_AVAILABLE:
            messagebox.showerror("Error", "R integration is not available.")
            return
            
        try:
            # Get input values
            age_from = int(self.age_from.get())
            age_to = int(self.age_to.get())
            interest_rate = float(self.interest_rate.get()) / 100
            table_type = self.mortality_table.get()
            gender = self.gender.get().lower()
            
            # R code for mortality calculations
            r_code = """
            calculate_mortality <- function(age_from, age_to, interest_rate, table_type, gender) {
              # This is a simplified example
              # In a real application, you would use actual mortality tables
              
              ages <- age_from:age_to
              
              # Different mortality rates based on table type and gender
              if (table_type == "Standard Mortality") {
                if (gender == "male") {
                  # Simplified Gompertz-Makeham for illustration
                  qx <- 0.0005 + 0.00008 * exp(0.09 * ages)
                } else if (gender == "female") {
                  qx <- 0.0004 + 0.00004 * exp(0.09 * ages)
                } else {
                  # Unisex
                  qx <- 0.00045 + 0.00006 * exp(0.09 * ages)
                }
              } else if (table_type == "Annuitant Mortality") {
                # Annuitant tables typically have lower mortality rates
                if (gender == "male") {
                  qx <- 0.0004 + 0.00006 * exp(0.085 * ages)
                } else if (gender == "female") {
                  qx <- 0.0003 + 0.00003 * exp(0.085 * ages)
                } else {
                  qx <- 0.00035 + 0.000045 * exp(0.085 * ages)
                }
              } else {
                # Custom mortality (simplified)
                qx <- 0.0003 + 0.00005 * exp(0.08 * ages)
              }
              
              # Calculate survival probabilities
              px <- 1 - qx
              lx <- c(100000, rep(0, length(ages)-1))
              for (i in 2:length(ages)) {
                lx[i] <- lx[i-1] * px[i-1]
              }
              
              # Calculate life expectancy
              ex <- rep(0, length(ages))
              for (i in 1:length(ages)) {
                future_lx <- c(lx[i:length(lx)])
                future_lx <- future_lx / future_lx[1]
                ex[i] <- sum(future_lx) - 0.5
              }
              
              # Discount factors
              v <- (1/(1+interest_rate))^(0:(length(ages)-1))
              
              # Calculate annuity factors
              ax <- rep(0, length(ages))
              for (i in 1:length(ages)) {
                future_lx <- lx[i:length(lx)] / lx[i]
                ax[i] <- sum(future_lx * v[1:length(future_lx)])
              }
              
              # Prepare results
              result <- data.frame(
                Age = ages,
                qx = qx,
                px = px,
                lx = lx,
                ex = ex,
                ax = ax
              )
              
              return(result)
            }
            
            result <- calculate_mortality(age_from, age_to, interest_rate, table_type, gender)
            result
            """
            
            # Run R code
            robjects.r(r_code)
            r_result = robjects.r(f"calculate_mortality({age_from}, {age_to}, {interest_rate}, '{table_type}', '{gender}')")
            
            # Convert to pandas dataframe
            import pandas as pd
            mortality_df = pd.DataFrame({
                'Age': r_result.rx2('Age'),
                'qx': r_result.rx2('qx'),
                'px': r_result.rx2('px'),
                'lx': r_result.rx2('lx'),
                'ex': r_result.rx2('ex'),
                'ax': r_result.rx2('ax')
            })
            
            # Create plot
            self.plot_mortality_data(mortality_df)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate mortality data: {str(e)}")
            
    def plot_mortality_data(self, df):
        """Plot mortality data."""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
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
        if not R_AVAILABLE:
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
            
            # R code for present value calculations
            r_code = """
            calculate_pv <- function(age, payment, interest_rate, term, freq_factor, 
                                   table_type, gender) {
              # Convert to equivalent annual interest rate
              i <- interest_rate
              
              # Number of payments
              n <- term * freq_factor
              
              if (table_type == "None (Fixed Term)") {
                # Fixed term annuity calculation
                v <- 1/(1+i)
                if (i == 0) {
                  pv <- payment * n / freq_factor
                } else {
                  pv <- payment * (1 - v^n) / (i * freq_factor)
                }
                
                expected_duration <- term
                
              } else {
                # Life contingent annuity
                # Simplified mortality calculation for demonstration
                
                # Different mortality rates based on table type and gender
                if (table_type == "Standard Mortality") {
                  if (gender == "male") {
                    # Simplified Gompertz-Makeham for illustration
                    qx_base <- 0.0005 + 0.00008 * exp(0.09 * age)
                  } else if (gender == "female") {
                    qx_base <- 0.0004 + 0.00004 * exp(0.09 * age)
                  } else {
                    # Unisex
                    qx_base <- 0.00045 + 0.00006 * exp(0.09 * age)
                  }
                } else if (table_type == "Annuitant Mortality") {
                  # Annuitant tables typically have lower mortality rates
                  if (gender == "male") {
                    qx_base <- 0.0004 + 0.00006 * exp(0.085 * age)
                  } else if (gender == "female") {
                    qx_base <- 0.0003 + 0.00003 * exp(0.085 * age)
                  } else {
                    qx_base <- 0.00035 + 0.000045 * exp(0.085 * age)
                  }
                }
                
                # Generate mortality rates for projection period
                ages <- age:(age+term)
                qx <- numeric(length(ages))
                
                for (j in 1:length(ages)) {
                  current_age <- ages[j]
                  if (table_type == "Standard Mortality") {
                    if (gender == "male") {
                      qx[j] <- 0.0005 + 0.00008 * exp(0.09 * current_age)
                    } else if (gender == "female") {
                      qx[j] <- 0.0004 + 0.00004 * exp(0.09 * current_age)
                    } else {
                      qx[j] <- 0.00045 + 0.00006 * exp(0.09 * current_age)
                    }
                  } else {
                    if (gender == "male") {
                      qx[j] <- 0.0004 + 0.00006 * exp(0.085 * current_age)
                    } else if (gender == "female") {
                      qx[j] <- 0.0003 + 0.00003 * exp(0.085 * current_age)
                    } else {
                      qx[j] <- 0.00035 + 0.000045 * exp(0.085 * current_age)
                    }
                  }
                }
                
                # Calculate survival probabilities
                px <- 1 - qx
                
                # Discount factors
                v <- (1/(1+i))^(0:(length(ages)-1))
                
                # Compute present value
                lx <- c(100000, rep(0, length(ages)-1))
                for (j in 2:length(ages)) {
                  lx[j] <- lx[j-1] * px[j-1]
                }
                
                # For frequency adjustment
                payment_times <- c()
                survival_probs <- c()
                
                for (t in 1:(term*freq_factor)) {
                  year_frac <- t / freq_factor
                  if (year_frac <= length(ages) - 1) {
                    payment_times <- c(payment_times, year_frac)
                    
                    # Interpolate survival probability
                    year_idx <- floor(year_frac) + 1
                    frac_part <- year_frac - floor(year_frac)
                    
                    if (year_idx < length(lx)) {
                      interp_lx <- lx[year_idx] * (1-frac_part) + lx[year_idx+1] * frac_part
                      survival_probs <- c(survival_probs, interp_lx / lx[1])
                    } else {
                      survival_probs <- c(survival_probs, lx[length(lx)] / lx[1])
                    }
                  }
                }
                
                # Discount factors for payment times
                payment_discount <- (1/(1+i))^payment_times
                
                # Present value calculation
                pv <- payment * sum(survival_probs * payment_discount) / freq_factor
                
                # Expected duration calculation (approximate)
                expected_duration <- sum(lx / lx[1]) - 0.5
                if (expected_duration > term) expected_duration <- term
              }
              
              # Calculate monthly equivalent
              monthly_payment <- pv * (i/12) / (1 - 1/((1+i/12)^(term*12)))
              
              return(list(
                present_value = pv,
                expected_duration = expected_duration,
                monthly_equivalent = monthly_payment
              ))
            }
            
            result <- calculate_pv(age, payment, interest_rate, term, freq_factor, table_type, gender)
            result
            """
            
            # Run R code
            robjects.r(r_code)
            r_result = robjects.r(f"calculate_pv({age}, {payment}, {interest_rate}, {term}, {freq_factor}, '{table_type}', '{gender}')")
            
            # Extract results
            pv = r_result.rx2('present_value')[0]
            duration = r_result.rx2('expected_duration')[0]
            monthly = r_result.rx2('monthly_equivalent')[0]
            
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