"""
R Service module - interface between Python and R.

This service provides a clean interface for running R scripts from Python,
allowing for separation of R and Python code while maintaining integration.
"""
import os
import importlib.util
from typing import Dict, List, Any, Optional, Union

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
    except Exception as e:
        print(f"Failed to initialize R: {str(e)}")


class RService:
    """Service for executing R scripts and interfacing with R functionality."""
    
    def __init__(self):
        """Initialize the R service."""
        self.r_available = R_AVAILABLE
        
        # Get the absolute path to the r_scripts directory
        self.scripts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'r_scripts')
        )
    
    def is_available(self) -> bool:
        """
        Check if R is available for use.
        
        Returns:
            bool: True if R is available, False otherwise
        """
        return self.r_available
    
    def execute_script(self, script_path: str, **kwargs) -> Any:
        """
        Execute an R script with the provided arguments.
        
        Args:
            script_path (str): Path to the R script, relative to the r_scripts directory
            **kwargs: Arguments to pass to the R script
            
        Returns:
            Any: Result from R execution, or None if execution failed
        """
        if not self.r_available:
            print("R is not available. Please install rpy2 package.")
            return None
            
        try:
            # Construct the full path to the script
            full_path = os.path.join(self.scripts_dir, script_path)
            
            if not os.path.exists(full_path):
                print(f"R script not found: {full_path}")
                return None
                
            # Source the R script
            robjects.r(f'source("{full_path}")')
            
            # Return the file path for further operations
            return full_path
        except Exception as e:
            print(f"Error executing R script: {str(e)}")
            return None
    
    def run_function(self, function_name: str, script_path: Optional[str] = None, 
                    **kwargs) -> Any:
        """
        Run an R function with the provided arguments.
        
        Args:
            function_name (str): Name of the R function to run
            script_path (str, optional): Path to the R script to load first
            **kwargs: Arguments to pass to the R function
            
        Returns:
            Any: Result from R function, or None if execution failed
        """
        if not self.r_available:
            print("R is not available. Please install rpy2 package.")
            return None
            
        try:
            # Source the script if provided
            if script_path:
                full_path = os.path.join(self.scripts_dir, script_path)
                robjects.r(f'source("{full_path}")')
            
            # Build the function call string
            args_str = ", ".join([f"{k}={self._convert_arg_to_r(v)}" for k, v in kwargs.items()])
            r_call = f"{function_name}({args_str})"
            
            # Execute the R function
            result = robjects.r(r_call)
            return result
        except Exception as e:
            print(f"Error executing R function: {str(e)}")
            return None
    
    def _convert_arg_to_r(self, value: Any) -> str:
        """
        Convert a Python value to a string representation for R.
        
        Args:
            value: Python value to convert
            
        Returns:
            str: R code representation of the value
        """
        if isinstance(value, str):
            # Escape quotes in strings
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(value, bool):
            # Convert Python bool to R logical
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (list, tuple)):
            # Convert Python list to R vector
            items = [self._convert_arg_to_r(item) for item in value]
            return f"c({', '.join(items)})"
        elif isinstance(value, dict):
            # Convert Python dict to R list
            items = [f"{self._convert_arg_to_r(k)}={self._convert_arg_to_r(v)}" for k, v in value.items()]
            return f"list({', '.join(items)})"
        else:
            # Numbers and None can be converted directly
            if value is None:
                return "NULL"
            return str(value)
    
    def run_actuarial_mortality(self, age_from: int, age_to: int, 
                              interest_rate: float, table_type: str, 
                              gender: str) -> Any:
        """
        Run the mortality calculation R function from the actuarial package.
        
        Args:
            age_from (int): Starting age
            age_to (int): Ending age
            interest_rate (float): Annual interest rate as a decimal (e.g., 0.035)
            table_type (str): Type of mortality table to use
            gender (str): Gender to use (male, female, unisex)
            
        Returns:
            Any: R data frame with mortality data
        """
        # Source the mortality script
        script_path = "actuarial/mortality.R"
        self.execute_script(script_path)
        
        # Call the calculate_mortality function
        return self.run_function(
            "calculate_mortality",
            age_from=age_from,
            age_to=age_to,
            interest_rate=interest_rate,
            table_type=table_type,
            gender=gender
        )
    
    def run_actuarial_pv(self, age: int, payment: float, interest_rate: float,
                        term: int, freq_factor: int, table_type: str, 
                        gender: str) -> Any:
        """
        Run the present value calculation R function from the actuarial package.
        
        Args:
            age (int): Age of the annuitant
            payment (float): Annual payment amount
            interest_rate (float): Annual interest rate as a decimal
            term (int): Term of the annuity in years
            freq_factor (int): Payment frequency factor (1=annual, 2=semi-annual, etc.)
            table_type (str): Type of mortality table to use
            gender (str): Gender to use (male, female, unisex)
            
        Returns:
            Any: R list with present value calculation results
        """
        # Source the present value script
        script_path = "actuarial/present_value.R"
        self.execute_script(script_path)
        
        # Call the calculate_pv function
        return self.run_function(
            "calculate_pv",
            age=age,
            payment=payment,
            interest_rate=interest_rate,
            term=term,
            freq_factor=freq_factor,
            table_type=table_type,
            gender=gender
        )


# Export a singleton instance that can be imported directly
r_service = RService()