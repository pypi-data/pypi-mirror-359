#!/usr/bin/env python3
"""
Demo: Time Window Verification
Test against signatures within a time window from a specific hash
"""

from typing import Literal

from stampr_ai import get_openai_api_key, verify_model


def main() -> Literal[0, 1]:
    api_key = get_openai_api_key()
    if not api_key:
        print("OpenAI API key not found")
        return 1

    result = verify_model("gpt-4o:615a76", "OpenAI", api_key, time_window_days=30)
    print(f"Verified: {result['verified']}")
    print(f"Mode: {result['mode']}")
    print(f"Days forward: {result.get('days_forward', 'N/A')}")
    return 0


if __name__ == "__main__":
    exit(main())
