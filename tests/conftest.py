"""pytest 共通フィクスチャ.

サンプル PDF は pdf/ または input/ に配置されている場合に利用可能。
"""

from pathlib import Path

import pytest


def _find_first_sample_pdf() -> Path | None:
    """プロジェクト内の最初のサンプル PDF パスを返す。見つからなければ None."""
    root = Path(__file__).resolve().parent.parent
    for dir_name in ("pdf", "input"):
        dir_path = root / dir_name
        if not dir_path.is_dir():
            continue
        for p in sorted(dir_path.glob("*.pdf")):
            if p.name.endswith(":Zone.Identifier"):
                continue
            return p
    return None


@pytest.fixture(scope="session")
def first_sample_pdf() -> Path | None:
    """サンプル PDF のパス。pdf/ または input/ に .pdf が無い場合は None."""
    return _find_first_sample_pdf()


@pytest.fixture(scope="session")
def first_sample_pdf_required(first_sample_pdf: Path | None) -> Path:
    """サンプル PDF が必須のテスト用。無い場合はスキップ."""
    if first_sample_pdf is None:
        pytest.skip("サンプル PDF がありません（pdf/ または input/ に .pdf を配置してください）")
    return first_sample_pdf
