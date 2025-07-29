"""Tokenizer utilities for different model types."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from functools import cache
from typing import Protocol

import tiktoken
from transformers import AutoTokenizer
from transformers.tokenization_utils_base import PreTrainedTokenizerBase

from ..config import get_huggingface_token

logger = logging.getLogger(__name__)


class Tokenizer(Protocol):
    def encode(self, text: str) -> list[int]: ...
    def decode(self, tokens: Sequence[int], /) -> str: ...


@cache
def get_tokenizer_for_model(
    model_name: str,
    tokenizer_name: str | None = None,
) -> Tokenizer:
    """
    Get the appropriate tokenizer for a model based on its name or a specific tokenizer name.
    Falls back to tiktoken for OpenAI models, uses transformers for others.

    Args:
        model_name: The name of the model
        tokenizer_name: Optional specific tokenizer to use (from config)

    Returns:
        Tuple of (tokenizer object, tokenizer_name)

    Raises:
        ValueError: If the specified tokenizer cannot be loaded
    """
    # Special case for GPT-4o models - use tiktoken directly
    if "gpt-4o" in model_name.lower() or (
        tokenizer_name and "gpt-4o" in tokenizer_name.lower()
    ):
        try:
            # Try specific model encoding first
            try:
                enc = tiktoken.encoding_for_model("gpt-4o")
                logger.info(f"Using gpt-4o tiktoken encoding for {model_name}")
            except KeyError:
                # Fall back to cl100k_base which is used by GPT-4 models
                enc = tiktoken.get_encoding("cl100k_base")
                logger.info(f"Falling back to cl100k_base encoding for {model_name}")

            return enc
        except Exception as e:
            logger.warning(
                f"Failed to load tiktoken for {model_name}, continuing with normal flow: {e!r}"
            )

    transformers_kwargs: dict[str, str] = {}
    if token := get_huggingface_token():
        transformers_kwargs["token"] = token

    # If a specific tokenizer is provided in the config, try to load it first
    tokenizer: PreTrainedTokenizerBase
    if tokenizer_name:
        logger.info(f"Attempting to load specified tokenizer: {tokenizer_name}")
        logger.debug(f"Model name: {model_name}, Tokenizer name: {tokenizer_name}")
        try:
            # Try loading with HuggingFace first
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    tokenizer_name, **transformers_kwargs
                )
                logger.info(
                    f"Successfully loaded specified tokenizer: {tokenizer_name}"
                )
                return tokenizer
            except Exception as e:
                # If it's not a HuggingFace tokenizer, try tiktoken
                if "gpt" in tokenizer_name.lower():
                    try:
                        return tiktoken.encoding_for_model(tokenizer_name)
                    except Exception as e2:
                        # If both attempts fail, raise error with both exceptions
                        raise ValueError(
                            f"Failed to load specified tokenizer '{tokenizer_name}'. "
                            f"HuggingFace error: {e!r}. Tiktoken error: {e2!r}"
                        ) from e2
                else:
                    # If it's not a GPT model and HuggingFace failed, raise the original error
                    raise ValueError(
                        f"Failed to load specified tokenizer '{tokenizer_name}': {e!r}"
                    ) from e
        except Exception as e:
            # Log the full traceback for debugging
            logger.error(
                f"Failed to load specified tokenizer '{tokenizer_name}': {e!r}"
            )
            logger.debug("", exc_info=e)
            raise ValueError(
                f"Failed to load specified tokenizer '{tokenizer_name}'. This is a critical error. Please check the tokenizer name and ensure you have the necessary permissions and dependencies."
            ) from e

    # Check if model name contains Llama or other HuggingFace models
    if "llama" in model_name.lower() or "meta-llama" in model_name.lower():
        try:
            # For Llama 3.3 models
            if "llama-3.3" in model_name.lower() or "llama3.3" in model_name.lower():
                # Use Llama 3.1 tokenizer which is more widely available
                base_model_name = "meta-llama/Llama-3.1-8B-Instruct"
                try:
                    tokenizer = AutoTokenizer.from_pretrained(
                        base_model_name, **transformers_kwargs
                    )
                    logger.info(
                        f"Using {base_model_name} tokenizer for model: {model_name}"
                    )
                    return tokenizer
                except Exception as e:
                    logger.warning(f"Failed to load {base_model_name} tokenizer: {e!r}")
                    logger.debug("", exc_info=e)

            # Use direct model name for Llama-4 models
            elif "llama-4" in model_name.lower() or "llama4" in model_name.lower():
                # Try for Llama-4-Scout first
                base_model_name = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
                try:
                    tokenizer = AutoTokenizer.from_pretrained(
                        base_model_name, **transformers_kwargs
                    )
                    logger.info(
                        f"Using {base_model_name} tokenizer for model: {model_name}"
                    )
                    return tokenizer
                except Exception as e:
                    logger.warning(f"Failed to load {base_model_name} tokenizer: {e!r}")
                    logger.debug("", exc_info=e)

                    # Try fallback to Llama-4-8B
                    base_model_name = "meta-llama/Llama-4-8B-Instruct"
                    try:
                        tokenizer = AutoTokenizer.from_pretrained(
                            base_model_name, **transformers_kwargs
                        )
                        logger.info(
                            f"Using {base_model_name} tokenizer for model: {model_name}"
                        )
                        return tokenizer
                    except Exception as e2:
                        logger.warning(
                            f"Failed to load {base_model_name} tokenizer: {e2!r}"
                        )
                        logger.debug("", exc_info=e2)

            # For other Llama models or general HF models, try loading directly
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name, **transformers_kwargs
                )
                logger.info(
                    f"Successfully loaded transformers tokenizer for: {model_name}"
                )
                return tokenizer
            except Exception as e:
                logger.warning(f"Failed to load {model_name} tokenizer: {e!r}")
                logger.debug("", exc_info=e)
                # Continue to fallbacks

        except Exception as e:
            logger.warning(
                f"Failed to load transformers tokenizer for {model_name}: {e!r}"
            )
            logger.debug("", exc_info=e)

        # Fall back to a default encoding if transformers fails
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            logger.info(f"Falling back to {enc.name} for {model_name}")
            return enc
        except Exception:
            try:
                enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
                logger.info(f"Falling back to {enc.name} for {model_name}")
                return enc
            except Exception as e:
                logger.exception(
                    f"All tokenizer fallbacks failed for {model_name}: {e!r}"
                )
                logger.debug("", exc_info=e)
                raise

    # Try tiktoken for other models
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        # If model is not found in tiktoken, try some fallbacks
        try:
            # For OpenAI/ChatGPT models
            if "gpt" in model_name.lower():
                return tiktoken.encoding_for_model("gpt-3.5-turbo")
            return tiktoken.get_encoding("cl100k_base")

        except Exception as e:
            raise ValueError(
                f"Could not find a suitable tokenizer for model: {model_name}. Error: {e!r}"
            ) from e
