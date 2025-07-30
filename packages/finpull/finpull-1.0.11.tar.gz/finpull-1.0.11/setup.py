#!/usr/bin/env python3
"""
Setup script for FinPull - Financial Data Scraper
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="finpull",
    version="1.0.11",
    author="Yevhenii Vasylevskyi",
    author_email="yevhenii+finpull@vasylevskyi.net",
    description="Financial data scraper with CLI interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lavarite/FinPull",
    project_urls={
        "Bug Reports": "https://github.com/Lavarite/FinPull/issues",
        "Source": "https://github.com/Lavarite/FinPull",
        "Documentation": "https://github.com/Lavarite/FinPull/blob/main/README.md",
    },
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.1",
        "beautifulsoup4>=4.9.3",
        "yfinance>=0.1.63",
        "openpyxl>=3.0.7",
    ],
    entry_points={
        "console_scripts": [
            "finpull=finpull.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="finance, scraping, stocks, financial-data, cli, api, finviz, yahoo-finance",
) 