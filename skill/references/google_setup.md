# Google Slides / Drive への書き込み設定(初回のみ)

このスキルは Google Slides API でスライドを作成し、生成した画像を Google Drive
経由でスライドに挿入する。そのため、個人の Google アカウントに対する OAuth
クライアントを一度だけ用意する必要がある。

## 手順

1. https://console.cloud.google.com/ を開き、プロジェクトを作成(または既存のものを選択)
2. 「APIとサービス」→「ライブラリ」から次の2つを有効化する
   - **Google Slides API**
   - **Google Drive API**
3. 「APIとサービス」→「OAuth同意画面」を設定する
   - User Type は個人利用なら「外部」でよい(公開申請は不要、テストユーザーとして
     自分のGoogleアカウントを追加すれば使える)
4. 「認証情報」→「認証情報を作成」→「OAuthクライアントID」
   - アプリケーションの種類は **デスクトップアプリ** を選ぶ
5. 作成後にダウンロードできる JSON ファイルを、リポジトリの外(例: `~/.config/gemini-slide-generator/credentials.json`)に保存する
   - **リポジトリ内には置かない・コミットしないこと**
6. 環境変数 `GOOGLE_CLIENT_SECRET_FILE` にそのファイルのパスを設定する

```
export GOOGLE_CLIENT_SECRET_FILE="$HOME/.config/gemini-slide-generator/credentials.json"
```

## 初回実行時の動き

`create_presentation.py` を初めて実行するとブラウザが自動で開き、Googleアカウントでの
ログインと権限の許可を求められる。許可すると、認証結果(トークン)が
`GOOGLE_TOKEN_FILE`(未設定なら `~/.config/gemini-slide-generator/token.json`)に
保存され、以降の実行では再認可なしで使える。

トークンが失効・破損した場合は、`GOOGLE_TOKEN_FILE` を削除して再実行すれば
もう一度ブラウザでの認可フローが走る。
