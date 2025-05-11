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
    
    def execute_script(self, script_path: str) -> Any:
        """
        Execute an R script.
        
        Args:
            script_path (str): Path to the R script, relative to the r_scripts directory
            
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
    
    def run_r_code(self, r_code: str) -> Any:
        """
        Run arbitrary R code.
        
        Args:
            r_code (str): R code to execute
            
        Returns:
            Any: Result from R execution, or None if execution failed
        """
        if not self.r_available:
            print("R is not available. Please install rpy2 package.")
            return None
            
        try:
            # Execute the R code
            return robjects.r(r_code)
        except Exception as e:
            print(f"Error executing R code: {str(e)}")
            return None
    
    def set_variable(self, name: str, value: Any) -> bool:
        """
        Set a variable in the R environment.
        
        Args:
            name (str): Name of the variable
            value (Any): Value to assign
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.r_available:
            print("R is not available. Please install rpy2 package.")
            return False
            
        try:
            # Convert Python value to R value
            if isinstance(value, str):
                r_value = robjects.StrVector([value])
            elif isinstance(value, bool):
                r_value = robjects.BoolVector([value])
            elif isinstance(value, (int, float)):
                r_value = robjects.FloatVector([value])
            elif isinstance(value, (list, tuple)):
                if all(isinstance(x, (int, float)) for x in value):
                    r_value = robjects.FloatVector(value)
                elif all(isinstance(x, str) for x in value):
                    r_value = robjects.StrVector(value)
                elif all(isinstance(x, bool) for x in value):
                    r_value = robjects.BoolVector(value)
                else:
                    print(f"Mixed type lists are not supported for R conversion: {value}")
                    return False
            else:
                # For other types, use pandas2ri conversion
                r_value = value
                
            # Assign to R environment
            robjects.r.assign(name, r_value)
            return True
        except Exception as e:
            print(f"Error setting R variable '{name}': {str(e)}")
            return False
    
    def call_function(self, function_name: str, **kwargs) -> Any:
        """
        Call an R function with the provided arguments, setting variables first.
        
        Args:
            function_name (str): Name of the R function to call
            **kwargs: Arguments to pass to the R function
            
        Returns:
            Any: Result from R function, or None if execution failed
        """
        if not self.r_available:
            print("R is not available. Please install rpy2 package.")
            return None
            
        try:
            # Set each argument as a variable in the R environment
            for name, value in kwargs.items():
                self.set_variable(name, value)
                
            # Build function call with argument names
            args_list = ", ".join(kwargs.keys())
            r_code = f"{function_name}({args_list})"
            
            # Call the function
            return robjects.r(r_code)
        except Exception as e:
            print(f"Error calling R function '{function_name}': {str(e)}")
            return None
    
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
        return self.call_function(
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
        return self.call_function(
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