from setuptools import setup, find_packages

setup(
    name="universal_app",
    version="0.1.0",
    packages=find_packages(include=["core", "ui", "ui.*", "utils"]),
    install_requires=[],  # No external dependencies, tkinter is included with Python
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "universal-app=core.app:create_app().run",
        ],
    },
)