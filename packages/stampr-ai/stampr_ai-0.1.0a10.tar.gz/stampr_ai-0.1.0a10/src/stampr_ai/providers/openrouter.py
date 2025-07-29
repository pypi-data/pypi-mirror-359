"""OpenRouter provider implementation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import requests

from ..utils.tokenizers import Tokenizer, get_tokenizer_for_model

logger = logging.getLogger(__name__)


@dataclass
class TokenObject:
    token: str
    id: int
    logprob: float = -1.0
    top_logprobs: list[dict[str, float]] = field(default_factory=list)


def get_openrouter_completion(
    model: str,
    prompt: str,
    api_key: str,
    config: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Prepare model parameters
    model_params = config["model_parameters"].copy()

    if "seed" in model_params and model_params["seed"] is not None:
        model_params["seed"] = int(model_params["seed"])

    # Replace placeholder in messages if present
    if "messages" in model_params:
        for message in model_params["messages"]:
            if (
                isinstance(message.get("content"), str)
                and "{{random_tokens}}" in message["content"]
            ):
                message["content"] = message["content"].replace(
                    "{{random_tokens}}", prompt
                )

    # Create payload
    payload = {"model": model, **model_params}

    # Add OpenRouter specific parameters if present
    if "openrouter_parameters" in config:
        or_params = config["openrouter_parameters"]

        # Handle special parameters that go at the top level
        for key, value in or_params.items():
            if key not in ["cache_control", "provider"] and key not in payload:
                payload[key] = value

        # Add cache_control and provider parameters if present
        if "cache_control" in or_params:
            payload["cache_control"] = or_params["cache_control"]
        if "provider" in or_params:
            payload["provider"] = or_params["provider"]

    # Handle the service_provider format with slashes (e.g., "OpenRouter/DeepInfra")
    service_provider = config.get(
        "original_service_provider", config.get("service_provider", "")
    )

    if service_provider and "/" in service_provider:
        parts = service_provider.split("/", 1)
        if len(parts) == 2 and parts[1]:
            # Extract the specific provider (DeepInfra, NCompass, etc.)
            specific_provider = parts[1]
            logger.debug(
                f"Using specific provider from service_provider: {specific_provider}"
            )

            # If provider is not already set in openrouter_parameters, add it
            if "provider" not in payload and specific_provider:
                payload["provider"] = {"order": [specific_provider]}
                logger.debug(
                    f"Added provider order from service_provider: {specific_provider}"
                )

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "stampr_ai_collector",  # OpenRouter tracking
        "X-Title": "stampr_ai Collector",  # OpenRouter tracking
    }

    logger.debug(
        f"Sending request to OpenRouter: {model} with prompt length: {len(prompt)}"
    )

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors

        response_data = response.json()

        # Debug: Log the original response structure
        logger.debug(f"OpenRouter response keys: {response_data.keys()}")
        if response_data.get("choices"):
            first_choice = response_data["choices"][0]
            logger.debug(f"First choice keys: {first_choice.keys()}")
            if "logprobs" in first_choice:
                logger.debug(f"Original logprobs: {first_choice['logprobs']}")
            else:
                logger.debug("No logprobs in original response")

        # Get tokenizer to create synthetic tokens
        tokenizer_name = config.get("tokenizer")
        if tokenizer_name:
            enc = get_tokenizer_for_model(model, tokenizer_name)
        else:
            enc = get_tokenizer_for_model(model)

        # Enhance the response with synthetic tokens
        enhanced_response = enhance_response_with_tokens(response_data, enc)

        # Create and return the OpenRouterResponse object
        return OpenRouterResponse(enhanced_response), payload
    except Exception as e:
        logger.error(f"OpenRouter API request failed: {e!r}")
        raise


def enhance_response_with_tokens(
    response_data: dict[str, Any],
    tokenizer: Tokenizer,
) -> dict[str, Any]:
    """
    Enhance OpenRouter response with synthetic tokens by tokenizing the response text.

    Args:
        response_data: Original response data from OpenRouter
        tokenizer: Tokenizer to use for tokenizing the text

    Returns:
        Enhanced response data with synthetic tokens
    """
    # Make a copy of the response data
    enhanced_data = response_data.copy()

    # Add synthetic token information to each choice
    if enhanced_data.get("choices"):
        for choice_idx, choice in enumerate(enhanced_data["choices"]):
            if "message" in choice and "content" in choice["message"]:
                # Get the text content
                text = choice["message"]["content"]
                logger.debug(f"Original response text: {text}")

                # Create synthetic tokens
                tokens = create_synthetic_tokens(text, tokenizer)
                logger.debug(f"Created {len(tokens)} synthetic tokens")
                if tokens:
                    token_preview = [t.token for t in tokens[:10]]
                    logger.debug(f"First tokens: {token_preview}")

                # Add synthetic logprobs to the choice
                if "logprobs" not in choice or choice["logprobs"] is None:
                    logger.debug(f"Adding synthetic logprobs for choice {choice_idx}")
                    choice["logprobs"] = {
                        "content": tokens,
                        "is_synthetic": True,  # Mark as synthetic
                    }
                    logger.debug(
                        f"Synthetic logprobs added, content type: {type(choice['logprobs']['content'])}"
                    )
                    if choice["logprobs"]["content"]:
                        logger.debug(
                            f"First synthetic token type: {type(choice['logprobs']['content'][0])}"
                        )
                        logger.debug(
                            f"First synthetic token has .token attribute: {hasattr(choice['logprobs']['content'][0], 'token')}"
                        )
                else:
                    logger.debug(
                        f"Choice {choice_idx} already has logprobs, not adding synthetic ones"
                    )

    return enhanced_data


def create_synthetic_tokens(text: str, tokenizer: Tokenizer) -> list[Any]:
    """
    Create synthetic tokens from text using the tokenizer.

    Args:
        text: Text to tokenize
        tokenizer: Tokenizer to use

    Returns:
        List of synthetic token objects with .token attribute
    """
    logger.debug(
        f"Tokenizing text of length {len(text)} with tokenizer: {type(tokenizer).__name__}"
    )

    tokens = []
    synthetic_tokens = []

    try:
        # For tiktoken and huggingface tokenizers
        # Encode the entire text
        token_ids = tokenizer.encode(text)
        logger.debug(f"Encoded to {len(token_ids)} token IDs")

        # Decode each token individually for proper token representation
        for token_id in token_ids:
            token_text = tokenizer.decode([token_id])
            tokens.append((token_text, token_id))

        # Create token objects and make sure they have the right interface
        for token, token_id in tokens:
            # Skip empty tokens
            if not token:
                continue

            token_obj = TokenObject(token, token_id)
            synthetic_tokens.append(token_obj)

        logger.debug(f"Created {len(synthetic_tokens)} synthetic token objects")

    except Exception as e:
        logger.error(f"Error creating synthetic tokens: {e!r}")

    if not synthetic_tokens:
        # Create a simple fallback token
        logger.warning("No tokens created, adding fallback token")

        return [TokenObject(text[:10] if len(text) > 10 else text, 0)]

    return synthetic_tokens


class OpenRouterResponse:
    """OpenRouter response model."""

    def __init__(self, response_data: dict[str, Any]):
        self.id = response_data.get("id", "")
        self.object = response_data.get("object", "")
        self.created = response_data.get("created", 0)
        self.model = response_data.get("model", "")
        self.choices = [
            OpenRouterChoice(choice) for choice in response_data.get("choices", [])
        ]
        self.usage = response_data.get("usage", {})
        self.system_fingerprint = response_data.get("system_fingerprint", "")

    def __str__(self) -> str:
        return f"OpenRouterResponse(id={self.id}, model={self.model}, choices={len(self.choices)})"

    def get_completion(self) -> str:
        """Get the completion text from the first choice."""
        if not self.choices:
            return ""
        return self.choices[0].get_completion()


class OpenRouterChoice:
    """OpenRouter choice model."""

    def __init__(self, choice_data: dict[str, Any]):
        self.index = choice_data.get("index", 0)
        self.message = OpenRouterMessage(choice_data.get("message", {}))
        self.logprobs = choice_data.get("logprobs")
        if self.logprobs is not None:
            self.logprobs = OpenRouterLogprobs(self.logprobs)
        self.finish_reason = choice_data.get("finish_reason", "")

    def get_completion(self) -> str:
        """Get the completion text from the message."""
        return self.message.get_content()


class OpenRouterMessage:
    """OpenRouter message model."""

    def __init__(self, message_data: dict[str, str]):
        self.role = message_data.get("role", "")
        self.content = message_data.get("content", "")

    def get_content(self) -> str:
        """Get the content of the message."""
        return self.content


class OpenRouterLogprobs:
    """OpenRouter logprobs model."""

    def __init__(self, logprobs_data: dict[str, Any]):
        self.is_synthetic = logprobs_data.get("is_synthetic", False)

        # Convert content tokens to objects with .token attributes
        raw_content = logprobs_data.get("content", [])
        self.content = []

        for token_data in raw_content:
            if isinstance(token_data, dict):
                token_obj = TokenObject(**token_data)
                self.content.append(token_obj)
            else:
                # Already an object (synthetic tokens), keep as is
                self.content.append(token_data)

        self.token_logprobs = logprobs_data.get("token_logprobs", [])
        self.tokens = logprobs_data.get("tokens", [])
        self.top_logprobs = logprobs_data.get("top_logprobs", [])
        self.text_offset = logprobs_data.get("text_offset", [])


class OpenRouterToken:
    """OpenRouter token model."""

    def __init__(self, token_data: dict[str, Any]):
        self.tokens = token_data
