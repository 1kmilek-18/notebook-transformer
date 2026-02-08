"""アプリケーション設定.

環境変数や設定ファイルからの設定値を一元管理する。
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """アプリケーション全体の設定."""

    # Anthropic API
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API Key",
    )
    llm_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="使用するLLMモデル名",
    )

    # 出力設定
    output_dir: Path = Field(
        default=Path("./output"),
        description="デフォルト出力ディレクトリ",
    )

    # ログ設定
    log_level: str = Field(
        default="INFO",
        description="ログレベル",
    )

    # PDF解析設定
    image_dpi: int = Field(
        default=300,
        description="画像レンダリングのDPI",
    )
    extract_images: bool = Field(
        default=True,
        description="画像を抽出するか",
    )

    # PPTX構築設定
    default_font: str = Field(
        default="Arial",
        description="デフォルトフォント名",
    )
    min_font_size: float = Field(
        default=6.0,
        description="最小フォントサイズ (pt)",
    )

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# シングルトンインスタンス
_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    """アプリケーション設定を取得する.

    Returns:
        AppSettings インスタンス
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings
