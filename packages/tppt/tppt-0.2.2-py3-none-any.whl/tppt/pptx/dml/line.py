from pptx.dml.line import LineFormat as _PptxLineFormat
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.util import Emu as _PptxEmu

from tppt.pptx.converter import PptxConvertible
from tppt.pptx.dml.color import ColorFormat
from tppt.pptx.dml.fill import FillFormat
from tppt.pptx.enum.dml import LiteralLineDashStyle, to_pptx_line_dash_style
from tppt.types._length import EnglishMetricUnits, to_english_metric_units


class LineFormat(PptxConvertible[_PptxLineFormat]):
    """Line format."""

    @property
    def color(self) -> ColorFormat:
        return ColorFormat(self._pptx.color)

    @property
    def dash_style(self) -> MSO_LINE_DASH_STYLE | None:
        return self._pptx.dash_style

    @dash_style.setter
    def dash_style(
        self, value: MSO_LINE_DASH_STYLE | LiteralLineDashStyle | None
    ) -> None:
        self._pptx.dash_style = to_pptx_line_dash_style(value)

    def set_dash_style(
        self, value: MSO_LINE_DASH_STYLE | LiteralLineDashStyle | None
    ) -> "LineFormat":
        self.dash_style = value
        return self

    @property
    def fill(self) -> FillFormat:
        return FillFormat(self._pptx.fill)

    @property
    def width(self) -> EnglishMetricUnits | None:
        return EnglishMetricUnits(self._pptx.width)

    @width.setter
    def width(self, value: EnglishMetricUnits | _PptxEmu) -> None:
        self._pptx.width = to_english_metric_units(value)

    def set_width(self, value: EnglishMetricUnits | _PptxEmu) -> "LineFormat":
        self.width = value
        return self
