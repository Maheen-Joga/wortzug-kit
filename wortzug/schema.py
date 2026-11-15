"""Typed result objects and strict validation for model output.

Model output is untrusted text. Everything is checked here before it reaches
callers, so a malformed reply becomes a SchemaError with the failing path,
not a KeyError three layers down.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REGISTERS = ("formal", "colloquial")
PARTS_OF_SPEECH = (
    "noun", "verb", "adjective", "adverb", "pronoun",
    "preposition", "conjunction", "article", "interjection", "other",
)
GENDERS = ("der", "die", "das")


class SchemaError(ValueError):
    """Raised when model output does not match the expected structure."""

    def __init__(self, path: str, message: str):
        super().__init__(f"{path}: {message}")
        self.path = path


@dataclass(frozen=True)
class Variant:
    register: str  # "formal" or "colloquial"
    text: str
    translation: str


@dataclass(frozen=True)
class LexiconEntry:
    word: str
    translation: str
    part_of_speech: str
    gender: str | None = None  # only for nouns: der / die / das
    note: str | None = None


@dataclass(frozen=True)
class TranslationResult:
    source: str
    target_language: str
    translation: str
    variants: list[Variant] = field(default_factory=list)
    lexicon: list[LexiconEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target_language": self.target_language,
            "translation": self.translation,
            "variants": [v.__dict__ for v in self.variants],
            "lexicon": [e.__dict__ for e in self.lexicon],
        }


def _require_str(data: dict, key: str, path: str, *, allow_empty: bool = False) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise SchemaError(f"{path}.{key}", "must be a string")
    if not allow_empty and not value.strip():
        raise SchemaError(f"{path}.{key}", "must not be empty")
    return value.strip()


def _require_object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise SchemaError(path, "must be an object")
    return value


def _parse_variant(raw: Any, path: str) -> Variant:
    data = _require_object(raw, path)
    register = _require_str(data, "register", path).lower()
    if register not in REGISTERS:
        raise SchemaError(f"{path}.register", f"must be one of {REGISTERS}")
    return Variant(
        register=register,
        text=_require_str(data, "text", path),
        translation=_require_str(data, "translation", path),
    )


def _parse_lexicon_entry(raw: Any, path: str) -> LexiconEntry:
    data = _require_object(raw, path)
    pos = _require_str(data, "part_of_speech", path).lower()
    if pos not in PARTS_OF_SPEECH:
        raise SchemaError(f"{path}.part_of_speech", f"must be one of {PARTS_OF_SPEECH}")

    gender = data.get("gender")
    if gender is not None:
        if not isinstance(gender, str) or gender.lower() not in GENDERS:
            raise SchemaError(f"{path}.gender", f"must be one of {GENDERS} or null")
        gender = gender.lower()
        if pos != "noun":
            raise SchemaError(f"{path}.gender", "is only valid for nouns")

    note = data.get("note")
    if note is not None and not isinstance(note, str):
        raise SchemaError(f"{path}.note", "must be a string or null")

    return LexiconEntry(
        word=_require_str(data, "word", path),
        translation=_require_str(data, "translation", path),
        part_of_speech=pos,
        gender=gender,
        note=note.strip() if note else None,
    )


def parse_result(data: Any) -> TranslationResult:
    """Validate a decoded JSON object and return a TranslationResult."""
    root = _require_object(data, "$")
    variants_raw = root.get("variants", [])
    lexicon_raw = root.get("lexicon", [])
    if not isinstance(variants_raw, list):
        raise SchemaError("$.variants", "must be a list")
    if not isinstance(lexicon_raw, list):
        raise SchemaError("$.lexicon", "must be a list")

    return TranslationResult(
        source=_require_str(root, "source", "$"),
        target_language=_require_str(root, "target_language", "$"),
        translation=_require_str(root, "translation", "$"),
        variants=[_parse_variant(v, f"$.variants[{i}]") for i, v in enumerate(variants_raw)],
        lexicon=[_parse_lexicon_entry(e, f"$.lexicon[{i}]") for i, e in enumerate(lexicon_raw)],
    )
