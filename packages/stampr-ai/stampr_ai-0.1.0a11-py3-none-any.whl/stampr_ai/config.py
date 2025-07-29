"""Configuration module for stampr_ai"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()  # Load .env file if it exists

# Map provider names to environment variable names
env_var_map = {
    "OPENAI": "OPENAI_API_KEY",
    "OPENROUTER": "OPENROUTER_API_KEY",
}


def get_api_key(provider: str) -> str | None:
    """Get API key for a specific provider from environment variables"""
    env_var = env_var_map.get(provider.upper())
    if not env_var:
        return None

    return os.getenv(env_var)


def get_openai_api_key() -> str | None:
    """Get OpenAI API key from environment"""
    return get_api_key("openai")


def get_huggingface_token() -> str | None:
    """
    Get Hugging Face token from environment variables or .env file.

    Returns:
        str | None: The token if found, None otherwise
    """

    token = None
    for env_var in ["HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGINGFACE_API_TOKEN"]:
        if env_var in os.environ:
            token = os.environ[env_var]
            break

    # Log token info (masked for security)
    if token:
        masked = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "****"
        logger.info(f"Found HF token: {masked}")
    else:
        logger.warning("No HF_TOKEN found. Add it to your .env file")

    return token
