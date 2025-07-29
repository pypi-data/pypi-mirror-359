#!/usr/bin/env python3
"""
Demo: Specific Hash Verification
Test against one specific signature by hash prefix
"""

from typing import Literal

from stampr_ai import get_openai_api_key, verify_model


def main() -> Literal[0, 1]:
    api_key = get_openai_api_key()
    if not api_key:
        print("OpenAI API key not found")
        return 1

    result = verify_model("gpt-4o:a0df75", "OpenAI", api_key)
    print(f"Verified: {result['verified']}")
    print(f"Mode: {result['mode']}")
    return 0


if __name__ == "__main__":
    exit(main())
