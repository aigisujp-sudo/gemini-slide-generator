#!/usr/bin/env python3
"""スライド構成生成のために Gemini へ送るプロンプト文を作成する。

Gemini にいきなり投げず、まずプロンプト本文をファイルに書き出すことで、
ユーザーが「この観点を足したい」「トーンを変えたい」といった調整を、
API を叩く前に直接テキストとして確認・編集できるようにする。
"""
import argparse
import sys
from pathlib import Path


def build_prompt(topic: str, reference_text: str, num_slides: int) -> str:
    parts = []
    if topic:
        parts.append(f"プレゼンテーションのテーマ: {topic}")
    if reference_text:
        parts.append(f"以下の資料の内容をもとに構成してください:\n\n{reference_text}")
    parts.append(
        f"{num_slides}枚程度のスライド構成を作成してください。\n"
        "- 1枚目はタイトルスライド(layout: title)にすること。\n"
        "- 話の区切りには章区切りスライド(layout: section)を適宜挟むこと。\n"
        "- それ以外は本文スライド(layout: content)とし、要点を簡潔な箇条書きにすること。\n"
        "- speaker_notes には発表者向けの補足を書くこと。"
    )
    return "\n\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="", help="スライドのテーマ(ゼロから企画する場合)")
    parser.add_argument("--input-file", default="", help="参考資料のテキスト/Markdownファイル")
    parser.add_argument("--num-slides", type=int, default=10)
    parser.add_argument("--output", default="prompt.txt")
    args = parser.parse_args()

    if not args.topic and not args.input_file:
        sys.exit("--topic か --input-file のいずれかを指定してください")

    reference_text = ""
    if args.input_file:
        reference_text = open(args.input_file, encoding="utf-8").read()

    prompt = build_prompt(args.topic, reference_text, args.num_slides)
    Path(args.output).write_text(prompt, encoding="utf-8")
    print(f"プロンプトを {args.output} に書き出しました。内容を確認・編集してから generate_outline.py に渡してください")


if __name__ == "__main__":
    main()
