"""
R Service module - interface between Python and R.

This service provides a clean interface for running R scripts from Python,
allowing for separation of R and Python code while maintaining integration.
"""
import os
import importlib.util
from typing import Dict, List, Any, Optional, Union

# Import the interface
from services.interfaces.r_service import RServiceInterface

# Import error handling
from utils.error_handling import ServiceError, handle_service_errors

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
    """
    Service for executing R scripts and interfacing with R functionality.

    This class implements the RServiceInterface protocol, providing a standard
    way to interact with R from Python code.
    """
    
    def __init__(self):
        """Initialize the R service."""
        self.r_available = R_AVAILABLE
        
        # Get the absolute path to the r_scripts directory
        self.scripts_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'r_scripts')
        )
    
    @handle_service_errors("R")
    def is_available(self) -> bool:
        """
        Check if R is available for use.

        Returns:
            bool: True if R is available, False otherwise
        """
        return self.r_available
    
    @handle_service_errors("R")
    def execute_script(self, script_path: str) -> bool:
        """
        Execute an R script.

        Args:
            script_path (str): Path to the R script, relative to the r_scripts directory

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ServiceError: If execution fails
        """
        if not self.r_available:
            raise ServiceError(
                "R is not available. Please install rpy2 package.",
                service="R",
                operation="execute_script"
            )

        # Construct the full path to the script
        full_path = os.path.join(self.scripts_dir, script_path)

        if not os.path.exists(full_path):
            raise ServiceError(
                f"R script not found: {full_path}",
                service="R",
                operation="execute_script",
                details={"script_path": script_path, "full_path": full_path}
            )

        # Source the R script
        robjects.r(f'source("{full_path}")')

        # Return success
        return True
    
    @handle_service_errors("R")
    def run_r_code(self, r_code: str) -> Any:
        """
        Run arbitrary R code.

        Note: This is an additional method not in the interface.

        Args:
            r_code (str): R code to execute

        Returns:
            Any: Result from R execution

        Raises:
            ServiceError: If execution fails
        """
        if not self.r_available:
            raise ServiceError(
                "R is not available. Please install rpy2 package.",
                service="R",
                operation="run_r_code"
            )

        # Execute the R code
        return robjects.r(r_code)
    
    @handle_service_errors("R")
    def set_variable(self, name: str, value: Any) -> bool:
        """
        Set a variable in the R environment.

        Args:
            name (str): Name of the variable
            value (Any): Value to assign

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ServiceError: If setting the variable fails
        """
        if not self.r_available:
            raise ServiceError(
                "R is not available. Please install rpy2 package.",
                service="R",
                operation="set_variable"
            )

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
                raise ServiceError(
                    f"Mixed type lists are not supported for R conversion: {value}",
                    service="R",
                    operation="set_variable",
                    details={"name": name, "value_type": str(type(value))}
                )
        else:
            # For other types, use pandas2ri conversion
            r_value = value

        # Assign to R environment
        robjects.r.assign(name, r_value)
        return True
    
    @handle_service_errors("R")
    def call_function(self, function_name: str, **kwargs) -> Any:
        """
        Call an R function with the provided arguments, setting variables first.

        Args:
            function_name (str): Name of the R function to call
            **kwargs: Arguments to pass to the R function

        Returns:
            Any: Result from R function

        Raises:
            ServiceError: If the function call fails
        """
        if not self.r_available:
            raise ServiceError(
                "R is not available. Please install rpy2 package.",
                service="R",
                operation="call_function"
            )

        # Set each argument as a variable in the R environment
        for name, value in kwargs.items():
            self.set_variable(name, value)

        # Build function call with argument names
        args_list = ", ".join(kwargs.keys())
        r_code = f"{function_name}({args_list})"

        # Call the function
        return robjects.r(r_code)
    
    @handle_service_errors("R")
    def get_script_path(self, script_path: str) -> str:
        """
        Get the full path to an R script.

        Note: This is an additional helper method not in the interface.

        Args:
            script_path (str): Path to the R script, relative to the r_scripts directory

        Returns:
            str: Full path to the R script

        Raises:
            ServiceError: If there's an issue with the path
        """
        full_path = os.path.join(self.scripts_dir, script_path)

        # Additional validation could be done here
        if not os.path.exists(os.path.dirname(full_path)):
            raise ServiceError(
                f"Directory does not exist for script: {os.path.dirname(full_path)}",
                service="R",
                operation="get_script_path",
                details={"script_path": script_path}
            )

        return full_path

    @handle_service_errors("R")
    def get_variable(self, name: str) -> Any:
        """
        Get a variable value from the R environment.

        Implementation of method required by RServiceInterface.

        Args:
            name (str): Variable name

        Returns:
            Any: Variable value

        Raises:
            ServiceError: If getting the variable fails
        """
        if not self.r_available:
            raise ServiceError(
                "R is not available. Please install rpy2 package.",
                service="R",
                operation="get_variable"
            )

        # Get variable from R environment
        return robjects.r(name)


# Export a singleton instance that can be imported directly
r_service = RService()