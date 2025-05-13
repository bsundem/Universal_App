"""
Actuarial Service Plugin for the Universal App.

This module provides a plugin implementation of the actuarial service,
using the plugin architecture system.
"""
import os
import tempfile
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

import pandas as pd
import numpy as np

# Import plugin base classes
from services.plugins.base import ServicePlugin

# Import service interface
from services.interfaces.actuarial_service import ActuarialServiceInterface

# Import R service
from services.plugins.r_service_plugin import RServicePlugin

# Import utils
from utils.error_handling import ServiceError, handle_service_errors
from utils.events import Event, event_bus

logger = logging.getLogger(__name__)


class MortalityCalculationEvent(Event):
    """Event published when mortality calculations are performed."""
    age_from: int
    age_to: int
    table_type: str
    gender: str
    success: bool


class PresentValueCalculationEvent(Event):
    """Event published when present value calculations are performed."""
    age: int
    payment: float
    term: int
    success: bool


class ActuarialServicePlugin(ServicePlugin):
    """
    Actuarial Service Plugin for actuarial calculations.
    
    This plugin provides actuarial calculations for the Universal App,
    including mortality tables and present value calculations.
    """
    # Plugin metadata
    plugin_id = "actuarial_service"
    plugin_name = "Actuarial Service"
    plugin_version = "1.0.0"
    plugin_description = "Provides actuarial calculations and mortality analysis"
    plugin_dependencies = ["r_service"]
    
    # Service interface
    service_interface = ActuarialServiceInterface
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the actuarial service plugin.
        
        Args:
            data_dir: Directory to store actuarial data
        """
        super().__init__()
        
        # Set up data directory
        if data_dir:
            self.data_dir = os.path.abspath(data_dir)
        else:
            self.data_dir = os.path.abspath(
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            'data', 'actuarial')
            )
        
        # R service reference
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
        
    def _initialize(self) -> bool:
        """Initialize the actuarial service plugin."""
        self.logger.info(f"Initializing actuarial service plugin with data dir: {self.data_dir}")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Check if R scripts directory exists
        if not os.path.isdir(self.r_scripts_dir):
            self.logger.error(f"R scripts directory does not exist: {self.r_scripts_dir}")
            return False
        
        # Try to get R service
        try:
            from services.plugins.registry import plugin_registry
            self._r_service = plugin_registry.get_plugin("r_service")
            if not self._r_service:
                raise ValueError("R service plugin not found")
                
            # Check if R is available
            if not self._r_service.is_available():
                self.logger.warning("R service is not available")
                
            self.logger.info("Actuarial service plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing actuarial service: {e}")
            return False
    
    def _shutdown(self) -> None:
        """Shut down the actuarial service plugin."""
        self.logger.info("Shutting down actuarial service plugin")
        
        # Clean up temporary directory
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            self.logger.debug(f"Removed temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to remove temporary directory: {e}")
    
    def _get_r_service(self):
        """
        Get the R service.
        
        If the R service isn't already available, try to get it again from the registry.
        
        Returns:
            R service instance
        """
        if not self._r_service:
            try:
                from services.plugins.registry import plugin_registry
                self._r_service = plugin_registry.get_plugin("r_service")
            except Exception as e:
                self.logger.error(f"Failed to get R service: {e}")
                
        return self._r_service
    
    @handle_service_errors("Actuarial")
    def is_r_available(self) -> bool:
        """
        Check if R integration is available for actuarial calculations.
        
        Returns:
            bool: True if R is available, False otherwise
        """
        # Get R service 
        r_service = self._get_r_service()
        return r_service and r_service.is_available()
    
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
        self.logger.info(
            f"Calculating mortality data: ages {age_from}-{age_to}, " 
            f"interest rate {interest_rate}, table {table_type}, gender {gender}",
            "calculate_mortality_data"
        )
        
        try:
            r_service = self._get_r_service()
            if not r_service:
                raise ServiceError(
                    "R service not available",
                    service="Actuarial",
                    operation="calculate_mortality_data"
                )

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
            
            # Publish event
            event_bus.publish(MortalityCalculationEvent(
                source="actuarial_service",
                age_from=age_from,
                age_to=age_to,
                table_type=table_type,
                gender=gender,
                success=True
            ))
            
            self.logger.info(f"Mortality calculation successful, returning {len(mortality_df)} rows")
            return mortality_df
            
        except Exception as e:
            # Publish event
            event_bus.publish(MortalityCalculationEvent(
                source="actuarial_service",
                age_from=age_from,
                age_to=age_to,
                table_type=table_type,
                gender=gender,
                success=False
            ))
            
            self.logger.error(f"Failed to calculate mortality data: {str(e)}", "calculate_mortality_data")
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
        self.logger.info(
            f"Calculating present value: age {age}, payment {payment}, " 
            f"interest rate {interest_rate}, term {term}, frequency {frequency}",
            "calculate_present_value"
        )
        
        try:
            # Determine payment frequency factor
            freq_map = {"Annual": 1, "Semi-annual": 2, "Quarterly": 4, "Monthly": 12}
            freq_factor = freq_map.get(frequency, 1)
            
            r_service = self._get_r_service()
            if not r_service:
                raise ServiceError(
                    "R service not available",
                    service="Actuarial",
                    operation="calculate_present_value"
                )

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
            
            # Publish event
            event_bus.publish(PresentValueCalculationEvent(
                source="actuarial_service",
                age=age,
                payment=payment,
                term=term,
                success=True
            ))
            
            self.logger.info(f"Present value calculation successful: {result}")
            return result
            
        except Exception as e:
            # Publish event
            event_bus.publish(PresentValueCalculationEvent(
                source="actuarial_service",
                age=age,
                payment=payment,
                term=term,
                success=False
            ))
            
            self.logger.error(f"Failed to calculate present value: {str(e)}", "calculate_present_value")
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
        self.logger.info("Getting available mortality tables", "get_available_mortality_tables")
        
        try:
            r_service = self._get_r_service()
            if not r_service:
                # If R service isn't available, return default tables
                self.logger.warning(
                    "R service not available, using default tables",
                    "get_available_mortality_tables"
                )
                return [
                    {"id": "soa_2012", "name": "SOA 2012 IAM", "description": "Society of Actuaries 2012 Individual Annuity Mortality"},
                    {"id": "cso_2001", "name": "CSO 2001", "description": "2001 Commissioners Standard Ordinary Mortality Table"}
                ]

            # Execute the R script
            r_service.execute_script(self.mortality_script_path)

            # Call the get_available_tables function
            r_result = r_service.call_function("get_available_tables")
            
            if r_result is None:
                # If R call fails, fall back to default tables
                self.logger.warning(
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
                self.logger.error(
                    f"Error parsing R result: {e}",
                    "get_available_mortality_tables"
                )
                # Fall back to default tables
                tables = [
                    {"id": "soa_2012", "name": "SOA 2012 IAM", "description": "Society of Actuaries 2012 Individual Annuity Mortality"},
                    {"id": "cso_2001", "name": "CSO 2001", "description": "2001 Commissioners Standard Ordinary Mortality Table"}
                ]
                
            self.logger.info(f"Retrieved {len(tables)} mortality tables")
            return tables
                
        except Exception as e:
            self.logger.error(
                f"Failed to get mortality tables: {str(e)}",
                "get_available_mortality_tables"
            )
            raise ServiceError(
                f"Failed to get available mortality tables: {str(e)}",
                service="Actuarial",
                operation="get_available_mortality_tables",
                cause=e
            )