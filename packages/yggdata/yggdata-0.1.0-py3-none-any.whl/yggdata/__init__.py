"""
YggData - A hierarchical tree-like data structure for Python.

This package provides:
1. Yggdrasil: A hierarchical tree-like data structure that extends Python's dict
2. Input validation utilities for getting user input with validation and retry logic
"""

__version__ = "0.1.0"

from .yggdrasil import Yggdrasil
from .inputs import (
    string_put,
    int_put,
    float_put,
    choice_put,
    bool_put,
    file_put,
    date_put,
    mail_put,
)

__all__ = [
    "Yggdrasil",
    "string_put",
    "int_put",
    "float_put",
    "choice_put",
    "bool_put",
    "file_put",
    "date_put",
    "mail_put",
]
