# outline.json のフォーマット

`generate_outline.py` が生成し、`generate_slide_images.py` と
`create_presentation.py` が読み込む中間ファイル。人間が直接編集してもよい。

```json
{
  "title": "プレゼンテーション全体のタイトル",
  "slides": [
    {
      "layout": "title",
      "title": "スライドの見出し",
      "bullets": ["箇条書き1", "箇条書き2"],
      "speaker_notes": "発表者向けの補足コメント(任意)",
      "image_path": "generate_slide_images.py 実行後に自動で入る、生成画像のローカルパス",
      "image_url": "create_presentation.py が Drive アップロード後に書き込む内部フィールド"
    }
  ]
}
```

## フィールド

| フィールド | 必須 | 説明 |
|---|---|---|
| `title` (トップレベル) | ○ | プレゼン全体のタイトル。Google スライド作成時のファイル名にも使う |
| `slides[].layout` | ○ | `title`(表紙) / `section`(章区切り) / `content`(通常の本文スライド) |
| `slides[].title` | ○ | スライド見出し |
| `slides[].bullets` | - | 本文の箇条書き。無い場合は省略 or 空配列 |
| `slides[].speaker_notes` | - | 発表者ノート。無ければ省略 |
| `slides[].image_path` | - | `generate_slide_images.py` が書き込む。スライド1枚を丸ごとデザインした画像のローカルパス。手動で既存画像のパスを指定してもよい |
| `slides[].image_url` | - | `create_presentation.py` が Drive アップロード後に書き込む内部フィールド |

## 編集のコツ

- スライドを1枚減らしたい: `slides` 配列からその要素を削除するだけでよい
- 画像を差し替えたい: `image_path` を用意した画像ファイルのパスに書き換える
  (`generate_slide_images.py` を再実行すると `image_path` が既に存在する
  スライドはスキップされるので、手動指定した画像は上書きされない)
- 手動でスライドを追加したい: 上記スキーマに沿ったオブジェクトを `slides` 配列に追加するだけでよい
- デザインのテイストを変えたい: `generate_slide_images.py --style "..."` で
  全スライド共通のデザイン指示(英語推奨)を差し替える
