#!/usr/bin/env python3
"""outline.json の各スライド画像を、Google スライドに1枚ずつ全面貼り付けで組み立てる。

Slides API は画像を URL 経由でしか配置できないため、ローカルの生成画像は
先に Google Drive にアップロードし、リンク共有を有効にしてから参照する。
"""
import argparse
import json
import mimetypes
import sys
import uuid
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from google_auth import get_credentials


def new_object_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def upload_image_to_drive(drive_service, image_path: str) -> str:
    """画像をDriveにアップロードし、リンクを知っていれば誰でも閲覧可にした上でURLを返す。"""
    mime_type, _ = mimetypes.guess_type(image_path)
    media = MediaFileUpload(image_path, mimetype=mime_type or "image/png")
    uploaded = (
        drive_service.files()
        .create(body={"name": Path(image_path).name}, media_body=media, fields="id")
        .execute()
    )
    file_id = uploaded["id"]
    drive_service.permissions().create(
        fileId=file_id, body={"type": "anyone", "role": "reader"}
    ).execute()
    return f"https://drive.google.com/uc?id={file_id}"


def set_speaker_notes(slides_service, presentation_id, notes):
    """notes: list of (slide_id, text). Notes placeholders only exist after the
    slide itself has been created, so this runs as a second pass."""
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    notes_by_slide = dict(notes)
    notes_requests = []
    for slide in presentation["slides"]:
        text = notes_by_slide.get(slide["objectId"])
        if not text:
            continue
        notes_page = slide.get("slideProperties", {}).get("notesPage", {})
        for element in notes_page.get("pageElements", []):
            placeholder = element.get("shape", {}).get("placeholder", {})
            if placeholder.get("type") == "BODY":
                notes_requests.append({"insertText": {"objectId": element["objectId"], "text": text}})
    if notes_requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": notes_requests}
        ).execute()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outline", required=True)
    parser.add_argument("--title", default=None)
    args = parser.parse_args()

    outline_path = Path(args.outline)
    outline = json.loads(outline_path.read_text(encoding="utf-8"))

    creds = get_credentials()
    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    presentation = (
        slides_service.presentations()
        .create(body={"title": args.title or outline.get("title", "Untitled")})
        .execute()
    )
    presentation_id = presentation["presentationId"]
    page_size = presentation["pageSize"]
    page_w = page_size["width"]["magnitude"]
    page_h = page_size["height"]["magnitude"]

    # presentations.create() auto-adds one default slide; remove it before
    # adding our own so the deck starts clean.
    default_slide_id = presentation["slides"][0]["objectId"]
    all_requests = [{"deleteObject": {"objectId": default_slide_id}}]

    notes = []
    for slide in outline["slides"]:
        if not slide.get("image_path"):
            sys.exit(
                f"スライド「{slide.get('title', '')}」に image_path がありません。"
                "先に generate_slide_images.py を実行してください。"
            )
        image_url = slide.get("image_url")
        if not image_url:
            image_url = upload_image_to_drive(drive_service, slide["image_path"])
            slide["image_url"] = image_url

        slide_id = new_object_id("slide")
        all_requests.append(
            {"createSlide": {"objectId": slide_id, "slideLayoutReference": {"predefinedLayout": "BLANK"}}}
        )
        all_requests.append(
            {
                "createImage": {
                    "url": image_url,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {"magnitude": page_w, "unit": "EMU"},
                            "height": {"magnitude": page_h, "unit": "EMU"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 0,
                            "translateY": 0,
                            "unit": "EMU",
                        },
                    },
                }
            }
        )
        if slide.get("speaker_notes"):
            notes.append((slide_id, slide["speaker_notes"]))

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id, body={"requests": all_requests}
    ).execute()

    if notes:
        set_speaker_notes(slides_service, presentation_id, notes)

    # Persist image_url back so re-runs don't re-upload the same images.
    outline_path.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"https://docs.google.com/presentation/d/{presentation_id}/edit")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # surface API errors clearly instead of a raw traceback
        sys.exit(f"エラー: {exc}")
