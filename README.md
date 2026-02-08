# NotebookLM PDF → PowerPoint Transformer

NotebookLMが生成するPDFスライドを、**編集可能なPowerPoint（.pptx）**に高品質で変換するツールです。

単なるスクリーンショット貼り付けではなく、テキストを座標・フォント・色情報を維持したまま再配置し、PowerPoint上で編集可能なテキストボックスとして再構築します。

## 特徴

- **座標ベースの忠実な再現**: PDFの正確な座標情報を使い、PPTX上で同じ位置にテキストを配置
- **フォント・色の再現**: フォント名、サイズ、太字/斜体、テキスト色を可能な限り再現
- **画像の自動抽出**: PDF内の画像を自動抽出し、PPTXに配置
- **AIレイアウト解析（オプション）**: Claude APIを使って「タイトル」「箇条書き」「本文」などの役割を高精度に判定
- **テンプレート対応**: 自社のPPTXテンプレートを適用可能
- **CLIインターフェース**: コマンドラインから簡単に変換を実行

## アーキテクチャ

```
PDF → [Extractor] → 座標付きJSON → [Analyzer] → 意味付きJSON → [Builder] → PPTX
         ↓                              ↓
      PyMuPDF                     ヒューリスティック
                                  + Claude API (opt)
```

## セットアップ

### 前提条件

- Python 3.10 以上

### インストール

```bash
# リポジトリのクローン
cd notebooklm-transformer

# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 依存パッケージのインストール
pip install -r requirements.txt

# 開発用パッケージも含める場合
pip install -e ".[dev]"
```

**注意**: Debian/Ubuntu で `python -m venv .venv` が失敗する場合は、`sudo apt install python3-venv` を実行してから再度お試しください。

### 動作確認

依存関係インストール後、以下で動作確認できます。

```bash
# 仮想環境を有効化してから
source .venv/bin/activate   # Linux/Mac

# ヘルプ表示
python -m src.main --help

# サンプル PDF で変換（pdf/ または input/ に .pdf を置いた場合）
python -m src.main pdf/sample.pdf -o output/out.pptx
```

一括で確認する場合はスクリプトを実行してください。

```bash
./scripts/verify-run.sh
```

（スクリプトは `pip install -r requirements.txt` 済みの状態で実行してください。）

### 環境変数の設定（LLM機能を使う場合）

```bash
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

## 使い方

### 基本的な変換

```bash
# PDFをPowerPointに変換（出力は入力ファイル名.pptx で同じディレクトリに保存）
python -m src.main input/slide.pdf

# 出力先を指定（親ディレクトリが無い場合は自動作成されます）
python -m src.main input/slide.pdf -o output/result.pptx

# プロジェクトに含まれるサンプル PDF で試す場合（pdf/ または input/ に .pdf を置く）
python -m src.main pdf/sample.pdf -o output/out.pptx

# CLIとして実行（pip install -e . 後）
pdf2pptx input/slide.pdf -o output/result.pptx
```

### オプション

```bash
# LLMレイアウト解析を有効にする
pdf2pptx input/slide.pdf --use-llm

# テンプレートを適用
pdf2pptx input/slide.pdf --template templates/my_template.pptx

# デバッグログを表示
pdf2pptx input/slide.pdf --log-level DEBUG

# ヘルプ表示
pdf2pptx --help
```

### Pythonコードから使用

```python
from src.extractor import PDFExtractor
from src.analyzer import LayoutAnalyzer
from src.builder import PPTXBuilder

# ステップ1: PDF解析
with PDFExtractor("input/slide.pdf") as extractor:
    data = extractor.extract_all()
    extractor.save_images(data, "output/images")

# ステップ2: レイアウト解析
analyzer = LayoutAnalyzer()
data = analyzer.analyze_presentation(data)

