#!/usr/bin/env python3
"""Gemini API でプレゼンテーションのスライド構成(outline.json)を生成する。

プロンプト本文は事前に generate_prompt.py で作成・確認したファイルを渡す。
See ../references/schemas.md for the output format.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

OUTLINE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "layout": {
                        "type": "string",
                        "enum": ["title", "section", "content"],
                    },
                    "title": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                    "speaker_notes": {"type": "string"},
                },
                "required": ["layout", "title"],
            },
        },
    },
    "required": ["title", "slides"],
}


def generate_outline(prompt: str, model: str) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=OUTLINE_SCHEMA,
        ),
    )
    return json.loads(response.text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prompt-file", required=True, help="generate_prompt.py が書き出したプロンプトファイル"
    )
    parser.add_argument(
        "--model", default=os.environ.get("GEMINI_TEXT_MODEL", "gemini-2.5-pro")
    )
    parser.add_argument("--output", default="outline.json")
    args = parser.parse_args()

    if "GEMINI_API_KEY" not in os.environ:
        sys.exit("GEMINI_API_KEY 環境変数が設定されていません")

    prompt = Path(args.prompt_file).read_text(encoding="utf-8")

    outline = generate_outline(prompt, args.model)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)

    print(f"{len(outline['slides'])} 枚の構成を {args.output} に書き出しました")


if __name__ == "__main__":
    main()
