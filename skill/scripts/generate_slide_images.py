#!/usr/bin/env python3
"""outline.json の各スライドを、AIが1枚のフルHD画像として丸ごとデザインする。

背景・文字・挿絵を別々のレイヤーとして組み立てるのではなく、スライド1枚を
完成したデザインとして Gemini の画像生成モデルに直接描かせる方式。
gemini-3-pro-image-preview は日本語の文字も正確に描画できるため、この方式が
成立する(gemini-2.5-flash-image など旧モデルでは日本語が崩れるため非推奨)。
"""
import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from image_utils import SLIDE_IMAGE_CONFIG, fit_to_full_hd

load_dotenv()

DEFAULT_STYLE = (
    "Digital/tech aesthetic: deep navy-to-black gradient background, glowing cyan and "
    "electric-blue circuit-line patterns, subtle grid and particle/node network motifs, "
    "soft neon glow accents, futuristic HUD-style geometric frame elements. "
    "Clean modern sans-serif typography, high contrast, well-balanced composition."
)

COMMON_SUFFIX = "No spelling mistakes, no watermark, 16:9 widescreen."


def build_prompt(slide: dict, style: str) -> str:
    layout = slide.get("layout", "content")
    title = slide.get("title", "")
    bullets = slide.get("bullets") or []

    if layout == "title":
        subtitle = "\n".join(bullets)
        return (
            "Design a complete, professional presentation title slide. "
            f"Main title text rendered clearly and legibly in Japanese, large and bold, "
            f"centered: '{title}'. "
            f"Subtitle text rendered clearly and legibly in Japanese, smaller, below the "
            f"title: '{subtitle}'. {style} {COMMON_SUFFIX}"
        )
    if layout == "section":
        return (
            "Design a complete, professional presentation section-divider slide. "
            f"Large impactful heading text rendered clearly and legibly in Japanese, "
            f"centered, multi-line if needed: '{title}'. Minimal decoration, strong focus "
            f"on the text itself. {style} {COMMON_SUFFIX}"
        )
    bullet_lines = "\n".join(f"・{b}" for b in bullets)
    return (
        "Design a complete, professional presentation content slide. "
        f"Heading text rendered clearly and legibly in Japanese at the top: '{title}'. "
        f"Below it, a clean bulleted list rendered clearly and legibly in Japanese, each "
        f"item on its own line inside a subtle panel:\n{bullet_lines}\n{style} {COMMON_SUFFIX}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outline", required=True)
    parser.add_argument("--output-dir", default="slide_images")
    parser.add_argument(
        "--style", default=DEFAULT_STYLE, help="全スライド共通のデザイン指示(英語推奨)"
    )
    parser.add_argument(
        "--model", default=os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")
    )
    args = parser.parse_args()

    if "GEMINI_API_KEY" not in os.environ:
        raise SystemExit("GEMINI_API_KEY 環境変数が設定されていません")

    outline_path = Path(args.outline)
    outline = json.loads(outline_path.read_text(encoding="utf-8"))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    for i, slide in enumerate(outline["slides"]):
        prompt = build_prompt(slide, args.style)
        response = client.models.generate_content(
            model=args.model, contents=prompt, config=SLIDE_IMAGE_CONFIG
        )
        image_path = out_dir / f"slide_{i:02d}.png"
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_path.write_bytes(fit_to_full_hd(part.inline_data.data))
                slide["image_path"] = str(image_path)
                print(f"slide {i}: {image_path}")
                break
        else:
            print(f"slide {i}: FAILED (no image returned)")

    outline_path.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
