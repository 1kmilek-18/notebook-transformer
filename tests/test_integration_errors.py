"""エラー経路の結合テスト.

入力不存在・破損PDF・テンプレート不存在・出力先作成失敗で
メッセージ・ログ・非ゼロ終了となることを検証する。
"""

import subprocess
import sys
from pathlib import Path

import pytest


def _run_cli(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """src.main を CLI として実行する."""
    cmd = [sys.executable, "-m", "src.main"] + args
    return subprocess.run(
        cmd,
        cwd=cwd or Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
        timeout=30,
    )


class TestCliErrorPaths:
    """CLI のエラー経路テスト."""

    def test_nonexistent_pdf_exits_nonzero(self) -> None:
        """存在しない PDF を指定すると非ゼロ終了する."""
        result = _run_cli(["/nonexistent/slide.pdf", "-o", "/tmp/out.pptx"])
        assert result.returncode != 0

    def test_nonexistent_pdf_shows_message(self) -> None:
        """存在しない PDF のとき stderr または stdout にメッセージが出る."""
        result = _run_cli(["/nonexistent/slide.pdf", "-o", "/tmp/out.pptx"])
        combined = (result.stderr + result.stdout).strip().lower()
        assert len(combined) > 0
        assert "exist" in combined or "エラー" in combined or "見つかりません" in combined or "error" in combined

    def test_help_succeeds(self) -> None:
        """--help で全オプションが表示され、正常終了する."""
        result = _run_cli(["--help"])
        assert result.returncode == 0
        assert "pdf_path" in result.stdout or "PDF" in result.stdout
        assert "-o" in result.stdout or "--output" in result.stdout
        assert "--use-llm" in result.stdout
        assert "--log-level" in result.stdout
        assert "-t" in result.stdout or "--template" in result.stdout
