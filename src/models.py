"""PDF要素とスライド構造を表すPydanticモデル群."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ElementType(str, Enum):
    """スライド内の要素タイプ."""

    TITLE = "title"
    SUBTITLE = "subtitle"
    BODY = "body"
    BULLET = "bullet"
    HEADER = "header"
    FOOTER = "footer"
    IMAGE = "image"
    SHAPE = "shape"
    TABLE = "table"
    UNKNOWN = "unknown"


class BoundingBox(BaseModel):
    """要素の座標情報（PDF座標系: ポイント単位）."""

    x0: float = Field(description="左上X座標 (pt)")
    y0: float = Field(description="左上Y座標 (pt)")
    x1: float = Field(description="右下X座標 (pt)")
    y1: float = Field(description="右下Y座標 (pt)")

    @property
    def width(self) -> float:
        """幅をポイント単位で返す."""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """高さをポイント単位で返す."""
        return self.y1 - self.y0

    @property
    def center_x(self) -> float:
        """中心X座標."""
        return (self.x0 + self.x1) / 2

    @property
    def center_y(self) -> float:
        """中心Y座標."""
        return (self.y0 + self.y1) / 2


class FontInfo(BaseModel):
    """フォント情報."""

    name: str = "Arial"
    size: float = Field(default=12.0, description="フォントサイズ (pt)")
    bold: bool = False
    italic: bool = False
    color: str = Field(default="#000000", description="16進数カラーコード")


class TextSpan(BaseModel):
    """テキスト内の書式付きスパン（1つのフォント設定が適用される範囲）."""

    text: str
    font: FontInfo = Field(default_factory=FontInfo)
    bbox: Optional[BoundingBox] = None


class TextBlock(BaseModel):
    """テキストブロック（1つのテキストボックスに相当）."""

    spans: list[TextSpan] = Field(default_factory=list)
    bbox: BoundingBox
    element_type: ElementType = ElementType.UNKNOWN
    line_spacing: float = Field(default=1.0, description="行間倍率")
    alignment: str = Field(default="left", description="テキスト揃え: left, center, right")

    @property
    def full_text(self) -> str:
        """すべてのスパンを連結したテキスト."""
        return "".join(span.text for span in self.spans)


class ImageBlock(BaseModel):
    """画像ブロック."""

    bbox: BoundingBox
    image_data: bytes = Field(default=b"", repr=False)
    image_format: str = Field(default="png", description="画像フォーマット: png, jpeg等")
    element_type: ElementType = ElementType.IMAGE
    source_path: Optional[str] = Field(default=None, description="保存先パス")


class SlideData(BaseModel):
    """1スライド分の抽出データ."""

    page_number: int
    width: float = Field(description="スライド幅 (pt)")
    height: float = Field(description="スライド高さ (pt)")
    text_blocks: list[TextBlock] = Field(default_factory=list)
    image_blocks: list[ImageBlock] = Field(default_factory=list)
    background_color: Optional[str] = Field(default=None, description="背景色")


class PresentationData(BaseModel):
    """プレゼンテーション全体の抽出データ."""

    source_path: str
    total_pages: int
    slides: list[SlideData] = Field(default_factory=list)
    slide_width: float = Field(default=720.0, description="標準スライド幅 (pt) - 10インチ")
    slide_height: float = Field(default=405.0, description="標準スライド高さ (pt) - 5.625インチ (16:9)")
