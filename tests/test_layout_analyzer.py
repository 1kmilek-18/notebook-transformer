"""レイアウト解析のユニットテスト."""

from src.analyzer.layout_analyzer import LayoutAnalyzer
from src.models import (
    BoundingBox,
    ElementType,
    FontInfo,
    SlideData,
    TextBlock,
    TextSpan,
)


def _make_block(
    text: str,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    font_size: float = 12.0,
    bold: bool = False,
) -> TextBlock:
    """テスト用のTextBlockを生成するヘルパー."""
    return TextBlock(
        spans=[
            TextSpan(
                text=text,
                font=FontInfo(size=font_size, bold=bold),
            )
        ],
        bbox=BoundingBox(x0=x0, y0=y0, x1=x1, y1=y1),
    )


class TestLayoutAnalyzer:
    """LayoutAnalyzerのヒューリスティック解析テスト."""

    def setup_method(self) -> None:
        self.analyzer = LayoutAnalyzer()

    def test_title_detection(self) -> None:
        """大きいフォントサイズで上部にある要素はtitleと判定."""
        slide = SlideData(
            page_number=1,
            width=720.0,
            height=405.0,
            text_blocks=[
                _make_block("スライドタイトル", 50, 30, 670, 80, font_size=28.0, bold=True),
                _make_block("本文テキスト", 50, 120, 670, 350, font_size=14.0),
            ],
        )
        self.analyzer._analyze_slide_heuristic(slide)
        assert slide.text_blocks[0].element_type == ElementType.TITLE

    def test_footer_detection(self) -> None:
        """下部にある小さいテキストはfooterと判定."""
        slide = SlideData(
            page_number=1,
            width=720.0,
            height=405.0,
            text_blocks=[
                _make_block("メインテキスト", 50, 100, 670, 300, font_size=24.0),
                _make_block("ページ 1", 300, 380, 420, 400, font_size=8.0),
            ],
        )
        self.analyzer._analyze_slide_heuristic(slide)
        assert slide.text_blocks[1].element_type == ElementType.FOOTER

    def test_bullet_detection(self) -> None:
        """箇条書き記号で始まるテキストはbulletと判定."""
        slide = SlideData(
            page_number=1,
            width=720.0,
            height=405.0,
            text_blocks=[
                _make_block("タイトル", 50, 30, 670, 80, font_size=24.0),
                _make_block("• 箇条書き項目", 70, 150, 670, 180, font_size=14.0),
            ],
        )
        self.analyzer._analyze_slide_heuristic(slide)
        assert slide.text_blocks[1].element_type == ElementType.BULLET
