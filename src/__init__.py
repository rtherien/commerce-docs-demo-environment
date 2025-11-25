"""
Coveo Commerce API Loader Package

This package provides tools for loading catalog data into Coveo Commerce sources
using the Coveo Stream API.
"""

__version__ = "1.0.0"
__author__ = "Coveo Documentation Team"
__email__ = "docs@coveo.com"

from .loader import CoveoLoader

__all__ = ["CoveoLoader"]