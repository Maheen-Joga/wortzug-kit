"""The translate() entry point: prompt, call the provider, validate, retry once."""

from __future__ import annotations

import json
import re

from .providers import Provider
from .schema import SchemaError, TranslationResult, parse_result

_FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)

SCHEMA_EXAMPLE = {
    "source": "Ich habe keine Zeit.",
    "target_language": "English",
    "translation": "I don't have time.",
    "variants": [
        {"register": "formal", "text": "Ich habe leider keine Zeit.", "translation": "Unfortunately, I don't have time."},
        {"register": "colloquial", "text": "Ich hab keine Zeit.", "translation": "I've got no time."},
    ],
    "lexicon": [
        {"word": "Ich", "translation": "I", "part_of_speech": "pronoun", "gender": None, "note": None},
        {"word": "Zeit", "translation": "time", "part_of_speech": "noun", "gender": "die", "note": None},
    ],
}


class TranslationError(RuntimeError):
    """The model did not return valid output after all attempts."""


def build_prompt(text: str, target_language: str = "English") -> str:
    return (
        "You are a German tutor. Translate the German text below into "
        f"{target_language}. Return ONLY a JSON object with this shape, no commentary:\n"
        f"{json.dumps(SCHEMA_EXAMPLE, ensure_ascii=False, indent=2)}\n\n"
        "Rules: include a formal and a colloquial variant when the text has a register that "
        "can change (for example Sie/du). Give a lexicon entry for each content word. "
        "Use der/die/das only for nouns and null otherwise.\n\n"
        f"German text:\n{text}"
    )


def strip_code_fences(raw: str) -> str:
    match = _FENCE.match(raw)
    return match.group(1) if match else raw.strip()


def translate(
    text: str,
    provider: Provider,
    target_language: str = "English",
    max_attempts: int = 2,
) -> TranslationResult:
    """Translate German text and return a validated TranslationResult.

    Model replies that fail to parse or validate are retried once with the
    error fed back, then raise TranslationError.
    """
    text = text.strip()
    if not text:
        raise ValueError("text must not be empty")

    prompt = build_prompt(text, target_language)
    last_error: Exception | None = None
    for _ in range(max_attempts):
        raw = provider.complete(prompt)
        try:
            return parse_result(json.loads(strip_code_fences(raw)))
        except (json.JSONDecodeError, SchemaError) as exc:
            last_error = exc
            prompt += (
                f"\n\nYour previous reply was rejected: {exc}. "
                "Return only valid JSON that matches the shape above."
            )
    raise TranslationError(f"no valid reply after {max_attempts} attempts: {last_error}")
