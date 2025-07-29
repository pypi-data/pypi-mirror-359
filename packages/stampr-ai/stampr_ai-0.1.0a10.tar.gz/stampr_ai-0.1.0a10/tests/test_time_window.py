"""Test: Time Window Verification"""

import pytest
from freezegun import freeze_time

from stampr_ai import verify_model
from stampr_ai.config import get_openai_api_key


@freeze_time("2025-06-26 10:00:00")
@pytest.mark.vcr
def test_time_window() -> None:
    """Test verification with time window"""
    api_key = get_openai_api_key() or "dummy_api_key"

    result = verify_model("gpt-4o:615a76", "OpenAI", api_key, time_window_days=30)
    assert result["mode"] == "hash_window"
    assert result["verified"]
    assert result["days_forward"] == 30
