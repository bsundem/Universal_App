"""
R Service Adapter module.

This module provides an adapter pattern implementation to enable the use of
local converters with R results while maintaining compatibility with code
that expects rx2 attributes on R objects.
"""
import importlib.util
from typing import Any, Dict, Optional, Union, List, Callable

# Check for rpy2
R_AVAILABLE = False
if importlib.util.find_spec("rpy2") is not None:
    try:
        import rpy2.robjects as robjects
        from rpy2.robjects import pandas2ri, numpy2ri
        from rpy2.robjects.conversion import localconverter
        # Don't activate global converters here
        R_AVAILABLE = True
    except Exception as e:
        print(f"Failed to initialize R: {str(e)}")


class RResult:
    """
    Adapter class for R results that provides rx2 method compatibility.
    
    This class wraps an R result object and provides the rx2 method,
    allowing code to use local converters instead of global activation
    while maintaining backward compatibility.
    """
    
    def __init__(self, r_object):
        """
        Initialize with an R object.
        
        Args:
            r_object: The R object to wrap
        """
        self._r_object = r_object
        self._cached_values = {}
    
    def rx2(self, name):
        """
        Mimic the rx2 method of R objects.
        
        Args:
            name: Name of the R object component to access
            
        Returns:
            The component value
        """
        if name in self._cached_values:
            return self._cached_values[name]
            
        # This is the key functionality - use robjects.r to access the component
        result = robjects.r(f'{self._r_object.names[0]}${name}')
        
        # Convert to Python object using local converters
        with localconverter(robjects.default_converter + 
                           pandas2ri.converter + 
                           numpy2ri.converter):
            py_result = robjects.conversion.rpy2py(result)
            
        # Cache for future access
        self._cached_values[name] = py_result
        return py_result
    
    def __getitem__(self, key):
        """
        Provide dictionary-like access.
        
        Args:
            key: Component name
            
        Returns:
            Component value
        """
        return self.rx2(key)


class RServiceAdapter:
    """
    Adapter for R service to handle local/global converter issues.
    
    This class provides methods that wrap R service calls and ensure
    results have rx2 method compatibility while using local converters.
    """
    
    @staticmethod
    def adapt_result(r_result: Any) -> Any:
        """
        Adapt an R result to ensure rx2 compatibility.
        
        Args:
            r_result: Result from an R operation
            
        Returns:
            Adapted result with rx2 compatibility
        """
        if r_result is None:
            return None
            
        # Check if this is an R object that might need rx2
        if hasattr(r_result, 'names') and hasattr(r_result, 'rclass'):
            return RResult(r_result)
            
        return r_result
    
    @staticmethod
    def call_r_function(func: Callable, *args, **kwargs) -> Any:
        """
        Call an R function with local converters and adapt the result.
        
        Args:
            func: R function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Adapted result with rx2 compatibility
        """
        # Call the function - prefer using local converters when possible
        with localconverter(robjects.default_converter):
            result = func(*args, **kwargs)
            
        # Adapt the result for rx2 compatibility
        return RServiceAdapter.adapt_result(result)