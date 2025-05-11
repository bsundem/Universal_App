"""
Dependency Injection Container module for the Universal App.

This module defines a centralized container for managing service dependencies
and implementing the Dependency Inversion Principle with a proper DI container.
The container uses a registration-based system that allows dynamic service
registration, interface-based resolution, and support for multiple
implementations of the same interface.

Key Features:
- Service registration with interface types
- Type-safe access to services by interface
- Support for multiple implementations of the same interface
- Identity preservation for testing
- Dynamic service resolution
"""
from dependency_injector import containers, providers
from typing import Optional, Dict, Any, Callable, Type, cast, TypeVar

# Import service interfaces
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

# Import concrete implementations
from services.r_service import r_service
from services.actuarial.actuarial_service import actuarial_service
from services.actuarial.actuarial_data_manager import actuarial_data_manager
from services.kaggle.kaggle_service import kaggle_service
from services.kaggle.kaggle_data_manager import kaggle_data_manager


# Type variable for interface types
T = TypeVar('T')


# Service registry to maintain metadata about services
class ServiceRegistry:
    """
    Registry for managing service registrations.

    This registry holds metadata about services, their instances,
    factory functions, and interface types, enabling a more
    extensible dependency injection system.

    Key features:
    - Maps service names to their metadata (instance, interface, factory function)
    - Maps interface types to their implementing services
    - Supports multiple implementations of the same interface
    - Maintains service identity for consistent behavior in tests
    - Provides lookup by both name and interface type
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._registry = {}
        self._interface_registry = {}
        self._interface_mappings = {}

    def register(self, name: str, instance: Any, interface_type: Type,
                 factory_fn: Callable) -> None:
        """
        Register a service with the container.

        Args:
            name: Service name (without '_provider' suffix)
            instance: Service singleton instance
            interface_type: Type of the service interface
            factory_fn: Factory function to create the provider
        """
        self._registry[name] = {
            'instance': instance,
            'interface': interface_type,
            'factory': factory_fn
        }

        # Register by interface for lookup (most recent implementation)
        self._interface_registry[interface_type] = name

        # Also track all implementations of each interface
        if interface_type not in self._interface_mappings:
            self._interface_mappings[interface_type] = []

        if name not in self._interface_mappings[interface_type]:
            self._interface_mappings[interface_type].append(name)
    
    def get_instance(self, name: str) -> Any:
        """
        Get the original instance of a service.
        
        Args:
            name: Service name
            
        Returns:
            Original service instance
            
        Raises:
            ValueError: If service not found
        """
        if name not in self._registry:
            raise ValueError(f"Service '{name}' not registered")
        return self._registry[name]['instance']
    
    def get_factory(self, name: str) -> Callable:
        """
        Get the factory function for a service.
        
        Args:
            name: Service name
            
        Returns:
            Factory function
            
        Raises:
            ValueError: If service not found
        """
        if name not in self._registry:
            raise ValueError(f"Service '{name}' not registered")
        return self._registry[name]['factory']
    
    def get_interface(self, name: str) -> Type:
        """
        Get the interface type for a service.
        
        Args:
            name: Service name
            
        Returns:
            Interface type
            
        Raises:
            ValueError: If service not found
        """
        if name not in self._registry:
            raise ValueError(f"Service '{name}' not registered")
        return self._registry[name]['interface']
    
    def get_by_interface(self, interface_type: Type) -> str:
        """
        Get service name by interface type.

        This returns the most recently registered service for the interface.

        Args:
            interface_type: Type of the service interface

        Returns:
            Service name

        Raises:
            ValueError: If interface not registered
        """
        if interface_type not in self._interface_registry:
            raise ValueError(f"No service registered for interface {interface_type.__name__}")
        return self._interface_registry[interface_type]

    def get_all_by_interface(self, interface_type: Type) -> list:
        """
        Get all service names that implement an interface type.

        Returns all service names that were registered with the specified
        interface type. This allows retrieving multiple implementations
        of the same interface, which is useful for strategy patterns,
        plugins, or composite patterns.

        Args:
            interface_type: Type of the service interface

        Returns:
            List of service names implementing the interface

        Raises:
            ValueError: If interface not registered

        Example:
            service_names = registry.get_all_by_interface(DataProcessorInterface)
            for name in service_names:
                print(f"Found processor: {name}")
        """
        if interface_type not in self._interface_mappings:
            raise ValueError(f"No services registered for interface {interface_type.__name__}")
        return self._interface_mappings[interface_type]
    
    def get_all_names(self) -> list:
        """Get all registered service names."""
        return list(self._registry.keys())
    
    def is_registered(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._registry


# Create the registry instance
registry = ServiceRegistry()


# Factory functions for creating providers
def create_r_service_provider():
    """Factory function for R service provider."""
    from services.r_service import r_service
    return providers.Singleton(lambda: r_service)


def create_actuarial_service_provider():
    """Factory function for actuarial service provider."""
    from services.actuarial.actuarial_service import actuarial_service
    return providers.Singleton(lambda: actuarial_service)


def create_actuarial_data_manager_provider():
    """Factory function for actuarial data manager provider."""
    from services.actuarial.actuarial_data_manager import actuarial_data_manager
    return providers.Singleton(lambda: actuarial_data_manager)


def create_kaggle_service_provider():
    """Factory function for Kaggle service provider."""
    from services.kaggle.kaggle_service import kaggle_service
    return providers.Singleton(lambda: kaggle_service)


def create_kaggle_data_manager_provider():
    """Factory function for Kaggle data manager provider."""
    from services.kaggle.kaggle_data_manager import kaggle_data_manager
    return providers.Singleton(lambda: kaggle_data_manager)


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Universal App.

    This container manages service dependencies and provides a clean way to
    access services through their interfaces, supporting the Dependency
    Inversion Principle.

    The container works with the ServiceRegistry to maintain registrations
    and support dynamic service resolution. It leverages dependency-injector's
    providers to manage service lifecycle and dependencies.
    """
    
    # Configuration provider (can be used to configure services)
    config = providers.Configuration()
    

