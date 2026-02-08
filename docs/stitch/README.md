# Stitch で生成した UI デザイン

NotebookLM PDF → PowerPoint 変換ツールのUIを、Stitch MCP の `generate_screen_from_text` で生成した成果物です。

## プロジェクト

- **Stitch プロジェクト**: NotebookLM PDF to PowerPoint Transformer  
- **プロジェクト ID**: `7975201906880339596`  

## 画面一覧（要求・実装に準拠したパイプライン表記）

| 画面 | 画面 ID | 説明 |
|------|---------|------|
| **NotebookLM Transformer (Updated Pipeline)** | `e2917665f74e4da8a3b4558da2cc222b` | **推奨** 要求定義・実装に合わせた3ステップ：構造抽出 → レイアウト解析 → PPTX構築。北欧風。 |
| NotebookLM Transformer (Nordic Style) | `44a35a2577ae454289323a0a8a7c2b3d` | 北欧風（旧「AI推定」表記をローカルで修正済み） |
| NotebookLM Transformer Home（初版） | `79526c09b3054d78a91503d3b6fbcb62` | 初回生成のデスクトップ版 |

## ファイル

| ファイル | 説明 |
|--------|------|
| **`stitch-notebooklm-transformer-pipeline-updated.html`** | **要求準拠** 3ステップ（構造抽出 / レイアウト解析「ヒューリスティック + LLM(opt)」/ PPTX構築）の北欧風HTML。 |
| `screen_e2917665f74e4da8a3b4558da2cc222b.png` | 上記のスクリーンショット。 |
| `stitch-notebooklm-transformer-nordic.html` | 北欧風（ステップ表記をローカルで修正済み）。 |
| `screen_44a35a2577ae454289323a0a8a7c2b3d.png` | 北欧版のスクリーンショット。 |
| `stitch-notebooklm-transformer-home.html` | 初版（ステップ表記をローカルで修正済み）。 |
| `screen_79526c09b3054d78a91503d3b6fbcb62.png` | 初版のスクリーンショット。 |

## 北欧版デザインの内容

- **カラー**: 背景 `#f5f3ef`、アクセント `#5b8a9e`、成功はセージ `#6b9080`、ボーダー `#e8e4df`
- **ヒーロー**: タイトル＋「構造解析と再構築で、スライドを編集可能なPowerPointに。AIがあなたの資料をフレキシブルにリデザインします。」
- **アップロード**: 角丸カード内のドラッグ＆ドロップゾーン、「変換を開始」ボタン（ソフトシャドウ）
- **3ステップパイプライン**: 構造抽出 → レイアウト解析（ヒューリスティック＋LLMオプション）→ PPTX構築
- **詳細設定**: 折りたたみ「詳細設定 (Template & AI Analysis)」、Template 選択・AI layout analysis トグル
- **結果エリア**: セージ系背景で「変換が完了しました」＋ダウンロードボタン
- **フッター**: Core Technology、Tech Stack タグ、「Handcrafted with Care」、Terms / Privacy

## 次のステップ

- `web/` の Next.js アプリは北欧風に合わせ済み。Stitch 北欧版のHTMLを参照して微調整可能
- Stitch 上で「詳細設定を展開した状態」「変換中ローディング」などのバリアントを追加する場合は、Cursor で `generate_screen_from_text` に続きのプロンプトを渡す
