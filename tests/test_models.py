"""データモデルのユニットテスト."""

from src.models import (
    BoundingBox,
    ElementType,
    FontInfo,
    PresentationData,
    SlideData,
    TextBlock,
    TextSpan,
)


class TestBoundingBox:
    """BoundingBoxモデルのテスト."""

    def test_width_and_height(self) -> None:
        bbox = BoundingBox(x0=10.0, y0=20.0, x1=110.0, y1=80.0)
        assert bbox.width == 100.0
        assert bbox.height == 60.0

    def test_center(self) -> None:
        bbox = BoundingBox(x0=0.0, y0=0.0, x1=100.0, y1=50.0)
        assert bbox.center_x == 50.0
        assert bbox.center_y == 25.0


class TestTextBlock:
    """TextBlockモデルのテスト."""

    def test_full_text(self) -> None:
        block = TextBlock(
            spans=[
                TextSpan(text="Hello "),
                TextSpan(text="World"),
            ],
            bbox=BoundingBox(x0=0, y0=0, x1=100, y1=20),
        )
        assert block.full_text == "Hello World"

    def test_default_element_type(self) -> None:
        block = TextBlock(
            spans=[],
            bbox=BoundingBox(x0=0, y0=0, x1=100, y1=20),
        )
        assert block.element_type == ElementType.UNKNOWN


class TestFontInfo:
    """FontInfoモデルのテスト."""

    def test_defaults(self) -> None:
        font = FontInfo()
        assert font.name == "Arial"
        assert font.size == 12.0
        assert font.bold is False
        assert font.italic is False
        assert font.color == "#000000"


class TestSlideData:
    """SlideDataモデルのテスト."""

    def test_empty_slide(self) -> None:
        slide = SlideData(page_number=1, width=720.0, height=405.0)
        assert len(slide.text_blocks) == 0
        assert len(slide.image_blocks) == 0


class TestPresentationData:
    """PresentationDataモデルのテスト."""

    def test_default_dimensions(self) -> None:
        pres = PresentationData(
            source_path="test.pdf",
            total_pages=0,
        )
        assert pres.slide_width == 720.0
        assert pres.slide_height == 405.0
