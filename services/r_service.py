"""
R Service module - interface between Python and R.

This service provides a clean interface for running R scripts from Python,
allowing for separation of R and Python code while maintaining integration.
"""
import os
from typing import Dict, List, Any, Optional, Union
import sys

# Try to import rpy2, but allow for graceful fallback if not available
try:
    import rpy2.robjects as robjects
    from rpy2.robjects import pandas2ri, numpy2ri
    from rpy2.robjects.packages import importr
    from rpy2.robjects.conversion import localconverter
    RPY2_AVAILABLE = True
except ImportError:
    RPY2_AVAILABLE = False
    # Create dummy robjects for type checking
    class DummyR:
        def __call__(self, *args, **kwargs):
            return None
        def assign(self, *args, **kwargs):
            return None
    
    class DummyRobjects:
        r = DummyR()
        def FloatVector(self, x):
            return x
        def StrVector(self, x):
            return x
        def BoolVector(self, x):
            return x
        
    robjects = DummyRobjects()
    pandas2ri = None
    numpy2ri = None
    
    def importr(name):
        return None
    
    class DummyConverter:
        def __init__(self):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    class LocalConverter:
        def __call__(self, *args):
            return DummyConverter()
    
    localconverter = LocalConverter()

import pandas as pd
import numpy as np

# Import the interface (for type checking only)
from services.interfaces.r_service import RServiceInterface

# Import error handling and logging
from utils.error_handling import ServiceError, handle_service_errors
from utils.logging import ServiceLogger

# Enable pandas-to-R conversion if available
if RPY2_AVAILABLE:
    pandas2ri.activate()

# Get service logger
logger = ServiceLogger("r_service")


