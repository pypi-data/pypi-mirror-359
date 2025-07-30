from pptx.enum.text import MSO_AUTO_SIZE, MSO_VERTICAL_ANCHOR
from pptx.text.text import TextFrame as PptxTextFrame
from pptx.util import Length as PptxLength

from tppt.pptx.converter import to_pptx_length
from tppt.pptx.shape import SubShape
from tppt.pptx.text.paragraph import Paragraph
from tppt.types._length import (
    EnglishMetricUnits,
    Length,
    LiteralLength,
    to_english_metric_units,
)


class TextFrame(SubShape[PptxTextFrame]):
    def __init__(self, pptx_obj: PptxTextFrame) -> None:
        super().__init__(pptx_obj)

    def add_paragraph(self) -> Paragraph:
        return Paragraph(self._pptx.add_paragraph())

    @property
    def auto_size(self) -> MSO_AUTO_SIZE | None:
        return self._pptx.auto_size

    @auto_size.setter
    def auto_size(self, value: MSO_AUTO_SIZE | None) -> None:
        self._pptx.auto_size = value

    def clear(self) -> None:
        self._pptx.clear()

    def fit_text(
        self,
        font_family: str = "Calibri",
        max_size: int = 18,
        bold: bool = False,
        italic: bool = False,
        font_file: str | None = None,
    ) -> None:
        self._pptx.fit_text(font_family, max_size, bold, italic, font_file)

    @property
    def margin_bottom(self) -> EnglishMetricUnits:
        return to_english_metric_units(self._pptx.margin_bottom)

    @margin_bottom.setter
    def margin_bottom(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.margin_bottom = to_pptx_length(value)

    @property
    def margin_left(self) -> EnglishMetricUnits:
        return to_english_metric_units(self._pptx.margin_left)

    @margin_left.setter
    def margin_left(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.margin_left = to_pptx_length(value)

    @property
    def margin_right(self) -> EnglishMetricUnits:
        return to_english_metric_units(self._pptx.margin_right)

    @margin_right.setter
    def margin_right(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.margin_right = to_pptx_length(value)

    @property
    def margin_top(self) -> EnglishMetricUnits:
        return to_english_metric_units(self._pptx.margin_top)

    @margin_top.setter
    def margin_top(self, value: Length | LiteralLength | PptxLength) -> None:
        self._pptx.margin_top = to_pptx_length(value)

    @property
    def paragraphs(self) -> tuple[Paragraph, ...]:
        return tuple(Paragraph(paragraph) for paragraph in self._pptx.paragraphs)

    @property
    def text(self) -> str:
        return self._pptx.text

    @text.setter
    def text(self, text: str) -> None:
        self._pptx.text = text

    @property
    def vertical_anchor(self) -> MSO_VERTICAL_ANCHOR | None:
        return self._pptx.vertical_anchor

    @vertical_anchor.setter
    def vertical_anchor(self, value: MSO_VERTICAL_ANCHOR | None) -> None:
        self._pptx.vertical_anchor = value

    @property
    def word_wrap(self) -> bool | None:
        return self._pptx.word_wrap

    @word_wrap.setter
    def word_wrap(self, value: bool | None) -> None:
        self._pptx.word_wrap = value
