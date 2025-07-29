from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from requests import HTTPError
from tqdm import tqdm

from .api import get_model_completion
from .api_types import APIParameters, Message, SignatureContent
from .signature import calculate_fresh_signature_hash

logger = logging.getLogger(__name__)


def filter_distribution_by_threshold(
    token_distribution: dict[str, Any], min_probability_threshold: float
) -> dict[str, Any]:
    """
    Filter a token distribution to only include tokens above the probability threshold.
    Args:
        token_distribution: Dictionary of token data with probabilities
        min_probability_threshold: Minimum probability threshold (0.0 to 1.0)
    Returns:
        Filtered token distribution containing only tokens above threshold
    """
    if min_probability_threshold <= 0:
        return token_distribution

    filtered_tokens = {}

    for token_key, token_data in token_distribution.items():
        if isinstance(token_data, dict):
            probability = token_data.get("probability", 0.0)
            if probability >= min_probability_threshold:
                filtered_tokens[token_key] = token_data

    logger.debug(
        f"Filtered {len(token_distribution)} tokens to {len(filtered_tokens)} "
        f"above threshold {min_probability_threshold}"
    )

    return filtered_tokens


class APIClient:
    """Client for making API calls to model providers for live verification using collector modules."""

    def __init__(self, api_key: str, verbose: bool = False):
        self.api_key = api_key
        self.verbose = verbose

    def collect_live_distribution_samples(
        self,
        model_name: str,
        api_parameters: APIParameters,
        path_tokens: list[str],
        target_position: int,
        service_provider: str,
        samples: int,
        expected_tokens: list[str]
        | None = None,  # Add expected tokens for early abortion
    ) -> tuple[list[str], bool]:  # Return tokens and early_abort flag
        """Collect token samples at target position using collector's exact approach.

        Returns:
            Tuple of (collected_tokens, early_abort_detected)
            early_abort_detected is True if we found a token not in expected_tokens
        """

        tokens_at_target = []
        samples_collected = 0
        attempts = 0
        max_attempts = samples * 10  # Match collector's retry logic
        early_abort_detected = False
        expected_token_set = set(expected_tokens) if expected_tokens else None

        # Build the config structure expected by get_model_completion
        config = {
            "model_parameters": api_parameters.copy(),
            "collector_parameters": {"target_position": target_position},
            "service_provider": service_provider.lower(),
            "original_service_provider": service_provider,  # Keep original case for OpenRouter provider selection
        }

        # Get the prompt from api_parameters messages
        prompt = self._extract_random_tokens_from_messages(
            api_parameters.get("messages", [])
        )

        logger.info(f"Collecting {samples} live samples at position {target_position}")
        logger.info(f"Using prompt: '{prompt[:50]}...' (length: {len(prompt)})")
        logger.info(f"Path tokens to match: {path_tokens}")
        if expected_tokens:
            logger.info(f"Expected tokens for early abort detection: {expected_tokens}")

        if self.verbose:
            print(
                f"Collecting {samples} token samples at position {target_position}..."
            )
            if expected_tokens:
                print(f"Expected tokens: {expected_tokens}")

        # Create progress bar for non-verbose mode
        pbar = None
        if not self.verbose:
            pbar = tqdm(
                total=samples, desc="Collecting samples", unit="sample", ncols=80
            )

        # Continue collecting until we have all samples OR we detect an unexpected token
        while samples_collected < samples and attempts < max_attempts:
            attempts += 1
            logger.debug(
                f"Attempt {attempts}/{max_attempts} (collected {samples_collected}/{samples} samples)"
            )

            try:
                # Use collector's get_model_completion function
                completion, _ = get_model_completion(
                    model_name, prompt, self.api_key, config
                )
                # Use collector's exact token extraction logic
                if (
                    not hasattr(completion.choices[0], "logprobs")
                    or completion.choices[0].logprobs is None
                ):
                    logger.debug(
                        f"No logprobs in completion, skipping (attempt {attempts})"
                    )
                    continue

                content_tokens = completion.choices[0].logprobs.content
                token_count = len(content_tokens) if content_tokens else 0
                logger.debug(f"Got response with {token_count} tokens")

                # Check if we have enough tokens to reach the target position
                if token_count <= target_position:
                    logger.debug(
                        f"Response too short ({token_count} tokens), need at least {target_position + 1}, retrying"
                    )
                    continue

                # Log the first few tokens for debugging
                if token_count > 0:
                    first_tokens = [
                        t.token for t in content_tokens[: min(10, token_count)]
                    ]
                    logger.debug(f"First tokens: {first_tokens}")

                # Check if all required path tokens match (collector's path matching logic)
                path_matches = True
                for i, required_token in enumerate(path_tokens):
                    if i >= token_count:
                        path_matches = False
                        logger.debug(
                            f"Not enough tokens to check path at position {i}, skipping"
                        )
                        break

                    actual_token = content_tokens[i].token
                    if actual_token != required_token:
                        path_matches = False
                        logger.debug(
                            f"Token mismatch at position {i}: expected '{required_token}', got '{actual_token}'"
                        )
                        break

                # If path matches, record the token at the target position
                if path_matches:
                    token = content_tokens[target_position].token

                    # EARLY ABORTION CHECK: Only abort if this token was never seen in the original signature
                    # This indicates definitive model behavior change
                    if expected_token_set and token not in expected_token_set:
                        logger.info(
                            f"Early abortion: New token '{token}' detected (not in original signature)"
                        )
                        logger.info(
                            "Model behavior change confirmed - stopping collection"
                        )
                        if self.verbose:
                            print(
                                f"Early detection: New token '{token}' found - model behavior changed!"
                            )
                        early_abort_detected = True
                        tokens_at_target.append(token)  # Include the discovery token
                        samples_collected += 1
                        if pbar:
                            pbar.update(1)
                        break  # Exit the sampling loop immediately

                    # Token is expected - continue collecting for statistical verification
                    tokens_at_target.append(token)
                    samples_collected += 1
                    if self.verbose:
                        print(f"Sample {samples_collected}/{samples}: '{token}'")
                    elif pbar:
                        pbar.update(1)
                    logger.info(
                        f"Collected sample {samples_collected}/{samples}: '{token}' (attempt {attempts})"
                    )
                else:
                    logger.debug("Path didn't match, skipping this response")
            except ImportError:
                raise
            except Exception as e:
                # Check if this is an HTTP error that shouldn't be retried
                if isinstance(e, HTTPError):
                    try:
                        status_code = e.response.status_code
                    except AttributeError:
                        status_code = None

                    # Don't retry the following errors. They indicate issues that won't be resolved by retrying
                    if status_code and 400 <= status_code < 500:
                        if status_code == 401:
                            logger.exception(
                                "Authentication failed (401 Unauthorized). Please check your API key and try again."
                            )
                        elif status_code == 403:
                            logger.exception(
                                "Access forbidden (403 Forbidden). Please check your API key permissions."
                            )
                        else:
                            logger.exception(f"Client error ({status_code})")
                        raise  # Don't retry client errors

                logger.warning(f"API call attempt {attempts} failed.", exc_info=e)
                if attempts >= max_attempts:
                    raise

        if early_abort_detected:
            logger.info(
                f"Collection aborted early after {samples_collected} sample(s) - model change detected"
            )
            if self.verbose:
                print(
                    f"Collection complete: {samples_collected} sample(s) collected (early abort - model changed)"
                )
        else:
            logger.info(
                f"Collected {len(tokens_at_target)} live samples: {tokens_at_target}"
            )
            if self.verbose:
                print(f"Collection complete: {len(tokens_at_target)} samples collected")

        # Close progress bar
        if pbar:
            pbar.close()

        return tokens_at_target, early_abort_detected

    def _extract_random_tokens_from_messages(self, messages: list[Message]) -> str:
        """Extract the random tokens from the messages structure."""
        for message in messages:
            content = message.get("content", "")
            if isinstance(content, str) and "{{random_tokens}}" not in content:
                # This might be the message with the actual random tokens
                return content
        return ""

    def verify_with_fresh_hash(
        self,
        signature_content: SignatureContent,
    ) -> dict[str, Any]:
        """
        Perform live verification with fresh data hash calculation.
        This method:
        1. Samples the model live using parameters from the signature
        2. Calculates a fresh hash from the live data
        3. Compares the fresh hash with the expected hash from the signature
        4. Returns a simplified verification result
        """
        metadata = signature_content.get("metadata", {})
        api_parameters = signature_content["api_parameters"]
        configuration = signature_content.get("configuration", {})
        distribution_results = signature_content.get("distribution_results", {})
        path_analysis = signature_content.get("path_analysis", {})
        signature_parameters = signature_content.get("signature_parameters", {})

        model_name = metadata.get("model_name", "")
        service_provider = metadata.get("service_provider", "OpenAI")
        target_position = configuration.get("target_position", 0)
        path_tokens = path_analysis.get("path_tokens", [])
        expected_hash = metadata.get("signature_hash", "")

        if not signature_parameters:
            logger.warning("No signature_parameters found in signature file")
            return {
                "verified": False,
                "error": "No signature_parameters found in signature file",
            }

        # Get the expected distribution from signature (keys only, as per collector)
        # Apply min_probability_threshold filtering if it was used during signature generation
        tokens_section = distribution_results.get("tokens", {})
        min_prob_threshold = configuration.get("min_probability_threshold", 0.0)

        if min_prob_threshold > 0:
            logger.debug(
                f"Applying min_probability_threshold filter for verification: {min_prob_threshold}"
            )
            # Import the filter function from verifier
            tokens_section = filter_distribution_by_threshold(
                tokens_section, min_prob_threshold
            )

        expected_tokens = list(tokens_section.keys())

        try:
            # Collect live samples using collector's approach
            live_samples, early_abort_detected = self.collect_live_distribution_samples(
                model_name,
                api_parameters,
                path_tokens,
                target_position,
                service_provider,
                samples=10,
                expected_tokens=expected_tokens,
            )
            # Create distribution from live samples

            live_distribution = Counter(live_samples)
            actual_tokens = list(live_distribution.keys())

            # Build config structure for hash calculation
            config = {
                "model_parameters": {
                    "seed": api_parameters.get("seed"),
                    "messages": api_parameters.get("messages"),
                },
                "collector_parameters": {
                    "target_position": configuration.get("target_position")
                },
                "complete_messages": configuration.get(
                    "complete_messages", api_parameters.get("messages")
                ),
            }

            # Build response_data structure with fresh live data
            response_data = {
                "system_fingerprint": metadata.get("system_fingerprint"),
                "path_tokens": path_tokens,
                "target_distribution": actual_tokens,  # Fresh tokens from live sampling
                "api_params": api_parameters,
            }

            # Calculate fresh hash from live data
            calculated_hash = calculate_fresh_signature_hash(
                signature_parameters, config, response_data
            )

            # Compare hashes
            hash_matches = calculated_hash == expected_hash

            # Check if we collected enough samples for reliable verification
            samples_required = 1  # The number of samples we requested
            samples_actual = len(live_samples)
            insufficient_samples = samples_actual < samples_required

            # If early abort was detected or not enough samples were collected, verification should fail regardless of other matches
            # Early abort means we found a token that wasn't in the original signature
            if early_abort_detected or insufficient_samples:
                verified = False
            else:
                verified = hash_matches
            result = {
                "verified": verified,
                "hash_matches": hash_matches,
                "expected_hash": expected_hash,
                "calculated_hash": calculated_hash,
                "expected_tokens": expected_tokens,
                "actual_tokens": actual_tokens,
                "live_samples": live_samples,
                "early_abort_detected": early_abort_detected,
                "samples_required": samples_required,
                "samples_actual": samples_actual,
                "insufficient_samples": insufficient_samples,
            }

            if verified:
                logger.info("Verification successful: Hash matches")
            else:
                if early_abort_detected:
                    logger.warning(
                        "Verification failed: Model behavior change detected (early abort)"
                    )
                elif insufficient_samples:
                    logger.warning(
                        f"Verification failed: Insufficient samples collected ({samples_actual}/{samples_required})"
                    )
                else:
                    logger.warning("Verification failed: Hash mismatch")
                    if expected_tokens != actual_tokens:
                        removed = set(expected_tokens) - set(actual_tokens)
                        added = set(actual_tokens) - set(expected_tokens)
                        if removed:
                            logger.warning(f"Missing tokens: {list(removed)}")
                        if added:
                            logger.warning(f"New tokens detected: {list(added)}")

            return result

        except Exception as e:
            logger.exception("Live verification with fresh hash failed")
            return {
                "verified": False,
                "error": repr(e),
                "expected_tokens": expected_tokens,
                "actual_tokens": None,
            }