class RService:
    """
    Service for executing R scripts and interfacing with R functionality.

    This class implements the RServiceInterface protocol, providing a standard
    way to interact with R from Python code.
    """
    
    def __init__(self, scripts_dir: Optional[str] = None):
        """
        Initialize the R service.
        
        Args:
            scripts_dir: Directory containing R scripts, defaults to 'r_scripts'
        """
        # Get the absolute path to the r_scripts directory
        if scripts_dir:
            self.scripts_dir = os.path.abspath(scripts_dir)
        else:
            self.scripts_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'r_scripts')
            )
            
        # Log initialization
        logger.info(f"Initializing R service with scripts directory: {self.scripts_dir}")
        
        # Initialize attributes
        self.base = None
        self.stats = None
        self.lifecontingencies = None
        
        # Check if R integration is available
        if not RPY2_AVAILABLE:
            logger.warning("R integration is not available: rpy2 module is not installed", "init")
            return
        
        # Try to initialize R
        try:
            # Try to load common R packages
            self.base = importr('base')
            self.stats = importr('stats')
            
            # Try to load lifecontingencies if available
            try:
                self.lifecontingencies = importr('lifecontingencies')
                logger.info("Loaded lifecontingencies package", "init")
            except Exception as e:
                logger.warning(f"Failed to load lifecontingencies package: {e}", "init")
                
            logger.info("R service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing R: {e}", "init")
            # Even if there's an error, we don't raise it here to allow graceful fallback
    
    @handle_service_errors("R")
    def is_available(self) -> bool:
        """
        Check if R is available for use.

        Returns:
            bool: True if R is available, False otherwise
        """
        if not RPY2_AVAILABLE:
            logger.warning("R integration is not available: rpy2 module is not installed", "is_available")
            return False
            
        try:
            # Try to evaluate a simple R expression
            result = robjects.r('1+1')
            return result[0] == 2
        except Exception as e:
            logger.error(f"R availability check failed: {e}", "is_available")
            return False
    
    @handle_service_errors("R")
    def execute_script(self, script_path: str) -> bool:
        """
        Execute an R script.

        Args:
            script_path: Path to the R script, relative to the r_scripts directory

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ServiceError: If execution fails
        """
        if not RPY2_AVAILABLE:
            raise ServiceError(
                "R integration is not available: rpy2 module is not installed",
                service="R",
                operation="execute_script",
                details={"script_path": script_path}
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

        logger.info(f"Executing R script: {script_path}", "execute_script")
        
        # Source the R script
        robjects.r(f'source("{full_path}")')

        # Return success
        return True
    
    @handle_service_errors("R")
    def run_r_code(self, r_code: str) -> Any:
        """
        Run arbitrary R code.

        Args:
            r_code: R code to execute

        Returns:
            Any: Result from R execution

        Raises:
            ServiceError: If execution fails
        """
        if not RPY2_AVAILABLE:
            raise ServiceError(
                "R integration is not available: rpy2 module is not installed",
                service="R",
                operation="run_r_code"
            )
            
        logger.debug(f"Running R code: {r_code}", "run_r_code")
        
        # Execute the R code
        return robjects.r(r_code)
    
    @handle_service_errors("R")
    def set_variable(self, name: str, value: Any) -> bool:
        """
        Set a variable in the R environment.

        Args:
            name: Name of the variable
            value: Value to assign

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ServiceError: If setting the variable fails
        """
        if not RPY2_AVAILABLE:
            raise ServiceError(
                "R integration is not available: rpy2 module is not installed",
                service="R",
                operation="set_variable",
                details={"name": name}
            )
            
        logger.debug(f"Setting R variable: {name}", "set_variable")
        
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
        elif isinstance(value, pd.DataFrame):
            # Convert pandas DataFrame to R data frame
            with localconverter(robjects.default_converter + pandas2ri.converter):
                r_value = pandas2ri.py2rpy(value)
        elif isinstance(value, np.ndarray):
            # Convert numpy array to R array
            with localconverter(robjects.default_converter + numpy2ri.converter):
                r_value = numpy2ri.py2rpy(value)
        else:
            # For other types, use direct conversion
            r_value = value

        # Assign to R environment
        robjects.r.assign(name, r_value)
        return True
    
    @handle_service_errors("R")
    def call_function(self, function_name: str, **kwargs) -> Any:
        """
        Call an R function with the provided arguments, setting variables first.

        Args:
            function_name: Name of the R function to call
            **kwargs: Arguments to pass to the R function

        Returns:
            Any: Result from R function

        Raises:
            ServiceError: If the function call fails
        """
        if not RPY2_AVAILABLE:
            raise ServiceError(
                "R integration is not available: rpy2 module is not installed",
                service="R",
                operation="call_function",
                details={"function_name": function_name}
            )
            
        logger.debug(f"Calling R function: {function_name} with arguments {kwargs}", "call_function")

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

        Args:
            script_path: Path to the R script, relative to the r_scripts directory

        Returns:
            str: Full path to the R script

        Raises:
            ServiceError: If there's an issue with the path
        """
        if not RPY2_AVAILABLE:
            logger.warning("R integration is not available, but script path can still be provided", "get_script_path")
            
        full_path = os.path.join(self.scripts_dir, script_path)

        # Additional validation
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

        Args:
            name: Variable name

        Returns:
            Any: Variable value

        Raises:
            ServiceError: If getting the variable fails
        """
        if not RPY2_AVAILABLE:
            raise ServiceError(
                "R integration is not available: rpy2 module is not installed",
                service="R",
                operation="get_variable",
                details={"name": name}
            )
            
        logger.debug(f"Getting R variable: {name}", "get_variable")
        
        # Get variable from R environment
        return robjects.r(name)
        
    @handle_service_errors("R")
    def get_dataframe(self, r_expression: str) -> pd.DataFrame:
        """
        Execute R code and convert the result to a pandas DataFrame.
        
        Args:
            r_expression: R expression that returns a data frame
            
        Returns:
            pandas DataFrame with the result
            
        Raises:
            ServiceError: If execution fails or result is not a data frame
        """
        if not RPY2_AVAILABLE:
            raise ServiceError(
                "R integration is not available: rpy2 module is not installed",
                service="R",
                operation="get_dataframe",
                details={"r_expression": r_expression}
            )
            
        logger.debug(f"Getting DataFrame from R expression: {r_expression}", "get_dataframe")
        
        # Execute the R code
        r_result = robjects.r(r_expression)
        
        # Convert to pandas DataFrame
        try:
            with localconverter(robjects.default_converter + pandas2ri.converter):
                df = pandas2ri.rpy2py(r_result)
                
            if not isinstance(df, pd.DataFrame):
                raise TypeError(f"Result is not a DataFrame, got {type(df)}")
                
            return df
        except Exception as e:
            raise ServiceError(
                f"Failed to convert R result to DataFrame: {e}",
                service="R",
                operation="get_dataframe",
                cause=e
            )


# Export a singleton instance that can be imported directly
r_service = RService()