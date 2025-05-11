"""
Dependency Injection Container module for the Universal App.

This module defines a centralized container for managing service dependencies
and implementing the Dependency Inversion Principle with a proper DI container.
"""
from dependency_injector import containers, providers
from typing import Optional, Dict, Any, Callable, Type
import inspect

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


# Provider factory functions for better testability and reset capability
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


# Registry of provider factories for reset operations
PROVIDER_FACTORIES = {
    "r_service_provider": create_r_service_provider,
    "actuarial_service_provider": create_actuarial_service_provider,
    "actuarial_data_manager_provider": create_actuarial_data_manager_provider,
    "kaggle_service_provider": create_kaggle_service_provider,
    "kaggle_data_manager_provider": create_kaggle_data_manager_provider,
}


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Universal App.

    This container manages service dependencies and provides a clean way to
    access services through their interfaces, supporting the Dependency
    Inversion Principle.
    """

    # Configuration provider (can be used to configure services)
    config = providers.Configuration()

    # Core services - using factory functions for better testability
    r_service_provider = create_r_service_provider()

    # Actuarial services
    actuarial_service_provider = create_actuarial_service_provider()
    actuarial_data_manager_provider = create_actuarial_data_manager_provider()

    # Kaggle services
    kaggle_service_provider = create_kaggle_service_provider()
    kaggle_data_manager_provider = create_kaggle_data_manager_provider()


# Create a global container instance
container = Container()


# Original provider references for reset capability
_original_providers = {}

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


# Registry of services for lookup by interface type
SERVICE_REGISTRY = {
    RServiceInterface: get_r_service,
    ActuarialServiceInterface: get_actuarial_service,
    ActuarialDataManagerInterface: get_actuarial_data_manager,
    KaggleServiceInterface: get_kaggle_service,
    KaggleDataManagerInterface: get_kaggle_data_manager,
}


def get_service_by_interface(interface_type: Type) -> Any:
    """
    Get a service implementation by its interface type.

    This allows for more dynamic service resolution when the exact
    service type isn't known at compile time.

    Args:
        interface_type: The interface type to resolve

    Returns:
        Implementation of the specified interface

    Raises:
        ValueError: If no service is registered for the interface
    """
    if interface_type in SERVICE_REGISTRY:
        return SERVICE_REGISTRY[interface_type]()
    raise ValueError(f"No service registered for interface {interface_type.__name__}")


# Initialize original providers for reset capability
def _initialize_original_providers():
    """Store original provider references for reset capability."""
    global _original_providers
    for provider_name, factory_func in PROVIDER_FACTORIES.items():
        _original_providers[provider_name] = getattr(container, provider_name)
_initialize_original_providers()


# Testing support functions
def override_provider(provider_name: str, implementation: object) -> None:
    """
    Override a provider with a different implementation.

    This is particularly useful for testing, where you want to replace
    real implementations with mocks or test doubles.

    Args:
        provider_name: Name of the provider to override
        implementation: The implementation to use

    Raises:
        ValueError: If the provider doesn't exist
    """
    provider_attr = f"{provider_name}_provider"
    if hasattr(container, provider_attr):
        provider = getattr(container, provider_attr)
        provider.override(providers.Object(implementation))
    else:
        raise ValueError(f"Provider '{provider_name}' does not exist")


def reset_overrides() -> None:
    """
    Reset all provider overrides to their original implementations.

    This function is idempotent and can be called multiple times safely.
    It ensures the container returns to its original state.
    """
    # Use the provider factories to recreate the providers
    for provider_name, factory_func in PROVIDER_FACTORIES.items():
        provider_attr = f"{provider_name}_provider"
        setattr(container, provider_attr, factory_func())


def reset_single_provider(provider_name: str) -> None:
    """
    Reset a single provider to its original implementation.

    Args:
        provider_name: Name of the provider to reset

    Raises:
        ValueError: If the provider doesn't exist
    """
    provider_attr = f"{provider_name}_provider"
    if provider_name in PROVIDER_FACTORIES:
        setattr(container, provider_attr, PROVIDER_FACTORIES[provider_name]())
    else:
        raise ValueError(f"Provider '{provider_name}' not found in registry")


def get_all_providers() -> Dict[str, Any]:
    """
    Get all registered providers.

    Returns:
        Dict mapping provider names to their instances
    """
    result = {}
    for name in PROVIDER_FACTORIES.keys():
        provider_attr = f"{name}_provider"
        if hasattr(container, provider_attr):
            result[name] = getattr(container, provider_attr)
    return result