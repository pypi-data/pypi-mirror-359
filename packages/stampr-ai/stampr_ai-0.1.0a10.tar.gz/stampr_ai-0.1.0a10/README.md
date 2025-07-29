# stampr_ai

<div align="center">
  <img src="https://www.stampr-ai.com/images/stampr.png" alt="Stampr AI Logo" width="200"/>
</div>

[![PyPI version](https://badge.fury.io/py/stampr-ai.svg)](https://badge.fury.io/py/stampr-ai)
[![Python versions](https://img.shields.io/pypi/pyversions/stampr-ai.svg)](https://pypi.org/project/stampr-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Live verification of AI model signatures to detect model changes and ensure consistent AI behaviour.**

## Installation

```bash
pip install stampr-ai
```

## Setup

```python
import os
os.environ['OPENAI_API_KEY'] = "your_openai_api_key_here"
os.environ['OPENROUTER_API_KEY'] = "your_openrouter_api_key_here"
os.environ['HF_TOKEN'] = "your_huggingface_token_here"
```

## Quick Start

Install stampr_ai and run verification:

```bash
pip install stampr_ai

# CLI usage - most recent signature only
stampr gpt-4o:now OpenAI

# CLI usage - past 4 days (more robust)
stampr gpt-4o:latest OpenAI

# Or with explicit API key
stampr gpt-4o:latest OpenAI --api-key $OPENAI_API_KEY
```

## Python Usage

### OpenAI Example

```python
from stampr_ai import verify_model
import os

# Verify model matches a specific signature hash
result = verify_model("gpt-4o:bede20", "OpenAI", os.environ['OPENAI_API_KEY'])

if result['verified']:
    print("Signature Verified.")
else:
    print("Signature mismatch!")
print(f"Expected: {result['live_verification_result']['expected_tokens']}")
print(f"Actual: {result['live_verification_result']['actual_tokens']}")
```

### OpenRouter Example

```python
from stampr_ai import verify_model
import os

# OpenRouter example - robust verification
result = verify_model("Llama4_17b:latest", "OpenRouter/Parasail", os.environ['OPENROUTER_API_KEY'])

if result['verified']:
    print("Signature Verified.")
else:
    print("Signature mismatch!")
print(f"Expected: {result['live_verification_result']['expected_tokens']}")
print(f"Actual: {result['live_verification_result']['actual_tokens']}")
```

## License

MIT License - see [LICENSE](LICENSE) for details. 