import json

import pytest

from wortzug.core import TranslationError, build_prompt, strip_code_fences, translate
from wortzug.core import SCHEMA_EXAMPLE


class ScriptedProvider:
    """Returns queued replies in order and records the prompts it was sent."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return self.replies.pop(0)


VALID = json.dumps(SCHEMA_EXAMPLE, ensure_ascii=False)


def test_translate_returns_result_for_valid_reply():
    result = translate("Ich habe keine Zeit.", ScriptedProvider(VALID))
    assert result.translation == "I don't have time."
    assert {v.register for v in result.variants} == {"formal", "colloquial"}


def test_code_fenced_reply_is_accepted():
    fenced = f"```json\n{VALID}\n```"
    assert translate("Ich habe keine Zeit.", ScriptedProvider(fenced)).source == "Ich habe keine Zeit."


def test_invalid_reply_is_retried_with_error_feedback():
    provider = ScriptedProvider("not json at all", VALID)
    result = translate("Ich habe keine Zeit.", provider)
    assert result.translation == "I don't have time."
    assert len(provider.prompts) == 2
    assert "previous reply was rejected" in provider.prompts[1]


def test_gives_up_after_max_attempts():
    provider = ScriptedProvider("nope", "still nope")
    with pytest.raises(TranslationError):
        translate("Ich habe keine Zeit.", provider, max_attempts=2)


def test_empty_text_is_rejected_before_calling_provider():
    provider = ScriptedProvider()
    with pytest.raises(ValueError):
        translate("   ", provider)
    assert provider.prompts == []


def test_prompt_includes_target_language_and_text():
    prompt = build_prompt("Guten Morgen", "French")
    assert "into French" in prompt
    assert "Guten Morgen" in prompt


def test_strip_code_fences_handles_plain_text():
    assert strip_code_fences("  {\"a\": 1}  ") == '{"a": 1}'
