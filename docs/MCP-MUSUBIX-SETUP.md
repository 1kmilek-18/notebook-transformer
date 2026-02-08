# Musubix MCP 利用ガイド

[MUSUBIX](https://github.com/notebooklm-transformer/musubix) は、要件（EARS）・設計（C4）・タスク分解・コード検証・知識グラフを扱う MCP サーバーです。Cursor で接続すると、このプロジェクトの開発時に以下のツールを利用できます。

## 接続の確認

Cursor の **Settings → MCP** に `notebooklm-transformer-musubix` サーバーが追加されていれば、AI から次のツールが利用可能です。接続されていない場合は、使用している Musubix のセットアップ手順に従って MCP を追加してください。

---

## 利用可能なツール一覧

### 要件・設計・タスク（SDD）

| ツール | 説明 |
|--------|------|
| `create_requirements` | EARS 形式の要件ドキュメントを新規作成（プロジェクト名・機能名・説明を指定） |
| `validate_requirements` | 要件ドキュメントを EARS パターンと Constitution で検証 |
| `create_design` | 要件から C4 モデル設計ドキュメントを生成 |
| `validate_design` | 設計が要件をトレースしているか検証 |
| `create_tasks` | 設計から実装タスクを生成（スプリント日数指定可） |
| `query_knowledge` | 知識グラフでパターン・要件・設計・タスクを検索 |
| `update_knowledge` | 知識グラフにノードを追加・更新 |
| `validate_constitution` | ドキュメントを 9 つの Constitution 条文で検証 |
| `validate_traceability` | 要件→設計→タスクのトレーサビリティを検証 |
| `formal_verify` | EARS 要件を Z3 で形式的検証（SMT-LIB / VC 生成） |

### コード検証（Symbolic）

| ツール | 説明 |
|--------|------|
| `filter_code` | 生成コードをパイプラインで検証（ hallucination 検出・Constitution 適合・信頼度推定） |
| `detect_hallucination` | 存在しない API/モジュール/シンボル参照を検出 |
| `check_constitution` | コードが 9 つの Constitution 条文に適合するかチェック |
| `estimate_confidence` | 生成コードの信頼度スコア（0.0–1.0）を推定 |
| `pipeline_info` | シンボリックパイプラインの構成・閾値・条文一覧を取得 |

### 知識グラフ整合性（Consistency）

| ツール | 説明 |
|--------|------|
| `validate` | トリプル一覧の OWL 制約チェック（重複・循環・ disjoint 等） |
| `validate_triple` | 単一トリプルをコンテキスト付きで検証 |
| `check_circular` | 関係グラフの循環依存を検出 |

### エージェント・ワークフロー

| ツール | 説明 |
|--------|------|
| `agent_dispatch` | タスクをサブエージェントに分解して並列実行 |
| `agent_status` | ディスパッチ実行の進捗・完了・エラーを取得 |
| `agent_cancel` | 実行中タスクのキャンセル |
| `agent_analyze` | タスクの複雑度とサブタスク分解の要否を分析 |
| `workflow_create` | SDD ワークフロー作成（Phase 1: 要件定義開始） |
| `workflow_transition` | フェーズ遷移（要件→設計→タスク分解→実装→完了） |
| `workflow_status` | ワークフローの状態・進捗・アーティファクト取得 |
| `workflow_review` | 現在フェーズのセルフレビュー |
| `workflow_gate` | フェーズごとのクオリティゲート実行 |

### スキル

| ツール | 説明 |
|--------|------|
| `skill_list` | 利用可能スキル一覧（タイプ・タグでフィルタ可） |
| `skill_execute` | 指定スキルをパラメータ付きで実行 |
| `skill_validate` | スキル定義のメタデータ・パラメータを検証 |
| `skill_info` | スキルの詳細（パラメータ・タグ・使用例） |
| `skill_register` | 新規スキルを登録 |

---

## このプロジェクトでの使い方

### 1. 新機能の要件・設計から進める

1. **要件作成**: 「〇〇機能の要件を EARS で書いて」→ `create_requirements` でドキュメント生成
2. **検証**: `validate_requirements` で EARS/Constitution チェック
3. **設計**: `create_design` で C4 設計、`validate_design` でトレース確認
4. **タスク**: `create_tasks` で実装タスクに分解

### 2. ワークフローで一気通貫

- `workflow_create` でワークフロー作成
- 要件 → 設計 → タスク分解 → 実装 の順に `workflow_transition` で遷移
- 各フェーズで `workflow_review` / `workflow_gate` で品質確認

### 3. 生成コードの品質チェック

- 新規コードを書いたら `filter_code` で hallucination・Constitution・信頼度を一括チェック
- 既存シンボル一覧を `knownSymbols`、依存を `dependencies` に渡すと精度が上がる

### 4. スキルの実行

- `skill_list` で一覧を確認
- 例: EARS 要件分析 → `skill_execute` で `SKILL-REQ-EARS-001` に自然言語を渡す
- このリポジトリ用に登録したスキル（例: PDF→PPTX 変換）も `skill_list` に表示され、`skill_execute` で実行可能

### 5. 知識グラフの利用

- パターン・要件・設計を `query_knowledge` で検索
- 新規ノードは `update_knowledge` で追加
- 整合性は `validate` / `validate_triple` / `check_circular` で確認

---

## 登録済みスキル例（Musubix 側）

| ID | 名前 | 用途 |
|----|------|------|
| SKILL-REQ-EARS-001 | EARS Requirements Analysis | 自然言語 → EARS 形式要件 |
| SKILL-DES-C4-001 | C4 Design Generation | 要件 → C4 設計 |
| SKILL-CODE-ANALYZE-001 | Code Analysis | コード静的解析 |
| SKILL-TEST-GEN-001 | Test Generation | テスト自動生成（Vitest 等） |
| SKILL-KG-QUERY-001 | Knowledge Graph Query | 知識グラフ検索 |

このリポジトリ用に登録したスキル:

| ID | 名前 | 用途 |
|----|------|------|
| SKILL-PDF2PPTX-001 | NotebookLM PDF to PPTX Conversion | PDF→PPTX 変換（inputPath, outputPath, useLlm） |

その他、プロジェクト固有のスキルは `skill_register` で追加できます。

---

## トラブルシューティング

- **ツールが一覧に出ない**: Cursor の MCP 設定で `notebooklm-transformer-musubix` が有効か確認し、Cursor を再起動
- **workflow_transition で Phase 4 に直接遷移できない**: 設計(Phase 2) から実装(Phase 4) への直遷移は禁止。必ずタスク分解(Phase 3) を経由
- **formal_verify が重い**: `verificationMode: "syntax-only"` や `timeout` で調整可能

---

## 参考

- 本プロジェクトの技術方針: ルートの [.cursorrules](/.cursorrules) および [README](/README.md)
- Stitch MCP の設定: [MCP-STITCH-SETUP.md](./MCP-STITCH-SETUP.md)
