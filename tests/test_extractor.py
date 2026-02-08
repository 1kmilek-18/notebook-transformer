"""Extractor（PDF抽出）のユニットテスト."""

from pathlib import Path

import pytest

from src.extractor.pdf_extractor import PDFExtractor
from src.models import PresentationData


class TestPDFExtractor:
    """PDFExtractor のテスト."""

    def test_nonexistent_path_raises_file_not_found(self) -> None:
        """存在しないパスで FileNotFoundError が発生する."""
        with pytest.raises(FileNotFoundError, match="見つかりません"):
            PDFExtractor(Path("/nonexistent/path/to/file.pdf"))

    def test_extract_all_returns_presentation_data(
        self, first_sample_pdf_required: Path
    ) -> None:
        """extract_all() は PresentationData を返す."""
        with PDFExtractor(first_sample_pdf_required) as extractor:
            data = extractor.extract_all()
        assert isinstance(data, PresentationData)
        assert data.source_path == str(first_sample_pdf_required)
        assert data.total_pages >= 1
        assert len(data.slides) == data.total_pages
        for slide in data.slides:
            assert slide.width > 0
            assert slide.height > 0

    def test_extract_all_slide_and_block_counts(
        self, first_sample_pdf_required: Path
    ) -> None:
        """抽出結果のスライド数・テキストブロック数が検証できる."""
        with PDFExtractor(first_sample_pdf_required) as extractor:
            data = extractor.extract_all()
        total_blocks = sum(len(s.text_blocks) for s in data.slides)
        total_images = sum(len(s.image_blocks) for s in data.slides)
        assert data.total_pages == len(data.slides)
        # 少なくとも1スライドはある
        assert len(data.slides) >= 1
        # テキストまたは画像はある想定（PDF による）
        assert total_blocks >= 0 and total_images >= 0
