"""サンプル PDF を使った統合テスト.

pdf/ または input/ に .pdf が無い場合はスキップする。
"""

from pathlib import Path

import pytest

from src.main import convert_pdf_to_pptx


class TestSamplePdfIntegration:
    """サンプル PDF による E2E 統合テスト."""

    def test_convert_produces_pptx_file(
        self, first_sample_pdf_required: Path, tmp_path: Path
    ) -> None:
        """変換が完了し、出力ファイルが存在しサイズが 0 より大きい."""
        output_pptx = tmp_path / "result.pptx"
        result = convert_pdf_to_pptx(
            first_sample_pdf_required,
            output_pptx,
            use_llm=False,
            save_images=False,
        )
        assert result == output_pptx
        assert output_pptx.exists()
        assert output_pptx.stat().st_size > 0

    def test_convert_overwrites_existing_file(
        self, first_sample_pdf_required: Path, tmp_path: Path
    ) -> None:
        """既存の出力ファイルは上書きされる."""
        output_pptx = tmp_path / "result.pptx"
        convert_pdf_to_pptx(
            first_sample_pdf_required,
            output_pptx,
            use_llm=False,
            save_images=False,
        )
        size_first = output_pptx.stat().st_size
        convert_pdf_to_pptx(
            first_sample_pdf_required,
            output_pptx,
            use_llm=False,
            save_images=False,
        )
        assert output_pptx.exists()
        assert output_pptx.stat().st_size == size_first
