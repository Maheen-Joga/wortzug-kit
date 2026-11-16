"""wortzug-kit: structured German translation with register variants and a lexicon."""

from .core import TranslationError, translate
from .providers import GeminiProvider, ProviderError
from .schema import (
    LexiconEntry,
    SchemaError,
    TranslationResult,
    Variant,
)

__all__ = [
    "GeminiProvider",
    "LexiconEntry",
    "ProviderError",
    "SchemaError",
    "TranslationError",
    "TranslationResult",
    "Variant",
    "translate",
]
__version__ = "0.1.0"
