"""
R Service Plugin for the Universal App.

This module provides a plugin implementation of the R integration service,
using the plugin architecture system.
"""
import os
import logging
import tempfile
from typing import Dict, Any, Optional, List, Union, Callable

# Import plugin base classes
from services.plugins.base import ServicePlugin

# Import service interface
from services.interfaces.r_service import RServiceInterface

# Import utils
from utils.error_handling import ServiceError, handle_service_errors
from utils.events import Event, event_bus

logger = logging.getLogger(__name__)


class RScriptExecutedEvent(Event):
    """Event published when an R script is executed."""
    script_path: str
    success: bool


class RFunctionCalledEvent(Event):
    """Event published when an R function is called."""
    function_name: str
    args: Dict[str, Any]
    success: bool


class RServicePlugin(ServicePlugin):
    """
    R Service Plugin for executing R scripts and functions.
    
    This plugin provides integration with R for the Universal App,
    allowing services to execute R scripts for specialized calculations.
    """
    # Plugin metadata
    plugin_id = "r_service"
    plugin_name = "R Integration Service"
    plugin_version = "1.0.0"
    plugin_description = "Provides integration with R for statistical and actuarial calculations"
    
    # Service interface
    service_interface = RServiceInterface
    
    def __init__(self, scripts_dir: Optional[str] = None):
        """
        Initialize the R service plugin.
        
        Args:
            scripts_dir: Directory containing R scripts
        """
        super().__init__()
        
        # Path to directory containing R scripts
        if scripts_dir:
            self.scripts_dir = os.path.abspath(scripts_dir)
        else:
            self.scripts_dir = os.path.abspath(
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'r_scripts')
            )
        
        # Variables to track R module and robjects
        self._rpy2_available = False
        self._robjects = None
        self._r = None
        self._r_loaded = False
        
        # Directory for temporary files
        self.temp_dir = tempfile.mkdtemp(prefix="r_service_")
        
        # Cache for loaded scripts
        self._loaded_scripts = set()
        
    def _initialize(self) -> bool:
        """Initialize the R service plugin."""
        self.logger.info(f"Initializing R service plugin with scripts directory: {self.scripts_dir}")
        
        # Check if scripts directory exists
        if not os.path.isdir(self.scripts_dir):
            self.logger.error(f"Scripts directory does not exist: {self.scripts_dir}")
            return False
        
        # Try to import rpy2
        try:
            import rpy2.robjects as robjects
            self._robjects = robjects
            self._r = robjects.r
            self._rpy2_available = True
            
            # Try to load the lifecontingencies package
            try:
                self._r('library(lifecontingencies)')
                self.logger.info("Loaded lifecontingencies package")
            except Exception as e:
                self.logger.warning(f"Could not load lifecontingencies package: {e}")
            
            self._r_loaded = True
            self.logger.info("R service plugin initialized successfully")
            return True
            
        except ImportError:
            self.logger.error("Could not import rpy2; R integration is not available")
            return False
        except Exception as e:
            self.logger.error(f"Error initializing R service: {e}")
            return False
    
    def _shutdown(self) -> None:
        """Shut down the R service plugin."""
        self.logger.info("Shutting down R service plugin")
        
        # Clean up temporary directory
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            self.logger.debug(f"Removed temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to remove temporary directory: {e}")
        
        # Clear cache
        self._loaded_scripts.clear()
        
    @handle_service_errors("R")
    def is_available(self) -> bool:
        """
        Check if R integration is available.
        
        Returns:
            True if R integration is available, False otherwise
        """
        return self._rpy2_available and self._r_loaded
        
    @handle_service_errors("R")
    def execute_script(self, script_path: str) -> bool:
        """
        Execute an R script.
        
        Args:
            script_path: Path to the R script to execute
            
        Returns:
            True if the script was executed successfully, False otherwise
            
        Raises:
            ServiceError: If execution fails
        """
        # Check if R is available
        if not self.is_available():
            raise ServiceError(
                "R integration is not available",
                service="R",
                operation="execute_script"
            )
        
        # Normalize script path
        if os.path.isabs(script_path):
            full_path = script_path
        else:
            full_path = os.path.join(self.scripts_dir, script_path)
            
        self.logger.info(f"Executing R script: {script_path}", "execute_script")
        
        try:
            # Execute the script
            self._robjects.r(f'source("{full_path}")')
            
            # Add to cache
            self._loaded_scripts.add(script_path)
            
            # Publish event
            event_bus.publish(RScriptExecutedEvent(
                source="r_service",
                script_path=script_path,
                success=True
            ))
            
            return True
            
        except Exception as e:
            # Publish event
            event_bus.publish(RScriptExecutedEvent(
                source="r_service",
                script_path=script_path,
                success=False
            ))
            
            self.logger.error(f"Error executing R script: {e}", "execute_script")
            raise ServiceError(
                str(e),
                service="R",
                operation="execute_script",
                cause=e
            )
        
    @handle_service_errors("R")
    def call_function(
        self, 
        function_name: str, 
        **kwargs
    ) -> Any:
        """
        Call an R function with parameters.
        
        Args:
            function_name: Name of the R function to call
            **kwargs: Parameters to pass to the function
            
        Returns:
            Result of the function call
            
        Raises:
            ServiceError: If the function call fails
        """
        # Check if R is available
        if not self.is_available():
            raise ServiceError(
                "R integration is not available",
                service="R",
                operation="call_function"
            )
            
        self.logger.info(f"Calling R function: {function_name}", "call_function")
        
        try:
            # Convert parameters to R format
            r_args = []
            for name, value in kwargs.items():
                # Convert Python value to R value
                r_value = self._py_to_r(value)
                # Add as named argument
                r_args.append(f"{name}={r_value}")
                
            # Build R code to call the function
            r_code = f"{function_name}({', '.join(r_args)})"
            
            # Call the function
            result = self._robjects.r(r_code)
            
            # Publish event
            event_bus.publish(RFunctionCalledEvent(
                source="r_service",
                function_name=function_name,
                args=kwargs,
                success=True
            ))
            
            return result
            
        except Exception as e:
            # Publish event
            event_bus.publish(RFunctionCalledEvent(
                source="r_service",
                function_name=function_name,
                args=kwargs,
                success=False
            ))
            
            self.logger.error(f"Error calling R function: {e}", "call_function")
            raise ServiceError(
                str(e),
                service="R",
                operation="call_function",
                cause=e
            )
            
    @handle_service_errors("R")
    def run_r_code(self, code: str) -> Any:
        """
        Run arbitrary R code.
        
        Args:
            code: R code to execute
            
        Returns:
            Result of execution
            
        Raises:
            ServiceError: If execution fails
        """
        # Check if R is available
        if not self.is_available():
            raise ServiceError(
                "R integration is not available",
                service="R",
                operation="run_r_code"
            )
            
        self.logger.debug(f"Running R code: {code}", "run_r_code")
        
        try:
            # Execute the code
            result = self._robjects.r(code)
            return result
            
        except Exception as e:
            self.logger.error(f"Error running R code: {e}", "run_r_code")
            raise ServiceError(
                str(e),
                service="R",
                operation="run_r_code",
                cause=e
            )
            
    @handle_service_errors("R")
    def set_variable(self, name: str, value: Any) -> bool:
        """
        Set an R variable.
        
        Args:
            name: Name of the variable
            value: Value to set
            
        Returns:
            True if the variable was set successfully, False otherwise
            
        Raises:
            ServiceError: If setting the variable fails
        """
        # Check if R is available
        if not self.is_available():
            raise ServiceError(
                "R integration is not available",
                service="R",
                operation="set_variable"
            )
            
        try:
            # Convert Python value to R value
            r_value = self._py_to_r(value)
            
            # Set the variable
            self._robjects.r.assign(name, r_value)
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting R variable: {e}", "set_variable")
            raise ServiceError(
                str(e),
                service="R",
                operation="set_variable",
                cause=e
            )
            
    @handle_service_errors("R")
    def get_variable(self, name: str) -> Any:
        """
        Get an R variable.
        
        Args:
            name: Name of the variable
            
        Returns:
            Value of the variable
            
        Raises:
            ServiceError: If getting the variable fails
        """
        # Check if R is available
        if not self.is_available():
            raise ServiceError(
                "R integration is not available",
                service="R",
                operation="get_variable"
            )
            
        try:
            # Get the variable
            value = self._robjects.r[name]
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting R variable: {e}", "get_variable")
            raise ServiceError(
                str(e),
                service="R",
                operation="get_variable",
                cause=e
            )
            
    @handle_service_errors("R")
    def get_dataframe(self, name: str) -> Any:
        """
        Get an R dataframe as a pandas DataFrame.
        
        Args:
            name: Name of the dataframe
            
        Returns:
            pandas DataFrame
            
        Raises:
            ServiceError: If getting the dataframe fails
        """
        # Check if R is available
        if not self.is_available():
            raise ServiceError(
                "R integration is not available",
                service="R",
                operation="get_dataframe"
            )
            
        try:
            # Import conversion utilities
            from rpy2.robjects import pandas2ri
            pandas2ri.activate()
            
            # Get the dataframe
            r_expression = f'as.data.frame({name})'
            r_result = self._robjects.r(r_expression)
            
            # Convert to pandas DataFrame
            df = pandas2ri.rpy2py(r_result)
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting R dataframe: {e}", "get_dataframe")
            raise ServiceError(
                str(e),
                service="R",
                operation="get_dataframe",
                cause=e
            )
    
    def _py_to_r(self, value: Any) -> Any:
        """
        Convert a Python value to an R value.
        
        Args:
            value: Python value to convert
            
        Returns:
            R value
        """
        if value is None:
            return self._robjects.NULL
            
        # Simple types
        if isinstance(value, (int, float, str, bool)):
            return value
            
        # Lists/tuples
        if isinstance(value, (list, tuple)):
            # Check if all elements are of the same simple type
            if all(isinstance(x, (int, float, str, bool)) for x in value):
                import numpy as np
                return np.array(value)
                
        # Use the name directly for variables
        if isinstance(value, str) and value.isidentifier():
            return value
            
        # For more complex types, just return as is and hope for the best
        return value