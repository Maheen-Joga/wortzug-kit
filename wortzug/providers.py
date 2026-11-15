"""Model providers. Each provider takes a prompt string and returns raw text.

GeminiProvider uses only the standard library, so the package has no runtime
dependencies. The key is sent in a request header, never in the URL, so it
does not end up in proxy or server logs.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Callable, Protocol

DEFAULT_MODEL = os.environ.get("WORTZUG_MODEL", "gemini-2.5-flash")
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class ProviderError(RuntimeError):
    """The provider call failed or returned an unexpected shape."""


class Provider(Protocol):
    def complete(self, prompt: str) -> str: ...


def build_gemini_request(prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> urllib.request.Request:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }
    return urllib.request.Request(
        ENDPOINT.format(model=model),
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )


def extract_gemini_text(payload: dict) -> str:
    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("unexpected response shape from Gemini") from exc


class GeminiProvider:
    """Bring-your-own-key provider. Pass api_key or set GEMINI_API_KEY / WORTZUG_API_KEY."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        opener: Callable[..., object] = urllib.request.urlopen,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.environ.get("WORTZUG_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ProviderError("no API key: pass api_key or set WORTZUG_API_KEY / GEMINI_API_KEY")
        self.model = model
        self._opener = opener
        self._timeout = timeout

    def complete(self, prompt: str) -> str:
        request = build_gemini_request(prompt, self.api_key, self.model)
        try:
            with self._opener(request, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # Report the status only. The response body can echo request details.
            raise ProviderError(f"Gemini returned HTTP {exc.code}") from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderError(f"could not reach Gemini: {exc.__class__.__name__}") from None
        return extract_gemini_text(payload)

    def __repr__(self) -> str:  # never show the key
        return f"GeminiProvider(model={self.model!r}, api_key=***)"
