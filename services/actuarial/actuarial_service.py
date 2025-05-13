"""
Actuarial service for financial and statistical calculations.

This service provides actuarial calculations using R integration, including
mortality tables and present value calculations.
"""
import os
import tempfile
from typing import Dict, List, Optional, Any, Tuple, Union

import pandas as pd
import numpy as np

# Import service interfaces
from services.interfaces.actuarial_service import ActuarialServiceInterface

# Import error handling and logging
from utils.error_handling import ServiceError, handle_service_errors
from utils.logging import ServiceLogger

# Get service logger
logger = ServiceLogger("actuarial_service")


class ActuarialService:
    """Service for actuarial calculations using R integration."""

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the actuarial service.
        
        Args:
            data_dir: Directory to store actuarial data, defaults to 'data/actuarial'
        """
        # Set up data directory
        if data_dir:
            self.data_dir = os.path.abspath(data_dir)
        else:
            self.data_dir = os.path.abspath(
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'data', 'actuarial')
            )
            
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # To avoid circular imports, we don't import r_service here
        # Instead, we'll get it when needed in the methods
        self._r_service = None
            
        # Set up temporary directory for calculations
        self.temp_dir = tempfile.mkdtemp()
        
        # Paths to R scripts
        self.r_scripts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'r_scripts', 'actuarial'
        )
        self.mortality_script_path = "actuarial/mortality.R"
        self.present_value_script_path = "actuarial/present_value.R"

        # Log initialization
        logger.info(f"Initialized actuarial service with data dir: {self.data_dir}")
        logger.info(f"R scripts directory: {self.r_scripts_dir}")

    def _get_r_service(self):
        """Get the R service, importing it dynamically to avoid circular imports."""
        if self._r_service is None:
            # Import here to avoid circular imports
            # Fix circular import by importing inside the method
            from services.container import get_r_service
            self._r_service = get_r_service()
        return self._r_service
        
    @handle_service_errors("Actuarial")
    def is_r_available(self) -> bool:
        """
        Check if R integration is available for actuarial calculations.
        
        Returns:
            bool: True if R is available, False otherwise
        """
        # Get R service without circular imports
        r_service = self._get_r_service()
        return r_service.is_available()
        
    @handle_service_errors("Actuarial")
    def calculate_mortality_data(
        self, 
        age_from: int, 
        age_to: int, 
        interest_rate: float, 
        table_type: str, 
        gender: str
    ) -> pd.DataFrame:
        """
        Calculate mortality data using R.
        
        Args:
            age_from: Starting age
            age_to: Ending age
            interest_rate: Annual interest rate as a decimal (e.g., 0.035)
            table_type: Type of mortality table to use
            gender: Gender to use (male, female, unisex)
            
        Returns:
            DataFrame with mortality data
            
        Raises:
            ServiceError: If calculation fails
        """
        logger.info(
            f"Calculating mortality data: ages {age_from}-{age_to}, " 
            f"interest rate {interest_rate}, table {table_type}, gender {gender}",
            "calculate_mortality_data"
        )
        
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
            if r_result is None:
                raise ServiceError(
                    "R calculation returned None",
                    service="Actuarial",
                    operation="calculate_mortality_data"
                )
                
            # Create DataFrame from R result
            mortality_df = pd.DataFrame({
                'Age': r_result.rx2('Age'),
                'qx': r_result.rx2('qx'),
                'px': r_result.rx2('px'),
                'lx': r_result.rx2('lx'),
                'ex': r_result.rx2('ex'),
                'ax': r_result.rx2('ax')
            })
            
            logger.info(f"Mortality calculation successful, returning {len(mortality_df)} rows")
            return mortality_df
            
        except Exception as e:
            logger.error(f"Failed to calculate mortality data: {str(e)}", "calculate_mortality_data")
            raise ServiceError(
                f"Failed to calculate mortality data: {str(e)}",
                service="Actuarial",
                operation="calculate_mortality_data",
                cause=e
            )
            
    @handle_service_errors("Actuarial")
    def calculate_present_value(
        self, 
        age: int, 
        payment: float, 
        interest_rate: float,
        term: int, 
        frequency: str, 
        table_type: str, 
        gender: str
    ) -> Dict[str, float]:
        """
        Calculate present value of an annuity.
        
        Args:
            age: Age of the annuitant
            payment: Annual payment amount
            interest_rate: Annual interest rate as a decimal
            term: Term of the annuity in years
            frequency: Payment frequency (Annual, Semi-annual, Quarterly, Monthly)
            table_type: Type of mortality table to use
            gender: Gender to use (male, female, unisex)
            
        Returns:
            Dictionary with present value calculation results
            
        Raises:
            ServiceError: If calculation fails
        """
        logger.info(
            f"Calculating present value: age {age}, payment {payment}, " 
            f"interest rate {interest_rate}, term {term}, frequency {frequency}",
            "calculate_present_value"
        )
        
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
                raise ServiceError(
                    "R calculation returned None",
                    service="Actuarial",
                    operation="calculate_present_value"
                )
                
            # Extract results
            pv = r_result.rx2('present_value')[0]
            duration = r_result.rx2('expected_duration')[0]
            monthly = r_result.rx2('monthly_equivalent')[0]
            
            result = {
                'present_value': pv,
                'expected_duration': duration,
                'monthly_equivalent': monthly
            }
            
            logger.info(f"Present value calculation successful: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate present value: {str(e)}", "calculate_present_value")
            raise ServiceError(
                f"Failed to calculate present value: {str(e)}",
                service="Actuarial",
                operation="calculate_present_value",
                cause=e
            )
    
    @handle_service_errors("Actuarial")
    def get_available_mortality_tables(self) -> List[Dict[str, str]]:
        """
        Get a list of available mortality tables.
        
        Returns:
            List of dictionaries containing table metadata
            
        Raises:
            ServiceError: If retrieval fails
        """
        logger.info("Getting available mortality tables", "get_available_mortality_tables")
        
        try:
            r_service = self._get_r_service()

            # Execute the R script
            r_service.execute_script(self.mortality_script_path)

            # Call the get_available_tables function
            r_result = r_service.call_function("get_available_tables")
            
            if r_result is None:
                # If R call fails, fall back to default tables
                logger.warning(
                    "Failed to get tables from R, using defaults",
                    "get_available_mortality_tables"
                )
                # Return default tables
                return [
                    {"id": "soa_2012", "name": "SOA 2012 IAM", "description": "Society of Actuaries 2012 Individual Annuity Mortality"},
                    {"id": "cso_2001", "name": "CSO 2001", "description": "2001 Commissioners Standard Ordinary Mortality Table"}
                ]
                
            # Convert R result to Python list
            tables = []
            try:
                ids = r_result.rx2('id')
                names = r_result.rx2('name')
                descriptions = r_result.rx2('description')
                
                for i in range(len(ids)):
                    tables.append({
                        "id": ids[i],
                        "name": names[i],
                        "description": descriptions[i]
                    })
            except Exception as e:
                logger.error(
                    f"Error parsing R result: {e}",
                    "get_available_mortality_tables"
                )
                # Fall back to default tables
                tables = [
                    {"id": "soa_2012", "name": "SOA 2012 IAM", "description": "Society of Actuaries 2012 Individual Annuity Mortality"},
                    {"id": "cso_2001", "name": "CSO 2001", "description": "2001 Commissioners Standard Ordinary Mortality Table"}
                ]
                
            logger.info(f"Retrieved {len(tables)} mortality tables")
            return tables
                
        except Exception as e:
            logger.error(
                f"Failed to get mortality tables: {str(e)}",
                "get_available_mortality_tables"
            )
            raise ServiceError(
                f"Failed to get available mortality tables: {str(e)}",
                service="Actuarial",
                operation="get_available_mortality_tables",
                cause=e
            )


# Export a singleton instance that can be imported directly
actuarial_service = ActuarialService()