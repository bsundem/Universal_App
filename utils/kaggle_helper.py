"""
Utility functions for interacting with the Kaggle API.
"""
import os
import json
import tempfile
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi


def check_api_credentials():
    """
    Check if Kaggle API credentials are properly configured.
    
    Returns:
        bool: True if credentials are found, False otherwise
    """
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


def setup_credentials(username, key):
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


def get_dataset_list(search_term='', max_size_mb=None, file_type=None, user=None, max_results=20):
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
    try:
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


def download_dataset_file(dataset_ref, filename, output_dir=None):
    """
    Download a specific file from a Kaggle dataset.
    
    Args:
        dataset_ref (str): Dataset reference in the format 'owner/dataset-name'
        filename (str): File to download from the dataset
        output_dir (str, optional): Directory to save the file to. If None, uses a temp dir.
        
    Returns:
        str: Path to the downloaded file, or None if download failed
    """
    try:
        api = KaggleApi()
        api.authenticate()
        
        # Create temp directory if output_dir not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
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


def get_dataset_files(dataset_ref):
    """
    Get list of files in a Kaggle dataset.
    
    Args:
        dataset_ref (str): Dataset reference in the format 'owner/dataset-name'
        
    Returns:
        list: List of file information dictionaries
    """
    try:
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


def load_dataset_to_dataframe(file_path):
    """
    Load a downloaded dataset file into a pandas DataFrame.
    Supports CSV, Excel, JSON, and parquet formats.
    
    Args:
        file_path (str): Path to the dataset file
        
    Returns:
        pandas.DataFrame: Loaded dataframe, or None if loading failed
    """
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