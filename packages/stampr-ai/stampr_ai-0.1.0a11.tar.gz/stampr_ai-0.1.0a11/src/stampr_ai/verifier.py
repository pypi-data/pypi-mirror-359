from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timedelta
from typing import Any

import requests

from .api_client import APIClient
from .api_types import Signature, SignatureContent
from .utils import fetch_json_from_url
from .utils.keys import generate_model_key

logger = logging.getLogger(__name__)

SIGNATURES_BASE_URL = "https://www.stampr-ai.com/"
DEFAULT_SIGNATURES_INDEX_URL = f"{SIGNATURES_BASE_URL}signatures.json"


def _fetch_model_signatures(
    model_short_name: str,
    service_provider: str,
    signatures_index_url: str,
) -> tuple[list[Signature], str]:
    """
    Fetches the most recent signature file path and full hash for a given model.

    Args:
        model_short_name: The short name of the model (e.g., "gpt-4o", "Llama3_8b").
        service_provider: The service provider (e.g., "OpenAI", "OpenRouter/DeepInfra").
        signatures_index_url: URL to the main signatures.json index file.
    Returns:
        Tuple of (signatures_list, model_key)
    """
    logger.info(f"Fetching signature index from {signatures_index_url}")
    try:
        index_data = fetch_json_from_url(signatures_index_url)
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logger.exception("Failed to fetch or parse signature index: %s", e)
        return [], ""

    model_key = generate_model_key(model_short_name, service_provider)
    logger.info(f"Looking for model key: {model_key}")

    model_entry = index_data.get("models", {}).get(model_key)

    signatures = model_entry.get("signatures")
    if not signatures or not isinstance(signatures, list):
        logger.warning(f"No signatures found for model key '{model_key}'.")
        return [], model_key

    return signatures, model_key


def _get_signature_info(
    model_name: str,
    service_provider: str,
    signatures_index_url: str,
    hash_prefix: str | None = None,
) -> Signature | None:
    """
    Get signature info - either latest signature or by hash prefix.
    Args:
        model_name: Model name
        service_provider: Service provider
        signatures_index_url: URL to signatures index
        hash_prefix: If provided, find signature by hash prefix. If None, get latest.
    Returns:
        Signature info dict or None if not found
    """
    signatures, model_key = _fetch_model_signatures(
        model_name, service_provider, signatures_index_url
    )

    if not signatures:
        return None

    if hash_prefix:
        # Find signature with matching hash prefix
        logger.info(f"Looking for hash prefix: {hash_prefix}")
        for signature in signatures:
            if signature.get("hash", "").startswith(hash_prefix):
                logger.info(
                    f"Found signature with hash prefix '{hash_prefix}': file='{signature.get('file')}', hash='{signature.get('hash')}'"
                )
                return signature

        logger.warning(
            f"No signature found with hash prefix '{hash_prefix}' for model key '{model_key}'"
        )
        return None
    else:
        # Return latest (first) signature
        latest_signature = signatures[0]
        logger.info(
            f"Found most recent signature for {model_key}: file='{latest_signature.get('file')}', hash='{latest_signature.get('hash')}'"
        )
        return latest_signature


def _parse_signature_date(date_str: str) -> datetime:
    """Parse signature date string to datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")


def verify_signature_info(
    model_name: str,
    service_provider: str,
    signature_info: Signature,
    api_key: str,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Verify against a specific signature info dictionary.
    """
    model_key = generate_model_key(model_name, service_provider)

    try:
        signature_file_path = signature_info["file"]
        expected_hash = signature_info["full_hash"]

        # Convert relative path to full URL
        if signature_file_path.startswith("/"):
            signature_url_full = SIGNATURES_BASE_URL + signature_file_path[1:]
        else:
            signature_url_full = SIGNATURES_BASE_URL + "/" + signature_file_path

        logger.info(f"Fetching signature: {signature_url_full}")
        signature_content: SignatureContent
        signature_content = fetch_json_from_url(signature_url_full)  # type: ignore [assignment]

    except Exception as e:
        logger.exception("Failed to fetch signature")
        return {
            "model_key": model_key,
            "verified": False,
            "error": f"Failed to fetch signature: {e!r}",
            "signature_info": signature_info,
        }

    # Base result structure
    result = {
        "model_key": model_key,
        "signature_url": signature_url_full,
        "expected_hash": expected_hash,
        "signature_hash": signature_info.get("hash", "unknown"),
        "verified": False,
    }

    # Perform live verification with fresh data hash calculation
    logger.info(f"Starting live verification for {model_key}")
    try:
        api_client = APIClient(api_key, verbose=verbose)
        verification_result = api_client.verify_with_fresh_hash(signature_content)

        # Extract the verification status and other details
        result["verified"] = verification_result.get("verified", False)

        # Add additional details from the verification
        if "calculated_hash" in verification_result:
            result["calculated_hash"] = verification_result["calculated_hash"]
        if "actual_tokens" in verification_result:
            result["actual_tokens"] = verification_result["actual_tokens"]
        if "expected_tokens" in verification_result:
            result["expected_tokens"] = verification_result["expected_tokens"]
        if "error" in verification_result:
            result["error"] = verification_result["error"]

        if result["verified"]:
            logger.info(f"Verification successful for {model_key}")
        else:
            logger.warning(f"Verification failed for {model_key}")

    except Exception as e:
        logger.exception("Verification failed")
        result.update(
            {
                "verified": False,
                "error": repr(e),
            }
        )

    return result


