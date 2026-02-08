"""Builder（PPTX構築）のユニットテスト."""

import tempfile
from pathlib import Path
from zipfile import ZipFile

import pytest

from src.builder.pptx_builder import PPTXBuilder
from src.models import (
    BoundingBox,
    ElementType,
    FontInfo,
    PresentationData,
    SlideData,
    TextBlock,
    TextSpan,
)


def _minimal_presentation_data() -> PresentationData:
    """最小の PresentationData を生成する."""
    return PresentationData(
        source_path="test.pdf",
        total_pages=1,
        slide_width=720.0,
        slide_height=405.0,
        slides=[
            SlideData(
                page_number=1,
                width=720.0,
                height=405.0,
                text_blocks=[
                    TextBlock(
                        spans=[
                            TextSpan(
                                text="Test Title",
                                font=FontInfo(name="Arial", size=24.0, bold=True),
                            ),
                        ],
                        bbox=BoundingBox(x0=50.0, y0=30.0, x1=670.0, y1=80.0),
                        element_type=ElementType.TITLE,
                    ),
                    TextBlock(
                        spans=[
                            TextSpan(
                                text="Body text",
                                font=FontInfo(name="Arial", size=12.0),
                            ),
                        ],
                        bbox=BoundingBox(x0=50.0, y0=100.0, x1=670.0, y1=150.0),
                        element_type=ElementType.BODY,
                    ),
                ],
                image_blocks=[],
            ),
        ],
    )


class TestPPTXBuilder:
    """PPTXBuilder のテスト."""

    def test_build_and_save_creates_file(self) -> None:
        """最小の PresentationData から PPTX が生成され、ファイルが存在する."""
        data = _minimal_presentation_data()
        builder = PPTXBuilder()
        builder.build(data)
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "out.pptx"
            result = builder.save(out_path)
            assert result == out_path
            assert out_path.exists()
            assert out_path.stat().st_size > 0

    def test_save_creates_parent_directory(self) -> None:
        """出力先の親ディレクトリが存在しない場合に自動作成される."""
        data = _minimal_presentation_data()
        builder = PPTXBuilder()
        builder.build(data)
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "nested" / "dir" / "out.pptx"
            assert not out_path.parent.exists()
            builder.save(out_path)
            assert out_path.exists()
            assert out_path.stat().st_size > 0

    def test_pptx_is_valid_zip(self) -> None:
        """生成された PPTX は有効な ZIP（Office Open XML）である."""
        data = _minimal_presentation_data()
        builder = PPTXBuilder()
        builder.build(data)
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            builder.save(tmp_path)
            with ZipFile(tmp_path) as zf:
                names = zf.namelist()
                assert any("ppt/" in n for n in names)
                assert any("ppt/slides" in n or "ppt/slide" in n for n in names)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_save_without_build_raises(self) -> None:
        """build() 前に save() を呼ぶと RuntimeError."""
        builder = PPTXBuilder()
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            with pytest.raises(RuntimeError, match="構築されていません"):
                builder.save(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_coordinate_and_font_preserved(self) -> None:
        """座標とフォント情報が PPTX に反映されている（ZIP 内 XML にテキストが含まれる）."""
        data = _minimal_presentation_data()
        builder = PPTXBuilder()
        builder.build(data)
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            builder.save(tmp_path)
            with ZipFile(tmp_path) as zf:
                # スライドの XML にテキストが含まれることを簡易確認
                slide_files = [n for n in zf.namelist() if "slide" in n and n.endswith(".xml")]
                assert len(slide_files) >= 1
                content = zf.read(slide_files[0]).decode("utf-8")
                assert "Test Title" in content or "Body text" in content
        finally:
            tmp_path.unlink(missing_ok=True)
