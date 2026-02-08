# タスク分解・スプリント計画

**参照**: 設計書（design-c4.md 1.1）、要求定義書 1.2、EARS 分析  
**スプリント**: 5 日間、1 日あたり最大 6 時間の実作業、レビュー・結合用にバッファを考慮  
**タスク ID**: TSK-XXX-NNN（XXX=分類, NNN=連番）

---

## タスク一覧

### Setup（環境・設定）

| ID | Title | Description | Est.h | Dependencies | Design Ref | Acceptance Criteria |
|----|--------|-------------|-------|--------------|------------|---------------------|
| **TSK-SET-001** | 開発環境と依存関係の検証 | Python 3.10+ の venv、requirements.txt / pyproject.toml の依存が揃うことを確認。pytest が実行可能であること。 | 1 | なし | 3.2, 7 | venv で `pip install -r requirements.txt` 後、`pytest` と `python -m src.main --help` が成功する。 |
| **TSK-SET-002** | Config と環境変数の整備 | config/settings.py で API キー・ログレベル・画像 DPI 等を環境変数/.env から読む。.env.example に ANTHROPIC_API_KEY 等の例を記載。 | 1.5 | TSK-SET-001 | 4.5, ADR-5, 7 | 設定がハードコードされておらず、.env で上書きできる。REQ-CON-004 を満たす。 |
| **TSK-SET-003** | 出力ディレクトリ自動作成の実装 | 出力パスの親ディレクトリが存在しない場合に自動作成する。作成失敗時は例外を上げ、CLI でメッセージ・ログ・非ゼロ終了。 | 1 | TSK-SET-001 | 4.3, 4.4, ADR-6, REQ-ERR-003 | 存在しない親ディレクトリを指定したときに PPTX が出力される。作成権限がない場合はエラー終了する。 |

### Core（主要機能）

| ID | Title | Description | Est.h | Dependencies | Design Ref | Acceptance Criteria |
|----|--------|-------------|-------|--------------|------------|---------------------|
| **TSK-COR-001** | Models の型ヒントと整合性確認 | models.py の PresentationData, SlideData, TextBlock, ImageBlock, BoundingBox, FontInfo, ElementType に型ヒントが付与されていることを確認し、不足があれば追加。 | 1 | TSK-SET-001 | 4.5, 7, REQ-CON-006 | 全公開モデルに型ヒントがあり、mypy が通る（または既存の型が設計と一致する）。 |
| **TSK-COR-002** | utils/coordinate の pt→EMU 実装確認 | pt から EMU への変換が EMU = pt × 12,700 で一貫して実装されていることを確認。Builder がここを経由していることを確認。 | 0.5 | TSK-COR-001 | 4.3, 4.5, ADR-4, REQ-CON-003 | 変換式が 1 箇所に集約され、単体テストで検証されている。 |
| **TSK-COR-003** | utils/image_processing の確認 | 画像の切り出しが OpenCV または Pillow で実装されていることを確認。Extractor/Builder から利用されていること。 | 0.5 | TSK-COR-001 | 4.1, 4.5, REQ-IMG-002 | 画像処理が OpenCV/Pillow に依存し、既存テストまたは手動で動作確認できる。 |
| **TSK-COR-004** | Extractor のインターフェースと例外の整備 | PDFExtractor が extract_all() で PresentationData を返すことを確認。ファイル不存在は FileNotFoundError、破損 PDF は ValueError 等で伝播するようにする。 | 2 | TSK-COR-001, TSK-SET-002 | 4.1, ADR-6 | 存在しないパスで FileNotFoundError、破損 PDF で適切な例外。REQ-ERR-001, REQ-ERR-002。 |
| **TSK-COR-005** | Analyzer のヒューリスティックと LLM フォールバック | 座標・フォントサイズによるタイトル/本文/箇条書きの判定を確認。LLM 有効かつ API キー未設定時は警告ログを出してヒューリスティックにフォールバック。 | 2 | TSK-COR-001, TSK-SET-002 | 4.2, REQ-LAY-001, REQ-LAY-003 | API キー未設定時も変換が完了し、警告がログに出る。REQ-ERR-006 のフォールバックが動作する。 |
| **TSK-COR-006** | Builder のテキスト・画像・テンプレートと親ディレクトリ作成 | add_textbox で座標維持・フォント再現。画像挿入。テンプレート指定時はマスターを利用。出力前に親ディレクトリを自動作成（TSK-SET-003 と連携）。 | 3 | TSK-COR-001, TSK-COR-002, TSK-SET-003 | 4.3, REQ-TXT-001〜003, REQ-IMG-001, REQ-TMP-001/002 | 出力 PPTX が PowerPoint で編集可能。テンプレート未指定時は空白プレゼン。親ディレクトリが自動作成される。 |
| **TSK-COR-007** | CLI のオプションとエラー処理の統一 | pdf_path, -o, -t, --use-llm, --log-level を解釈。例外捕捉でメッセージ・ログ・sys.exit(non_zero)。ログレベルで INFO/ERROR/DEBUG を切り替え。 | 2 | TSK-COR-004, TSK-COR-005, TSK-COR-006 | 4.4, ADR-6, 6.4 | --help に全オプションが表示される。異常終了時に非ゼロ exit とログが記録される。REQ-CLI-001〜004, REQ-NF-001。 |

