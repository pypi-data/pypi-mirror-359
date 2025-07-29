"""Utility functions for the stampr_ai_collector package."""

import requests

from .tokenizers import get_tokenizer_for_model as get_tokenizer_for_model


def fetch_json_from_url(url: str) -> dict:
    """Fetch JSON data from a URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()  # type: ignore [no-any-return] # response.json has return type Any on purpose
