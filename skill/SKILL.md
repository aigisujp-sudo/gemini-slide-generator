---
name: gemini-slide-generator
description: Gemini API を使ってプレゼンテーション(スライド)を企画・生成し、Google スライドとして実際に作成する。ユーザーが「スライドを作って」「プレゼン資料を作って」「発表資料をまとめて」など、テーマや資料からスライド一式を作りたいと言ったら、明示的に「Gemini」や「Googleスライド」と言っていなくても必ずこのスキルを使うこと。既存の文章・PDF・Markdownを要約してスライド化したい場合も対象。
---

# Gemini Slide Generator

Gemini API でスライドの構成を生成し、スライド1枚1枚を完成したデザインとして
丸ごと画像化した上で、Google Slides API で実際に開けるスライドとして組み立てる
スキル。パイプラインは4段階:

1. `scripts/generate_prompt.py` — Gemini に送る「スライド構成生成用」のプロンプト文を作成
2. `scripts/generate_outline.py` — そのプロンプトを Gemini(テキスト)に投げてスライド構成を JSON で生成
3. `scripts/generate_slide_images.py` — 各スライドを Gemini(画像生成)で1枚のフルHD画像として丸ごとデザイン
4. `scripts/create_presentation.py` — 生成画像をスライドに全面貼り付けし、編集URLを返す

各スライドは背景・文字・装飾を分けて組み立てるのではなく、`gemini-3-pro-image-preview`
に1枚の完成デザインとして直接描かせる。このモデルは日本語の文字も正確に描画できる
ため、この方式が成立している ── `gemini-2.5-flash-image` など旧世代の画像モデルでは
日本語タイトルが崩れて実用にならないため、画像生成には必ず `gemini-3-pro-image-preview`
系のモデルを使うこと(`GEMINI_IMAGE_MODEL` で上書き可能だが、変更する場合は日本語の
描画品質を必ず実機確認する)。

プロンプト・構成(outline)をそれぞれファイルとして一度書き出してから次に進むのは、
API を叩く前後にユーザーが内容を確認・手直しできるようにするため。プロンプト段階で
「この観点を足したい」「もっとカジュアルに」を反映しておけば、Gemini への依頼を何度も
やり直すより早く狙った構成に辿り着ける。構成が固まった後の細かい修正も、Gemini に
再依頼するより `outline.json` を直接編集して `create_presentation.py` を再実行する方が速い。

## 前提条件

- `GEMINI_API_KEY` 環境変数(すでに取得済みで `.env` 等で管理されている前提)
- Google Slides / Drive への書き込み用 OAuth 認証情報。まだ用意していない場合は
  `references/google_setup.md` の手順(Google Cloud Console でのAPI有効化・OAuthクライアント作成)
  を最初にユーザーと一緒に進めること。初回のみブラウザでの同意操作が必要。
- 依存パッケージは `requirements.txt` を参照。未インストールなら
  `pip install -r requirements.txt`(このスキルのディレクトリ内で実行)を案内する。

認証情報(`credentials.json` や `token.json`)やAPIキーをリポジトリにコミットしないよう
常に注意する。ユーザーのプロジェクトの `.gitignore` にこれらのパターンが無ければ追加を提案する。

## ワークフロー

### 1. 要件を確認する

ユーザーの依頼から次を把握する(全部揃っていなければ聞く):

- **テーマ**(ゼロから企画する場合)または **参考資料**(要約してスライド化したい文章・PDF・Markdown)。両方渡されることもある。
- 想定スライド枚数(指定が無ければ 8〜12 枚程度を提案)
- 想定オーディエンス・トーン(社内向け/顧客向け/カジュアル/フォーマルなど)。分かれば構成の精度が上がるので軽く聞く。
- デザインテイスト(指定が無ければ、清潔感のあるモダンな配色で `generate_slide_images.py` の既定スタイルを使う旨を伝えればよい)。

### 2. プロンプトを作成する

```bash
python scripts/generate_prompt.py \
  --topic "テーマ文" \
  --input-file "参考資料.md" \
  --num-slides 10 \
  --output prompt.txt
```

`--topic` と `--input-file` はどちらか一方でも両方でもよい(最低どちらか必須)。

**Gemini に投げる前に、`prompt.txt` の中身を必ずユーザーに見せて確認を取ること。**
トーンを変えたい、特定の観点を足したい、などの要望があれば、この段階でプロンプト文を
直接書き換える。ここで固めておくほど、次のステップの手戻りが減る。

### 3. 構成(outline)を生成する

```bash
python scripts/generate_outline.py --prompt-file prompt.txt --output outline.json
```

承認済みのプロンプトを Gemini(テキスト)に投げ、スライド構成を JSON で生成する。
出力される `outline.json` のスキーマは `references/schemas.md` を参照。

**生成したら、画像を作る前に必ずユーザーに構成を見せて確認を取ること。** ここで
「このスライドはいらない」「順番を変えて」などのフィードバックが来たら、`outline.json` を
直接編集するか、`prompt.txt` を調整して `generate_outline.py` を再実行する。画像生成・
スライド組み立ては API 呼び出しのコストが掛かるので、構成が固まってから進める。

### 4. スライド画像を生成する

```bash
python scripts/generate_slide_images.py --outline outline.json --output-dir slide_images
```

`outline.json` の各スライド(layout/title/bullets)から、1枚ずつ完成デザインの
フルHD画像を生成し、`outline.json` に `image_path` として書き戻す。デザインテイストを
変えたい場合は `--style "..."` で全スライド共通のスタイル指示(英語推奨)を渡す。
既に `image_path` があるスライドはスキップされるので、一部だけ差し替えたい場合は
該当スライドの `image_path` を outline から削除してから再実行する。

### 5. Google スライドとして組み立てる

```bash
python scripts/create_presentation.py --outline outline.json --title "プレゼンタイトル"
```

各スライド画像を Google Drive にアップロードし、スライド全面に貼り付ける形で
Google スライドを組み立てる。初回実行時はブラウザが開いて Google アカウントでの
認可を求められる(以降はトークンがキャッシュされ再認可は不要)。実行が終わると
編集用URL(`https://docs.google.com/presentation/d/.../edit`)が出力されるので、
そのままユーザーに渡す。

### 6. 仕上がりを一緒に確認する

URLをユーザーに共有し、実際に開いて見てもらう。文字はすべて画像に焼き込まれているため、
文言を直したい場合は Google スライド上でのテキスト編集ではなく、`outline.json` の該当
スライドを直して `generate_slide_images.py` → `create_presentation.py` を再実行する
流れになる点を伝えること。再実行すると新しいプレゼンファイルが作られる点にも注意する。

## 注意点・判断基準

- レイアウトは `layout` フィールドで決まる: `title`(表紙)/ `section`(章区切り)/
  `content`(通常の本文スライド)。迷ったら `content` を使う。
- 画像生成モデルは日本語描画品質が最優先。`GEMINI_IMAGE_MODEL` を変更する場合は
  必ず1枚テスト生成して日本語タイトルが崩れないか確認してから本番枚数を回すこと。
- モデル名(`GEMINI_TEXT_MODEL` / `GEMINI_IMAGE_MODEL`)は環境変数で上書き可能。
  Gemini のモデルラインナップは更新され続けるため、スクリプトのデフォルト値が古くなって
  いないか、実行前に https://ai.google.dev/gemini-api/docs/models で最新のモデルIDを
  確認するとよい。

## 参考ファイル

- `references/google_setup.md` — Google Cloud での OAuth クライアント作成手順(初回のみ)
- `references/schemas.md` — `outline.json` のフォーマット定義
