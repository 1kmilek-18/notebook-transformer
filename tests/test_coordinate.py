"""座標変換ユーティリティのテスト."""

from src.utils.coordinate import cm_to_emu, emu_to_pt, inches_to_emu, pt_to_emu


class TestCoordinateConversion:
    """座標変換のテスト."""

    def test_pt_to_emu(self) -> None:
        """1pt = 12700 EMU."""
        assert pt_to_emu(1.0) == 12700
        assert pt_to_emu(72.0) == 914400  # 1インチ

    def test_emu_to_pt(self) -> None:
        """12700 EMU = 1pt."""
        assert emu_to_pt(12700) == 1.0
        assert emu_to_pt(914400) == 72.0

    def test_roundtrip(self) -> None:
        """ptからEMUへの変換と逆変換の一致."""
        original = 36.5
        converted = emu_to_pt(pt_to_emu(original))
        assert abs(converted - original) < 0.01

    def test_inches_to_emu(self) -> None:
        """1インチ = 914400 EMU."""
        assert inches_to_emu(1.0) == 914400
        assert inches_to_emu(10.0) == 9144000

    def test_cm_to_emu(self) -> None:
        """1cm = 360000 EMU."""
        assert cm_to_emu(1.0) == 360000
        assert cm_to_emu(2.54) == 914400  # 1インチ ≈ 2.54cm

    def test_pt_to_emu_zero(self) -> None:
        """0pt = 0 EMU."""
        assert pt_to_emu(0.0) == 0

    def test_pt_to_emu_rounding(self) -> None:
        """小数 pt は四捨五入で EMU に変換される."""
        assert pt_to_emu(1.5) == 19050  # 1.5 * 12700