# Create a global container instance
container = Container()


# Register the services with the registry
registry.register('r_service', r_service, RServiceInterface, create_r_service_provider)
registry.register('actuarial_service', actuarial_service, ActuarialServiceInterface, create_actuarial_service_provider)
registry.register('actuarial_data_manager', actuarial_data_manager, ActuarialDataManagerInterface, create_actuarial_data_manager_provider)
registry.register('kaggle_service', kaggle_service, KaggleServiceInterface, create_kaggle_service_provider)
registry.register('kaggle_data_manager', kaggle_data_manager, KaggleDataManagerInterface, create_kaggle_data_manager_provider)


# Initialize the container with providers
for name in registry.get_all_names():
    factory = registry.get_factory(name)
    setattr(container, f"{name}_provider", factory())


# Helper functions for retrieving services
def get_r_service() -> RServiceInterface:
    """Get the R service implementation."""
    return container.r_service_provider()


def get_actuarial_service() -> ActuarialServiceInterface:
    """Get the actuarial service implementation."""
    return container.actuarial_service_provider()


def get_actuarial_data_manager() -> ActuarialDataManagerInterface:
    """Get the actuarial data manager implementation."""
    return container.actuarial_data_manager_provider()


def get_kaggle_service() -> KaggleServiceInterface:
    """Get the Kaggle service implementation."""
    return container.kaggle_service_provider()


def get_kaggle_data_manager() -> KaggleDataManagerInterface:
    """Get the Kaggle data manager implementation."""
    return container.kaggle_data_manager_provider()


def get_service_by_interface(interface_type: Type[T]) -> T:
    """
    Get a service implementation by its interface type.

    This returns the most recently registered service for the interface.
    When multiple services implement the same interface, this function
    returns the implementation that was registered last.

    Args:
        interface_type: The interface type to resolve

    Returns:
        Implementation of the specified interface

    Raises:
        ValueError: If no service is registered for the interface

    Example:
        ```python
        # Get implementation of LoggerInterface
        logger = get_service_by_interface(LoggerInterface)
        logger.log("Service resolved dynamically")
        ```
    """
    try:
        service_name = registry.get_by_interface(interface_type)
        provider = getattr(container, f"{service_name}_provider")
        return cast(T, provider())
    except (ValueError, AttributeError):
        raise ValueError(f"No service registered for interface {interface_type.__name__}")


def get_all_services_by_interface(interface_type: Type[T]) -> Dict[str, T]:
    """
    Get all service implementations for an interface type.

    This returns a dictionary mapping service names to their implementations
    for all services registered with the specified interface. This is useful
    when you need to access multiple implementations of the same interface,
    such as for strategy patterns or plugin systems.

    Args:
        interface_type: The interface type to resolve

    Returns:
        Dictionary mapping service names to implementations

    Raises:
        ValueError: If no services are registered for the interface

    Example:
        ```python
        # Get all implementations of StorageInterface
        storage_services = get_all_services_by_interface(StorageInterface)

        # Use each storage service
        for name, storage in storage_services.items():
            print(f"Using {name}")
            storage.save(data)
        ```
    """
    try:
        service_names = registry.get_all_by_interface(interface_type)
        result = {}

        for name in service_names:
            provider = getattr(container, f"{name}_provider")
            result[name] = cast(T, provider())

        return result
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Error retrieving services for interface {interface_type.__name__}: {str(e)}")


