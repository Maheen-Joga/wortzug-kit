import json

from wortzug.cli import main, render_text
from wortzug.core import SCHEMA_EXAMPLE
from wortzug.schema import parse_result

from .test_core import ScriptedProvider, VALID


def test_render_text_shows_variants_and_lexicon():
    text = render_text(parse_result(SCHEMA_EXAMPLE))
    assert "I don't have time." in text
    assert "[formal]" in text and "[colloquial]" in text
    assert "die Zeit" in text


def test_missing_text_returns_usage_error(capsys):
    assert main(["   "]) == 2
    assert "no text" in capsys.readouterr().err


def test_cli_reports_missing_key_without_traceback(monkeypatch, capsys):
    monkeypatch.delenv("WORTZUG_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert main(["Guten Tag"]) == 1
    assert "no API key" in capsys.readouterr().err


def test_json_output_round_trips(monkeypatch, capsys):
    import wortzug.cli as cli
    monkeypatch.setattr(cli, "GeminiProvider", lambda **kw: ScriptedProvider(VALID))
    assert main(["--json", "Ich habe keine Zeit."]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["translation"] == "I don't have time."
    assert data["lexicon"][1]["gender"] == "die"
