"""Test: Latest Mode Verification (Past 4 Days)"""

import pytest
from freezegun import freeze_time

from stampr_ai import verify_model
from stampr_ai.config import get_openai_api_key


@freeze_time("2025-06-23 23:00:00")
@pytest.mark.vcr
def test_latest_signature() -> None:
    """Test verification against signatures from past 4 days"""
    api_key = get_openai_api_key() or "dummy_api_key"

    result = verify_model("gpt-4o:latest", "OpenAI", api_key)

    assert result["verified"]  # Should always pass as it's against OpenAI
    assert result["mode"] == "latest"
    assert result["days_back"] == 4