# ステップ3: PPTX構築
builder = PPTXBuilder()
builder.build(data)
builder.save("output/result.pptx")
```

## Web UI（Next.js）

`web/` にNext.jsアプリがあります。開発サーバーで起動できます。

```bash
cd web
npm install
npm run dev
```

ブラウザで http://localhost:3000 を開いてください。

## プロジェクト構造

```
notebooklm-transformer/
├── web/                         # Next.js フロントエンド
│   ├── src/app/                 # App Router
│   └── package.json
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLIエントリーポイント
│   ├── models.py               # Pydanticデータモデル
│   ├── extractor/
│   │   ├── __init__.py
│   │   └── pdf_extractor.py    # PyMuPDFによるPDF解析
│   ├── analyzer/
│   │   ├── __init__.py
│   │   └── layout_analyzer.py  # レイアウト意味解釈（ルールベース + LLM）
│   ├── builder/
│   │   ├── __init__.py
│   │   └── pptx_builder.py     # python-pptxによるPPTX構築
│   └── utils/
│       ├── __init__.py
│       ├── coordinate.py       # 座標変換（pt ⇔ EMU）
│       └── image_processing.py # 画像処理ユーティリティ
├── config/
│   ├── __init__.py
│   └── settings.py             # アプリケーション設定
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # フィクスチャ（first_sample_pdf 等）
│   ├── test_models.py
│   ├── test_coordinate.py
│   ├── test_layout_analyzer.py
│   ├── test_builder.py          # Builder ユニットテスト
│   ├── test_extractor.py        # Extractor ユニットテスト（PDF ありで実行）
│   ├── test_sample_pdf_integration.py  # サンプル PDF による E2E
│   └── test_integration_errors.py      # CLI エラー経路テスト
├── docs/                       # 設計・要求・タスク（docs/tasks-sprint.md 等）
├── input/                      # 入力PDFファイル置き場
├── output/                     # 変換結果の出力先（自動作成可）
├── pdf/                        # サンプルPDF置き場（テスト・手元確認用）
├── templates/                  # PPTXテンプレート置き場
├── pyproject.toml
├── requirements.txt
├── .cursorrules
├── .env.example
├── .gitignore
└── README.md
```

## 技術スタック

| ライブラリ | 用途 |
|---|---|
| **PyMuPDF (fitz)** | PDF解析・テキスト/画像/座標抽出 |
| **python-pptx** | PowerPointファイル構築 |
| **Pillow** | 画像処理 |
| **OpenCV** | 画像前処理（OCR準備等） |
| **Anthropic (Claude API)** | AIレイアウト解析（オプション） |
| **Pydantic** | データモデル・バリデーション |
| **Click** | CLIフレームワーク |
| **Rich** | ターミナルUI（プログレスバー等） |

## 開発

```bash
# テスト実行（サンプル PDF が pdf/ または input/ にあると統合テストも実行）
pytest tests/ -v

# カバレッジ付きテスト（pytest-cov を入れた場合）
pytest tests/ --cov=src --cov-report=html

# リンター（ruff を入れた場合）
ruff check src/ tests/

# 型チェック（mypy を入れた場合）
mypy src/
```

- **設計・タスク**: 要求定義やタスク分解は `docs/` を参照（例: `docs/tasks-sprint.md`）。
- **テスト**: `tests/test_extractor.py` と `tests/test_sample_pdf_integration.py` は、`pdf/` または `input/` に .pdf が無い場合は該当ケースがスキップされます。

## 座標系について

- **PDF座標**: ポイント（pt）単位、1pt = 1/72インチ、左上原点
- **PPTX座標**: EMU（English Metric Unit）、1インチ = 914,400 EMU
- **変換式**: `EMU = pt × 12,700`

## 今後の拡張予定

- [ ] 図表のベクトルデータ変換
- [ ] OCRによる図内テキスト抽出
- [ ] バッチ処理（複数PDF一括変換）
- [ ] MCP（Model Context Protocol）サーバー統合
- [ ] スライドマスター/レイアウトの自動検出
- [ ] テーブル構造の再構築

## Stitch MCP（オプション）

Cursor から [Google Stitch](https://stitch.withgoogle.com/) のデザインを参照・操作するには、Stitch MCP サーバーを接続できます。

- **MCP 設定**: プロジェクトでは `.cursor/mcp.json` に Stitch サーバーが既に登録されています。
- **Stitch API の有効化（GCP）**: 未有効の場合は、gcloud ログイン後に以下を実行してください。
  ```bash
  ./scripts/enable-stitch-api.sh
  ```
  詳細は [docs/MCP-STITCH-SETUP.md](docs/MCP-STITCH-SETUP.md) を参照。参考: [Stitch、リモートStitch MCPサーバーを発表（gihyo.jp）](https://gihyo.jp/article/2026/01/google-stitch-mcp)

## ライセンス

MIT
