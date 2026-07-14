# gemini-slide-generator

Gemini API でプレゼンテーションの構成を生成し、スライド1枚1枚を完成したデザインとして
丸ごと画像化した上で、Google Slides として組み立てる [Claude Code](https://claude.com/claude-code)
スキルです。

ランディングページ: https://gemini-slide-generator.netlify.app

## インストール

```bash
curl -fsSL https://gemini-slide-generator.netlify.app/install.sh | bash
```

`~/.claude/skills/gemini-slide-generator` にスキル本体がインストールされます。

## セットアップ

1. 依存パッケージのインストール
   ```bash
   cd ~/.claude/skills/gemini-slide-generator
   pip install -r requirements.txt
   ```
2. `GEMINI_API_KEY` を環境変数に設定(取得先: [Google AI Studio](https://aistudio.google.com/apikey))
3. Google Slides / Drive 書き込み用の OAuth クライアントを用意
   ([skill/references/google_setup.md](skill/references/google_setup.md) の手順を参照)

## 使い方

Claude Code 上で「〇〇についてスライド作って」のように依頼するだけで、
このスキルが自動的に起動します。詳しいパイプラインは
[skill/SKILL.md](skill/SKILL.md) を参照してください。

## 仕組み

1. `generate_prompt.py` — Gemini に送る構成生成用プロンプトを作成
2. `generate_outline.py` — Gemini(テキスト)でスライド構成をJSON生成
3. `generate_slide_images.py` — Gemini(画像, `gemini-3-pro-image-preview`)で
   スライド1枚を丸ごとフルHDデザインとして生成
4. `create_presentation.py` — 生成画像をGoogle スライドに全面貼り付けし、編集URLを発行

日本語の文字を画像に直接焼き込むため、画像生成モデルには文字描画精度の高い
`gemini-3-pro-image-preview` を使用しています。

## リポジトリ構成

```
skill/    Claude Code スキル本体(SKILL.md / scripts / references)
site/     ランディングページ(Netlify にデプロイ)
install.sh  ワンコマンドインストーラ
```

## License

MIT
