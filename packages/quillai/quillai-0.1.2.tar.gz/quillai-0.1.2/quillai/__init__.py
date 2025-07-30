"""
Quill Python API - Simplified interface to Quill Express API
"""

from .client import fillDfModel, fillDfModelDetailed, PredictionResult, QuillResponse

__version__ = "0.1.2"
__all__ = ["fillDfModel", "fillDfModelDetailed", "PredictionResult", "QuillResponse"]
