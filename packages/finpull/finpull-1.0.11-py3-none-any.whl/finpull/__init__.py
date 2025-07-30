"""
FinPull - Comprehensive Financial Data Scraper

A powerful, cross-platform financial data scraping tool that fetches comprehensive 
financial data from multiple sources with fallback mechanisms.
"""

__version__ = "1.0.11"
__author__ = "Yevhenii Vasylevskyi"
__email__ = "yevhenii+finpull@vasylevskyi.net"

# Import main classes for easy access
from .core.data_models import FinancialData
from .core.scraper import FinancialDataScraper
from .interfaces.api import FinancialDataAPI

# Define what gets imported with "from finpull import *"
__all__ = [
    "FinancialDataScraper",
    "FinancialData", 
    "FinancialDataAPI",
]

# Utility functions available as module-level functions
def batch_fetch_tickers(tickers):
    """Batch fetch multiple tickers"""
    from .utils.batch import batch_fetch_tickers as _batch_fetch_tickers
    return _batch_fetch_tickers(tickers)

def get_available_features():
    """Get available features"""
    from .utils.compatibility import get_available_features as _get_available_features
    return _get_available_features() 