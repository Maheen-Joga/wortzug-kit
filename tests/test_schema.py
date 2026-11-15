import pytest

from wortzug.schema import SchemaError, parse_result

GOOD = {
    "source": "Ich habe keine Zeit.",
    "target_language": "English",
    "translation": "I don't have time.",
    "variants": [{"register": "Formal", "text": "x", "translation": "y"}],
    "lexicon": [
        {"word": "Zeit", "translation": "time", "part_of_speech": "Noun", "gender": "DIE"},
        {"word": "habe", "translation": "have", "part_of_speech": "verb"},
    ],
}


def test_valid_payload_parses_and_normalises_case():
    result = parse_result(GOOD)
    assert result.variants[0].register == "formal"
    assert result.lexicon[0].gender == "die"
    assert result.lexicon[0].part_of_speech == "noun"
    assert result.lexicon[1].gender is None


def test_gender_on_non_noun_is_rejected():
    bad = {**GOOD, "lexicon": [{"word": "habe", "translation": "have",
                                "part_of_speech": "verb", "gender": "die"}]}
    with pytest.raises(SchemaError) as exc:
        parse_result(bad)
    assert exc.value.path == "$.lexicon[0].gender"


def test_unknown_register_is_rejected_with_path():
    bad = {**GOOD, "variants": [{"register": "slangy", "text": "x", "translation": "y"}]}
    with pytest.raises(SchemaError) as exc:
        parse_result(bad)
    assert exc.value.path == "$.variants[0].register"


def test_missing_translation_is_rejected():
    bad = {k: v for k, v in GOOD.items() if k != "translation"}
    with pytest.raises(SchemaError, match="translation"):
        parse_result(bad)


def test_non_object_root_is_rejected():
    with pytest.raises(SchemaError):
        parse_result(["not", "an", "object"])


def test_empty_variants_and_lexicon_are_allowed():
    result = parse_result({**GOOD, "variants": [], "lexicon": []})
    assert result.variants == [] and result.lexicon == []
