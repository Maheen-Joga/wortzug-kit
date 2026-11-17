# wortzug-kit

Structured German translation. Give it a German sentence and get back:

- a plain English translation
- **register variants**: the same sentence in formal (*Sie*) and colloquial (*du*) form, each translated
- a **word-by-word lexicon** with part of speech and der/die/das for nouns

It is a Python package, a CLI, and a [Claude Code skill](skill/wortzug-translate/SKILL.md).
It uses the Python standard library only and a bring-your-own Gemini key.

## Install and run

```bash
pip install -e ".[dev]"
export GEMINI_API_KEY=your-key        # or WORTZUG_API_KEY
wortzug "Ich habe keine Zeit."
wortzug --json --target French "Könnten Sie mir helfen?"
```

Example text output (illustrative, from the test fixture):

```
Ich habe keine Zeit.
  -> I don't have time.

Register variants:
  [formal] Ich habe leider keine Zeit.  ->  Unfortunately, I don't have time.
  [colloquial] Ich hab keine Zeit.  ->  I've got no time.

Lexicon:
  die Zeit  noun         time
```

Use `WORTZUG_MODEL` or `--model` to pick any Gemini model your key can access.

## Use it from Python

```python
from wortzug import GeminiProvider, translate

result = translate("Könnten Sie mir helfen?", GeminiProvider())
for v in result.variants:
    print(v.register, v.text, "->", v.translation)
```

For tests or offline work, pass any object with a `complete(prompt) -> str` method
in place of `GeminiProvider`.

## Design choices

- **Model output is validated, not trusted.** `wortzug/schema.py` checks every field and
  reports the failing path (for example `$.lexicon[0].gender: is only valid for nouns`).
  A malformed reply triggers one retry with the error fed back to the model.
- **No key in logs or URLs.** The key goes in the `x-goog-api-key` header. Error messages
  report only the HTTP status, so an echoed request body cannot leak the key.
- **No runtime dependencies.** `urllib` handles the HTTP call, so the package installs anywhere.

## Tests

```bash
pytest
```

24 tests run offline. They cover schema validation, code-fence stripping, the retry loop,
request construction, error handling, and the CLI, using scripted fake providers.

## Status

Version 0.1.0. The lexicon and variants depend on the model's output quality, which is
why the schema validation exists. There is no offline dictionary yet.

## License

MIT
