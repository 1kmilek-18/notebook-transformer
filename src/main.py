"""NotebookLM PDF → PowerPoint 変換ツール メインエントリーポイント.

CLIインターフェースを提供し、PDF→PPTX変換パイプラインを実行する。
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.analyzer import LayoutAnalyzer
from src.builder import PPTXBuilder
from src.extractor import PDFExtractor

console = Console()

# 環境変数の読み込み
load_dotenv()


def setup_logging(level: str = "INFO") -> None:
    """ログの設定を行う.

    Args:
        level: ログレベル（DEBUG, INFO, WARNING, ERROR）
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def convert_pdf_to_pptx(
    pdf_path: str | Path,
    output_path: str | Path,
    template_path: Optional[str | Path] = None,
    use_llm: bool = False,
    save_images: bool = True,
) -> Path:
    """PDFファイルをPowerPointに変換する.

    Args:
        pdf_path: 入力PDFファイルパス
        output_path: 出力PPTXファイルパス
        template_path: テンプレートファイルパス（オプション）
        use_llm: LLMによるレイアウト解析を使用するか
        save_images: 画像を中間ファイルとして保存するか

    Returns:
        保存されたPPTXファイルのPath
    """
    logger = logging.getLogger(__name__)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # ステップ1: PDF解析
        task1 = progress.add_task("PDFを解析中...", total=None)
        with PDFExtractor(pdf_path) as extractor:
            presentation_data = extractor.extract_all()

            if save_images:
                images_dir = Path(output_path).parent / "images"
                extractor.save_images(presentation_data, images_dir)

        progress.update(task1, completed=True, description="[green]PDF解析完了")
        logger.info(
            "抽出完了: %d スライド, テキスト %d ブロック, 画像 %d 個",
            len(presentation_data.slides),
            sum(len(s.text_blocks) for s in presentation_data.slides),
            sum(len(s.image_blocks) for s in presentation_data.slides),
        )

        # ステップ2: レイアウト解析
        task2 = progress.add_task("レイアウトを解析中...", total=None)

        analyzer: LayoutAnalyzer
        if use_llm:
            try:
                import anthropic

                client = anthropic.Anthropic()
                analyzer = LayoutAnalyzer(anthropic_client=client)
                logger.info("LLMレイアウト解析を使用")
            except ImportError:
                logger.warning("anthropicパッケージが見つかりません。ルールベース解析を使用します。")
                analyzer = LayoutAnalyzer()
        else:
            analyzer = LayoutAnalyzer()

        presentation_data = analyzer.analyze_presentation(presentation_data)
        progress.update(task2, completed=True, description="[green]レイアウト解析完了")

        # ステップ3: PPTX構築
        task3 = progress.add_task("PowerPointを構築中...", total=None)
        builder = PPTXBuilder(template_path=template_path)
        builder.build(presentation_data)
        result_path = builder.save(output_path)
        progress.update(task3, completed=True, description="[green]PowerPoint構築完了")

    return result_path


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="出力PPTXファイルパス（デフォルト: 入力ファイル名.pptx）",
)
@click.option(
    "-t",
    "--template",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="PowerPointテンプレートファイルパス (.potx / .pptx)",
)
@click.option(
    "--use-llm / --no-llm",
    default=False,
    help="LLM（Claude API）によるレイアウト解析を使用する",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="ログレベル",
)
@click.option(
    "--save-images / --no-save-images",
    default=True,
    help="中間画像ファイルを保存する",
)
@click.version_option(version="0.1.0")
def cli(
    pdf_path: Path,
    output: Optional[Path],
    template: Optional[Path],
    use_llm: bool,
    log_level: str,
    save_images: bool,
) -> None:
    """NotebookLM PDFスライドを編集可能なPowerPointに変換します.

    PDF_PATH: 変換するPDFファイルのパス
    """
    setup_logging(log_level)

    # 出力パスのデフォルト設定
    if output is None:
        output = pdf_path.with_suffix(".pptx")

    console.print(f"\n[bold blue]NotebookLM PDF → PowerPoint 変換ツール[/bold blue]\n")
    console.print(f"  入力: {pdf_path}")
    console.print(f"  出力: {output}")
    if template:
        console.print(f"  テンプレート: {template}")
    console.print(f"  LLM解析: {'有効' if use_llm else '無効'}")
    console.print()

    try:
        result = convert_pdf_to_pptx(
            pdf_path=pdf_path,
            output_path=output,
            template_path=template,
            use_llm=use_llm,
            save_images=save_images,
        )
        console.print(f"\n[bold green]変換完了![/bold green] → {result}\n")
    except FileNotFoundError as e:
        console.print(f"\n[bold red]エラー:[/bold red] {e}\n")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]予期しないエラー:[/bold red] {e}\n")
        logging.getLogger(__name__).exception("変換処理中にエラーが発生")
        sys.exit(1)


if __name__ == "__main__":
    cli()
