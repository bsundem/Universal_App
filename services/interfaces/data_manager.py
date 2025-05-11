"""
Data Manager Interface module.
Defines the protocol for data management services.
"""
from typing import Protocol, Any, Optional, Dict, List, Union, BinaryIO
import pandas as pd


class DataManagerInterface(Protocol):
    """
    Protocol defining the base interface for data management services.
    
    This is a general interface that all data managers should implement.
    More specialized interfaces can extend this one.
    """
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check the availability of required dependencies.
        
        Returns:
            Dict[str, bool]: Dictionary with dependency availability status
        """
        ...
    
    def export_dataframe(self, df: pd.DataFrame, file_path: str, 
                         format: Optional[str] = None) -> Dict[str, Any]:
        """
        Export DataFrame to a file in the specified format.
        
        Args:
            df: Pandas DataFrame
            file_path: Path to save the file
            format: Export format (csv, excel, json). If None, determined from file extension.
            
        Returns:
            Dict[str, Any]: Result of the export operation
        """
        ...


class VisualizationManagerInterface(Protocol):
    """
    Protocol defining the interface for visualization data preparation.
    
    This interface defines methods for preparing data for visualization.
    """
    
    def prepare_data_for_visualization(self, data: Any) -> Dict[str, Any]:
        """
        Prepare data for visualization.
        
        Args:
            data: Data to prepare for visualization
            
        Returns:
            Dict[str, Any]: Prepared data for visualization
        """
        ...


class ActuarialDataManagerInterface(Protocol):
    """
    Protocol defining the interface for actuarial data management.
    """
    
    def prepare_mortality_data_for_visualization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Prepare mortality data for visualization.
        
        Args:
            df: DataFrame containing mortality data
            
        Returns:
            Dict[str, Any]: Prepared data for visualization
        """
        ...
    
    def prepare_pv_data_for_visualization(self, pv_results: Dict[str, float], 
                                         params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare present value data for visualization.
        
        Args:
            pv_results: Results from present value calculation
            params: Parameters used for calculation
            
        Returns:
            Dict[str, Any]: Formatted data for display
        """
        ...
    
    def export_mortality_data_to_csv(self, df: pd.DataFrame, 
                                    file_path: Optional[str] = None) -> str:
        """
        Export mortality data to CSV.
        
        Args:
            df: DataFrame with mortality data
            file_path: Path to save the file, or None to use a temp file
            
        Returns:
            str: Path to the exported file
        """
        ...


class KaggleDataManagerInterface(Protocol):
    """
    Protocol defining the interface for Kaggle data management.
    """
    
    def get_dataframe_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get information about a pandas DataFrame.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dict[str, Any]: Dictionary with DataFrame information
        """
        ...
    
    def generate_plot_data(self, df: pd.DataFrame, chart_type: str, 
                          x_column: str, y_column: Optional[str] = None, 
                          **kwargs) -> Dict[str, Any]:
        """
        Generate plot data based on the selected chart type.
        
        Args:
            df: Pandas DataFrame
            chart_type: Type of chart to generate
            x_column: Column name for X-axis or primary data column
            y_column: Column name for Y-axis (for applicable chart types)
            **kwargs: Additional parameters for specific chart types
            
        Returns:
            Dict[str, Any]: Chart data ready for visualization
        """
        ...
    
    def filter_dataframe(self, df: pd.DataFrame, 
                        filters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Filter DataFrame based on column conditions.
        
        Args:
            df: Pandas DataFrame
            filters: Dictionary mapping column names to filter conditions
                
        Returns:
            Dict[str, Any]: Filtered DataFrame result
        """
        ...