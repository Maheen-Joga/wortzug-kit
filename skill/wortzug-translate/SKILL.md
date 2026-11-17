---
name: wortzug-translate
description: Translate German text into English with formal and colloquial variants and a word-by-word lexicon (with der/die/das genders). Use when the user asks to translate German, explain German words or grammar gender, or check how a German sentence changes between Sie and du.
---

# wortzug-translate

Structured German translation through the `wortzug` CLI from the wortzug-kit package.
Use it when the user wants more than a plain translation: register variants or a lexicon.

## Setup (once)

```bash
pip install -e path/to/wortzug-kit   # from a clone of this repo
export GEMINI_API_KEY=...       # bring your own key; never paste it into chat
```

## Steps

1. Run the CLI with JSON output so the result can be checked:

   ```bash
   wortzug --json "Ich habe keine Zeit."
   ```

2. Read the JSON. It contains `translation`, `variants` (each with `register`
   `formal` or `colloquial`), and `lexicon` (each with `word`, `translation`,
   `part_of_speech`, `gender`, `note`).

3. Present the answer to the user in plain prose or a short list. Keep the
   German text as written. For a lexicon, show the article for nouns (for example
   "die Zeit").

## Notes

- If the command reports `no API key`, ask the user to set `GEMINI_API_KEY` or
  `WORTZUG_API_KEY` in their own shell. Do not ask them to paste the key.
- If the output is not valid JSON or the command fails, say so and fall back to a
  normal translation written directly, marked as unverified against the lexicon.
- For other target languages, pass `--target French` (or similar).
