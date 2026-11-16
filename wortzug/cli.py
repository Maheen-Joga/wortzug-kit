"""Command-line interface: `wortzug "Ich habe keine Zeit."` or `wortzug --json ...`."""

from __future__ import annotations

import argparse
import json
import sys

from .core import TranslationError, translate
from .providers import GeminiProvider, ProviderError
from .schema import TranslationResult


def render_text(result: TranslationResult) -> str:
    lines = [f"{result.source}", f"  -> {result.translation}", ""]
    if result.variants:
        lines.append("Register variants:")
        for v in result.variants:
            lines.append(f"  [{v.register}] {v.text}  ->  {v.translation}")
        lines.append("")
    if result.lexicon:
        lines.append("Lexicon:")
        labels = [f"{e.gender} {e.word}" if e.gender else e.word for e in result.lexicon]
        width = max(len(label) for label in labels)
        for e, label in zip(result.lexicon, labels):
            note = f"  ({e.note})" if e.note else ""
            lines.append(f"  {label.ljust(width)}  {e.part_of_speech:<12} {e.translation}{note}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wortzug", description="Structured German translation.")
    parser.add_argument("text", nargs="?", help="German text to translate (reads stdin if omitted)")
    parser.add_argument("--target", default="English", help="target language (default: English)")
    parser.add_argument("--model", default=None, help="Gemini model name (or set WORTZUG_MODEL)")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        print("error: no text given", file=sys.stderr)
        return 2
    try:
        provider = GeminiProvider(model=args.model) if args.model else GeminiProvider()
        result = translate(text, provider, target_language=args.target)
    except (ProviderError, TranslationError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
