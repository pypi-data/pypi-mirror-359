"""OpenAI provider implementation."""

from __future__ import annotations

import logging
from typing import Any

try:
    from openai import OpenAI
except ImportError as e:
    raise ImportError("The openai package must be installed to use OpenAI.") from e


logger = logging.getLogger(__name__)


def get_openai_completion(
    model: str,
    prompt: str,
    api_key: str,
    config: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    """Get completion from OpenAI API.

    Args:
        model: Name of the model to use
        prompt: Random tokens prompt to send to the model
        api_key: API key
        config: Configuration parameters

    Returns:
        Tuple containing (response, api_parameters)

    Raises:
        ValueError: If API key is not found or invalid
        Exception: For other API-related errors
    """
    client = OpenAI(api_key=api_key)

    # Get model parameters from config
    model_params = config[
        "model_parameters"
    ].copy()  # Make a copy to avoid modifying the original

    if "seed" in model_params:
        model_params["seed"] = int(model_params["seed"])

    # Replace {{random_tokens}} in messages with the actual random tokens
    if "messages" in model_params:
        for message in model_params["messages"]:
            if (
                isinstance(message.get("content"), str)
                and "{{random_tokens}}" in message["content"]
            ):
                message["content"] = message["content"].replace(
                    "{{random_tokens}}", prompt
                )

    # Prepare API parameters using only what's in model_parameters
    api_params = {
        "model": model,
        **model_params,  # Include all model parameters from config
    }

    logger.debug(
        f"Sending request to OpenAI: {model} with prompt length: {len(prompt)}"
    )

    try:
        response = client.chat.completions.create(**api_params)
        return response, api_params
    except Exception as e:
        logger.error(f"OpenAI API request failed: {e!r}")
        raise
