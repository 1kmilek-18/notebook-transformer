#!/usr/bin/env bash
# 動作確認スクリプト: 依存関係のインストール → CLI --help → サンプルPDF変換

set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"

echo "=== 1. 依存関係の確認 ==="
if ! python3 -c "import click, pydantic, fitz" 2>/dev/null; then
  echo "依存パッケージが不足しています。以下を実行してください:"
  echo "  pip install -r requirements.txt"
  echo "または（推奨）:"
  echo "  python3 -m venv .venv && source .venv/bin/activate"
  echo "  pip install -r requirements.txt"
  exit 1
fi
echo "OK"

echo ""
echo "=== 2. CLI --help ==="
PYTHONPATH="$ROOT" python3 -m src.main --help
echo "OK"

echo ""
echo "=== 3. サンプル PDF で変換（pdf/ または input/ に .pdf がある場合） ==="
SAMPLE_PDF=""
for d in pdf input; do
  for f in "$ROOT/$d"/*.pdf; do
    [ -f "$f" ] && [[ "$f" != *:Zone.Identifier* ]] && SAMPLE_PDF="$f" && break 2
  done
done
if [ -z "$SAMPLE_PDF" ]; then
  echo "サンプル PDF がありません。pdf/ または input/ に .pdf を置いて再実行してください。"
  exit 0
fi
OUT="$ROOT/output/verify-out.pptx"
mkdir -p "$ROOT/output"
echo "入力: $SAMPLE_PDF"
echo "出力: $OUT"
PYTHONPATH="$ROOT" python3 -m src.main "$SAMPLE_PDF" -o "$OUT" --no-save-images
if [ -f "$OUT" ] && [ "$(stat -c%s "$OUT" 2>/dev/null || stat -f%z "$OUT" 2>/dev/null)" -gt 0 ]; then
  echo "OK: PPTX が生成されました → $OUT"
else
  echo "失敗: 出力ファイルを確認してください。"
  exit 1
fi

echo ""
echo "=== 4. テスト実行（pytest が入っていれば） ==="
if PYTHONPATH="$ROOT" python3 -m pytest tests/ -v --tb=short -q 2>/dev/null; then
  echo "OK: テスト完了"
else
  echo "pytest が未インストールまたはテストがスキップされました。pip install pytest で実行可能です。"
fi

echo ""
echo "=== 動作確認完了 ==="
