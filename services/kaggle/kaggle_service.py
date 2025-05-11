"""
Kaggle service for fetching and processing Kaggle datasets.
Provides business logic separated from UI components.
"""
import os
import json
import tempfile
import importlib.util
import threading
from typing import List, Dict, Optional, Any, Tuple

# Check if pandas is available
try:
    import pandas as pd
except ImportError:
    pd = None

# Check if kaggle is installed but don't import the API directly
# to avoid immediate authentication
kaggle_available = importlib.util.find_spec("kaggle") is not None


class KaggleService:
    """Service for interacting with Kaggle API and datasets."""
    
    def __init__(self):
        """Initialize the Kaggle service."""
        self.temp_dir = tempfile.mkdtemp()
        
    def check_api_credentials(self) -> bool:
        """
        Check if Kaggle API credentials are properly configured.
        
        Returns:
            bool: True if credentials are found, False otherwise
        """
        if not kaggle_available:
            return False

        kaggle_dir = os.path.expanduser('~/.kaggle')
        kaggle_file = os.path.join(kaggle_dir, 'kaggle.json')

        if not os.path.exists(kaggle_file):
            return False

        # Check if the file has valid JSON content
        try:
            with open(kaggle_file, 'r') as f:
                creds = json.load(f)
                return 'username' in creds and 'key' in creds
        except Exception:
            return False

    def setup_credentials(self, username: str, key: str) -> bool:
        """
        Set up Kaggle API credentials.
        
        Args:
            username (str): Kaggle username
            key (str): Kaggle API key
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the .kaggle directory if it doesn't exist
            kaggle_dir = os.path.expanduser('~/.kaggle')
            os.makedirs(kaggle_dir, exist_ok=True)
            
            # Create the kaggle.json file
            kaggle_file = os.path.join(kaggle_dir, 'kaggle.json')
            with open(kaggle_file, 'w') as f:
                json.dump({'username': username, 'key': key}, f)
            
            # Set permissions to 600 to avoid warning
            os.chmod(kaggle_file, 0o600)
            
            return True
        except Exception:
            return False

    def get_dataset_list(self, search_term: str = '', 
                         max_size_mb: Optional[int] = None, 
                         file_type: Optional[str] = None, 
                         user: Optional[str] = None, 
                         max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch a list of datasets from Kaggle matching the search criteria.

        Args:
            search_term (str): Search term to filter datasets
            max_size_mb (int, optional): Maximum dataset size in MB
            file_type (str, optional): Filter by file type (csv, sqlite, json, etc.)
            user (str, optional): Filter by a specific Kaggle user
            max_results (int): Maximum number of results to return

        Returns:
            list: List of dataset metadata dictionaries
        """
        if not kaggle_available:
            print("Kaggle API not available. Please install with: pip install kaggle")
            return []

        try:
            # Import KaggleAPI only when needed
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()

            # Convert max_size to bytes for filtering
            max_size_bytes = max_size_mb * 1024 * 1024 if max_size_mb else None

            # Get datasets list
            datasets = api.dataset_list(search=search_term)

            # Apply filters
            filtered_datasets = []
            for dataset in datasets:
                # Skip if dataset is larger than max_size
                if max_size_bytes and dataset.size > max_size_bytes:
                    continue

                # Skip if user doesn't match
                if user and dataset.ownerName != user:
                    continue

                # Add dataset to filtered list
                dataset_dict = {
                    'ref': f"{dataset.ownerName}/{dataset.slug}",
                    'title': dataset.title,
                    'subtitle': dataset.subtitle,
                    'url': f"https://www.kaggle.com/datasets/{dataset.ownerName}/{dataset.slug}",
                    'lastUpdated': dataset.lastUpdated,
                    'size': dataset.size,
                    'sizeGB': round(dataset.size / (1024 * 1024 * 1024), 2),
                    'sizeMB': round(dataset.size / (1024 * 1024), 2),
                    'downloadCount': dataset.downloadCount,
                    'voteCount': dataset.voteCount,
                    'usabilityRating': dataset.usabilityRating,
                    'owner': dataset.ownerName
                }
                filtered_datasets.append(dataset_dict)

                if len(filtered_datasets) >= max_results:
                    break

            # Further filter by file type if specified
            if file_type and filtered_datasets:
                file_filtered = []
                for dataset_dict in filtered_datasets:
                    # Get file list
                    ref = dataset_dict['ref']
                    try:
                        files = api.dataset_list_files(ref).files
                        has_matching_file = any(f.name.endswith(f".{file_type}") for f in files)
                        if has_matching_file:
                            file_filtered.append(dataset_dict)
                    except Exception:
                        # Skip datasets with errors
                        continue
                return file_filtered

            return filtered_datasets
        except Exception as e:
            print(f"Error fetching datasets: {e}")
            return []

    def download_dataset_file(self, dataset_ref: str, filename: str, 
                             output_dir: Optional[str] = None) -> Optional[str]:
        """
        Download a specific file from a Kaggle dataset.

        Args:
            dataset_ref (str): Dataset reference in the format 'owner/dataset-name'
            filename (str): File to download from the dataset
            output_dir (str, optional): Directory to save the file to. If None, uses a temp dir.

        Returns:
            str: Path to the downloaded file, or None if download failed
        """
        if not kaggle_available:
            print("Kaggle API not available. Please install with: pip install kaggle")
            return None

        try:
            # Import KaggleAPI only when needed
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()

            # Create temp directory if output_dir not specified
            if output_dir is None:
                output_dir = self.temp_dir

            # Download the file
            api.dataset_download_file(dataset_ref, filename, path=output_dir, force=True)

            # Return path to the downloaded file
            file_path = os.path.join(output_dir, filename)
            if os.path.exists(file_path):
                return file_path
            return None
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None

    def get_dataset_files(self, dataset_ref: str) -> List[Dict[str, Any]]:
        """
        Get list of files in a Kaggle dataset.

        Args:
            dataset_ref (str): Dataset reference in the format 'owner/dataset-name'

        Returns:
            list: List of file information dictionaries
        """
        if not kaggle_available:
            print("Kaggle API not available. Please install with: pip install kaggle")
            return []

        try:
            # Import KaggleAPI only when needed
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()

            # Get file list
            file_list = api.dataset_list_files(dataset_ref).files

            # Convert to list of dictionaries
            result = []
            for file in file_list:
                file_info = {
                    'name': file.name,
                    'size': file.size,
                    'sizeMB': round(file.size / (1024 * 1024), 2)
                }
                result.append(file_info)

            return result
        except Exception as e:
            print(f"Error getting dataset files: {e}")
            return []

    def load_dataset_to_dataframe(self, file_path: str) -> Optional[Any]:
        """
        Load a downloaded dataset file into a pandas DataFrame.
        Supports CSV, Excel, JSON, and parquet formats.

        Args:
            file_path (str): Path to the dataset file

        Returns:
            pandas.DataFrame: Loaded dataframe, or None if loading failed
        """
        if pd is None:
            print("Pandas is not installed. Please install with: pip install pandas")
            return None

        try:
            file_lower = file_path.lower()
            if file_lower.endswith('.csv'):
                return pd.read_csv(file_path)
            elif file_lower.endswith(('.xls', '.xlsx')):
                return pd.read_excel(file_path)
            elif file_lower.endswith('.json'):
                return pd.read_json(file_path)
            elif file_lower.endswith('.parquet'):
                return pd.read_parquet(file_path)
            else:
                print(f"Unsupported file format: {file_path}")
                return None
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return None

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
        def search_thread():
            # Fetch datasets
            datasets = self.get_dataset_list(
                search_term=search_term,
                max_size_mb=max_size_mb,
                file_type=file_type,
                max_results=max_results
            )
            # Call the callback function with results
            callback(datasets)
            
        # Start search in a separate thread
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
        
    def get_dataset_files_async(self, callback, dataset_ref):
        """
        Asynchronously get files for a Kaggle dataset.
        
        Args:
            callback: Function to call with results
            dataset_ref: Dataset reference
        """
        def files_thread():
            # Fetch files
            files = self.get_dataset_files(dataset_ref)
            # Call the callback function with results
            callback(files)
            
        # Start in a separate thread
        thread = threading.Thread(target=files_thread)
        thread.daemon = True
        thread.start()
        
    def download_and_load_file_async(self, callback, dataset_ref, filename, output_dir=None):
        """
        Asynchronously download and load a file into a DataFrame.
        
        Args:
            callback: Function to call with the DataFrame
            dataset_ref: Dataset reference
            filename: File to download
            output_dir: Directory to save file to
        """
        def download_thread():
            # Download file
            file_path = self.download_dataset_file(
                dataset_ref,
                filename,
                output_dir=output_dir or self.temp_dir
            )
            
            if file_path:
                # Load into DataFrame
                df = self.load_dataset_to_dataframe(file_path)
                # Call callback with the DataFrame
                callback(df)
            else:
                # Call callback with None to indicate failure
                callback(None)
                
        # Start in a separate thread
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()


# Export a singleton instance that can be imported directly
kaggle_service = KaggleService()