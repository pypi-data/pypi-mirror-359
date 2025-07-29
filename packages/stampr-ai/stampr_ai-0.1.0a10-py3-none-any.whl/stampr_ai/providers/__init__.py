"""Provider implementations for different AI service providers."""

from .openai import get_openai_completion as get_openai_completion
from .openrouter import get_openrouter_completion as get_openrouter_completion
