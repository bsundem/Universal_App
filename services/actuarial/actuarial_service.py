"""
Actuarial service for financial and statistical calculations.
Provides business logic separated from UI components.
"""
import os
import tempfile
import importlib.util
from typing import Dict, List, Optional, Any, Tuple, Union

# Check for numpy
if importlib.util.find_spec("numpy") is not None:
    import numpy as np
else:
    np = None

# Check for pandas
try:
    import pandas as pd
except ImportError:
    pd = None

# Import the R service
from services.interfaces.r_service import RServiceInterface


class ActuarialService:
    """Service for actuarial calculations using R integration."""

    def __init__(self):
        """Initialize the actuarial service."""
        self.temp_dir = tempfile.mkdtemp()
        self.r_scripts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'r_scripts')

        # Paths to R scripts
        self.mortality_script_path = "actuarial/mortality.R"
        self.present_value_script_path = "actuarial/present_value.R"

        # R service will be retrieved from provider when needed
        self._r_service = None

    def _get_r_service(self) -> RServiceInterface:
        """Get the R service from the provider."""
        if self._r_service is None:
            # Import here to avoid circular imports
            from services.provider import get_r_service
            self._r_service = get_r_service()
        return self._r_service

    def is_r_available(self) -> bool:
        """
        Check if R integration is available.

        Returns:
            bool: True if R is available, False otherwise
        """
        return self._get_r_service().is_available()
        
    def calculate_mortality_data(self, age_from: int, age_to: int, 
                                interest_rate: float, table_type: str, 
                                gender: str) -> Optional[pd.DataFrame]:
        """
        Calculate mortality data using R.
        
        Args:
            age_from (int): Starting age
            age_to (int): Ending age
            interest_rate (float): Annual interest rate as a decimal (e.g., 0.035)
            table_type (str): Type of mortality table to use
            gender (str): Gender to use (male, female, unisex)
            
        Returns:
            pd.DataFrame: DataFrame with mortality data, or None if calculation failed
        """
        if not self.is_r_available():
            return None
            
        try:
            r_service = self._get_r_service()

            # Execute the R script
            r_service.execute_script(self.mortality_script_path)

            # Call the calculate_mortality function with the provided parameters
            r_result = r_service.call_function(
                "calculate_mortality",
                age_from=age_from,
                age_to=age_to,
                interest_rate=interest_rate,
                table_type=table_type,
                gender=gender
            )
            
            # Convert to pandas dataframe
            if pd is None or r_result is None:
                return None
                
            mortality_df = pd.DataFrame({
                'Age': r_result.rx2('Age'),
                'qx': r_result.rx2('qx'),
                'px': r_result.rx2('px'),
                'lx': r_result.rx2('lx'),
                'ex': r_result.rx2('ex'),
                'ax': r_result.rx2('ax')
            })
            
            return mortality_df
            
        except Exception as e:
            print(f"Failed to calculate mortality data: {str(e)}")
            return None
            
    def calculate_present_value(self, age: int, payment: float, interest_rate: float,
                               term: int, frequency: str, table_type: str, 
                               gender: str) -> Optional[Dict[str, float]]:
        """
        Calculate present value of an annuity.
        
        Args:
            age (int): Age of the annuitant
            payment (float): Annual payment amount
            interest_rate (float): Annual interest rate as a decimal
            term (int): Term of the annuity in years
            frequency (str): Payment frequency (Annual, Semi-annual, Quarterly, Monthly)
            table_type (str): Type of mortality table to use
            gender (str): Gender to use (male, female, unisex)
            
        Returns:
            Dict: Dictionary with present value calculation results
        """
        if not self.is_r_available():
            return None
            
        try:
            # Determine payment frequency factor
            freq_map = {"Annual": 1, "Semi-annual": 2, "Quarterly": 4, "Monthly": 12}
            freq_factor = freq_map.get(frequency, 1)
            
            r_service = self._get_r_service()

            # Execute the R script
            r_service.execute_script(self.present_value_script_path)

            # Call the calculate_pv function with the provided parameters
            r_result = r_service.call_function(
                "calculate_pv",
                age=age,
                payment=payment,
                interest_rate=interest_rate,
                term=term,
                freq_factor=freq_factor,
                table_type=table_type,
                gender=gender
            )
            
            if r_result is None:
                return None
                
            # Extract results
            pv = r_result.rx2('present_value')[0]
            duration = r_result.rx2('expected_duration')[0]
            monthly = r_result.rx2('monthly_equivalent')[0]
            
            return {
                'present_value': pv,
                'expected_duration': duration,
                'monthly_equivalent': monthly
            }
            
        except Exception as e:
            print(f"Failed to calculate present value: {str(e)}")
            return None


# Export a singleton instance that can be imported directly
actuarial_service = ActuarialService()