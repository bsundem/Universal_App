"""
Data management service for Kaggle datasets.
Handles data transformations, visualizations, and exports.
"""
import os
import importlib.util
from typing import Optional, Dict, Any, List, Tuple, Union

# Check if pandas is available
try:
    import pandas as pd
except ImportError:
    pd = None

# Check if numpy is available
try:
    import numpy as np
except ImportError:
    np = None


class KaggleDataManager:
    """
    Service for managing Kaggle dataset data operations.
    Handles data transformations, statistical operations, and export functionality.
    """

    def __init__(self):
        """Initialize the KaggleDataManager."""
        # Feature flags for checking available dependencies
        self.pandas_available = pd is not None
        self.numpy_available = np is not None

    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check the availability of required dependencies.

        Returns:
            Dict[str, bool]: Dictionary with dependency availability status
        """
        # Check for matplotlib without importing
        matplotlib_available = importlib.util.find_spec("matplotlib") is not None
        
        return {
            "pandas": self.pandas_available,
            "numpy": self.numpy_available,
            "matplotlib": matplotlib_available
        }

    def get_dataframe_info(self, df: Any) -> Dict[str, Any]:
        """
        Get information about a pandas DataFrame.

        Args:
            df: Pandas DataFrame

        Returns:
            Dict[str, Any]: Dictionary with DataFrame information
        """
        if not self.pandas_available or df is None:
            return {"error": "Pandas is not available or DataFrame is None"}

        try:
            # Extract basic information
            info = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "dtypes": {col: str(df[col].dtype) for col in df.columns},
                "missing_values": df.isnull().sum().to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum() / (1024 * 1024)  # in MB
            }

            # Add basic statistics for numeric columns
            numeric_stats = {}
            for col in df.select_dtypes(include=['number']).columns:
                numeric_stats[col] = {
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std()
                }
            info["numeric_stats"] = numeric_stats

            # Add value counts for categorical columns (limited to top 10)
            categorical_stats = {}
            for col in df.select_dtypes(exclude=['number']).columns:
                categorical_stats[col] = df[col].value_counts().head(10).to_dict()
            info["categorical_stats"] = categorical_stats

            return info
        except Exception as e:
            return {"error": f"Error getting DataFrame info: {str(e)}"}

    def prepare_histogram_data(self, df: Any, column: str, bins: int = 30) -> Dict[str, Any]:
        """
        Prepare data for histogram visualization.

        Args:
            df: Pandas DataFrame
            column: Column name to create histogram for
            bins: Number of bins for the histogram

        Returns:
            Dict[str, Any]: Histogram data ready for visualization
        """
        if not self.pandas_available or df is None:
            return {"error": "Pandas is not available or DataFrame is None"}

        try:
            if column not in df.columns:
                return {"error": f"Column '{column}' not found in DataFrame"}

            if not pd.api.types.is_numeric_dtype(df[column]):
                return {"error": "Histogram requires numeric data"}

            # Calculate histogram data
            hist_data = np.histogram(df[column].dropna(), bins=bins)
            
            # Convert to serializable format
            hist_result = {
                "counts": hist_data[0].tolist(),
                "bin_edges": hist_data[1].tolist(),
                "bin_centers": [(hist_data[1][i] + hist_data[1][i+1]) / 2 for i in range(len(hist_data[1])-1)],
                "stats": {
                    "min": float(df[column].min()),
                    "max": float(df[column].max()),
                    "mean": float(df[column].mean()),
                    "median": float(df[column].median()),
                    "std": float(df[column].std())
                }
            }
            
            return {
                "type": "histogram", 
                "data": hist_result,
                "column": column
            }
        except Exception as e:
            return {"error": f"Error preparing histogram data: {str(e)}"}

    def prepare_bar_chart_data(self, df: Any, column: str, top_n: int = 20) -> Dict[str, Any]:
        """
        Prepare data for bar chart visualization.

        Args:
            df: Pandas DataFrame
            column: Column name to create bar chart for
            top_n: Number of top categories to include (for categorical data)

        Returns:
            Dict[str, Any]: Bar chart data ready for visualization
        """
        if not self.pandas_available or df is None:
            return {"error": "Pandas is not available or DataFrame is None"}

        try:
            if column not in df.columns:
                return {"error": f"Column '{column}' not found in DataFrame"}

            # Handle differently based on data type
            if pd.api.types.is_numeric_dtype(df[column]):
                # For numeric data, bin it first
                bins = pd.cut(df[column], bins=10)
                value_counts = bins.value_counts().sort_index()
                
                # Create result
                result = {
                    "labels": [str(x) for x in value_counts.index],
                    "values": value_counts.values.tolist(),
                    "is_numeric": True
                }
            else:
                # For categorical data
                value_counts = df[column].value_counts().head(top_n)
                
                # Create result
                result = {
                    "labels": [str(x) for x in value_counts.index],
                    "values": value_counts.values.tolist(),
                    "is_numeric": False
                }
            
            return {
                "type": "bar_chart",
                "data": result,
                "column": column
            }
        except Exception as e:
            return {"error": f"Error preparing bar chart data: {str(e)}"}

    def prepare_scatter_plot_data(self, df: Any, x_column: str, y_column: str, 
                                 sample_size: int = 1000) -> Dict[str, Any]:
        """
        Prepare data for scatter plot visualization.

        Args:
            df: Pandas DataFrame
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            sample_size: Maximum number of points to include (to prevent performance issues)

        Returns:
            Dict[str, Any]: Scatter plot data ready for visualization
        """
        if not self.pandas_available or df is None:
            return {"error": "Pandas is not available or DataFrame is None"}

        try:
            if x_column not in df.columns or y_column not in df.columns:
                return {"error": f"Columns '{x_column}' or '{y_column}' not found in DataFrame"}

            if not pd.api.types.is_numeric_dtype(df[x_column]) or not pd.api.types.is_numeric_dtype(df[y_column]):
                return {"error": "Scatter plot requires numeric data for both axes"}

            # Get data, potentially sampling to limit point count
            working_df = df[[x_column, y_column]].dropna()
            if len(working_df) > sample_size:
                working_df = working_df.sample(sample_size, random_state=42)
            
            # Calculate correlation
            correlation = float(working_df[x_column].corr(working_df[y_column]))
            
            # Create result
            result = {
                "x": working_df[x_column].tolist(),
                "y": working_df[y_column].tolist(),
                "correlation": correlation,
                "x_stats": {
                    "min": float(working_df[x_column].min()),
                    "max": float(working_df[x_column].max()),
                    "mean": float(working_df[x_column].mean())
                },
                "y_stats": {
                    "min": float(working_df[y_column].min()),
                    "max": float(working_df[y_column].max()),
                    "mean": float(working_df[y_column].mean())
                }
            }
            
            return {
                "type": "scatter_plot",
                "data": result,
                "x_column": x_column,
                "y_column": y_column
            }
        except Exception as e:
            return {"error": f"Error preparing scatter plot data: {str(e)}"}

    def prepare_line_chart_data(self, df: Any, x_column: str, y_column: str) -> Dict[str, Any]:
        """
        Prepare data for line chart visualization.

        Args:
            df: Pandas DataFrame
            x_column: Column name for X-axis
            y_column: Column name for Y-axis

        Returns:
            Dict[str, Any]: Line chart data ready for visualization
        """
        if not self.pandas_available or df is None:
            return {"error": "Pandas is not available or DataFrame is None"}

        try:
            if x_column not in df.columns or y_column not in df.columns:
                return {"error": f"Columns '{x_column}' or '{y_column}' not found in DataFrame"}

            if not pd.api.types.is_numeric_dtype(df[y_column]):
                return {"error": "Line chart requires numeric data for Y-axis"}

            # Handle differently based on x-axis data type
            if pd.api.types.is_numeric_dtype(df[x_column]):
                # For numeric x-axis, sort values
                plot_df = df.sort_values(by=x_column)
                result = {
                    "x": plot_df[x_column].tolist(),
                    "y": plot_df[y_column].tolist(),
                    "x_is_numeric": True
                }
            else:
                # For categorical x-axis
                categories = df[x_column].unique()
                category_means = [df[df[x_column] == cat][y_column].mean() for cat in categories]
                result = {
                    "x": [str(cat) for cat in categories],
                    "y": [float(mean) for mean in category_means],
                    "x_is_numeric": False
                }
            
            return {
                "type": "line_chart",
                "data": result,
                "x_column": x_column,
                "y_column": y_column
            }
        except Exception as e:
            return {"error": f"Error preparing line chart data: {str(e)}"}

    def prepare_box_plot_data(self, df: Any, column: str) -> Dict[str, Any]:
        """
        Prepare data for box plot visualization.

        Args:
            df: Pandas DataFrame
            column: Column name to create box plot for

        Returns:
            Dict[str, Any]: Box plot data ready for visualization
        """
        if not self.pandas_available or df is None:
            return {"error": "Pandas is not available or DataFrame is None"}

        try:
            if column not in df.columns:
                return {"error": f"Column '{column}' not found in DataFrame"}

            if not pd.api.types.is_numeric_dtype(df[column]):
                return {"error": "Box plot requires numeric data"}

            # Calculate box plot statistics
            data = df[column].dropna()
            q1 = float(data.quantile(0.25))
            q2 = float(data.median())
            q3 = float(data.quantile(0.75))
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Find outliers
            outliers = data[(data < lower_bound) | (data > upper_bound)].tolist()
            
            # Create result
            result = {
                "min": float(data.min()),
                "q1": q1,
                "median": q2,
                "q3": q3,
                "max": float(data.max()),
                "whisker_low": float(max(lower_bound, data.min())),
                "whisker_high": float(min(upper_bound, data.max())),
                "outliers": outliers[:100] if len(outliers) > 100 else outliers  # Limit outliers
            }
            
            return {
                "type": "box_plot",
                "data": result,
                "column": column
            }
        except Exception as e:
            return {"error": f"Error preparing box plot data: {str(e)}"}

    def generate_plot_data(self, df: Any, chart_type: str, x_column: str, 
                          y_column: Optional[str] = None, **kwargs) -> Dict[str, Any]:
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
        if not self.pandas_available or df is None:
            return {"error": "Pandas is not available or DataFrame is None"}

        chart_type = chart_type.lower()
        
        try:
            if chart_type == 'histogram':
                return self.prepare_histogram_data(df, x_column, bins=kwargs.get('bins', 30))
            elif chart_type == 'bar chart':
                return self.prepare_bar_chart_data(df, x_column, top_n=kwargs.get('top_n', 20))
            elif chart_type == 'scatter plot':
                if not y_column:
                    return {"error": "Scatter plot requires both X and Y columns"}
                return self.prepare_scatter_plot_data(
                    df, x_column, y_column, sample_size=kwargs.get('sample_size', 1000)
                )
            elif chart_type == 'line chart':
                if not y_column:
                    return {"error": "Line chart requires both X and Y columns"}
                return self.prepare_line_chart_data(df, x_column, y_column)
            elif chart_type == 'box plot':
                return self.prepare_box_plot_data(df, x_column)
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
        except Exception as e:
            return {"error": f"Error generating plot data: {str(e)}"}

    def export_dataframe(self, df: Any, file_path: str, format: Optional[str] = None) -> Dict[str, Any]:
        """
        Export DataFrame to a file in the specified format.

        Args:
            df: Pandas DataFrame
            file_path: Path to save the file
            format: Export format (csv, excel, json). If None, determined from file extension.

        Returns:
            Dict[str, Any]: Result of the export operation
        """
        if not self.pandas_available or df is None:
            return {"success": False, "error": "Pandas is not available or DataFrame is None"}

        try:
            # Determine format from file extension if not specified
            if not format:
                file_lower = file_path.lower()
                if file_lower.endswith('.csv'):
                    format = 'csv'
                elif file_lower.endswith(('.xlsx', '.xls')):
                    format = 'excel'
                elif file_lower.endswith('.json'):
                    format = 'json'
                else:
                    format = 'csv'  # Default to CSV

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Export based on format
            if format.lower() == 'csv':
                df.to_csv(file_path, index=False)
            elif format.lower() == 'excel':
                df.to_excel(file_path, index=False)
            elif format.lower() == 'json':
                df.to_json(file_path, orient='records')
            else:
                return {"success": False, "error": f"Unsupported export format: {format}"}
            
            return {
                "success": True, 
                "file_path": file_path,
                "format": format,
                "rows": len(df),
                "columns": len(df.columns)
            }
        except Exception as e:
            return {"success": False, "error": f"Error exporting data: {str(e)}"}

    def filter_dataframe(self, df: Any, filters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Filter DataFrame based on column conditions.

        Args:
            df: Pandas DataFrame
            filters: Dictionary mapping column names to filter conditions
                Each filter condition is a dict with operator and value keys
                Example: {'age': {'operator': '>', 'value': 30}}

        Returns:
            Dict[str, Any]: Filtered DataFrame result
        """
        if not self.pandas_available or df is None:
            return {"success": False, "error": "Pandas is not available or DataFrame is None"}

        try:
            result_df = df.copy()
            applied_filters = []
            
            for column, condition in filters.items():
                if column not in df.columns:
                    return {"success": False, "error": f"Column '{column}' not found in DataFrame"}
                
                operator = condition.get('operator', '==')
                value = condition.get('value')
                
                if value is None:
                    continue
                
                # Apply filter based on operator
                if operator == '==':
                    result_df = result_df[result_df[column] == value]
                elif operator == '!=':
                    result_df = result_df[result_df[column] != value]
                elif operator == '>':
                    result_df = result_df[result_df[column] > value]
                elif operator == '>=':
                    result_df = result_df[result_df[column] >= value]
                elif operator == '<':
                    result_df = result_df[result_df[column] < value]
                elif operator == '<=':
                    result_df = result_df[result_df[column] <= value]
                elif operator == 'contains':
                    result_df = result_df[result_df[column].astype(str).str.contains(str(value), na=False)]
                elif operator == 'starts_with':
                    result_df = result_df[result_df[column].astype(str).str.startswith(str(value), na=False)]
                elif operator == 'ends_with':
                    result_df = result_df[result_df[column].astype(str).str.endswith(str(value), na=False)]
                else:
                    return {"success": False, "error": f"Unsupported operator: {operator}"}
                
                applied_filters.append(f"{column} {operator} {value}")
            
            return {
                "success": True,
                "data": result_df,
                "original_rows": len(df),
                "filtered_rows": len(result_df),
                "applied_filters": applied_filters
            }
        except Exception as e:
            return {"success": False, "error": f"Error filtering data: {str(e)}"}

    def get_column_summary(self, df: Any, column: str) -> Dict[str, Any]:
        """
        Get detailed summary statistics for a specific column.

        Args:
            df: Pandas DataFrame
            column: Column name to get summary for

        Returns:
            Dict[str, Any]: Column summary information
        """
        if not self.pandas_available or df is None:
            return {"success": False, "error": "Pandas is not available or DataFrame is None"}

        try:
            if column not in df.columns:
                return {"success": False, "error": f"Column '{column}' not found in DataFrame"}
            
            col_data = df[column]
            summary = {
                "name": column,
                "dtype": str(col_data.dtype),
                "count": int(col_data.count()),
                "missing": int(col_data.isnull().sum()),
                "missing_pct": float(col_data.isnull().mean() * 100),
                "unique_values": int(col_data.nunique())
            }
            
            # Add type-specific statistics
            if pd.api.types.is_numeric_dtype(col_data):
                # Numeric column
                summary.update({
                    "type": "numeric",
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "skew": float(col_data.skew()),
                    "kurtosis": float(col_data.kurtosis()),
                    "quantiles": {
                        "25%": float(col_data.quantile(0.25)),
                        "50%": float(col_data.median()),
                        "75%": float(col_data.quantile(0.75)),
                        "90%": float(col_data.quantile(0.90)),
                        "95%": float(col_data.quantile(0.95)),
                        "99%": float(col_data.quantile(0.99))
                    }
                })
            else:
                # Categorical/string column
                value_counts = col_data.value_counts()
                summary.update({
                    "type": "categorical",
                    "top_values": {
                        str(val): int(count) 
                        for val, count in value_counts.head(10).items()
                    },
                    "top_frequency": float(value_counts.iloc[0] / col_data.count() * 100) if not value_counts.empty else 0,
                })
                
                # Add string-specific metrics if it's a string column
                if pd.api.types.is_string_dtype(col_data) or pd.api.types.is_object_dtype(col_data):
                    # Calculate length statistics on non-null values
                    clean_data = col_data.dropna()
                    if len(clean_data) > 0:
                        # Get string lengths
                        str_lengths = clean_data.astype(str).str.len()
                        summary.update({
                            "length_stats": {
                                "min_length": int(str_lengths.min()),
                                "max_length": int(str_lengths.max()),
                                "mean_length": float(str_lengths.mean())
                            }
                        })
            
            return {"success": True, "summary": summary}
        except Exception as e:
            return {"success": False, "error": f"Error getting column summary: {str(e)}"}


# Export a singleton instance that can be imported directly
kaggle_data_manager = KaggleDataManager()