def get_signatures_in_time_window(
    model_short_name: str,
    hash_prefix: str,
    time_window_days: int,
    service_provider: str,
    signatures_index_url: str = DEFAULT_SIGNATURES_INDEX_URL,
) -> list[Signature]:
    """
    Get signatures within a time window starting from a specific signature's date.

    Args:
        model_short_name: The short name of the model (e.g., "gpt-4o").
        hash_prefix: Hash prefix to find the starting signature.
        time_window_days: Number of days after the starting signature to include.
        service_provider: The service provider (e.g., "OpenAI").
        signatures_index_url: URL to the main signatures.json index file.

    Returns:
        A list of signature dictionaries within the time window, sorted by closeness to target hash.
    """
    signatures, model_key = _fetch_model_signatures(
        model_short_name, service_provider, signatures_index_url
    )

    if not signatures:
        return []

    logger.info(f"Looking for signatures in time window for model key: {model_key}")

    # Find the starting signature by hash prefix (ignore future signatures)
    current_time = datetime.now()
    start_signature = None
    for signature in signatures:
        if signature.get("hash", "").startswith(hash_prefix):
            start_date_str = signature.get("date")
            if not start_date_str:
                continue

            try:
                start_date = _parse_signature_date(start_date_str)
            except ValueError:
                continue

            if start_date < current_time:  # ignore future signatures during testing
                start_signature = signature
                break

    if not start_signature:
        logger.warning(
            f"No signature found with hash prefix '{hash_prefix}' for model key '{model_key}'"
        )
        return []

    end_date = start_date + timedelta(days=time_window_days)

    # Limit end_date to current time to prevent verification against future signatures
    if end_date > current_time:
        end_date = current_time

    logger.info(
        f"Time window: {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')} ({time_window_days} days)"
    )

    # Filter signatures within the time window
    filtered_signatures = []
    for signature in signatures:
        sig_date_str = signature.get("date")
        if not sig_date_str:
            continue

        try:
            sig_date = _parse_signature_date(sig_date_str)
            # Only include signatures that are not from the future
            if start_date <= sig_date <= end_date and sig_date <= current_time:
                filtered_signatures.append(signature)
        except ValueError:
            logger.warning(f"Failed to parse signature date '{sig_date_str}', skipping")
            continue

    # Sort by closeness to target hash (start_date), with target hash first
    def distance_from_target(signature: Signature) -> float:
        sig_date_str = signature.get("date", "")
        try:
            sig_date = _parse_signature_date(sig_date_str)
            # Calculate absolute time difference from target hash
            time_diff = abs((sig_date - start_date).total_seconds())
            # If this is the target hash itself, give it priority (distance = -1)
            if signature.get("hash", "").startswith(hash_prefix):
                return -1
            return time_diff
        except ValueError:
            # If we can't parse the date, put it last
            return math.inf

    filtered_signatures.sort(key=distance_from_target)

    logger.info(f"Found {len(filtered_signatures)} signatures within time window")
    for sig in filtered_signatures:
        logger.info(f"  - {sig.get('hash', 'unknown')} ({sig.get('date', 'unknown')})")

    return filtered_signatures


