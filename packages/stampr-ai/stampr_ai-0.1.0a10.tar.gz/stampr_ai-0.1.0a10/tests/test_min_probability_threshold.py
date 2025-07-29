"""Test min_probability_threshold filtering functionality."""

from stampr_ai.api_client import filter_distribution_by_threshold


def test_filter_distribution_by_threshold_no_filtering() -> None:
    """Test that no filtering occurs when threshold is 0."""
    token_distribution = {
        "token1": {"token_string": "token1", "probability": 0.5, "count": 5},
        "token2": {"token_string": "token2", "probability": 0.3, "count": 3},
        "token3": {"token_string": "token3", "probability": 0.2, "count": 2},
    }

    result = filter_distribution_by_threshold(token_distribution, 0.0)
    assert result == token_distribution
    assert len(result) == 3


def test_filter_distribution_by_threshold_exact_threshold() -> None:
    """Test that tokens exactly at threshold are included."""
    token_distribution = {
        # Exactly at threshold
        "token1": {"token_string": "token1", "probability": 0.02, "count": 1},
        # Below threshold
        "token2": {"token_string": "token2", "probability": 0.019, "count": 1},
    }

    result = filter_distribution_by_threshold(token_distribution, 0.02)

    # Only token1 should remain (probability == 0.02)
    expected = {
        "token1": {"token_string": "token1", "probability": 0.02, "count": 1},
    }

    assert result == expected
    assert len(result) == 1
    assert "token2" not in result


def test_filter_distribution_by_threshold_empty_distribution() -> None:
    """Test that empty distribution returns empty result."""
    result = filter_distribution_by_threshold({}, 0.5)
    assert result == {}


def test_filter_distribution_by_threshold_all_filtered() -> None:
    """Test that all tokens below threshold are filtered out."""
    token_distribution = {
        "token1": {"token_string": "token1", "probability": 0.01, "count": 1},
        "token2": {"token_string": "token2", "probability": 0.005, "count": 1},
    }

    result = filter_distribution_by_threshold(token_distribution, 0.02)
    assert result == {}


def test_filter_distribution_by_threshold_malformed_data() -> None:
    """Test that malformed token data is handled gracefully."""
    token_distribution = {
        "token1": {"token_string": "token1", "probability": 0.5, "count": 5},
        "token2": "invalid_format",  # Not a dict
        "token3": {"token_string": "token3", "count": 3},  # Missing probability
    }

    result = filter_distribution_by_threshold(token_distribution, 0.2)

    # Only token1 should remain (valid format and above threshold)
    expected = {
        "token1": {"token_string": "token1", "probability": 0.5, "count": 5},
    }

    assert result == expected
    assert len(result) == 1
