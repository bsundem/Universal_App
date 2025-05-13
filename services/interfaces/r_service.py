"""
R Service Interface module.

Defines the protocol for R integration services.
"""
from typing import Protocol, Any, Optional, Dict, List, Union
from pandas import DataFrame


class RServiceInterface(Protocol):
    """
    Protocol defining the interface for R integration services.
    
    This interface defines the contract that any R service implementation must fulfill,
    allowing for different implementations (like mock services for testing).
    """
    
    def is_available(self) -> bool:
        """
        Check if R integration is available.
        
        Returns:
            bool: True if R is available, False otherwise
        """
        ...
    
    def execute_script(self, script_path: str) -> bool:
        """
        Execute an R script file.
        
        Args:
            script_path: Path to the R script file, relative to r_scripts directory
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    def call_function(self, function_name: str, **kwargs) -> Any:
        """
        Call an R function with the provided arguments.
        
        Args:
            function_name: Name of the R function to call
            **kwargs: Arguments to pass to the R function
            
        Returns:
            Result from R function
        """
        ...
    
    def set_variable(self, name: str, value: Any) -> bool:
        """
        Set a variable in the R environment.
        
        Args:
            name: Variable name
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    def get_variable(self, name: str) -> Any:
        """
        Get a variable value from the R environment.
        
        Args:
            name: Variable name
            
        Returns:
            Variable value
        """
        ...
        
    def run_r_code(self, r_code: str) -> Any:
        """
        Run arbitrary R code.
        
        Args:
            r_code: R code to execute
            
        Returns:
            Result from R execution
        """
        ...
        
    def get_dataframe(self, r_expression: str) -> DataFrame:
        """
        Execute R code and convert the result to a pandas DataFrame.
        
        Args:
            r_expression: R expression that returns a data frame
            
        Returns:
            pandas DataFrame with the result
        """
        ...