def verify_model(
    model_spec: str,
    service_provider: str,
    api_key: str | None = None,
    signature_url: str = DEFAULT_SIGNATURES_INDEX_URL,
    time_window_days: int | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Verify a model against its signatures (supports different verification modes).

    Args:
        model_spec: Model specification in format:
                   - "gpt-4o" (test all signatures until match)
                   - "gpt-4o:now" (test only most recent signature)
                   - "gpt-4o:latest" (test signatures from past 4 days)
                   - "gpt-4o:hash_prefix" (test specific signature or time window)
        service_provider: Provider name (e.g., "OpenAI")
        api_key: API key for the provider
        signature_url: URL to fetch signatures from
        time_window_days: For hash mode, test signatures within N days from the hash date
        verbose: Enable verbose output

    Returns:
        Dictionary with verification results
    """
    # Parse model_spec
    if ":" in model_spec:
        model_name, mode_or_hash = model_spec.split(":", 1)
        if mode_or_hash == "now":
            mode = "now"
            hash_prefix = None
        elif mode_or_hash == "latest":
            mode = "latest"
            hash_prefix = None
        else:
            mode = "hash"
            hash_prefix = mode_or_hash
    else:
        model_name = model_spec
        mode = "all"
        hash_prefix = None

    # Generate model key early for consistent use in all return paths
    model_key = generate_model_key(model_name, service_provider)
    logger.info(f"Starting verification for {model_key} in mode '{mode}'")

    if not api_key:
        return {
            "model_key": model_key,
            "verified": False,
            "error": "API key is required for verification",
        }

    # Handle different verification modes
    if mode == "now":
        signature_info = _get_signature_info(
            model_name, service_provider, signature_url
        )

        if not signature_info:
            return {
                "model_key": model_key,
                "verified": False,
                "error": f"No signature found for {model_key}",
                "mode": "now",
                "days_back": 0,
                "days_forward": 0,
            }

        result = verify_signature_info(
            model_name,
            service_provider,
            signature_info,
            api_key,
            verbose,
        )
        result.update(
            {
                "mode": "now",
                "days_back": 0,
                "days_forward": 0,
            }
        )
        return result

    elif mode == "latest":
        signatures, model_key = _fetch_model_signatures(
            model_name, service_provider, signature_url
        )
        if not signatures:
            return {
                "model_key": model_key,
                "verified": False,
                "error": "No signatures found for model",
                "mode": "latest",
                "days_back": 4,
                "days_forward": 0,
            }

        # Filter signatures to only include those from the past 4 days
        today = datetime.now().date()
        start_date = today - timedelta(days=4)

        logger.info(
            f"Filtering signatures for past 4 days: {start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
        )

        recent_signatures = []
        for signature in signatures:
            sig_date_str = signature.get("date")
            if not sig_date_str:
                continue

            try:
                sig_date = _parse_signature_date(sig_date_str).date()
                # Check if signature date is within our range (inclusive)
                if start_date <= sig_date <= today:
                    recent_signatures.append(signature)
            except ValueError:
                logger.warning(
                    f"Failed to parse signature date '{sig_date_str}', skipping"
                )
                continue

        if not recent_signatures:
            return {
                "model_key": model_key,
                "verified": False,
                "error": "No signatures found in the past 4 days",
                "mode": "latest",
                "days_back": 4,
                "days_forward": 0,
            }

        # Try each signature in the past 4 days starting from the most recent
        logger.info(
            f"Testing against {len(recent_signatures)} signatures from the past 4 days..."
        )

        for i, signature_info in enumerate(recent_signatures):
            signature_hash = signature_info.get("hash", "unknown")
            signature_date = signature_info.get("date", "unknown")
            logger.info(
                f"Testing signature {i + 1}/{len(recent_signatures)}: {signature_hash} ({signature_date})"
            )

            result = verify_signature_info(
                model_name,
                service_provider,
                signature_info,
                api_key,
                verbose,
            )

            # Check if verification was successful
            if result.get("verified"):
                logger.info(f"Match found with signature: {signature_hash}")
                result.update(
                    {
                        "mode": "latest",
                        "matched_hash": signature_hash,
                        "matched_date": signature_date,
                        "days_back": 4,
                        "days_forward": 0,
                    }
                )
                return result
            else:
                logger.info(f"No match with signature {signature_hash}")

        # No matching signature found in the past 4 days
        return {
            "model_key": model_key,
            "verified": False,
            "error": f"Model behavior doesn't match any of the {len(recent_signatures)} signatures from the past 4 days",
            "mode": "latest",
            "days_back": 4,
            "days_forward": 0,
        }

    elif mode == "hash":
        # If time_window_days is specified, get signatures in that window
        if time_window_days is not None:
            if hash_prefix is None:
                return {
                    "model_key": model_key,
                    "verified": False,
                    "error": "Hash prefix is required for time window verification",
                    "mode": "hash_window",
                    "days_back": 0,
                    "days_forward": time_window_days,
                }

            signatures = get_signatures_in_time_window(
                model_name,
                hash_prefix,
                time_window_days,
                service_provider,
                signature_url,
            )
            if not signatures:
                return {
                    "model_key": model_key,
                    "verified": False,
                    "error": f"No signatures found within {time_window_days} days from hash '{hash_prefix}'",
                    "mode": "hash_window",
                    "hash_prefix": hash_prefix,
                    "days_back": 0,
                    "days_forward": time_window_days,
                }

            # Try each signature in the time window starting from the target hash, then closest to it
            logger.info(
                f"Testing against {len(signatures)} signatures within {time_window_days} days from {hash_prefix}..."
            )

            for i, signature_info in enumerate(signatures):
                signature_hash = signature_info.get("hash", "unknown")
                signature_date = signature_info.get("date", "unknown")
                logger.info(
                    f"Testing signature {i + 1}/{len(signatures)}: {signature_hash} ({signature_date})"
                )

                result = verify_signature_info(
                    model_name,
                    service_provider,
                    signature_info,
                    api_key,
                    verbose,
                )

                # Check if verification was successful
                if result.get("verified"):
                    logger.info(f"Match found with signature: {signature_hash}")
                    result.update(
                        {
                            "mode": "hash_window",
                            "hash_prefix": hash_prefix,
                            "matched_hash": signature_hash,
                            "matched_date": signature_date,
                            "days_back": 0,
                            "days_forward": time_window_days,
                        }
                    )
                    return result
                else:
                    logger.info(f"No match with signature {signature_hash}")

            # No matching signature found in time window
            return {
                "model_key": model_key,
                "verified": False,
                "error": f"Model doesn't match any of the {len(signatures)} signatures within {time_window_days} days",
                "mode": "hash_window",
                "hash_prefix": hash_prefix,
                "days_back": 0,
                "days_forward": time_window_days,
            }

        else:
            # Original behavior: test just the specific hash
            signature_info = _get_signature_info(
                model_name, service_provider, signature_url, hash_prefix
            )
            if not signature_info:
                return {
                    "model_key": model_key,
                    "verified": False,
                    "error": f"No signature found with hash prefix '{hash_prefix}'",
                    "mode": mode,
                    "hash_prefix": hash_prefix,
                    "days_back": 0,
                    "days_forward": 0,
                }

            result = verify_signature_info(
                model_name,
                service_provider,
                signature_info,
                api_key,
                verbose,
            )
            result.update(
                {
                    "mode": mode,
                    "hash_prefix": hash_prefix,
                    "days_back": 0,
                    "days_forward": 0,
                }
            )
            return result

    elif mode == "all":
        signatures, model_key = _fetch_model_signatures(
            model_name, service_provider, signature_url
        )
        if not signatures:
            return {
                "model_key": model_key,
                "verified": False,
                "error": "No signatures found for model",
                "mode": mode,
                "days_back": 0,
                "days_forward": 0,
            }

        # Calculate actual time span from available signatures
        oldest_signature_date_str = signatures[-1].get("date")
        actual_days_back = 0
        if oldest_signature_date_str:
            try:
                oldest_date = _parse_signature_date(oldest_signature_date_str).date()
                actual_days_back = (datetime.now().date() - oldest_date).days
            except ValueError:
                logger.warning(
                    f"Failed to parse oldest signature date '{oldest_signature_date_str}'"
                )

        # Try each signature starting from the most recent until we find a match
        logger.info(
            f"Testing against {len(signatures)} signatures starting from most recent..."
        )

        for i, signature_info in enumerate(signatures):
            signature_hash = signature_info.get("hash", "unknown")
            logger.info(
                f"Testing signature {i + 1}/{len(signatures)}: {signature_hash}"
            )

            result = verify_signature_info(
                model_name,
                service_provider,
                signature_info,
                api_key,
                verbose,
            )

            # Check if verification was successful
            if result.get("verified"):
                logger.info(f"Match found with signature: {signature_hash}")
                result.update(
                    {
                        "mode": mode,
                        "matched_hash": signature_hash,
                        "days_back": actual_days_back,
                        "days_forward": 0,
                    }
                )
                return result
            logger.info(f"No match with signature {signature_hash}")

        # No matching signature found
        return {
            "model_key": model_key,
            "verified": False,
            "error": f"Model doesn't match any of the {len(signatures)} available signatures",
            "mode": mode,
            "days_back": actual_days_back,
            "days_forward": 0,
        }

    else:
        return {
            "model_key": model_key,
            "verified": False,
            "error": f"Unknown verification mode: {mode}",
        }
