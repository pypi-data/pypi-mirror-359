from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _follow_nested_path(path: str, nested_dict: dict[str, Any]) -> Any:
    """
    Args:
        path: period separated path
        nested_dict: structure of nested dictionaries to extract value from

    Returns:
        Any: value extracted from the nested dictionary

    Raises:
        KeyError: if nested dictionary does not contain key
        TypeError: if nested value is not dictionary
    """
    current = nested_dict
    for part in path.split("."):
        current = current[part]
    return current


def calculate_fresh_signature_hash(
    signature_parameters: dict[str, str],
    config: dict[str, Any],
    response_data: dict[str, Any],
) -> str:
    """
    Calculate signature hash from fresh data using signature parameters.

    Args:
        signature_parameters: Dictionary mapping field names to paths (from signature file)
        config: Configuration data with model parameters and collector parameters
        response_data: Response data with fresh live sampling results
    Returns:
        Calculated hash as hex string
    """
    hasher = hashlib.sha256()

    # Process each field in the signature_parameters in order
    for field_name, field_path in signature_parameters.items():
        logger.debug(f"Processing signature field: {field_name} with path {field_path}")

        # Extract the value using simple path navigation
        # Special case for model_parameters.messages to return the complete messages with random tokens
        value = None
        if field_path == "model_parameters.messages" and "complete_messages" in config:
            logger.debug(
                "Using complete_messages with integrated random tokens for signature"
            )
            value = config["complete_messages"]
        elif field_path.startswith("response."):
            # Handle response data paths
            if response_data is None:
                logger.warning(f"Response data not provided for path {field_path}")
                continue
            response_path = field_path.split(".", 1)[1]
            try:
                value = _follow_nested_path(response_path, response_data)
            except (KeyError, TypeError) as e:
                logger.warning(f"Response path '{field_path}' is invalid: {e!r}")
        else:
            # Handle config data paths
            try:
                value = _follow_nested_path(field_path, config)
            except (KeyError, TypeError) as e:
                logger.warning(f"Config path '{field_path}' is invalid: {e!r}")

        if value is None:
            logger.warning(
                f"Could not find value for signature field {field_name} at path {field_path}"
            )
            continue

        # Handle different types of values
        if isinstance(value, str):
            hasher.update(value.encode("utf-8"))
            logger.debug(f"Added string value for {field_name}: {value!r}")
        elif isinstance(value, (int, float, bool)):
            str_value = str(value)
            hasher.update(str_value.encode("utf-8"))
            logger.debug(f"Added numeric/bool value for {field_name}: {str_value}")
        elif isinstance(value, list):
            # For list values (like path_tokens), add each item
            for item in value:
                if isinstance(item, str):
                    hasher.update(item.encode("utf-8"))
                else:
                    hasher.update(str(item).encode("utf-8"))
            logger.debug(f"Added list value for {field_name}: {value}")
        elif isinstance(value, dict):
            # Handle dict values with special logic for target_distribution fields (matching collector logic)
            if field_name == "target_distribution_keys":
                # Sort the token keys and hash only those
                sorted_tokens = sorted(value.keys())
                for token in sorted_tokens:
                    hasher.update(token.encode("utf-8"))
                logger.debug(
                    f"Added target_distribution_keys for {field_name}: {sorted_tokens}"
                )
            elif field_name == "target_distribution":
                # For full target_distribution, process the dictionary directly (matching collector)
                for key in sorted(value.keys()):
                    hasher.update(key.encode("utf-8"))
                    # Hash the nested dictionary values in a stable way
                    token_info = value[key]
                    for info_key in sorted(token_info.keys()):
                        hasher.update(str(token_info[info_key]).encode("utf-8"))
                logger.debug(
                    f"Added full target_distribution for {field_name}: {value}"
                )
            else:
                # For other dict values, use a stable representation
                sorted_dict = json.dumps(value, sort_keys=True)
                hasher.update(sorted_dict.encode("utf-8"))
                logger.debug(f"Added dict value for {field_name}: {sorted_dict}")
        else:
            # For other types, convert to string
            str_value = str(value)
            hasher.update(str_value.encode("utf-8"))
            logger.debug(f"Added other value for {field_name}: {str_value}")

    hex_digest = hasher.hexdigest()
    logger.info(f"Calculated fresh hash: {hex_digest}")
    return hex_digest
