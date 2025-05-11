from setuptools import setup, find_packages

setup(
    name="universal_app",
    version="0.1.0",
    description="Universal application framework for hosting multiple projects",
    author="Your Name",
    packages=find_packages(include=["core", "core.*", "ui", "ui.*", "utils", "utils.*", "services", "services.*"]),
    install_requires=[
        "dependency-injector>=4.41.0",
        # Optional dependencies (commented out by default)
        # "rpy2>=3.5.0",         # For R integration
        # "pandas>=1.3.0",       # For data analysis
        # "matplotlib>=3.5.0",   # For visualization
        # "kaggle>=1.5.0",       # For Kaggle API
        # "requests>=2.26.0",    # For HTTP requests
    ],
    extras_require={
        "r": ["rpy2>=3.5.0"],
        "data": ["pandas>=1.3.0", "matplotlib>=3.5.0"],
        "kaggle": ["kaggle>=1.5.0"],
        "dev": ["black", "flake8", "pytest"],
        "all": [
            "rpy2>=3.5.0",
            "pandas>=1.3.0",
            "matplotlib>=3.5.0",
            "kaggle>=1.5.0",
            "requests>=2.26.0",
            "black",
            "flake8",
            "pytest",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "universal-app=core.app:create_app().run",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)