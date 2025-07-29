"""Test: All Signatures Verification"""

import pytest
from freezegun import freeze_time

from stampr_ai import verify_model
from stampr_ai.config import get_openai_api_key


@freeze_time("2025-06-23 23:00:00")
@pytest.mark.vcr
def test_all_signatures() -> None:
    """Test verification against all signatures"""
    api_key = get_openai_api_key() or "dummy_api_key"

    result = verify_model("gpt-4o", "OpenAI", api_key)
    assert result["mode"] == "all"
    assert result["verified"]
