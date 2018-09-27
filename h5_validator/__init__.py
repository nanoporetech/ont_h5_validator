"""
HDF5 Validator.

Use this package to verify an HDF5 file meets a given schema
"""
from .cli import validate

__all__ = ('validate',)
__version__ = '2.0.1'
SCHEMA_VERSION = "9530c6a"
