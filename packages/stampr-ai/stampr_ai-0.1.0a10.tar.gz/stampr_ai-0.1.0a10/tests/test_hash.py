"""Test: Specific Hash Verification"""

import pytest
from freezegun import freeze_time

from stampr_ai import verify_model
from stampr_ai.config import get_openai_api_key


@freeze_time("2025-06-26 10:00:00")
@pytest.mark.vcr
def test_hash_signature_fail() -> None:
    """Test verification against specific hash"""
    api_key = get_openai_api_key() or "dummy_api_key"

    result = verify_model("gpt-4o:1337", "OpenAI", api_key)

    assert result["mode"] == "hash"
    assert not result["verified"]


@pytest.mark.vcr
def test_hash_signature_success() -> None:
    """Test verification against specific hash"""
    api_key = get_openai_api_key() or "dummy_api_key"

    result = verify_model("gpt-4o:615a76", "OpenAI", api_key)

    assert result["mode"] == "hash"
    assert result["verified"]
