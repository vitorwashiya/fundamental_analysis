#!/usr/bin/env python3
"""
Main entry point for the Brazilian Stock Fundamental Analysis Screener.
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fundamental_screener.cli import main

if __name__ == "__main__":
    main()