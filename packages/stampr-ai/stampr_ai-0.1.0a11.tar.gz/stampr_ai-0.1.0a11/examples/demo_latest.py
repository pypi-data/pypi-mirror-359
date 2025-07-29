#!/usr/bin/env python3
"""
Demo: Most Recent Signature Verification
"""

from typing import Literal

from stampr_ai import verify_model
from stampr_ai.config import get_openai_api_key


def main() -> Literal[0, 1]:
    api_key = get_openai_api_key()
    if not api_key:
        print("OpenAI API key not found")
        return 1

    result = verify_model("gpt-4o:latest", "OpenAI", api_key)
    print(f"Verified: {result['verified']}")
    print(f"Mode: {result['mode']}")
    return 0


if __name__ == "__main__":
    exit(main())
