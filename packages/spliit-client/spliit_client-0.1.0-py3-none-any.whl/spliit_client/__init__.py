#!/usr/bin/env python3
"""
Spliit Client - A Python client for the Spliit API (group expense sharing).

This package provides a simple interface to interact with the Spliit API,
allowing you to create groups, manage participants, and handle expenses
programmatically.
"""

from .client import Spliit, SplitMode, CATEGORIES

__version__ = "0.1.0"
__author__ = "Abhinav"
__email__ = "gptabhinav0148@gmail.com"

__all__ = ["Spliit", "SplitMode", "CATEGORIES"] 