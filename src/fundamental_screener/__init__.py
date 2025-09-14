"""
Brazilian Stock Fundamental Analysis Screener.

A comprehensive tool for analyzing Brazilian stocks using fundamental indicators
such as P/L, margins, EV/EBITDA, and debt ratios with sector-specific criteria.
"""

from .screener import FundamentalScreener
from .models import StockData, Sector, ScreeningCriteria, AnalysisResult
from .data_provider import DataProvider, FundamentusProvider, MockDataProvider

__version__ = "1.0.0"
__all__ = [
    "FundamentalScreener",
    "StockData", 
    "Sector", 
    "ScreeningCriteria", 
    "AnalysisResult",
    "DataProvider", 
    "FundamentusProvider", 
    "MockDataProvider"
]
