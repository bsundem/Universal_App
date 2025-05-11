"""
Dependency checking utility for the Universal App.

This module provides functions to check for the availability of
required and optional dependencies, helping users understand
what features are available and what might be missing.
"""
import importlib.util
import sys
from typing import Dict, List, Tuple, Set


# Core dependencies that must be available
CORE_DEPENDENCIES = {
    "dependency_injector": "Dependency Injection Container",
    "requests": "HTTP Requests",
}

# Optional dependencies by feature group
OPTIONAL_DEPENDENCIES = {
    "R Integration": {
        "rpy2": "R Language Integration",
    },
    "Data Analysis": {
        "pandas": "Data Analysis and Manipulation",
        "numpy": "Numerical Computing",
        "matplotlib": "Data Visualization",
    },
    "Kaggle Integration": {
        "kaggle": "Kaggle API",
        "PIL": "Python Imaging Library",
    },
    "Development": {
        "pytest": "Testing Framework",
        "black": "Code Formatting",
        "flake8": "Code Linting",
    },
}


def check_module_available(module_name: str) -> bool:
    """
    Check if a Python module is available.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        True if the module is available, False otherwise
    """
    try:
        # Special case for PIL/Pillow
        if module_name == "PIL":
            return importlib.util.find_spec("PIL") is not None
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError):
        return False


def check_dependencies() -> Tuple[Dict[str, bool], Dict[str, Dict[str, bool]]]:
    """
    Check the availability of all dependencies.
    
    Returns:
        Tuple containing:
        - Dict mapping core dependency names to availability status
        - Dict mapping feature groups to dicts of dependency status
    """
    # Check core dependencies
    core_status = {dep: check_module_available(dep) for dep in CORE_DEPENDENCIES}
    
    # Check optional dependencies
    optional_status = {}
    for feature, deps in OPTIONAL_DEPENDENCIES.items():
        optional_status[feature] = {dep: check_module_available(dep) for dep in deps}
    
    return core_status, optional_status


def print_dependency_status(show_only_missing: bool = False) -> None:
    """
    Print the status of all dependencies.
    
    Args:
        show_only_missing: If True, only show missing dependencies
    """
    core_status, optional_status = check_dependencies()
    
    # Print header
    print("\n=== Universal App Dependency Check ===\n")
    
    # Print core dependencies
    print("Core Dependencies:")
    core_missing = False
    for dep, available in core_status.items():
        if available and not show_only_missing:
            print(f"  [✓] {dep}: {CORE_DEPENDENCIES[dep]}")
        elif not available:
            print(f"  [✗] {dep}: {CORE_DEPENDENCIES[dep]} - MISSING")
            core_missing = True
    
    if show_only_missing and not core_missing:
        print("  All core dependencies are available.")
    
    # Print optional dependencies by feature
    print("\nOptional Features:")
    for feature, deps in optional_status.items():
        missing = [dep for dep, available in deps.items() if not available]
        available = [dep for dep, available in deps.items() if available]
        
        if not missing:
            status = "AVAILABLE"
            symbol = "✓"
        elif len(missing) == len(deps):
            status = "UNAVAILABLE"
            symbol = "✗"
        else:
            status = "PARTIAL"
            symbol = "!"
            
        if not show_only_missing or missing:
            print(f"  [{symbol}] {feature}: {status}")
            
            if not show_only_missing:
                for dep in available:
                    print(f"    [✓] {dep}: {OPTIONAL_DEPENDENCIES[feature][dep]}")
            
            for dep in missing:
                print(f"    [✗] {dep}: {OPTIONAL_DEPENDENCIES[feature][dep]} - MISSING")
    
    # Print installation instructions
    print("\nInstallation Instructions:")
    if core_missing:
        print("  To install core dependencies:")
        print("  pip install -e .")
    
    feature_missing = {feature for feature, deps in optional_status.items()
                     if any(not available for available in deps.values())}
    
    if feature_missing:
        print("  To install optional dependencies by feature:")
        for feature in feature_missing:
            feature_slug = feature.lower().replace(" ", "")
            print(f"  pip install -e \".[{feature_slug}]\"")
        
        print("\n  To install all dependencies:")
        print("  pip install -e \".[all]\"")
    else:
        print("  All optional dependencies are already installed.")


def validate_dependencies() -> bool:
    """
    Validate that all core dependencies are available.
    
    Returns:
        True if all core dependencies are available, False otherwise
    """
    core_status, _ = check_dependencies()
    return all(core_status.values())


def get_available_features() -> Set[str]:
    """
    Get the set of available features based on installed dependencies.
    
    Returns:
        Set of feature names that are fully available
    """
    _, optional_status = check_dependencies()
    return {feature for feature, deps in optional_status.items()
            if all(deps.values())}


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Check dependencies for Universal App")
    parser.add_argument('--missing', action='store_true', help='Show only missing dependencies')
    parser.add_argument('--validate', action='store_true', help='Validate core dependencies only')
    args = parser.parse_args()
    
    if args.validate:
        if validate_dependencies():
            print("All core dependencies are available.")
            sys.exit(0)
        else:
            print("Some core dependencies are missing. Run without --validate for details.")
            sys.exit(1)
    else:
        print_dependency_status(args.missing)