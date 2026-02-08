"""PyMuPDFを使用してPDFからスライドデータを抽出するモジュール."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from src.models import (
    BoundingBox,
    FontInfo,
    ImageBlock,
    PresentationData,
    SlideData,
    TextBlock,
    TextSpan,
)

logger = logging.getLogger(__name__)


class PDFExtractor:
    """PDFファイルからスライド構造データを抽出するクラス.

    PyMuPDFを使用して各ページのテキストブロック、画像、座標情報を
    正確に抽出し、PresentationDataモデルに格納する。
    """

    def __init__(self, pdf_path: str | Path) -> None:
        """PDFExtractorを初期化する.

        Args:
            pdf_path: 読み込むPDFファイルのパス
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDFファイルが見つかりません: {self.pdf_path}")
        self._doc: Optional[fitz.Document] = None

    def open(self) -> None:
        """PDFドキュメントを開く."""
        logger.info("PDFを開いています: %s", self.pdf_path)
        self._doc = fitz.open(str(self.pdf_path))
        logger.info("ページ数: %d", len(self._doc))

    def close(self) -> None:
        """PDFドキュメントを閉じる."""
        if self._doc:
            self._doc.close()
            self._doc = None

    def __enter__(self) -> PDFExtractor:
        self.open()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @property
    def doc(self) -> fitz.Document:
        """開かれたドキュメントを返す."""
        if self._doc is None:
            raise RuntimeError("PDFが開かれていません。open()を先に呼び出してください。")
        return self._doc

    def extract_all(self) -> PresentationData:
        """全ページからスライドデータを抽出する.

        Returns:
            PresentationData: プレゼンテーション全体の構造データ
        """
        slides: list[SlideData] = []
        for page_num in range(len(self.doc)):
            logger.debug("ページ %d を処理中...", page_num + 1)
            slide = self._extract_page(page_num)
            slides.append(slide)

        first_page = self.doc[0]
        return PresentationData(
            source_path=str(self.pdf_path),
            total_pages=len(self.doc),
            slides=slides,
            slide_width=first_page.rect.width,
            slide_height=first_page.rect.height,
        )

    def _extract_page(self, page_num: int) -> SlideData:
        """1ページ分のスライドデータを抽出する.

        Args:
            page_num: ページ番号（0始まり）

        Returns:
            SlideData: 1スライド分の構造データ
        """
        page = self.doc[page_num]

        text_blocks = self._extract_text_blocks(page)
        image_blocks = self._extract_images(page, page_num)

        return SlideData(
            page_number=page_num + 1,
            width=page.rect.width,
            height=page.rect.height,
            text_blocks=text_blocks,
            image_blocks=image_blocks,
        )

    def _extract_text_blocks(self, page: fitz.Page) -> list[TextBlock]:
        """ページからテキストブロックを抽出する.

        PyMuPDFの `get_text("dict")` を使用して、フォント情報付きで
        テキストを抽出する。

        Args:
            page: PyMuPDFのPageオブジェクト

        Returns:
            テキストブロックのリスト
        """
        blocks: list[TextBlock] = []
        page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # type 0 = テキストブロック
                continue

            block_bbox = BoundingBox(
                x0=block["bbox"][0],
                y0=block["bbox"][1],
                x1=block["bbox"][2],
                y1=block["bbox"][3],
            )

            spans: list[TextSpan] = []
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    color_int = span.get("color", 0)
                    color_hex = f"#{color_int:06x}"

                    font_info = FontInfo(
                        name=span.get("font", "Arial"),
                        size=round(span.get("size", 12.0), 1),
                        bold="Bold" in span.get("font", "")
                        or "bold" in span.get("font", "").lower(),
                        italic="Italic" in span.get("font", "")
                        or "italic" in span.get("font", "").lower(),
                        color=color_hex,
                    )

                    span_bbox = BoundingBox(
                        x0=span["bbox"][0],
                        y0=span["bbox"][1],
                        x1=span["bbox"][2],
                        y1=span["bbox"][3],
                    )

                    spans.append(
                        TextSpan(
                            text=span.get("text", ""),
                            font=font_info,
                            bbox=span_bbox,
                        )
                    )

            if spans:
                blocks.append(
                    TextBlock(
                        spans=spans,
                        bbox=block_bbox,
                    )
                )

        logger.debug("テキストブロック %d 個を抽出", len(blocks))
        return blocks

    def _extract_images(self, page: fitz.Page, page_num: int) -> list[ImageBlock]:
        """ページから画像を抽出する.

        Args:
            page: PyMuPDFのPageオブジェクト
            page_num: ページ番号（0始まり）

        Returns:
            画像ブロックのリスト
        """
        images: list[ImageBlock] = []

        for img_index, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]

            try:
                base_image = self.doc.extract_image(xref)
                if base_image is None:
                    continue

                image_data = base_image.get("image", b"")
                image_ext = base_image.get("ext", "png")

                # 画像の表示位置を取得
                img_rects = page.get_image_rects(xref)
                if not img_rects:
                    continue

                rect = img_rects[0]
                bbox = BoundingBox(
                    x0=rect.x0,
                    y0=rect.y0,
                    x1=rect.x1,
                    y1=rect.y1,
                )

                images.append(
                    ImageBlock(
                        bbox=bbox,
                        image_data=image_data,
                        image_format=image_ext,
                    )
                )

            except Exception as e:
                logger.warning(
                    "ページ %d の画像 %d の抽出に失敗: %s",
                    page_num + 1,
                    img_index,
                    e,
                )

        logger.debug("画像 %d 個を抽出", len(images))
        return images

    def save_images(self, presentation: PresentationData, output_dir: str | Path) -> None:
        """抽出した画像をファイルに保存する.

        Args:
            presentation: 抽出済みプレゼンテーションデータ
            output_dir: 画像保存先ディレクトリ
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for slide in presentation.slides:
            for idx, img_block in enumerate(slide.image_blocks):
                filename = f"slide{slide.page_number:03d}_img{idx:03d}.{img_block.image_format}"
                filepath = output_path / filename
                filepath.write_bytes(img_block.image_data)
                img_block.source_path = str(filepath)
                logger.info("画像を保存: %s", filepath)
