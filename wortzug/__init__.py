"""wortzug-kit: structured German translation with register variants and a lexicon."""

from .schema import LexiconEntry, SchemaError, TranslationResult, Variant

__all__ = [
    "LexiconEntry",
    "SchemaError",
    "TranslationResult",
    "Variant",
]
__version__ = "0.1.0"
