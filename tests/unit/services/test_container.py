"""
Tests for the dependency injection container in services/container.py.
"""
import pytest
from unittest.mock import MagicMock, patch

from dependency_injector import providers
from services.container import Container, ContainerManager
from services.container import get_r_service, get_actuarial_service, get_finance_service
from services.r_service import RService
from services.actuarial.actuarial_service import ActuarialService
from services.finance.finance_service import FinanceService


@pytest.fixture
def mock_config_manager():
    """Create a mock for the config manager."""
    with patch('services.container.config_manager') as mock:
        mock.get_config.return_value.model_dump.return_value = {
            'services': {
                'r_integration': {'scripts_dir': 'test_scripts', 'enabled': True},
                'actuarial': {'data_dir': 'test_actuarial_data', 'enabled': True},
                'finance': {'data_dir': 'test_finance_data', 'enabled': True}
            }
        }
        yield mock


@pytest.fixture
def container_manager(mock_config_manager):
    """Create a container manager instance with mock configuration."""
    return ContainerManager()


class TestContainer:
    """Test cases for the Container class."""
    
    def test_container_providers(self):
        """Test that container provides expected services."""
        container = Container()
        
        # Check that the required services are registered
        assert hasattr(container, 'r_service')
        assert hasattr(container, 'actuarial_service')
        assert hasattr(container, 'finance_service')
        
        # Check that they're singleton providers
        assert isinstance(container.r_service, providers.Singleton)
        assert isinstance(container.actuarial_service, providers.Singleton)
        assert isinstance(container.finance_service, providers.Singleton)
    
    def test_container_configuration(self):
        """Test container configuration setup."""
        container = Container()
        
        # Set test configuration
        test_config = {
            'services': {
                'r_integration': {'scripts_dir': 'test_dir'},
                'actuarial': {'data_dir': 'test_act_dir'},
                'finance': {'data_dir': 'test_fin_dir'}
            }
        }
        container.config.from_dict(test_config)
        
        # Mock the service classes to avoid actual instantiation
        with patch('services.r_service.RService') as MockRService:
            with patch('services.actuarial.actuarial_service.ActuarialService') as MockActuarialService:
                with patch('services.finance.finance_service.FinanceService') as MockFinanceService:
                    # Get services from container
                    container.r_service()
                    container.actuarial_service()
                    container.finance_service()
                    
                    # Verify services were initialized with correct parameters
                    MockRService.assert_called_once_with(scripts_dir='test_dir')
                    MockActuarialService.assert_called_once_with(data_dir='test_act_dir')
                    MockFinanceService.assert_called_once_with(data_dir='test_fin_dir')


class TestContainerManager:
    """Test cases for the ContainerManager class."""
    
    def test_init(self, container_manager):
        """Test initialization of container manager."""
        assert container_manager._container is not None
        assert isinstance(container_manager._container, Container)
        assert container_manager._initialized is False
    
    def test_get_container(self, container_manager):
        """Test get_container method."""
        container = container_manager.get_container()
        assert isinstance(container, Container)
    
    def test_init_resources(self, container_manager):
        """Test initializing container resources."""
        test_resources = {'resource1': 'value1', 'resource2': 'value2'}
        
        # Initialize resources
        container_manager.init_resources(**test_resources)
        assert container_manager._initialized is True
        
        # Check resources were added to container
        container_resources = container_manager.get_container().resources()
        assert container_resources['resource1'] == 'value1'
        assert container_resources['resource2'] == 'value2'
        
        # Test idempotence - calling again shouldn't update resources
        container_manager.init_resources(resource3='value3')
        container_resources = container_manager.get_container().resources()
        assert 'resource3' not in container_resources
    
    def test_override_provider(self, container_manager):
        """Test overriding a provider with a different implementation."""
        # Create a mock service
        mock_r_service = MagicMock(spec=RService)
        mock_r_service.is_available.return_value = True
        
        # Override the r_service provider
        container_manager.override_provider('r_service', mock_r_service)
        
        # Get the service from the container
        r_service = container_manager.get_container().r_service()
        
        # Verify it's our mock
        assert r_service is mock_r_service
        assert r_service.is_available() is True
    
    def test_override_nonexistent_provider(self, container_manager):
        """Test attempting to override a non-existent provider."""
        mock_service = MagicMock()
        
        # This should log a warning but not raise an exception
        container_manager.override_provider('non_existent_service', mock_service)
        
        # Container should still function normally
        assert container_manager.get_container() is not None
    
    def test_reset_overrides(self, container_manager):
        """Test resetting provider overrides."""
        # Create a mock service and override a provider
        mock_r_service = MagicMock(spec=RService)
        container_manager.override_provider('r_service', mock_r_service)
        
        # Verify the override worked
        assert container_manager.get_container().r_service() is mock_r_service
        
        # Reset overrides
        container_manager.reset_overrides()
        
        # Get service again - should be a real RService instance
        r_service = container_manager.get_container().r_service()
        assert r_service is not mock_r_service
        assert isinstance(r_service, RService)


class TestHelperFunctions:
    """Test cases for the helper functions."""
    
    @patch('services.container.container.get_container')
    def test_get_r_service(self, mock_get_container):
        """Test get_r_service helper function."""
        mock_container = MagicMock()
        mock_r_service = MagicMock(spec=RService)
        mock_container.r_service.return_value = mock_r_service
        mock_get_container.return_value = mock_container
        
        result = get_r_service()
        
        assert result is mock_r_service
        mock_container.r_service.assert_called_once()
    
    @patch('services.container.container.get_container')
    def test_get_actuarial_service(self, mock_get_container):
        """Test get_actuarial_service helper function."""
        mock_container = MagicMock()
        mock_actuarial_service = MagicMock(spec=ActuarialService)
        mock_container.actuarial_service.return_value = mock_actuarial_service
        mock_get_container.return_value = mock_container
        
        result = get_actuarial_service()
        
        assert result is mock_actuarial_service
        mock_container.actuarial_service.assert_called_once()
    
    @patch('services.container.container.get_container')
    def test_get_finance_service(self, mock_get_container):
        """Test get_finance_service helper function."""
        mock_container = MagicMock()
        mock_finance_service = MagicMock(spec=FinanceService)
        mock_container.finance_service.return_value = mock_finance_service
        mock_get_container.return_value = mock_container
        
        result = get_finance_service()
        
        assert result is mock_finance_service
        mock_container.finance_service.assert_called_once()