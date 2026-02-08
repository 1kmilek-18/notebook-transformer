# NotebookLM PDF → PowerPoint 変換ツール UI デザイン仕様

> **Stitch MCP について**: Stitch API がプロジェクトで有効でない場合、`list_projects` 等で 403 が出ます。Google Cloud Console で [Stitch API を有効化](https://console.developers.google.com/apis/api/stitch.googleapis.com/overview)し、`GOOGLE_CLOUD_PROJECT` を設定してください。手順は [MCP-STITCH-SETUP.md](./MCP-STITCH-SETUP.md) を参照。

## 概要

NotebookLMで生成されたスライドPDFを**編集可能なPowerPoint（.pptx）**に変換するWeb UI。単なる形式変換ではなく「構造解析と再構築」のプロセスを可視化し、**AI-DLC（AI主導開発）**のハイブリッド再構築ワークフローをユーザーに示す。

---

## デザイン方針

- **信頼感**: 技術スタック（PyMuPDF / python-pptx / LLM）を控えめに表示し、専門性を伝える
- **透明性**: 3ステップ（構造抽出 → レイアウト解析 → PPTX構築）を常に見える化し、何が行われているか分かりやすくする
- **最小操作**: PDFをドロップして「変換」するだけで完了するMVP。上級者向けにテンプレート選択・オプションを展開可能に

---

## 画面構成

### 1. ヒーロー / 説明エリア

- **タイトル**: 「NotebookLM Transformer」または「PDF → PowerPoint 変換」
- **サブタイトル**: 「構造解析と再構築で、スライドを編集可能なPowerPointに」
- **補足1行**: 例「PyMuPDFで座標を抽出し、AIでレイアウトを解釈、python-pptxで再描画します」

### 2. メイン操作エリア

- **PDFアップロードゾーン**
  - ドラッグ＆ドロップまたはクリックでファイル選択
  - 対応: `.pdf` のみ表示
  - 選択後: ファイル名・ページ数（取得可能なら）を表示し、「変換を開始」ボタンを有効化

- **オプション（折りたたみまたはセカンダリ）**
  - **テンプレート**: 「デフォルト」「自社テンプレートをアップロード（.potx）」を選択可能
  - **AIレイアウト解析**: オン/オフ（オフの場合は座標のみで再現）

### 3. 変換パイプラインの可視化（3ステップ）

変換中・変換後に、次の3ステップをステップインジケータで表示する。

| ステップ | ラベル（短） | 説明（ツールチップまたは下段テキスト） |
|----------|--------------|----------------------------------------|
| 1 | 構造抽出 | PyMuPDFでテキスト・画像・座標をJSONとして抽出（PDF解析） |
| 2 | レイアウト解析 | ヒューリスティック＋LLM(オプション)でタイトル・箇条書き等の役割を判定 |
| 3 | PPTX構築 | python-pptxで同じ位置にテキストボックス・図を配置 |

- 状態: **待機** / **実行中** / **完了** / **エラー**
- 実行中はスピナーまたはプログレスバー、完了はチェックマーク

### 4. 結果エリア

- **成功時**
  - 「変換が完了しました」
  - 出力ファイル名（例: `result.pptx`）
  - **ダウンロード**ボタン（.pptxをダウンロード）
  - 任意: 「もう1つ変換する」でアップロードゾーンをリセット

- **エラー時**
  - 短いエラーメッセージ
  - どのステップで失敗したかを表示
  - 「再試行」で同じファイルで再実行可能に

### 5. フッター / 技術情報

- 「MVP: PyMuPDFでテキスト座標を抽出し、python-pptxで同じ位置に配置」
- 技術スタックのアイコンまたはテキスト: PyMuPDF, python-pptx, OpenCV/Pillow, LLM (Claude)
- リンク: CLIの使い方、README、MCP拡張の説明（将来）

---

## Stitch MCP 用プロンプト（画面生成）

Stitch API を有効にしたうえで、以下のプロンプトで `generate_screen_from_text` を呼ぶと、上記仕様に沿ったUIデザインを生成できます。

```
Create a single-page web UI for a "NotebookLM PDF to PowerPoint" converter with:

1. Hero: Title "NotebookLM Transformer", subtitle "構造解析と再構築で、スライドを編集可能なPowerPointに" (structure analysis and reconstruction into editable PowerPoint).

2. Main area: A large drag-and-drop zone for PDF upload, with "変換を開始" (Start conversion) button. Optional collapsed section for "Template" (default / upload .potx) and "AI layout analysis" toggle.

3. Pipeline steps indicator (horizontal, 3 steps): 
   - Step 1: "構造抽出" (Structure extraction) - PyMuPDF extracts text, images, coordinates
   - Step 2: "レイアウト解析" (Layout analysis) - Heuristic + optional LLM for title/bullets role
   - Step 3: "PPTX構築" (PPTX build) - python-pptx places content
   Each step shows state: waiting / running / done / error with icons.

4. Result area: On success, "変換が完了しました" with a download button for .pptx. On error, show message and "再試行" button.

5. Footer: Short line "MVP: 座標抽出 → python-pptxで同一位置に配置" and tech stack: PyMuPDF, python-pptx, LLM.

Style: Clean, professional, modern. Use a neutral background (e.g. stone/slate), clear typography, and distinct states for the 3-step pipeline. Desktop-first layout, not mobile.
```

---

## 技術スタック（UI実装）

- **Next.js** (App Router) + **React**
- **Tailwind CSS** でレイアウト・ステップ表示・状態に応じた色分け
- ファイルアップロード: クライアントで `input type="file"` またはドロップゾーン（APIは別途バックエンドまたはCLI連携で実装）

---

## 今後の拡張（MCP・テンプレート）

- **MCP**: Cursor内で「このPDFをパワポにして」と指示するだけで変換するワークフロー用に、同じ3ステップの説明をMCPの説明文に含める
- **テンプレート**: 自社 .potx をアップロードしてベースに流し込むオプションは、UIにプレースホルダを用意済み
