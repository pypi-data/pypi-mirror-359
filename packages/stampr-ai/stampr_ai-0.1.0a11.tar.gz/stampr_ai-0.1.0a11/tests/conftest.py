import os
from typing import Any

import freezegun
import pytest
from pytest_recording.utils import ConfigType

# Disable tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configure freezegun to ignore transformers to avoid tokenizer errors
freezegun.configure(extend_ignore_list=["transformers", "huggingface_hub"])


def remove_org(response: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    response["headers"].pop("openai-organization", None)
    return response


@pytest.fixture(scope="module")
def vcr_config() -> ConfigType:
    return {
        "before_record_response": remove_org,
        "filter_headers": [
            "Authorization",
        ],
        "ignore_hosts": [
            "huggingface.co",
            "hf.co",  # HF CDN
            "*.hf.co",  # HF CDN (it needs both)
            "windows.net",  # tiktoken
        ],
    }
