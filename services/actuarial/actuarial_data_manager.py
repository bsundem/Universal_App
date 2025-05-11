"""
Actuarial Data Manager module.

This module provides a data management layer for actuarial calculations,
handling data transformations, visualizations, and file exports while
keeping business logic separate from UI components.
"""
import os
import tempfile
import importlib.util
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
import datetime

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

# Check for matplotlib
if importlib.util.find_spec("matplotlib") is not None:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
else:
    matplotlib = None
    plt = None
    Figure = None


class ActuarialDataManager:
    """
    Manages actuarial data transformations, visualizations, and exports.
    
    This class handles all data-specific operations for actuarial calculations,
    separating data logic from both business logic and UI components.
    """
    
    def __init__(self):
        """Initialize the actuarial data manager."""
        self.temp_dir = tempfile.mkdtemp()
    
    def prepare_mortality_data_for_visualization(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Prepare mortality data for visualization.
        
        Args:
            df (pd.DataFrame): DataFrame containing mortality data
            
        Returns:
            Dict[str, Any]: Dictionary with prepared data for plotting
            
        Raises:
            ValueError: If DataFrame is None or empty
            ImportError: If required libraries are not available
        """
        if df is None or df.empty:
            raise ValueError("Mortality data is empty or None")
            
        if pd is None:
            raise ImportError("pandas is required for data preparation")
        
        # Extract relevant columns for visualization
        try:
            visualization_data = {
                'ages': df['Age'].values,
                'mortality_rates': df['qx'].values,
                'life_expectancy': df['ex'].values,
                'ax_values': df['ax'].values if 'ax' in df.columns else None,
                'stats': {
                    'min_age': df['Age'].min(),
                    'max_age': df['Age'].max(),
                    'avg_mortality': df['qx'].mean(),
                    'avg_life_expectancy': df['ex'].mean()
                }
            }
            return visualization_data
        except KeyError as e:
            raise KeyError(f"Missing required column in mortality data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error preparing mortality data: {str(e)}")
    
    def prepare_pv_data_for_visualization(self, pv_results: Dict[str, float], 
                                          params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare present value data for visualization and display.
        
        Args:
            pv_results (Dict[str, float]): Results from present value calculation
            params (Dict[str, Any]): Parameters used for calculation
            
        Returns:
            Dict[str, Any]: Dictionary with formatted data for display
            
        Raises:
            ValueError: If results or params are None
        """
        if pv_results is None:
            raise ValueError("Present value results are None")
            
        if params is None:
            raise ValueError("Parameters are None")
            
        # Format currency values
        formatted_results = {
            'present_value': f"${pv_results.get('present_value', 0):,.2f}",
            'expected_duration': f"{pv_results.get('expected_duration', 0):.2f} years",
            'monthly_equivalent': f"${pv_results.get('monthly_equivalent', 0):,.2f} / month",
            'summary': (
                f"Present Value: ${pv_results.get('present_value', 0):,.2f}\n\n"
                f"This represents the lump sum amount needed today to fund "
                f"the specified stream of payments.\n\n"
                f"Based on a {params.get('frequency', 'annual').lower()} payment of "
                f"${params.get('payment', 0):,.2f} for {params.get('term', 0)} years or life, "
                f"using an interest rate of {params.get('interest_rate', 0)*100:.2f}%.\n\n"
                f"The expected duration of payments is {pv_results.get('expected_duration', 0):.2f} years."
            )
        }
        
        return formatted_results
    
    def create_mortality_visualization(self, data: Dict[str, Any]) -> Optional[Figure]:
        """
        Create a visualization figure for mortality data without displaying it.
        
        Args:
            data (Dict[str, Any]): Prepared data from prepare_mortality_data_for_visualization
            
        Returns:
            Optional[Figure]: Matplotlib figure object or None if visualization not possible
            
        Raises:
            ImportError: If matplotlib is not available
        """
        if matplotlib is None or plt is None:
            raise ImportError("matplotlib is required for visualization")
            
        try:
            # Create a new figure with two subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), 
                                          gridspec_kw={'height_ratios': [1, 1]})
            
            # Plot mortality rates
            ax1.plot(data['ages'], data['mortality_rates'], 'b-', 
                    label='Mortality Rate (qx)')
            ax1.set_title('Mortality Rates by Age')
            ax1.set_xlabel('Age')
            ax1.set_ylabel('Rate')
            ax1.legend()
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            # Plot life expectancy
            ax2.plot(data['ages'], data['life_expectancy'], 'r-', 
                    label='Life Expectancy (ex)')
            ax2.set_title('Life Expectancy by Age')
            ax2.set_xlabel('Age')
            ax2.set_ylabel('Years')
            ax2.legend()
            ax2.grid(True, linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            
            return fig
        except Exception as e:
            print(f"Error creating mortality visualization: {str(e)}")
            return None
    
    def export_mortality_data_to_csv(self, df: pd.DataFrame, 
                                     file_path: Optional[str] = None) -> str:
        """
        Export mortality data to a CSV file.
        
        Args:
            df (pd.DataFrame): DataFrame containing mortality data
            file_path (Optional[str]): Path to save the file, or None to use a temp file
            
        Returns:
            str: Path to the exported file
            
        Raises:
            ValueError: If DataFrame is None or empty
            ImportError: If pandas is not available
        """
        if pd is None:
            raise ImportError("pandas is required for CSV export")
            
        if df is None or df.empty:
            raise ValueError("Cannot export empty DataFrame")
            
        try:
            # Generate a temp file name if not provided
            if file_path is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(
                    self.temp_dir, 
                    f"mortality_data_{timestamp}.csv"
                )
                
            # Export to CSV
            df.to_csv(file_path, index=False)
            return file_path
        except Exception as e:
            raise Exception(f"Error exporting mortality data: {str(e)}")
    
    def export_mortality_data_to_excel(self, df: pd.DataFrame, 
                                      file_path: Optional[str] = None) -> str:
        """
        Export mortality data to an Excel file.
        
        Args:
            df (pd.DataFrame): DataFrame containing mortality data
            file_path (Optional[str]): Path to save the file, or None to use a temp file
            
        Returns:
            str: Path to the exported file
            
        Raises:
            ValueError: If DataFrame is None or empty
            ImportError: If pandas or openpyxl are not available
        """
        if pd is None:
            raise ImportError("pandas is required for Excel export")
            
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl is required for Excel export")
            
        if df is None or df.empty:
            raise ValueError("Cannot export empty DataFrame")
            
        try:
            # Generate a temp file name if not provided
            if file_path is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(
                    self.temp_dir, 
                    f"mortality_data_{timestamp}.xlsx"
                )
                
            # Export to Excel
            df.to_excel(file_path, index=False, sheet_name="Mortality Data")
            
            return file_path
        except Exception as e:
            raise Exception(f"Error exporting mortality data: {str(e)}")
    
    def export_mortality_data_to_json(self, df: pd.DataFrame, 
                                     file_path: Optional[str] = None) -> str:
        """
        Export mortality data to a JSON file.
        
        Args:
            df (pd.DataFrame): DataFrame containing mortality data
            file_path (Optional[str]): Path to save the file, or None to use a temp file
            
        Returns:
            str: Path to the exported file
            
        Raises:
            ValueError: If DataFrame is None or empty
            ImportError: If pandas is not available
        """
        if pd is None:
            raise ImportError("pandas is required for JSON export")
            
        if df is None or df.empty:
            raise ValueError("Cannot export empty DataFrame")
            
        try:
            # Generate a temp file name if not provided
            if file_path is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(
                    self.temp_dir, 
                    f"mortality_data_{timestamp}.json"
                )
                
            # Export to JSON
            df.to_json(file_path, orient="records", indent=4)
            
            return file_path
        except Exception as e:
            raise Exception(f"Error exporting mortality data: {str(e)}")
    
    def get_formatted_mortality_summary(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Generate a formatted summary of mortality data.
        
        Args:
            df (pd.DataFrame): DataFrame containing mortality data
            
        Returns:
            Dict[str, str]: Dictionary with formatted summary statistics
            
        Raises:
            ValueError: If DataFrame is None or empty
        """
        if df is None or df.empty:
            raise ValueError("Cannot summarize empty DataFrame")
            
        try:
            summary = {
                "age_range": f"{df['Age'].min()} - {df['Age'].max()}",
                "average_mortality": f"{df['qx'].mean():.4f}",
                "median_mortality": f"{df['qx'].median():.4f}",
                "average_life_expectancy": f"{df['ex'].mean():.2f} years",
                "life_expectancy_range": f"{df['ex'].min():.2f} - {df['ex'].max():.2f} years"
            }
            
            return summary
        except Exception as e:
            raise Exception(f"Error generating mortality summary: {str(e)}")
    
    def get_mortality_data_as_text(self, df: pd.DataFrame) -> str:
        """
        Convert mortality data to a text representation for display.
        
        Args:
            df (pd.DataFrame): DataFrame containing mortality data
            
        Returns:
            str: Text representation of the data
            
        Raises:
            ValueError: If DataFrame is None or empty
        """
        if df is None or df.empty:
            raise ValueError("Cannot format empty DataFrame")
            
        try:
            return f"Mortality Data:\n\n{df.to_string()}"
        except Exception as e:
            raise Exception(f"Error converting mortality data to text: {str(e)}")


# Export a singleton instance that can be imported directly
actuarial_data_manager = ActuarialDataManager()