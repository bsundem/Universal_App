"""
Actuarial Service Interface module.

Defines the protocol for actuarial calculation services.
"""
from typing import Protocol, Any, Optional, Dict, List, Union
from pandas import DataFrame


class ActuarialServiceInterface(Protocol):
    """
    Protocol defining the interface for actuarial services.
    
    This interface defines the contract that any actuarial service implementation
    must fulfill, allowing for different implementations (like mock services for testing).
    """
    
    def is_r_available(self) -> bool:
        """
        Check if R integration is available for actuarial calculations.
        
        Returns:
            True if R is available, False otherwise
        """
        ...
    
    def calculate_mortality_data(
        self, 
        age_from: int, 
        age_to: int, 
        interest_rate: float, 
        table_type: str, 
        gender: str
    ) -> DataFrame:
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
        """
        ...
    
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
        """
        ...
        
    def get_available_mortality_tables(self) -> List[Dict[str, str]]:
        """
        Get a list of available mortality tables.
        
        Returns:
            List of dictionaries containing table metadata
        """
        ...