from setuptools import setup, find_packages

setup(
    name="universal_app",
    version="0.1.0",
    description="Universal application framework for hosting multiple projects",
    author="Your Name",
    packages=find_packages(include=["core", "core.*", "ui", "ui.*", "utils", "utils.*", "services", "services.*"]),
    # Core dependencies - required for basic functionality
    install_requires=[
        "dependency-injector>=4.41.0",
        "requests>=2.26.0",
    ],
    # Optional dependencies - grouped by feature
    extras_require={
        # R integration
        "r": ["rpy2>=3.5.0"],

        # Data analysis
        "data": [
            "pandas>=1.3.0",
            "numpy>=1.20.0",
            "matplotlib>=3.4.0"
        ],

        # Kaggle integration
        "kaggle": [
            "kaggle>=1.5.0",
            "Pillow>=8.0.0"
        ],

        # Development tools
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0"
        ],

        # All optional dependencies combined
        "all": [
            # R integration
            "rpy2>=3.5.0",

            # Data analysis
            "pandas>=1.3.0",
            "numpy>=1.20.0",
            "matplotlib>=3.4.0",

            # Kaggle integration
            "kaggle>=1.5.0",
            "Pillow>=8.0.0",

            # Development tools
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "universal-app=core.app:create_app().run",
            "universal-app-check-deps=utils.dependency_check:print_dependency_status"
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)