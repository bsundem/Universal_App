"""
Unit tests for the Actuarial service.
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from services.actuarial.actuarial_service import ActuarialService


class TestActuarialService:
    """Test cases for the ActuarialService class."""

    @pytest.fixture
    def actuarial_service(self, mock_r_service):
        """Fixture to create an Actuarial service for testing."""
        with patch('services.actuarial.actuarial_service.r_service', mock_r_service):
            service = ActuarialService()
            return service

    def test_is_r_available(self, actuarial_service, mock_r_service):
        """Test checking if R is available."""
        # Setup
        mock_r_service.is_available.return_value = True
        
        # Call the method
        result = actuarial_service.is_r_available()
        
        # Check the result
        assert result is True
        mock_r_service.is_available.assert_called_once()

    def test_calculate_mortality_data_r_not_available(self, actuarial_service, mock_r_service):
        """Test mortality calculation when R is not available."""
        # Setup
        mock_r_service.is_available.return_value = False
        
        # Call the method
        result = actuarial_service.calculate_mortality_data(
            age_from=30,
            age_to=90,
            interest_rate=0.03,
            table_type="Standard Mortality",
            gender="male"
        )
        
        # Check the result
        assert result is None

    def test_calculate_mortality_data_success(self, actuarial_service, mock_r_service):
        """Test successful mortality calculation."""
        # Setup
        mock_r_service.is_available.return_value = True
        
        # Mock r_result with a structure similar to what would be returned from R
        mock_r_result = MagicMock()
        mock_r_result.rx2.side_effect = lambda col: [1, 2, 3]  # Return simple list for each column
        mock_r_service.run_actuarial_mortality.return_value = mock_r_result
        
        # Mock pandas to return a dataframe
        with patch('services.actuarial.actuarial_service.pd') as mock_pd:
            mock_pd.DataFrame.return_value = "mortality dataframe"
            
            # Call the method
            result = actuarial_service.calculate_mortality_data(
                age_from=30,
                age_to=90,
                interest_rate=0.03,
                table_type="Standard Mortality",
                gender="male"
            )
            
            # Check the result
            assert result == "mortality dataframe"
            mock_r_service.run_actuarial_mortality.assert_called_once_with(
                age_from=30,
                age_to=90,
                interest_rate=0.03,
                table_type="Standard Mortality",
                gender="male"
            )

    def test_calculate_present_value_r_not_available(self, actuarial_service, mock_r_service):
        """Test present value calculation when R is not available."""
        # Setup
        mock_r_service.is_available.return_value = False
        
        # Call the method
        result = actuarial_service.calculate_present_value(
            age=65,
            payment=10000,
            interest_rate=0.03,
            term=20,
            frequency="Annual",
            table_type="Standard Mortality",
            gender="male"
        )
        
        # Check the result
        assert result is None

    def test_calculate_present_value_success(self, actuarial_service, mock_r_service):
        """Test successful present value calculation."""
        # Setup
        mock_r_service.is_available.return_value = True
        
        # Mock r_result with a structure similar to what would be returned from R
        mock_r_result = MagicMock()
        mock_r_result.rx2.side_effect = lambda col: [150000] if col == 'present_value' else [15.5] if col == 'expected_duration' else [1250]
        mock_r_service.run_actuarial_pv.return_value = mock_r_result
        
        # Call the method
        result = actuarial_service.calculate_present_value(
            age=65,
            payment=10000,
            interest_rate=0.03,
            term=20,
            frequency="Annual",
            table_type="Standard Mortality",
            gender="male"
        )
        
        # Check the result
        assert result == {
            'present_value': 150000,
            'expected_duration': 15.5,
            'monthly_equivalent': 1250
        }
        
        # Check that the R service was called with the correct parameters
        mock_r_service.run_actuarial_pv.assert_called_once()
        call_args = mock_r_service.run_actuarial_pv.call_args[1]
        assert call_args['age'] == 65
        assert call_args['payment'] == 10000
        assert call_args['interest_rate'] == 0.03
        assert call_args['term'] == 20
        assert call_args['freq_factor'] == 1  # Annual
        assert call_args['table_type'] == "Standard Mortality"
        assert call_args['gender'] == "male"