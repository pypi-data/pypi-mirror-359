#!/usr/bin/env python3
"""
Demo: All Signatures Verification
Test against all signatures starting from most recent until match found
"""

from typing import Literal

from stampr_ai import get_openai_api_key, verify_model


def main() -> Literal[0, 1]:
    api_key = get_openai_api_key()
    if not api_key:
        print("OpenAI API key not found")
        return 1

    result = verify_model("gpt-4o", "OpenAI", api_key)
    print(f"Verified: {result['verified']}")
    print(f"Mode: {result['mode']}")
    return 0


if __name__ == "__main__":
    exit(main())
