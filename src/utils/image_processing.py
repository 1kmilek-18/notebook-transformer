"""画像処理ユーティリティ.

OpenCVとPillowを使用した画像のトリミング・変換機能を提供する。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def crop_region_from_image(
    image_path: str | Path,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    output_path: Optional[str | Path] = None,
) -> Image.Image:
    """画像から指定領域を切り出す.

    Args:
        image_path: 入力画像パス
        x0: 左上X座標（ピクセル）
        y0: 左上Y座標（ピクセル）
        x1: 右下X座標（ピクセル）
        y1: 右下Y座標（ピクセル）
        output_path: 保存先パス（Noneの場合は保存しない）

    Returns:
        切り出されたPillow Imageオブジェクト
    """
    img = Image.open(image_path)
    cropped = img.crop((x0, y0, x1, y1))

    if output_path:
        cropped.save(str(output_path))
        logger.info("画像を切り出して保存: %s", output_path)

    return cropped


def render_pdf_page_to_image(
    page: object,
    dpi: int = 300,
    output_path: Optional[str | Path] = None,
) -> Image.Image:
    """PyMuPDFのページをPillow画像にレンダリングする.

    Args:
        page: fitz.Pageオブジェクト
        dpi: 解像度（デフォルト300dpi）
        output_path: 保存先パス（Noneの場合は保存しない）

    Returns:
        レンダリングされたPillow Imageオブジェクト
    """
    zoom = dpi / 72.0
    mat = __import__("fitz").Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)  # type: ignore[attr-defined]

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    if output_path:
        img.save(str(output_path))
        logger.info("ページを画像化して保存: %s", output_path)

    return img


def extract_region_as_image(
    page: object,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    dpi: int = 300,
    output_path: Optional[str | Path] = None,
) -> Image.Image:
    """PDFページの指定領域を画像として切り出す.

    Args:
        page: fitz.Pageオブジェクト
        x0: 左上X座標（pt）
        y0: 左上Y座標（pt）
        x1: 右下X座標（pt）
        y1: 右下Y座標（pt）
        dpi: 解像度
        output_path: 保存先パス

    Returns:
        切り出されたPillow Imageオブジェクト
    """
    import fitz

    clip = fitz.Rect(x0, y0, x1, y1)
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=clip)  # type: ignore[attr-defined]

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    if output_path:
        img.save(str(output_path))
        logger.info("領域を画像として保存: %s", output_path)

    return img


def enhance_image_for_ocr(image: Image.Image) -> Image.Image:
    """OCR精度向上のために画像を前処理する.

    Args:
        image: 入力Pillow Imageオブジェクト

    Returns:
        前処理済みPillow Imageオブジェクト
    """
    # Pillow -> OpenCV(numpy)
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # グレースケール変換
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # 二値化（大津の方法）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # ノイズ除去
    denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

    # OpenCV -> Pillow
    result = Image.fromarray(denoised)
    return result
