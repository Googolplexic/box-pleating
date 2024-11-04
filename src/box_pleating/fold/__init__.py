"""
FOLD Format Converter Module

This module provides functionality for converting between BoxPleatingPattern and FOLD format.
The FOLD format is a standard file format for origami crease patterns designed by 
Erik Demaine and others (https://github.com/edemaine/fold).

Example usage:
    from box_pleating.fold import FoldConverter
    
    converter = FoldConverter()
    
    # Load from FOLD file
    pattern = converter.load_fold("pattern.fold")
    
    # Save to FOLD file
    converter.save_fold(pattern, "output.fold")
"""

from .converter import FoldConverter

__all__ = ["FoldConverter"]
