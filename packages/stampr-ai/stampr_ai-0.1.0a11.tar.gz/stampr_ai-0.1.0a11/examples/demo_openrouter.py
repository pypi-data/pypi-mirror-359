#!/usr/bin/env python3
"""OpenRouter Comprehensive Demo - Test multiple models and providers"""

from typing import Literal

from stampr_ai import get_api_key, verify_model


def main() -> Literal[0, 1]:
    api_key = get_api_key("openrouter")
    if not api_key:
        print("OpenRouter API key not found")
        return 1

    result = verify_model("Llama4_17b:latest", "OpenRouter/Lambda", api_key)
    print(f"Verified: {result['verified']}")
    print(f"Mode: {result['mode']}")
    return 0


if __name__ == "__main__":
    exit(main())
