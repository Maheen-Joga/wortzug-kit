# wortzug-kit

Structured German translation: an English translation, formal and colloquial
register variants, and a word-by-word lexicon with der/die/das for nouns.

**Status: early development.** Built in small steps; checked items exist and are tested.

- [x] Result schema and strict validation of model output
- [x] Gemini provider (bring your own key, stdlib only)
- [x] translate(): prompt, parse, validate, retry once
- [x] Command-line interface (text and JSON output)
- [x] Claude Code skill
- [ ] Full documentation and design notes

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
