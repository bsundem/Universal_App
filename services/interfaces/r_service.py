"""
R Service Interface module.
Defines the protocol for R integration services.
"""
from typing import Protocol, Any, Optional, Dict, List, Union


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
            script_path (str): Path to the R script file, relative to r_scripts directory
            
        Returns:
            bool: True if successful, False otherwise
        """
        ...
    
    def call_function(self, function_name: str, **kwargs) -> Any:
        """
        Call an R function with the provided arguments.
        
        Args:
            function_name (str): Name of the R function to call
            **kwargs: Arguments to pass to the R function
            
        Returns:
            Any: Result from R function, or None if execution failed
        """
        ...
    
    def set_variable(self, name: str, value: Any) -> bool:
        """
        Set a variable in the R environment.
        
        Args:
            name (str): Variable name
            value (Any): Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        ...
    
    def get_variable(self, name: str) -> Any:
        """
        Get a variable value from the R environment.
        
        Args:
            name (str): Variable name
            
        Returns:
            Any: Variable value, or None if not found
        """
        ...