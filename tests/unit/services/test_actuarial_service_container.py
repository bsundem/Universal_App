"""
Unit tests for the actuarial service using the dependency injection container.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import container and services
from services.container import get_actuarial_service, get_actuarial_data_manager


@pytest.mark.container
@pytest.mark.r_dependent
class TestActuarialServiceContainer:
    """Test cases for the ActuarialService class using the container."""
    
    def test_is_r_available(self, mock_actuarial_service):
        """Test checking if R is available."""
        # Get service from container (will be our mock)
        actuarial_service = get_actuarial_service()
        
        # Call the method
        result = actuarial_service.is_r_available()
        
        # Verify the mock was called
        mock_actuarial_service.is_r_available.assert_called_once()
        
        # Check the result
        assert result is True
    
    def test_calculate_mortality_data(self, mock_actuarial_service):
        """Test calculating mortality data."""
        # Get service from container (will be our mock)
        actuarial_service = get_actuarial_service()
        
        # Test parameters
        test_params = {
            "age_from": 30,
            "age_to": 90,
            "interest_rate": 0.035,
            "table_type": "Standard Mortality",
            "gender": "male"
        }
        
        # Call the method
        result = actuarial_service.calculate_mortality_data(**test_params)
        
        # Verify the mock was called correctly
        mock_actuarial_service.calculate_mortality_data.assert_called_once_with(**test_params)
        
        # Check that a result was returned
        assert result is not None
    
    def test_calculate_present_value(self, mock_actuarial_service):
        """Test calculating present value."""
        # Get service from container (will be our mock)
        actuarial_service = get_actuarial_service()
        
        # Test parameters
        test_params = {
            "age": 65,
            "payment": 10000,
            "interest_rate": 0.035,
            "term": 20,
            "frequency": "Annual",
            "table_type": "Standard Mortality",
            "gender": "male"
        }
        
        # Call the method
        result = actuarial_service.calculate_present_value(**test_params)
        
        # Verify the mock was called correctly
        mock_actuarial_service.calculate_present_value.assert_called_once_with(**test_params)
        
        # Check the result structure
        assert "present_value" in result
        assert "expected_duration" in result
        assert "monthly_equivalent" in result


@pytest.mark.container
class TestActuarialDataManagerContainer:
    """Test cases for the ActuarialDataManager class using the container."""
    
    def test_prepare_mortality_data_for_visualization(self, mock_actuarial_data_manager):
        """Test preparing mortality data for visualization."""
        # Get service from container (will be our mock)
        data_manager = get_actuarial_data_manager()
        
        # Create a mock DataFrame
        mock_df = MagicMock()
        
        # Call the method
        result = data_manager.prepare_mortality_data_for_visualization(mock_df)
        
        # Verify the mock was called correctly
        mock_actuarial_data_manager.prepare_mortality_data_for_visualization.assert_called_once_with(mock_df)
        
        # Check the result structure
        assert "ages" in result
        assert "mortality_rates" in result
    
    def test_prepare_pv_data_for_visualization(self, mock_actuarial_data_manager):
        """Test preparing present value data for visualization."""
        # Get service from container (will be our mock)
        data_manager = get_actuarial_data_manager()
        
        # Test data
        pv_results = {
            "present_value": 10000.0,
            "expected_duration": 20.5,
            "monthly_equivalent": 100.0
        }
        
        params = {
            "age": 65,
            "payment": 10000,
            "interest_rate": 0.035,
            "term": 20,
            "frequency": "Annual",
            "table_type": "Standard Mortality",
            "gender": "male"
        }
        
        # Call the method
        result = data_manager.prepare_pv_data_for_visualization(pv_results, params)
        
        # Verify the mock was called correctly
        mock_actuarial_data_manager.prepare_pv_data_for_visualization.assert_called_once_with(pv_results, params)
        
        # Check the result structure
        assert "present_value" in result
        assert "expected_duration" in result
        assert "monthly_equivalent" in result
        assert "summary" in result
    
    def test_create_mortality_visualization(self, mock_actuarial_data_manager):
        """Test creating mortality visualization."""
        # Get service from container (will be our mock)
        data_manager = get_actuarial_data_manager()
        
        # Test data
        visualization_data = {
            "ages": [30, 40, 50],
            "mortality_rates": [0.001, 0.002, 0.003]
        }
        
        # Call the method
        result = data_manager.create_mortality_visualization(visualization_data)
        
        # Verify the mock was called correctly
        mock_actuarial_data_manager.create_mortality_visualization.assert_called_once_with(visualization_data)
        
        # Check that a result was returned
        assert result is not None