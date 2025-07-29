"""stampr_ai - Verification of AI model signatures to detect model changes.

This package provides tools to verify AI model signatures and detect changes
in model behavior by comparing current API responses with recorded signatures.
"""

from importlib.metadata import version

__version__ = version("stampr_ai")

__author__ = "stampr_ai Team"
__email__ = "contact@stampr-ai.com"

from .config import get_api_key, get_openai_api_key
from .verifier import (
    verify_model,
)

__all__ = [
    "__version__",
    "get_api_key",
    "get_openai_api_key",
    "verify_model",
]
