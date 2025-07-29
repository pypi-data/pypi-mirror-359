"""Key generation utilities for the stampr_ai package."""

from __future__ import annotations

import re


def sanitize_key(key: str) -> str:
    key_sanitized = key.lower().replace(" ", "_").replace("-", "_")
    return re.sub(r"[^a-z0-9_]", "", key_sanitized)  # Keep underscores


def generate_model_key(
    model_short_name: str | None, service_provider: str | None
) -> str:
    """
    Generate unique key for model+provider combination.

    Args:
        model_short_name: The short name of the model (e.g., "gpt-4o", "Llama3_8b")
        service_provider: The service provider (e.g., "OpenAI", "OpenRouter/DeepInfra")

    Returns:
        A sanitized model key string in format "model-provider"
    """
    if not model_short_name:
        model_short_name = "unknown"

    # Sanitize model name
    sanitized_model = sanitize_key(model_short_name)

    provider_suffix = service_provider or "unknown"
    provider_suffix = provider_suffix.replace("/", "_")
    sanitized_provider = sanitize_key(provider_suffix)

    return f"{sanitized_model}-{sanitized_provider}"
