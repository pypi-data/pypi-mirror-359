"""Test: OpenRouter Most Recent Signature Verification"""

import os

import pytest
from freezegun import freeze_time

from stampr_ai import verify_model
from stampr_ai.config import get_api_key


@freeze_time("2025-06-27 23:00:00")
@pytest.mark.vcr
def test_openrouter_llama4_latest() -> None:
    """Test signatures from the latest Llama4_17b version via OpenRouter/Lambda"""
    api_key = get_api_key("openrouter") or "dummy_api_key"
    os.environ["HF_HUB_DISABLE_XET"] = "1"

    result = verify_model("Llama4_17b:latest", "OpenRouter/Lambda", api_key)

    assert result["mode"] == "latest"
    assert result["verified"]