### Integration（結合）

| ID | Title | Description | Est.h | Dependencies | Design Ref | Acceptance Criteria |
|----|--------|-------------|-------|--------------|------------|---------------------|
| **TSK-INT-001** | パイプライン E2E の結合確認 | main から Extractor → Analyzer → Builder の順で 1 本の PDF が PPTX に変換されることを確認。既存ファイルは上書きされることを確認。 | 1.5 | TSK-COR-007 | 3, 4.4, REQ-FLO-001, REQ-CLI-004 | `python -m src.main input/sample.pdf -o output/out.pptx` で PPTX が生成され、再実行で上書きされる。 |
| **TSK-INT-002** | エラー経路の結合確認 | 入力不存在・破損 PDF・テンプレート不存在・出力先作成失敗の各経路で、メッセージ・ログ・終了コードが要求どおりであることを確認。 | 1 | TSK-INT-001 | 4.4, ADR-6, REQ-ERR-* | 各エラー条件で stderr にメッセージが出て、非ゼロ終了し、ログに記録される。 |

### Testing（テスト）

| ID | Title | Description | Est.h | Dependencies | Design Ref | Acceptance Criteria |
|----|--------|-------------|-------|--------------|------------|---------------------|
| **TSK-TST-001** | Models と coordinate のユニットテスト | test_models.py, test_coordinate.py が設計のデータ契約と変換式をカバーしていることを確認。不足ケースを追加。 | 1 | TSK-COR-001, TSK-COR-002 | 4.5, 7 | 既存テストが通る。境界値・不正入力のケースが含まれる。 |
| **TSK-TST-002** | LayoutAnalyzer のユニットテスト | ヒューリスティックでタイトル/本文/箇条書きが付与されることをテスト。モックで LLM 未使用時の挙動を検証。 | 1.5 | TSK-COR-005 | 4.2, REQ-LAY-001 | test_layout_analyzer で ElementType が期待どおり付与される。 |
| **TSK-TST-003** | Extractor のユニットテスト | 小さな PDF またはモックで extract_all() が PresentationData を返すことを検証。例外経路のテスト。 | 1.5 | TSK-COR-004 | 4.1 | 抽出結果のスライド数・テキストブロック数が検証できる。FileNotFoundError のテストがある。 |
| **TSK-TST-004** | Builder のユニットテスト | 最小の PresentationData から PPTX が生成され、テキストボックスが存在することを検証。座標・フォントの再現を 1 件以上確認。 | 2 | TSK-COR-006 | 4.3, REQ-TXT-001 | 生成 PPTX を開いてテキストが編集可能であることを確認するテストまたは手動手順が明文化されている。 |
| **TSK-TST-005** | サンプル PDF による統合テスト | conftest の first_sample_pdf を使い、変換が完了して出力ファイルが存在・サイズ>0 であることを検証。サンプルが無い場合はスキップ。 | 0.5 | TSK-INT-001 | 6（要求定義 セクション 6） | tests/test_sample_pdf_integration.py がサンプル PDF ありでパスする。 |

### Documentation（ドキュメント）

| ID | Title | Description | Est.h | Dependencies | Design Ref | Acceptance Criteria |
|----|--------|-------------|-------|--------------|------------|---------------------|
| **TSK-DOC-001** | 公開 API の docstring と型ヒントの揃え | main.convert_pdf_to_pptx、Extractor.extract_all、Analyzer.analyze_presentation、Builder.build/save 等に Google style の docstring と型ヒントを揃える。 | 1.5 | TSK-COR-007 | 4.x, REQ-CON-006, 7 | 主要関数に docstring があり、型ヒントが付与されている。 |
| **TSK-DOC-002** | README と設計・要求の参照更新 | README の使い方・オプション・サンプル PDF パスを要求定義・設計と一致させる。設計書 7 のコード配置が実装と一致していることを確認。 | 1 | TSK-INT-001 | 1, 7 | README から CLI の基本的な実行ができ、docs への参照が正しい。 |

---

## スプリント割り当て（5 日間 × 最大 6h/日）

| Day | タスク | 内容 | 合計 h |
|-----|--------|------|--------|
| **1** | TSK-SET-001, TSK-SET-002, TSK-COR-001, TSK-COR-002 | 環境検証、Config 整備、Models 確認、coordinate 確認 | 4 |
| **2** | TSK-SET-003, TSK-COR-003, TSK-COR-004 | 出力ディレクトリ自動作成、image_processing 確認、Extractor 整備 | 3.5 |
| **3** | TSK-COR-005, TSK-COR-006 | Analyzer ヒューリスティック・LLM フォールバック、Builder テキスト・画像・テンプレート | 5 |
| **4** | TSK-COR-007, TSK-INT-001, TSK-INT-002 | CLI オプション・エラー統一、E2E 結合、エラー経路確認 | 4.5 |
| **5** | TSK-TST-001〜005, TSK-DOC-001, TSK-DOC-002 | ユニット・統合テスト、docstring・README 更新 | 7.5 |

---

*本タスク分解は設計書 design-c4.md に基づく。実装状況に応じて「確認」を「実装」に読み替え、見積もりを調整すること。*
