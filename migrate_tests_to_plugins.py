#!/usr/bin/env python3
"""
Test migration script for helping to update test files to use the plugin system.

This script scans test files for imports of the old service classes
and provides recommendations on how to update them to use plugins.
"""
import os
import re
import glob
import logging
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"test_migration_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Patterns to search for
IMPORT_PATTERNS = [
    r"from services\.r_service import .*",
    r"from services\.actuarial\.actuarial_service import .*",
    r"from services\.finance\.finance_service import .*",
    r"import services\.r_service.*",
    r"import services\.actuarial\.actuarial_service.*",
    r"import services\.finance\.finance_service.*"
]

# Service classes to check for
SERVICE_CLASSES = [
    "RService",
    "ActuarialService",
    "FinanceService"
]

def find_test_files():
    """Find all test files in the test directory"""
    return glob.glob("tests/**/*.py", recursive=True)

def scan_file(file_path):
    """
    Scan a file for old service imports and usage
    
    Returns:
        dict: Information about the file including imports found and usage
    """
    with open(file_path, "r") as f:
        content = f.read()
    
    # Check for imports
    imports_found = []
    for pattern in IMPORT_PATTERNS:
        matches = re.findall(pattern, content)
        imports_found.extend(matches)
    
    # Check for service class usage
    class_usage = {}
    for service_class in SERVICE_CLASSES:
        pattern = r"\b" + service_class + r"\b"
        matches = re.findall(pattern, content)
        if matches:
            class_usage[service_class] = len(matches)
    
    # Look for mocking or override patterns
    mocking_patterns = [
        r"mock\s*\.\s*patch",
        r"override_provider",
        r"\.return_value",
        r"MagicMock",
        r"Mock\s*\("
    ]
    
    mocking_used = False
    for pattern in mocking_patterns:
        if re.search(pattern, content):
            mocking_used = True
            break
    
    return {
        "file_path": file_path,
        "imports_found": imports_found,
        "class_usage": class_usage,
        "mocking_used": mocking_used
    }

def generate_recommendations(file_info):
    """
    Generate recommendations for updating the file
    
    Args:
        file_info: Information about the file
        
    Returns:
        str: Recommendations for updating the file
    """
    recommendations = []
    
    if file_info["imports_found"]:
        recommendations.append("Update imports:")
        for old_import in file_info["imports_found"]:
            if "RService" in old_import:
                recommendations.append(f"  - Replace: {old_import}")
                recommendations.append("    With: from services.plugins.r_service_plugin import RServicePlugin")
            elif "ActuarialService" in old_import:
                recommendations.append(f"  - Replace: {old_import}")
                recommendations.append("    With: from services.plugins.actuarial_service_plugin import ActuarialServicePlugin")
            elif "FinanceService" in old_import:
                recommendations.append(f"  - Replace: {old_import}")
                recommendations.append("    With: from services.plugins.finance_service_plugin import FinanceServicePlugin")
    
    if file_info["class_usage"]:
        recommendations.append("Update class references:")
        for service_class, count in file_info["class_usage"].items():
            if service_class == "RService":
                recommendations.append(f"  - Replace {count} occurrences of {service_class} with RServicePlugin")
            elif service_class == "ActuarialService":
                recommendations.append(f"  - Replace {count} occurrences of {service_class} with ActuarialServicePlugin")
            elif service_class == "FinanceService":
                recommendations.append(f"  - Replace {count} occurrences of {service_class} with FinanceServicePlugin")
    
    if file_info["mocking_used"]:
        recommendations.append("Update mocking strategy:")
        recommendations.append("  - Update mock patches to target plugin classes instead of traditional services")
        recommendations.append("  - Update any container overrides to use plugin versions")
        recommendations.append("  - Consider using the event system for more flexible testing")
    
    if not recommendations:
        return "No changes needed."
    
    return "\n".join(recommendations)

def main():
    """Main function"""
    logger.info("Starting test migration analysis")
    
    test_files = find_test_files()
    logger.info(f"Found {len(test_files)} test files")
    
    files_needing_updates = 0
    
    for file_path in test_files:
        file_info = scan_file(file_path)
        
        if file_info["imports_found"] or file_info["class_usage"]:
            files_needing_updates += 1
            print(f"\n{'=' * 80}")
            print(f"File: {file_path}")
            print(f"{'=' * 80}")
            
            if file_info["imports_found"]:
                print("Imports found:")
                for imp in file_info["imports_found"]:
                    print(f"  - {imp}")
            
            if file_info["class_usage"]:
                print("Service class usage:")
                for service_class, count in file_info["class_usage"].items():
                    print(f"  - {service_class}: {count} occurrences")
            
            if file_info["mocking_used"]:
                print("Mocking/override patterns detected")
            
            print("\nRecommendations:")
            print(generate_recommendations(file_info))
            
            logger.info(f"Analysis complete for {file_path}")
    
    print(f"\n{'=' * 80}")
    print(f"Analysis complete. {files_needing_updates} files need updates.")
    print(f"{'=' * 80}")
    logger.info(f"Analysis complete. {files_needing_updates} files need updates.")

if __name__ == "__main__":
    main()