#!/usr/bin/env python3
"""スライド全面に使う画像の解像度をFull HDに揃えるユーティリティ。

Gemini の画像生成モデルは `aspect_ratio` (縦横比) は指定できるが、
出力ピクセル数までは厳密に制御できない。そのため生成後に中央クロップ+
リサイズしてFull HD(1920x1080, 16:9)ちょうどに統一する。
"""
import io

from google.genai import types
from PIL import Image

FULL_HD = (1920, 1080)

SLIDE_IMAGE_CONFIG = types.GenerateContentConfig(
    image_config=types.ImageConfig(aspect_ratio="16:9"),
)


def fit_to_full_hd(image_bytes: bytes) -> bytes:
    """画像バイト列を中央クロップ+リサイズしてFull HDのPNGバイト列にする。"""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    target_w, target_h = FULL_HD
    target_ratio = target_w / target_h
    src_ratio = img.width / img.height

    if src_ratio > target_ratio:
        crop_w = round(img.height * target_ratio)
        left = (img.width - crop_w) // 2
        img = img.crop((left, 0, left + crop_w, img.height))
    else:
        crop_h = round(img.width / target_ratio)
        top = (img.height - crop_h) // 2
        img = img.crop((0, top, img.width, top + crop_h))

    img = img.resize(FULL_HD, Image.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
