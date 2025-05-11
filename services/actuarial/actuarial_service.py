"""
Actuarial service for financial and statistical calculations.
Provides business logic separated from UI components.
"""
import os
import tempfile
import importlib.util
from typing import Dict, List, Optional, Any, Tuple, Union

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

# Check for rpy2
R_AVAILABLE = False
if importlib.util.find_spec("rpy2") is not None:
    try:
        import rpy2.robjects as robjects
        from rpy2.robjects import pandas2ri
        from rpy2.robjects.packages import importr
        
        # Enable pandas to R conversion
        pandas2ri.activate()
        
        # Set R_AVAILABLE to True
        R_AVAILABLE = True
    except Exception:
        pass


class ActuarialService:
    """Service for actuarial calculations using R integration."""
    
    def __init__(self):
        """Initialize the actuarial service."""
        self.temp_dir = tempfile.mkdtemp()
        self.r_scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'r_scripts')

    def is_r_available(self) -> bool:
        """
        Check if R integration is available.
        
        Returns:
            bool: True if R is available, False otherwise
        """
        return R_AVAILABLE
        
    def calculate_mortality_data(self, age_from: int, age_to: int, 
                                interest_rate: float, table_type: str, 
                                gender: str) -> Optional[pd.DataFrame]:
        """
        Calculate mortality data using R.
        
        Args:
            age_from (int): Starting age
            age_to (int): Ending age
            interest_rate (float): Annual interest rate as a decimal (e.g., 0.035)
            table_type (str): Type of mortality table to use
            gender (str): Gender to use (male, female, unisex)
            
        Returns:
            pd.DataFrame: DataFrame with mortality data, or None if calculation failed
        """
        if not self.is_r_available():
            return None
            
        try:
            # R code for mortality calculations - in the future, this should be moved to a separate R script file
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
            if pd is None:
                return None
                
            mortality_df = pd.DataFrame({
                'Age': r_result.rx2('Age'),
                'qx': r_result.rx2('qx'),
                'px': r_result.rx2('px'),
                'lx': r_result.rx2('lx'),
                'ex': r_result.rx2('ex'),
                'ax': r_result.rx2('ax')
            })
            
            return mortality_df
            
        except Exception as e:
            print(f"Failed to calculate mortality data: {str(e)}")
            return None
            
    def calculate_present_value(self, age: int, payment: float, interest_rate: float,
                               term: int, frequency: str, table_type: str, 
                               gender: str) -> Optional[Dict[str, float]]:
        """
        Calculate present value of an annuity.
        
        Args:
            age (int): Age of the annuitant
            payment (float): Annual payment amount
            interest_rate (float): Annual interest rate as a decimal
            term (int): Term of the annuity in years
            frequency (str): Payment frequency (Annual, Semi-annual, Quarterly, Monthly)
            table_type (str): Type of mortality table to use
            gender (str): Gender to use (male, female, unisex)
            
        Returns:
            Dict: Dictionary with present value calculation results
        """
        if not self.is_r_available():
            return None
            
        try:
            # Determine payment frequency factor
            freq_map = {"Annual": 1, "Semi-annual": 2, "Quarterly": 4, "Monthly": 12}
            freq_factor = freq_map.get(frequency, 1)
            
            # R code for present value calculations - in the future, this should be moved to a separate R script file
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
            
            return {
                'present_value': pv,
                'expected_duration': duration,
                'monthly_equivalent': monthly
            }
            
        except Exception as e:
            print(f"Failed to calculate present value: {str(e)}")
            return None
            
    def save_r_scripts_to_files(self):
        """
        Extract R code from this service and save it to R script files.
        This is a one-time operation to help with the transition to external R scripts.
        """
        try:
            # Create the r_scripts directory structure if it doesn't exist
            os.makedirs(os.path.join(self.r_scripts_dir, 'actuarial'), exist_ok=True)
            
            # Save mortality calculation script
            mortality_script = """# Mortality Table Calculations
# This script provides functions for calculating mortality tables

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
"""
            
            # Save the present value calculation script
            present_value_script = """# Present Value Calculations
# This script provides functions for calculating present values of annuities

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
"""

            # Write the scripts to R files
            with open(os.path.join(self.r_scripts_dir, 'actuarial', 'mortality.R'), 'w') as f:
                f.write(mortality_script)
                
            with open(os.path.join(self.r_scripts_dir, 'actuarial', 'present_value.R'), 'w') as f:
                f.write(present_value_script)
                
            return True
        except Exception as e:
            print(f"Failed to save R scripts: {str(e)}")
            return False


# Export a singleton instance that can be imported directly
actuarial_service = ActuarialService()