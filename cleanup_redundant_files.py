#!/usr/bin/env python3
"""
Cleanup script for removing redundant files after plugin conversion.

This script will create a backup of files before removing them and
will log the operations performed.
"""
import os
import shutil
import logging
import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"cleanup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Files to be removed
REDUNDANT_FILES = [
    "services/r_service.py",
    "services/actuarial/actuarial_service.py",
    "services/finance/finance_service.py",
    "services/actuarial/__init__.py",
    "services/finance/__init__.py"
]

# Create backup directory
def create_backup_dir():
    """Create a backup directory for redundant files"""
    backup_dir = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def backup_file(file_path, backup_dir):
    """Backup a file to the backup directory"""
    if not os.path.exists(file_path):
        logger.warning(f"File does not exist: {file_path}")
        return False
    
    # Create directory structure in backup dir
    backup_path = os.path.join(backup_dir, file_path)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    # Copy file to backup
    shutil.copy2(file_path, backup_path)
    logger.info(f"Backed up: {file_path} -> {backup_path}")
    return True

def remove_file(file_path):
    """Remove a file"""
    if not os.path.exists(file_path):
        logger.warning(f"File does not exist: {file_path}")
        return False
    
    os.remove(file_path)
    logger.info(f"Removed: {file_path}")
    return True

def main():
    """Main function"""
    logger.info("Starting cleanup of redundant files")
    
    # Get confirmation
    confirm = input("This will remove redundant files after plugin conversion. Continue? (y/n): ")
    if confirm.lower() not in ['y', 'yes']:
        logger.info("Cleanup cancelled")
        return
    
    # Create backup directory
    backup_dir = create_backup_dir()
    logger.info(f"Created backup directory: {backup_dir}")
    
    # Backup and remove files
    for file_path in REDUNDANT_FILES:
        if backup_file(file_path, backup_dir):
            remove_file(file_path)
    
    # Check for empty directories to remove
    dirs_to_check = [
        "services/actuarial",
        "services/finance"
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path) and not os.listdir(dir_path):
            # Empty dir, remove it after backing up
            if os.path.exists(os.path.join(dir_path, "__init__.py")):
                backup_file(os.path.join(dir_path, "__init__.py"), backup_dir)
            
            shutil.rmtree(dir_path)
            logger.info(f"Removed empty directory: {dir_path}")
    
    logger.info("Cleanup completed successfully")
    print(f"Backup created in: {backup_dir}")
    print("Cleanup completed successfully")

if __name__ == "__main__":
    main()