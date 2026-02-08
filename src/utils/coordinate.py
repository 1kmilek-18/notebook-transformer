"""座標変換ユーティリティ.

PDF座標（ポイント単位）とPowerPoint座標（EMU単位）間の変換を提供する。

単位系:
- PDF: ポイント (pt) - 1pt = 1/72インチ
- PPTX: EMU (English Metric Unit) - 1インチ = 914400 EMU
- 変換: 1pt = 914400 / 72 = 12700 EMU
"""

from __future__ import annotations

# 1ポイント = 12700 EMU
PT_TO_EMU_FACTOR: int = 12700

# 1インチ = 914400 EMU
INCH_TO_EMU: int = 914400

# 1インチ = 72ポイント
INCH_TO_PT: float = 72.0

# 1センチ = 360000 EMU
CM_TO_EMU: int = 360000


def pt_to_emu(pt: float) -> int:
    """ポイントをEMUに変換する.

    Args:
        pt: ポイント値

    Returns:
        EMU値（整数）
    """
    return round(pt * PT_TO_EMU_FACTOR)


def emu_to_pt(emu: int) -> float:
    """EMUをポイントに変換する.

    Args:
        emu: EMU値

    Returns:
        ポイント値
    """
    return emu / PT_TO_EMU_FACTOR


def inches_to_emu(inches: float) -> int:
    """インチをEMUに変換する.

    Args:
        inches: インチ値

    Returns:
        EMU値（整数）
    """
    return round(inches * INCH_TO_EMU)


def cm_to_emu(cm: float) -> int:
    """センチメートルをEMUに変換する.

    Args:
        cm: センチメートル値

    Returns:
        EMU値（整数）
    """
    return round(cm * CM_TO_EMU)
