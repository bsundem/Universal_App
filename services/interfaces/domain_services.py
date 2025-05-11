"""
Domain Service Interface module.
Defines the protocols for domain-specific services.
"""
from typing import Protocol, Any, Optional, Dict, List, Union
import pandas as pd


class ActuarialServiceInterface(Protocol):
    """
    Protocol defining the interface for actuarial services.
    """
    
    def is_r_available(self) -> bool:
        """
        Check if R integration is available.
        
        Returns:
            bool: True if R is available, False otherwise
        """
        ...
    
    def calculate_mortality_data(self, age_from: int, age_to: int, 
                                interest_rate: float, table_type: str, 
                                gender: str) -> Optional[pd.DataFrame]:
        """
        Calculate mortality data using R.
        
        Args:
            age_from: Starting age
            age_to: Ending age
            interest_rate: Annual interest rate as a decimal
            table_type: Type of mortality table to use
            gender: Gender to use (male, female, unisex)
            
        Returns:
            pd.DataFrame: DataFrame with mortality data, or None if calculation failed
        """
        ...
    
    def calculate_present_value(self, age: int, payment: float, interest_rate: float,
                               term: int, frequency: str, table_type: str, 
                               gender: str) -> Optional[Dict[str, float]]:
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
            Dict: Dictionary with present value calculation results
        """
        ...


class KaggleServiceInterface(Protocol):
    """
    Protocol defining the interface for Kaggle services.
    """
    
    def check_api_credentials(self) -> bool:
        """
        Check if Kaggle API credentials are properly configured.
        
        Returns:
            bool: True if credentials are found, False otherwise
        """
        ...
    
    def setup_credentials(self, username: str, key: str) -> bool:
        """
        Set up Kaggle API credentials.
        
        Args:
            username: Kaggle username
            key: Kaggle API key
        
        Returns:
            bool: True if successful, False otherwise
        """
        ...
    
    def get_dataset_list(self, search_term: str = '', 
                         max_size_mb: Optional[int] = None, 
                         file_type: Optional[str] = None, 
                         user: Optional[str] = None, 
                         max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch a list of datasets from Kaggle matching the search criteria.

        Args:
            search_term: Search term to filter datasets
            max_size_mb: Maximum dataset size in MB
            file_type: Filter by file type (csv, sqlite, json, etc.)
            user: Filter by a specific Kaggle user
            max_results: Maximum number of results to return

        Returns:
            list: List of dataset metadata dictionaries
        """
        ...
    
    def download_dataset_file(self, dataset_ref: str, filename: str, 
                             output_dir: Optional[str] = None) -> Optional[str]:
        """
        Download a specific file from a Kaggle dataset.

        Args:
            dataset_ref: Dataset reference in the format 'owner/dataset-name'
            filename: File to download from the dataset
            output_dir: Directory to save the file to. If None, uses a temp dir.

        Returns:
            str: Path to the downloaded file, or None if download failed
        """
        ...
    
    def get_dataset_files(self, dataset_ref: str) -> List[Dict[str, Any]]:
        """
        Get list of files in a Kaggle dataset.

        Args:
            dataset_ref: Dataset reference in the format 'owner/dataset-name'

        Returns:
            list: List of file information dictionaries
        """
        ...
    
    def load_dataset_to_dataframe(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load a downloaded dataset file into a pandas DataFrame.

        Args:
            file_path: Path to the dataset file

        Returns:
            pandas.DataFrame: Loaded dataframe, or None if loading failed
        """
        ...
    
    def search_datasets_async(self, callback, search_term='', max_size_mb=None, 
                             file_type=None, max_results=20):
        """
        Asynchronously search for Kaggle datasets.
        
        Args:
            callback: Function to call with results
            search_term: Search term to filter datasets
            max_size_mb: Maximum dataset size in MB
            file_type: Filter by file type
            max_results: Maximum number of results to return
        """
        ...
    
    def get_dataset_files_async(self, callback, dataset_ref):
        """
        Asynchronously get files for a Kaggle dataset.
        
        Args:
            callback: Function to call with results
            dataset_ref: Dataset reference
        """
        ...
    
    def download_and_load_file_async(self, callback, dataset_ref, filename, output_dir=None):
        """
        Asynchronously download and load a file into a DataFrame.
        
        Args:
            callback: Function to call with the DataFrame
            dataset_ref: Dataset reference
            filename: File to download
            output_dir: Directory to save file to
        """
        ...