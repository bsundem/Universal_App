"""
Service Provider module.

This module implements the Dependency Inversion Principle by providing
a service locator/provider mechanism that allows components to depend on
abstractions (protocols) rather than concrete implementations.
"""
from typing import Dict, Any, Type, TypeVar, Optional, cast

# Import interfaces
from services.interfaces.r_service import RServiceInterface
from services.interfaces.data_manager import (
    DataManagerInterface,
    VisualizationManagerInterface,
    ActuarialDataManagerInterface, 
    KaggleDataManagerInterface
)
from services.interfaces.domain_services import (
    ActuarialServiceInterface,
    KaggleServiceInterface
)

# Type variable for generic service interface
T = TypeVar('T')


class ServiceProvider:
    """
    Service provider for managing and retrieving service instances.
    
    This class acts as a service locator that provides access to services
    through their interface types, allowing components to depend on
    abstractions rather than concrete implementations.
    """
    
    def __init__(self):
        """Initialize the service provider."""
        self._services: Dict[Type, Any] = {}
        self._fallback_providers: Dict[Type, callable] = {}
    
    def register(self, interface_type: Type[T], implementation: T) -> None:
        """
        Register a service implementation for a given interface type.
        
        Args:
            interface_type: The interface (protocol) type
            implementation: The implementation instance
        """
        self._services[interface_type] = implementation
    
    def register_factory(self, interface_type: Type[T], factory: callable) -> None:
        """
        Register a factory function for lazy instantiation of a service.
        
        Args:
            interface_type: The interface (protocol) type
            factory: A callable that returns an implementation of the interface
        """
        self._fallback_providers[interface_type] = factory
    
    def get(self, interface_type: Type[T]) -> Optional[T]:
        """
        Get a service implementation by its interface type.
        
        Args:
            interface_type: The interface (protocol) type
            
        Returns:
            The service implementation, or None if not registered
        """
        # Check if service is already instantiated
        if interface_type in self._services:
            return cast(T, self._services[interface_type])
            
        # Try to instantiate via factory
        if interface_type in self._fallback_providers:
            implementation = self._fallback_providers[interface_type]()
            self._services[interface_type] = implementation
            return cast(T, implementation)
            
        return None


# Create a global service provider instance
provider = ServiceProvider()


# Initialize with default implementations
def initialize_provider():
    """Initialize the service provider with default implementations."""
    from services.r_service import r_service
    from services.actuarial.actuarial_service import actuarial_service
    from services.actuarial.actuarial_data_manager import actuarial_data_manager
    
    # Register R service
    provider.register(RServiceInterface, r_service)
    
    # Register actuarial services
    provider.register(ActuarialServiceInterface, actuarial_service)
    provider.register(ActuarialDataManagerInterface, actuarial_data_manager)
    
    # Additional registrations would go here as new services are added


# Helper functions for retrieving common services
def get_r_service() -> RServiceInterface:
    """Get the R service implementation."""
    service = provider.get(RServiceInterface)
    if service is None:
        raise RuntimeError("R service is not registered with the service provider")
    return service


def get_actuarial_service() -> ActuarialServiceInterface:
    """Get the actuarial service implementation."""
    service = provider.get(ActuarialServiceInterface)
    if service is None:
        raise RuntimeError("Actuarial service is not registered with the service provider")
    return service


def get_actuarial_data_manager() -> ActuarialDataManagerInterface:
    """Get the actuarial data manager implementation."""
    service = provider.get(ActuarialDataManagerInterface)
    if service is None:
        raise RuntimeError("Actuarial data manager is not registered with the service provider")
    return service


# Initialize provider with default implementations
initialize_provider()