"""
Dependency Injection Container module for the Universal App.

This module defines a centralized container for managing service dependencies
and implementing the Dependency Inversion Principle with a proper DI container.
"""
from dependency_injector import containers, providers
from typing import Optional

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


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container for the Universal App.
    
    This container manages service dependencies and provides a clean way to
    access services through their interfaces, supporting the Dependency
    Inversion Principle.
    """
    
    # Configuration provider (can be used to configure services)
    config = providers.Configuration()
    
    # Core services
    r_service_provider = providers.Singleton(lambda: r_service)
    
    # Actuarial services
    actuarial_service_provider = providers.Singleton(lambda: actuarial_service)
    actuarial_data_manager_provider = providers.Singleton(lambda: actuarial_data_manager)
    
    # Kaggle services
    kaggle_service_provider = providers.Singleton(lambda: kaggle_service)
    kaggle_data_manager_provider = providers.Singleton(lambda: kaggle_data_manager)


# Create a global container instance
container = Container()


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


# Testing support functions
def override_provider(provider_name: str, implementation: object) -> None:
    """
    Override a provider with a different implementation.
    
    This is particularly useful for testing, where you want to replace
    real implementations with mocks or test doubles.
    
    Args:
        provider_name: Name of the provider to override
        implementation: The implementation to use
    """
    if hasattr(container, f"{provider_name}_provider"):
        provider = getattr(container, f"{provider_name}_provider")
        provider.override(providers.Singleton(lambda: implementation))
    else:
        raise ValueError(f"Provider '{provider_name}' does not exist")


def reset_overrides() -> None:
    """Reset all provider overrides."""
    container.reset_override_providers()