# Testing support functions
def override_provider(service_name: str, implementation: object) -> None:
    """
    Override a provider with a different implementation.

    This is particularly useful for testing, where you want to replace
    real implementations with mocks or test doubles. The override
    is temporary and can be reset using reset_overrides() or
    reset_single_provider().

    Args:
        service_name: Name of the service to override (without '_provider' suffix)
        implementation: The implementation to use (typically a mock object)

    Raises:
        ValueError: If the provider doesn't exist

    Example:
        ```python
        # Create a mock service
        mock_service = MagicMock()
        mock_service.get_data.return_value = {'mocked': True}

        # Override the real service
        override_provider('data_service', mock_service)

        # Later reset to the original implementation
        reset_overrides()
        ```
    """
    provider_attr = f"{service_name}_provider"
    if hasattr(container, provider_attr):
        provider = getattr(container, provider_attr)
        provider.override(providers.Object(implementation))
    else:
        raise ValueError(f"Provider '{service_name}' does not exist")


def reset_overrides() -> None:
    """
    Reset all provider overrides to their original implementations.

    This function is idempotent and can be called multiple times safely.
    It ensures the container returns to its original state. This is particularly
    useful in test teardown to ensure tests don't affect each other.

    The function safely handles cases where providers might not exist in the
    container but are registered in the registry.

    Example:
        ```python
        try:
            # Override some services for testing
            override_provider('service1', mock1)
            override_provider('service2', mock2)

            # Run the test
            run_test()
        finally:
            # Reset all overrides to original implementations
            reset_overrides()
        ```
    """
    for service_name in registry.get_all_names():
        provider_attr = f"{service_name}_provider"
        # Check if the provider exists in the container
        if hasattr(container, provider_attr):
            provider = getattr(container, provider_attr)
            # Get the original service instance
            original_service = registry.get_instance(service_name)
            # Override with the original instance to preserve identity
            provider.override(providers.Object(original_service))


def reset_single_provider(service_name: str) -> None:
    """
    Reset a single provider to its original implementation.

    This function resets only one specific service provider to its original
    implementation, rather than resetting all providers as reset_overrides does.
    This is useful when you want to maintain some mock services while resetting others.

    Args:
        service_name: Name of the service to reset

    Raises:
        ValueError: If the service doesn't exist

    Example:
        ```python
        # Override multiple services
        override_provider('service1', mock1)
        override_provider('service2', mock2)

        # Reset just one of them
        reset_single_provider('service1')

        # Now service1 is reset but service2 is still mocked
        ```
    """
    if not registry.is_registered(service_name):
        raise ValueError(f"Service '{service_name}' not registered")

    provider_attr = f"{service_name}_provider"
    # Check if the provider exists in the container
    if not hasattr(container, provider_attr):
        return  # Nothing to reset if provider doesn't exist in container

    provider = getattr(container, provider_attr)
    # Get the original service instance
    original_service = registry.get_instance(service_name)
    # Override with the original instance to preserve identity
    provider.override(providers.Object(original_service))


def get_all_services() -> Dict[str, Any]:
    """
    Get all registered services with their metadata.

    This function returns a dictionary containing information about all
    registered services, including their interface types and instances.
    This is primarily useful for debugging and inspecting the container state.

    Returns:
        Dict mapping service names to their metadata (interface name and instance)

    Example:
        ```python
        # Get all registered services
        services = get_all_services()

        # Print service information
        for name, info in services.items():
            print(f"Service: {name}, Interface: {info['interface']}")
        ```
    """
    result = {}
    for service_name in registry.get_all_names():
        interface_type = registry.get_interface(service_name)
        result[service_name] = {
            'interface': interface_type.__name__,
            'instance': registry.get_instance(service_name),
        }
    return result


def register_service(name: str, instance: Any, interface_type: Type,
                    factory_fn: Callable) -> None:
    """
    Register a new service with the container.

    This function allows dynamic registration of new services without
    modifying the container code directly. It adds the service to the
    registry and creates a provider in the container.

    Args:
        name: Service name (without '_provider' suffix)
        instance: Service singleton instance
        interface_type: Type of the service interface (Protocol class)
        factory_fn: Factory function to create the provider

    Raises:
        ValueError: If service already registered

    Example:
        ```python
        # Define a service and its factory
        payment_service = PaymentService()

        def create_payment_service_provider():
            from dependency_injector import providers
            return providers.Singleton(lambda: payment_service)

        # Register with the container
        register_service(
            'payment_service',
            payment_service,
            PaymentServiceInterface,
            create_payment_service_provider
        )
        ```
    """
    if registry.is_registered(name):
        raise ValueError(f"Service '{name}' already registered")
    
    # Register with the registry
    registry.register(name, instance, interface_type, factory_fn)
    
    # Create and add the provider to the container
    provider = factory_fn()
    setattr(container, f"{name}_provider", provider)