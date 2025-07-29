"""Command-line interface for stampr_ai verification."""

import argparse
import sys
from typing import NoReturn

from . import __version__, verify_model
from .config import get_api_key


def main() -> NoReturn:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Verify AI model signatures with stampr_ai"
    )
    parser.add_argument(
        "--version", action="version", version=f"stampr_ai {__version__}"
    )
    parser.add_argument(
        "model",
        help="Model to verify (e.g., 'gpt-4o:now', 'gpt-4o:latest', 'gpt-4o:bede20', 'gpt-4o')",
    )
    parser.add_argument("provider", help="Provider name (e.g., 'OpenAI', 'OpenRouter')")
    parser.add_argument(
        "--api-key", help="API key for the provider (or set via environment variable)"
    )
    parser.add_argument(
        "--time-window", type=int, help="Time window in days for signature matching"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Get API key from argument or environment
    api_key = args.api_key or get_api_key(args.provider)

    if not api_key:
        print(f"Error: No API key found for {args.provider}")
        print(
            f"Set {args.provider.upper()}_API_KEY environment variable or use --api-key"
        )
        sys.exit(1)

    try:
        result = verify_model(
            args.model,
            args.provider,
            api_key,
            verbose=args.verbose,
            time_window_days=args.time_window,
        )

        if args.verbose:
            print(f"Verification result: {result}")

        if result.get("verified"):
            print("✓ Verification PASSED")
            sys.exit(0)
        else:
            print("✗ Verification FAILED")
            if "error" in result:
                print(f"Error: {result['error']}")
            sys.exit(1)

    except Exception as e:
        print(f"Error during verification: {e!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
