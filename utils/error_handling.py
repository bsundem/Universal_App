"""
Error handling utilities for the Universal App.

This module provides standardized error handling mechanisms to ensure
consistent error handling across the application.
"""
from typing import Dict, Any, Optional, Union, Type, Callable
import traceback
import sys


class AppError(Exception):
    """Base exception class for application-specific errors."""
    
    def __init__(self, message: str, code: str = None, details: Any = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            code: Error code for programmatic handling
            details: Additional error details (can be any serializable object)
        """
        self.message = message
        self.code = code or 'UNKNOWN_ERROR'
        self.details = details
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the exception to a dictionary representation.
        
        Returns:
            Dict containing error information
        """
        result = {
            'error': True,
            'code': self.code,
            'message': self.message,
        }
        
        if self.details:
            result['details'] = self.details
            
        return result


class ValidationError(AppError):
    """Exception raised for input validation errors."""
    
    def __init__(self, message: str, field: str = None, details: Any = None):
        """
        Initialize the validation error.
        
        Args:
            message: Human-readable error message
            field: Specific field that failed validation
            details: Additional error details
        """
        self.field = field
        super().__init__(message, code='VALIDATION_ERROR', details=details)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with field information."""
        result = super().to_dict()
        if self.field:
            result['field'] = self.field
        return result


class ServiceError(AppError):
    """Exception raised for service-level errors."""
    
    def __init__(self, message: str, service: str = None, operation: str = None, details: Any = None):
        """
        Initialize the service error.
        
        Args:
            message: Human-readable error message
            service: Name of the service where the error occurred
            operation: Specific operation that failed
            details: Additional error details
        """
        self.service = service
        self.operation = operation
        
        # Create a more specific code based on service and operation
        code = 'SERVICE_ERROR'
        if service:
            code = f"{service.upper()}_ERROR"
            if operation:
                code = f"{service.upper()}_{operation.upper()}_ERROR"
        
        super().__init__(message, code=code, details=details)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with service information."""
        result = super().to_dict()
        if self.service:
            result['service'] = self.service
        if self.operation:
            result['operation'] = self.operation
        return result


class DataError(AppError):
    """Exception raised for data-related errors."""
    
    def __init__(self, message: str, data_type: str = None, source: str = None, details: Any = None):
        """
        Initialize the data error.
        
        Args:
            message: Human-readable error message
            data_type: Type of data that caused the error
            source: Source of the data (file, API, etc.)
            details: Additional error details
        """
        self.data_type = data_type
        self.source = source
        
        code = 'DATA_ERROR'
        if data_type:
            code = f"{data_type.upper()}_DATA_ERROR"
        
        super().__init__(message, code=code, details=details)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with data information."""
        result = super().to_dict()
        if self.data_type:
            result['data_type'] = self.data_type
        if self.source:
            result['source'] = self.source
        return result


class ConfigurationError(AppError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, section: str = None, details: Any = None):
        """
        Initialize the configuration error.
        
        Args:
            message: Human-readable error message
            section: Section of configuration that caused the error
            details: Additional error details
        """
        self.section = section
        
        code = 'CONFIG_ERROR'
        if section:
            code = f"{section.upper()}_CONFIG_ERROR"
        
        super().__init__(message, code=code, details=details)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with configuration information."""
        result = super().to_dict()
        if self.section:
            result['section'] = self.section
        return result


def safe_execute(func: Callable, 
                error_class: Type[AppError] = ServiceError, 
                default_return: Any = None, 
                **error_kwargs) -> Any:
    """
    Execute a function with standardized error handling.
    
    Args:
        func: Function to execute
        error_class: Error class to use for exceptions
        default_return: Default return value if an exception occurs
        **error_kwargs: Additional keyword arguments to pass to the error class constructor
        
    Returns:
        Result of the function or default_return if an exception occurs
    """
    try:
        return func()
    except AppError as e:
        # Re-raise application errors as-is
        raise
    except Exception as e:
        # Wrap other exceptions
        error_kwargs['details'] = {
            'exception_type': type(e).__name__,
            'exception_msg': str(e),
            'traceback': traceback.format_exc()
        }
        raise error_class(str(e), **error_kwargs)


def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format an exception as a standardized error response dictionary.
    
    Args:
        error: Exception to format
        
    Returns:
        Dictionary containing error information
    """
    if isinstance(error, AppError):
        return error.to_dict()
    
    # For non-app errors, create a generic error response
    return {
        'error': True,
        'code': 'UNKNOWN_ERROR',
        'message': str(error),
        'details': {
            'exception_type': type(error).__name__,
            'traceback': traceback.format_exc()
        }
    }


def handle_service_errors(service_name: str) -> Callable:
    """
    Decorator for handling service errors consistently.
    
    Args:
        service_name: Name of the service for error reporting
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except AppError:
                # Re-raise app errors as they're already handled
                raise
            except Exception as e:
                # Get operation name from function name
                operation = func.__name__
                
                # Wrap in ServiceError
                raise ServiceError(
                    message=f"Error in {service_name} service: {str(e)}",
                    service=service_name,
                    operation=operation,
                    details={
                        'exception_type': type(e).__name__,
                        'exception_msg': str(e),
                        'traceback': traceback.format_exc()
                    }
                )
        return wrapper
    return decorator