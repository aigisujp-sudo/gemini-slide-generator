#!/usr/bin/env python3
"""Google Slides / Drive 用の OAuth 認証ヘルパー。

初回は GOOGLE_CLIENT_SECRET_FILE を使ってブラウザでの認可フローを実行し、
結果のトークンを GOOGLE_TOKEN_FILE にキャッシュする。以降はキャッシュを使い回す。
一度きりのセットアップ手順は ../references/google_setup.md を参照。
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive.file",
]

DEFAULT_TOKEN_PATH = Path.home() / ".config" / "gemini-slide-generator" / "token.json"


def get_credentials() -> Credentials:
    client_secret_file = os.environ.get("GOOGLE_CLIENT_SECRET_FILE")
    if not client_secret_file:
        raise RuntimeError(
            "GOOGLE_CLIENT_SECRET_FILE が設定されていません。"
            "references/google_setup.md の手順でOAuthクライアントを作成してください。"
        )

    token_file = Path(os.environ.get("GOOGLE_TOKEN_FILE", DEFAULT_TOKEN_PATH))
    token_file.parent.mkdir(parents=True, exist_ok=True)

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")

    return creds
