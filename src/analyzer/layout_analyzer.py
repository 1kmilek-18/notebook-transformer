"""LLMを活用してスライドレイアウトの意味を解釈するモジュール."""

from __future__ import annotations

import json
import logging
from typing import Optional

from src.models import (
    ElementType,
    PresentationData,
    SlideData,
    TextBlock,
)

logger = logging.getLogger(__name__)

# レイアウト解析用のシステムプロンプト
LAYOUT_ANALYSIS_PROMPT = """\
あなたはPDFスライドのレイアウト解析のエキスパートです。
以下のJSON形式のテキストブロック情報を分析し、各ブロックの役割を判定してください。

判定カテゴリ:
- title: スライドのメインタイトル
- subtitle: サブタイトル
- body: 本文テキスト
- bullet: 箇条書き項目
- header: ヘッダー領域
- footer: フッター領域（ページ番号、日付など）
- unknown: 判定不能

判定基準:
1. 座標: 上部にあるものはtitle/header、下部はfooter
2. フォントサイズ: 大きいものはtitle、中くらいはsubtitle
3. テキスト内容: 番号や記号で始まるものはbullet
4. 位置関係: インデントされているものはbullet/body

JSON配列で返してください。各要素は {"block_index": int, "element_type": str} の形式です。
"""


class LayoutAnalyzer:
    """スライドレイアウトを解析し、各要素の意味的役割を判定するクラス.

    ヒューリスティック（ルールベース）分析と、
    オプションでLLM（Claude API）による高精度分析を提供する。
    """

    def __init__(self, anthropic_client: Optional[object] = None, model: str = "claude-sonnet-4-20250514") -> None:
        """LayoutAnalyzerを初期化する.

        Args:
            anthropic_client: Anthropic APIクライアント（Noneの場合はルールベースのみ）
            model: 使用するLLMモデル名
        """
        self.client = anthropic_client
        self.model = model

    def analyze_presentation(self, presentation: PresentationData) -> PresentationData:
        """プレゼンテーション全体のレイアウトを解析する.

        Args:
            presentation: 抽出済みプレゼンテーションデータ

        Returns:
            要素タイプが付与されたプレゼンテーションデータ
        """
        for slide in presentation.slides:
            self._analyze_slide_heuristic(slide)

        logger.info("レイアウト解析完了: %d スライド", len(presentation.slides))
        return presentation

    def _analyze_slide_heuristic(self, slide: SlideData) -> None:
        """ヒューリスティック（ルールベース）でスライドレイアウトを解析する.

        座標、フォントサイズ、テキスト内容に基づいて各テキストブロックの
        ElementTypeを判定する。

        Args:
            slide: 1スライド分のデータ
        """
        if not slide.text_blocks:
            return

        # フォントサイズで降順ソートし、最大サイズを取得
        sorted_by_size = sorted(
            slide.text_blocks,
            key=lambda b: max((s.font.size for s in b.spans), default=0),
            reverse=True,
        )
        max_font_size = max(
            (s.font.size for b in slide.text_blocks for s in b.spans), default=12.0
        )

        for block in slide.text_blocks:
            block.element_type = self._classify_block(block, slide, max_font_size)

    def _classify_block(
        self, block: TextBlock, slide: SlideData, max_font_size: float
    ) -> ElementType:
        """個別のテキストブロックを分類する.

        Args:
            block: 分類対象のテキストブロック
            slide: スライドデータ（相対位置の計算に使用）
            max_font_size: スライド内の最大フォントサイズ

        Returns:
            判定されたElementType
        """
        text = block.full_text.strip()
        if not text:
            return ElementType.UNKNOWN

        avg_font_size = (
            sum(s.font.size for s in block.spans) / len(block.spans) if block.spans else 12.0
        )

        # 相対位置（0.0 = 上端, 1.0 = 下端）
        relative_y = block.bbox.y0 / slide.height if slide.height > 0 else 0.5

        # フッター判定: 下部 20% にある小さいテキスト
        if relative_y > 0.85 and avg_font_size < max_font_size * 0.6:
            return ElementType.FOOTER

        # ヘッダー判定: 上部 10% にある小さいテキスト
        if relative_y < 0.1 and avg_font_size < max_font_size * 0.7:
            return ElementType.HEADER

        # タイトル判定: 大きいフォントサイズ
        if avg_font_size >= max_font_size * 0.85 and relative_y < 0.4:
            return ElementType.TITLE

        # サブタイトル判定
        if avg_font_size >= max_font_size * 0.65 and relative_y < 0.45:
            return ElementType.SUBTITLE

        # 箇条書き判定: 先頭文字が箇条書き記号
        bullet_chars = {"•", "・", "‣", "◦", "▪", "▸", "►", "■", "-", "–", "―"}
        if text and (text[0] in bullet_chars or (len(text) > 2 and text[1] == ".")):
            return ElementType.BULLET

        # それ以外は本文
        return ElementType.BODY

    async def analyze_slide_with_llm(self, slide: SlideData) -> None:
        """LLM（Claude API）を使用してスライドレイアウトを解析する.

        Args:
            slide: 1スライド分のデータ

        Raises:
            RuntimeError: APIクライアントが設定されていない場合
        """
        if self.client is None:
            raise RuntimeError("Anthropic APIクライアントが設定されていません。")

        # テキストブロック情報をJSON化
        blocks_info = []
        for idx, block in enumerate(slide.text_blocks):
            blocks_info.append(
                {
                    "block_index": idx,
                    "text": block.full_text[:200],  # 長すぎるテキストは切り詰め
                    "bbox": {
                        "x0": round(block.bbox.x0, 1),
                        "y0": round(block.bbox.y0, 1),
                        "x1": round(block.bbox.x1, 1),
                        "y1": round(block.bbox.y1, 1),
                    },
                    "avg_font_size": round(
                        sum(s.font.size for s in block.spans) / len(block.spans)
                        if block.spans
                        else 12.0,
                        1,
                    ),
                    "is_bold": any(s.font.bold for s in block.spans),
                }
            )

        user_message = (
            f"スライドサイズ: {slide.width:.0f} x {slide.height:.0f} pt\n\n"
            f"テキストブロック:\n{json.dumps(blocks_info, ensure_ascii=False, indent=2)}"
        )

        try:
            # Anthropic API呼び出し
            response = await self.client.messages.create(  # type: ignore[union-attr]
                model=self.model,
                max_tokens=1024,
                system=LAYOUT_ANALYSIS_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )

            # レスポンス解析
            result_text = response.content[0].text  # type: ignore[index]
            results = json.loads(result_text)

            for item in results:
                idx = item.get("block_index")
                etype = item.get("element_type", "unknown")
                if idx is not None and 0 <= idx < len(slide.text_blocks):
                    try:
                        slide.text_blocks[idx].element_type = ElementType(etype)
                    except ValueError:
                        logger.warning("不明な要素タイプ: %s", etype)

            logger.info("LLM解析完了: %d ブロック", len(results))

        except Exception as e:
            logger.error("LLM解析に失敗: %s. ヒューリスティック解析にフォールバック", e)
            self._analyze_slide_heuristic(slide)
