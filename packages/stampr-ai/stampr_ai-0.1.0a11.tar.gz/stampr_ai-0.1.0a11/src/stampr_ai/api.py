# ruff: noqa PLC0415  # disable imports at top-level so unused dependencies (e.g. openAI) are not always required
"""API client functionality for interacting with model APIs."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_model_completion(
    model: str,
    prompt: str,
    api_key: str,
    config: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    """
    Fetches completion from a given model with proper error handling.

    Args:
        model: Name of the model to use
        prompt: Input prompt for the model
        api_key: API key for the model
        config: Configuration dictionary containing API details

    Returns:
        Tuple of (completion_response, response_metadata)

    Raises:
        ValueError: If required configuration is missing
        Exception: If API call fails
    """
    service_provider = config.get("service_provider", "").lower()

    # Extract base provider name (handle formats like "openrouter/parasail")
    base_provider = service_provider.split("/")[0]

    logger.debug(f"Getting completion from {service_provider} for model {model}")

    # Route to appropriate provider using base provider name
    if base_provider == "openai":
        from .providers.openai import get_openai_completion

        return get_openai_completion(model, prompt, api_key, config)
    elif base_provider == "openrouter":
        from .providers.openrouter import get_openrouter_completion

        return get_openrouter_completion(model, prompt, api_key, config)
    else:
        # Provide helpful error message with supported providers
        supported_providers = ["openai", "openrouter"]

        raise ValueError(
            f"Unsupported service provider: {service_provider}. "
            f"Supported providers: {', '.join(supported_providers)}"
        )
