import io
import json
import urllib.error

import pytest

from wortzug.providers import GeminiProvider, ProviderError, build_gemini_request, extract_gemini_text


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def make_opener(payload):
    calls = []

    def opener(request, timeout):
        calls.append((request, timeout))
        return FakeResponse(json.dumps(payload).encode())

    return opener, calls


def test_key_is_sent_in_header_not_url():
    request = build_gemini_request("hi", "SECRET-KEY-123", "gemini-test")
    assert request.get_header("X-goog-api-key") == "SECRET-KEY-123"
    assert "SECRET-KEY-123" not in request.full_url
    assert request.full_url.endswith("/models/gemini-test:generateContent")


def test_request_body_asks_for_json():
    request = build_gemini_request("hello", "k", "m")
    body = json.loads(request.data)
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    assert body["contents"][0]["parts"][0]["text"] == "hello"


def test_complete_extracts_text_from_response():
    reply = {"candidates": [{"content": {"parts": [{"text": "{\"ok\": true}"}]}}]}
    opener, calls = make_opener(reply)
    provider = GeminiProvider(api_key="k", opener=opener)
    assert provider.complete("prompt") == '{"ok": true}'
    assert len(calls) == 1


def test_missing_key_fails_fast(monkeypatch):
    monkeypatch.delenv("WORTZUG_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="no API key"):
        GeminiProvider()


def test_repr_never_shows_key():
    assert "SECRET" not in repr(GeminiProvider(api_key="SECRET"))


def test_unexpected_response_shape_raises():
    with pytest.raises(ProviderError):
        extract_gemini_text({"candidates": []})


def test_http_error_reports_status_only():
    def opener(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO(b"echoed key"))

    with pytest.raises(ProviderError) as exc:
        GeminiProvider(api_key="k", opener=opener).complete("p")
    assert "HTTP 403" in str(exc.value)
    assert "echoed key" not in str(exc.value)
