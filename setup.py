"""
Setup configuration for hs_standardization package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="hs_standardization",
    version="1.0.0",
    author="Sports Roster Data",
    description="A utility for normalizing and standardizing high school names across datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sports-Roster-Data/utilities",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    keywords="high school, standardization, normalization, data cleaning, education",
    project_urls={
        "Bug Reports": "https://github.com/Sports-Roster-Data/utilities/issues",
        "Source": "https://github.com/Sports-Roster-Data/utilities",
    },
)
